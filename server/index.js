const express = require('express');
const path = require('path');
const db = require('./db');
const util = require('./util')

const app = express();

const port = process.env.PORT || 5000;

/**
 * API endpoints
 */
app.get('/api/test/', (req, res) => {
    data = {
      text: 'Lorem Ipsum',
    };

    res.send(data);
});

app.get('/api/racer/:id', async (req, res) => {
    // TODO we should cache known racer_ids in memory and short circuit out for unknown ones
    const racerId = req.params.id;

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
        text: `
            SELECT
                rr.gender_place,
                rr.overall_place,
                rr.duration,
                r.distance,
                r.discipline,
                eo.date as event_date,
                e.name as event_name
            FROM race_result rr
            JOIN race r
                ON rr.race_id = r.id
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
        console.log(racerElo);

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
