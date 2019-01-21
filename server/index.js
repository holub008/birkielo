const express = require('express');
const path = require('path');
const db = require('./db');
const store = require('./store');
const logging = require('./logging');

const util = require('./util');
const data = require('./data');

const app = express();

const port = process.env.PORT || 5000;
const isProduction = process.env.NODE_ENV === "production";

const racerStore = new store.RacerStore();
const raceMetricStore = new store.RaceMetricStore([2018]);
const eventLogger = new logging.EventLogger();

/**
 * API endpoints
 */

// this just for AWS ELB health checks, an endpoint with no https redirect :(
app.get('/status', (req, res) => {
    res.send({
        content: "hail overlord bezos"
    });
});

// tsl redirect logic
// this function is highly deployment specific & will likely need to change depending on it
// in current deployment, all requests (http on 80 & https on 443) resolve to AWS ELB
// ELB forwards all these requests to the server EC2 instance over http.
// the X-Forwarded-Proto header represents the protocol of the ELB requests. if request to ELB is over http, we'd like
// the server to issue a https redirect. if the request to ELB is over https, all is well & the ELB <-> EC2 commune is
// over http
// TODO it might be worthwhile to prop up nginx or similar in front of express, to reduce dependency on AWS behavior
// this would also allow deployment of HSTS (which isn't a big deal for this site, with no cookies & little incentive
// for mitm)
function requireHTTPS(req, res, next) {
    if (req.get('X-Forwarded-Proto') !== 'https') {
        return res.redirect('https://' + req.get('host') + req.url);
    }
    next();
}

if (isProduction) {
    app.use(requireHTTPS);
}

app.get('/api/racers', async (req, res) => {
    const gender = req.query.gender;
    const minRank = parseInt(req.query.minRank);
    const racerId = parseInt(req.query.racerId);
    const pageSize = parseInt(req.query.nRacers) || 50;

    if (((gender != 'male' && gender != 'female') || !minRank) && !racerId) {
        res.send({});
        return;
    }

    let rankings;
    if (racerId) {
        rankings = await data.rankingsNeighborhood(racerId, Math.floor(pageSize / 2));
    }
    // note that via a preconditions check above, minRank is defined
    else {
        rankings = await data.rankings(gender, minRank, pageSize);
    }
    res.send({
        rankings: rankings
    })
});

// note that maxResults returns an arbitrary set up to maxResults (i.e. not selected via relevance)
app.get('/api/search/', (req, res) => {
    var maxResults = req.query.maxResults;
    const queryString = req.query.queryString;

    if (!queryString) {
        res.send({});
        return;
    }
    if (!maxResults || maxResults > 1000) {
        maxResults = 1000;
    }

    // since long search strings can be slow & don't add much value in a name search
    const queryStringLimited = queryString.slice(0, 25);
    const matches = racerStore.fuzzyRankNames(queryString).slice(0, maxResults);

    res.send({
        candidates: matches ? matches : null,
    });
});

