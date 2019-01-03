const express = require('express');
const path = require('path');
const db = require('./db');
const store = require('./store');
const util = require('./util');
const data = require('./data');

const app = express();

const port = process.env.PORT || 5000;

const racerStore = new store.RacerStore();

/**
 * API endpoints
 */

app.get('/api/racers', async (req, res) => {
    const gender = req.query.gender;
    const minRank = parseInt(req.query.minRank);
    const racerId = parseInt(req.query.racerId);

    const pageSize = 50;

    if (((gender != 'male' && gender != 'female') || !minRank) && !racerId) {
        res.send({});
        return;
    }

    let rankings;
    if (racerId) {
        rankings = await data.rankingsNeighborhood(racerId, pageSize / 2);
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
        res.send({});
        return;
    }

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
            WITH race_size AS (
                SELECT
                    race_id as race_id,
                    gender,
                    count(1) as race_size
                FROM race_result
                GROUP BY race_id, gender
            )
            SELECT
                rr.gender_place,
                rr.overall_place,
                rs.race_size,
                rr.duration,
                r.distance,
                r.discipline,
                eo.date as event_date,
                e.name as event_name
            FROM race_result rr
            JOIN race r
                ON rr.race_id = r.id
            JOIN race_size rs
                ON r.id = rs.race_id
                    AND rr.gender = rs.gender
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
        racer: racer && racer.rows.length ? racer.rows[0] : null,
        results: racerResults ? racerResults.rows : null,
        metrics: racerMetrics ? racerMetrics.rows : null,
        relativeStatistics: relativeStatistics,
    });
});

/**
 * Serve the client side application
 * We don't expect this endpoint to be hit in dev, where webpack should be serving the hot-reloaded application
 * So, technically this gross conditional check isn't necessary, but it's kept on the off chance of weird bugs
 */
if (process.env.NODE_ENV === 'production') {
    app.use(express.static(path.join(__dirname, '../client/build')));

    // down the line, we need to consider how routing should be handled. for now, allow react to handle everything
    app.get('*', function(req, res) {
        res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
    });
}

app.listen(port, () => console.log(`Listening on port ${port}`));
