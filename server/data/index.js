const db = require('../db');

module.exports ={
    rankings: async (gender, minRank, pageSize) => {
        const rankQuery = {
            name: "rankings",
            text: `
                WITH racer_to_elo AS (
                    SELECT DISTINCT ON (rm.racer_id)
                        rm.racer_id,
                        r.first_name,
                        r.middle_name,
                        r.last_name,
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
                ),
                ranked_racers AS (
                    SELECT
                        roe.racer_id,
                        roe.first_name,
                        roe.middle_name,
                        roe.last_name,
                        roe.elo,
                        RANK() OVER (ORDER BY roe.elo DESC) as rank
                    FROM racer_to_elo roe
                )
                SELECT
                    rr.racer_id,
                    rr.first_name,
                    rr.middle_name,
                    rr.last_name,
                    rr.elo,
                    rr.rank as rank
                FROM ranked_racers rr
                WHERE
                    rr.rank >= $2
                    AND rr.rank <= $2 + $3
        `,
            values: [ gender, minRank, pageSize ]
        };

        const rankings = await db.query(rankQuery)
            .catch(e => console.error(`Failed to query rankings.`));

        return rankings ? rankings.rows : null;
    },
    // note that n is the number of neighbors both above and below the given racer id
    rankingsNeighborhood: async (racerId, n) => {
        const neighborhoodQuery = {
            name: "rankings_neighborhood",
            text: `
                WITH center_racer_gender AS (
                  SELECT
                    r.gender
                  FROM racer r
                  WHERE
                    r.id = $1  
                ),
                racer_to_elo AS (
                    SELECT DISTINCT ON (rm.racer_id)
                        rm.racer_id,
                        r.first_name,
                        r.middle_name,
                        r.last_name,
                        LAST_VALUE(elo) OVER racer_window as elo
                    FROM racer_metrics rm
                    JOIN racer r
                        ON rm.racer_id = r.id
                    JOIN center_racer_gender crg
                        ON crg.gender = r.gender
                    WINDOW racer_window AS (
                        PARTITION BY rm.racer_id ORDER BY rm.date
                        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                    )
                ),
                ranked_racers AS (
                    SELECT
                        roe.racer_id,
                        roe.first_name,
                        roe.middle_name,
                        roe.last_name,
                        roe.elo,
                        RANK() OVER (ORDER BY roe.elo DESC) as rank
                    FROM racer_to_elo roe
                ),
                center_racer AS (
                    SELECT
                        rr.rank
                    FROM ranked_racers rr
                    WHERE
                        rr.racer_id = $1
                )
                SELECT
                    rr.racer_id,
                    rr.first_name,
                    rr.middle_name,
                    rr.last_name,
                    rr.elo,
                    rr.rank as rank
                FROM ranked_racers rr
                JOIN center_racer cr
                    ON cr.rank >= (rr.rank - $2) 
                        AND cr.rank <= (rr.rank + $2) 
        `,
            values: [ racerId, n ]
        };

        const neighborhood = await db.query(neighborhoodQuery)
            .catch(e => console.error(`Failed to query rankings neighborhood.`));

        return neighborhood ? neighborhood.rows : null;
    },
};