app.get('/api/racer/:id', async (req, res) => {
    const racerId = parseInt(req.params.id);

    if (!racerId || !racerStore.containsRacerId(racerId)) {
        res.send({valid: false});
        return;
    }

    // async, does not block progression
    eventLogger.logForELBForwardedRequest(req, "racer_summary", racerId);

    const racerQuery = {
        name: "racer",
        text: `
            SELECT
                r.first_name,
                r.middle_name,
                r.last_name,
                r.gender,
                r.age_lower,
                r.age_upper,
                r.location
            FROM racer r
            WHERE
                r.id = $1 
        `,
        values: [ racerId ]
    };

    // TODO almost all these queries could all be run in parallel...
    const racer = await db.query(racerQuery)
        .catch(e => console.error(`Failed to query racer details for id = '${racerId}'`));

    const racerResultQuery = {
        name: "racer_results",
        // TODO the race size calculation is a full table scan & this query may not quite produce a valid ranking
        text: `
            WITH gender_race_size AS (
                SELECT
                    race_id as race_id,
                    gender,
                    count(1) as racers
                FROM race_result
                GROUP BY race_id, gender
            ),
            total_race_size AS (
                SELECT
                    race_id,
                    SUM(racers) as racers
                 FROM gender_race_size
                 GROUP BY race_id
            )
            SELECT
                rr.gender_place,
                rr.overall_place,
                grs.racers as gender_racers,
                trs.racers as total_racers,
                rr.duration,
                r.id as race_id,
                r.distance,
                r.discipline,
                eo.date as event_date,
                e.name as event_name,
                e.id as event_id
            FROM race_result rr
            JOIN race r
                ON rr.race_id = r.id
            JOIN gender_race_size grs
                ON r.id = grs.race_id
                    AND rr.gender = grs.gender
            JOIN total_race_size trs
                ON r.id = trs.race_id
            JOIN event_occurrence eo
                ON r.event_occurrence_id = eo.id
            JOIN event e
                ON eo.event_id = e.id
            WHERE
                rr.racer_id = $1
        `,
        values: [ racerId ]
    };

    const racerResults = await db.query(racerResultQuery)
        .catch(e => console.error(`Failed to query race results for racer_id = '${racerId}'`));

    const racerMetricsQuery = {
        name: "racer_metrics",
        text: `
            SELECT
                rm.date,
                rm.elo
            FROM racer_metrics rm
            WHERE
                rm.racer_id = $1
            ORDER BY date desc
        `,
        values: [ racerId ]
    };

    const racerMetrics = await db.query(racerMetricsQuery)
        .catch(e => console.error(`Failed to query race metrics for racer_id = '${racerId}'`));

    let relativeStatistics;
    if (racer && racer.rows.length &&
        racerMetrics && racerMetrics.rows.length) {
        const racerGender = racer.rows[0].gender;
        const racerElo = racerMetrics.rows[0].elo;

        // TODO this query is expensive to run on a per-request basis
        const rankQuery = {
            name: "rank_metrics",
            text: `
                SELECT DISTINCT ON (rm.racer_id)
                    rm.racer_id,
                    LAST_VALUE(elo) OVER racer_window as elo
                FROM racer_metrics rm
                JOIN racer r
                    ON rm.racer_id = r.id
                WHERE
                    r.gender = $1
                WINDOW racer_window AS (
                    PARTITION BY rm.racer_id ORDER BY rm.date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                )
        `,
            values: [ racerGender ]
        };

        const scoreResultSet = await db.query(rankQuery)
            .catch(e => console.error(`Failed to query rankings.`));

        if (scoreResultSet && scoreResultSet.rows.length) {
            const rankings = scoreResultSet.rows.map(row => row.elo);
            relativeStatistics = {
                totalDistribution: util.histogramBin(rankings),
                ranking: util.rank(rankings, racerElo),
                totalCompetitors: rankings.length
            }
        }

    }

    res.send({
        valid: true,
        racer: racer && racer.rows.length ? racer.rows[0] : null,
        results: racerResults ? racerResults.rows : null,
        metrics: racerMetrics ? racerMetrics.rows : null,
        relativeStatistics: relativeStatistics,
    });
});

app.get('/api/events/', async (req, res) => {

    const eventsQuery = {
        name: "events",
        text: `
            SELECT
                e.name as event_name,
                e.id as event_id
            FROM event e
        `,
        values: [],
    };

    const events = await db.query(eventsQuery)
        .catch(e => console.error(`Failed to query all events`));

    res.send({events: events ? events.rows : []});
});

