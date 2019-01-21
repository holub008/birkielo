const db = require('../db');
const util = require('../util');


class RacerStore {
    constructor() {
        const racerQuery = {
            name: "racer_store",
            text: `
            SELECT
                r.id as racer_id,
                r.first_name,
                r.middle_name,
                r.last_name,
                r.gender
            FROM racer r
        `,
            values: []
        };

        this.racers = [];

        db.query(racerQuery)
            .then(rs => {
                this.racers = rs.rows;
                Object.freeze(this);
            })
            .catch(e => {
                throw "Failed to query racers: " + e;
            });
    }

    fuzzyRankNames(query) {
        const queryLower = query.toLowerCase();
        const candidateRacers = this.racers
            // this is a quick hack for faster responses - limit the number of things we compute levenshtein distance on
            .filter(x => x.first_name && x.first_name.toLowerCase().startsWith(queryLower[0]) ||
                x.last_name && x.last_name.toLowerCase().startsWith(queryLower[0]));

        // caching distances because levenshtein is an n^2 procedure
        const racerIdsToDistance = {};
        candidateRacers.forEach(racer => {
            const nameLower = `${racer.first_name} ${racer.last_name}`.toLowerCase();

            racerIdsToDistance[racer.racer_id] =  util.levenshtein(nameLower, queryLower)
                - Math.max(0, nameLower.length - queryLower.length);
        });

        // since the search may include prefixes (autocomplete), we don't wish to penalize longer names when the
        // query is short - else short names would always rank highest
        // TODO subtraction yields funky search results for small strings. this should be smoothed on query
        // length or made a ratio
        return candidateRacers
            .sort((a, b) => racerIdsToDistance[a.racer_id] - racerIdsToDistance[b.racer_id]);

    }

    containsRacerId(id) {
        return this.racers.filter(x => x.racer_id === id).length > 0
    }
}

class RaceMetricStore {
    /*
     this class acts as a pre-loaded cache on commonly requested & expensive to compute data
     it is NOT intended to be used for anything other than toys - e.g. visualizations, where faithfulness to DB is not
     that important
     TODO could be feasible to replace with materialized views
     */

    constructor(years) {

        this.flowData = {};

        years.forEach(year => {
            const raceFlowQuery = {
                name: "race_flow",
                text: `
                    with year_races as (
                        select
                            r.id as race_id,
                            eo.date,
                            e.name as event_name
                        from event_occurrence eo
                        join event e
                            on e.id = eo.event_id
                        join race r
                            on r.event_occurrence_id = eo.id
                        where
                            eo.date >= to_date($1::varchar, 'yyyy')
                            and eo.date <  to_date($1::varchar, 'yyyy') + interval '1 year'
                    ),
                    repeat_racers as (
                        select
                            rr.racer_id
                        from race_result rr
                        join year_races yr
                            on yr.race_id = rr.race_id
                        group by 
                            rr.racer_id
                        having
                            count(1) > 1
                    ),
                    repeat_racer_races as (
                        select
                          rr.racer_id,
                          yr.date,
                          yr.event_name
                        from repeat_racers rpr
                        join race_result rr
                          on rpr.racer_id = rr.racer_id
                        join year_races yr
                          on yr.race_id = rr.race_id
                    ),
                    source_target_pairings as (
                        select
                          rrr1.racer_id,
                          rrr1.event_name as source_event,
                          rrr1.date as source_date,
                          rrr2.event_name as target_event,
                          rrr2.date as target_date,
                          rrr2.date - rrr1.date as days_between,
                          row_number() OVER (partition by rrr1.racer_id, rrr1.date order by rrr2.date - rrr1.date) as event_source_date_proximity
                        from repeat_racer_races rrr1
                        join repeat_racer_races rrr2
                          on rrr1.racer_id = rrr2.racer_id
                            and rrr1.date < rrr2.date 
                        order by racer_id
                    )
                    select
                         stp.source_event,
                         stp.source_date,
                         stp.target_event,
                         stp.target_date,
                         count(1) as n_racers
                    from source_target_pairings stp
                    where
                      stp.event_source_date_proximity = 1
                    group by
                      stp.source_event, 
                      stp.source_date, 
                      stp.target_event, 
                      stp.target_date
            `,
                values: [year.toString()]
            };

            db.query(raceFlowQuery)
                .then(rs => {
                    this.flowData[year] = rs.rows;
                })
                .catch(e => {
                    throw "Failed to query racer flow: " + e;
                });
        });

        this.shareData = {};

        years.forEach(year => {
            const eventShareQuery = {
                name: "event_share",
                text: `
                        select
                          e.id as event_id,
                          e.name as event_name,
                          avg(rm.elo) as mean_elo,
                          count(1) as total_entrants
                        from race_result rr
                        join racer rcr
                          on rcr.id = rr.racer_id
                        join race r
                          on r.id = rr.race_id
                        join event_occurrence eo
                          on r.event_occurrence_id = eo.id
                        join event e
                          on e.id = eo.event_id
                        join racer_metrics rm
                          on rm.racer_id = rcr.id
                            and rm.date = eo.date
                        where
                            eo.date >= to_date($1::varchar, 'yyyy')
                            and eo.date <  to_date($1::varchar, 'yyyy') + interval '1 year'
                        group by 1  
                        order by 2 desc
                `,
                values: [year.toString()]
            };

            db.query(eventShareQuery)
                .then(rs => {
                    this.shareData[year] = rs.rows;
                })
                .catch(e => {
                    throw "Failed to query event share: " + e;
                });
        });

        this.averageEloByYear = [];

        const averageEloQuery = {
            name: "average_elo_by_year",
            text: `
                        select
                            make_date(cast(date_part('year', rm.date) as integer), 1, 1) as date,
                            avg(rm.elo) as elo
                        from racer_metrics rm
                        group by 1
                        order by 1 desc
                `,
            values: []
        };

        db.query(averageEloQuery)
            .then(rs => {
                this.averageEloByYear = rs.rows;
            })
            .catch(e => {
                throw "Failed to query average elo by year: " + e;
            });
    }

    getFlowData(year) {
        return this.flowData[year];
    }

    getShareData(year) {
        return this.shareData[year];
    }

    getAverageEloByYear() {
        return this.averageEloByYear;
    }
}


module.exports = {
    RacerStore: RacerStore,
    RaceMetricStore: RaceMetricStore,
};