app.get('/api/events/:id', async (req, res) => {
    const eventId = parseInt(req.params.id);

    if (!eventId) {
        res.send({
            event_name: null,
            races: []
        });
        return;
    }

    const raceQuery = {
        name: "races_for_event",
        text: `
            SELECT
                e.name as event_name,
                eo.date as event_date,
                r.discipline as discipline,
                r.distance as distance,
                r.id as race_id
            FROM event e
            JOIN event_occurrence eo
                ON e.id = eo.event_id
            JOIN race r
                ON r.event_occurrence_id = eo.id
            WHERE
                e.id = $1
        `,
        values: [ eventId ],
    };

    const races = await db.query(raceQuery)
        .catch(e => console.error(`Failed to query races for event_id = '${eventId}'`));

    const eventTimelineQuery = {
        name: "event_timeline",
        text: `
            SELECT
              eo.date,
              -- node-postgres doesn't handle integer types nicely
              CAST(COUNT(distinct rr.racer_id) AS FLOAT) as n_racers,
              AVG(rm.elo) as elo
            FROM event e
            JOIN event_occurrence eo
              ON e.id = eo.event_id
            JOIN race r 
              ON r.event_occurrence_id = eo.id
            JOIN race_result rr
              ON rr.race_id = r.id
            JOIN racer_metrics rm
              ON rm.racer_id = rr.racer_id
                -- TODO this is a somewhat weak reliance
                AND eo.date = rm.date
            WHERE
                e.id = $1
            GROUP BY 1
            ORDER BY 1 desc
        `,
        values: [ eventId ],
    };

    const eventTimeline = await db.query(eventTimelineQuery)
        .catch(e => console.error(`Failed to query event timeline for event_id = '${eventId}'`));

    const averageEloByYear = raceMetricStore.getAverageEloByYear();

    res.send({
        event_name: races && races.rows.length ? races.rows[0].event_name : null,
        event_timeline: eventTimeline ? eventTimeline.rows : [],
        average_timeline: averageEloByYear,
        races: races ? races.rows : [],
    });
});

app.get('/api/races/:id', async (req, res) => {
    const raceId = parseInt(req.params.id);

    if (!raceId) {
        res.send({results:[], raceMetadata: {}});
        return;
    }

    const raceResultQuery = {
        name: "results_for_race",
        text: `
            SELECT
                e.name as event_name,
                e.id as event_id,
                eo.date,
                r.discipline,
                r.distance,
                rcr.id as racer_id,
                rr.name,
                rr.gender,
                rr.gender_place,
                rr.overall_place,
                rr.duration
            FROM race r
            JOIN event_occurrence eo
                ON eo.id = r.event_occurrence_id
            JOIN event e
                ON e.id = eo.event_id
            JOIN race_result rr
                ON r.id = rr.race_id
            LEFT JOIN racer rcr
                ON rcr.id = rr.racer_id
            WHERE
                r.id = $1
        `,
        values: [ raceId ],
    };

    const results = await db.query(raceResultQuery)
        .catch(e => console.error(`Failed to query results for race_id = '${raceId}'`));

    const raceMetadata = {
        eventName: results && results.rows.length ? results.rows[0].event_name : null,
        eventId: results && results.rows.length ? results.rows[0].event_id : null,
        date: results && results.rows.length ? results.rows[0].date : null,
        discipline: results && results.rows.length ? results.rows[0].discipline : null,
        distance: results && results.rows.length ? results.rows[0].distance : null,
    };

    const resultsMinimal = results ?
        results.rows.map(result => {
            const {racer_id, name, gender, gender_place, overall_place, duration, ...shared } = result;
            return {racer_id, name, gender, gender_place, overall_place, duration}
        })
        :
        [];

    res.send({
        raceMetadata: raceMetadata,
        results: resultsMinimal,
    });
});

app.get('/api/events/flow/:year', (req, res) => {
    const year = parseInt(req.params.year);

    if (!year) {
        res.send({});
        return;
    }

    const flowData = raceMetricStore.getFlowData(year);
    res.send({flowData:flowData});
});

app.get('/api/events/share/:year', (req, res) => {
    const year = parseInt(req.params.year);

    if (!year) {
        res.send({});
        return;
    }

    const shareData = raceMetricStore.getShareData(year);
    res.send({shareData: shareData});
});

/**
 * Serve the client side application
 * We don't expect this endpoint to be hit in dev, where webpack should be serving the hot-reloaded application
 * So, technically this gross conditional check isn't necessary, but it's kept on the off chance of weird bugs
 */
if (isProduction) {
    // this middleware just for logging site load when the root is hit
    // pretty gross, but I don't know how to inject logging into express.static
    app.get('*', function(req, res, next) {
        if (req.path === "/") {
            eventLogger.logForELBForwardedRequest(req, "site_load");
        }
        next();
    });

    app.use(express.static(path.join(__dirname, '../client/build')));

    // down the line, we need to consider how routing should be handled. for now, allow react to handle everything
    app.get('*', function(req, res) {
        eventLogger.logForELBForwardedRequest(req, "site_load");
        res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
    });
}

app.listen(port, () => console.log(`Listening on port ${port}`));
