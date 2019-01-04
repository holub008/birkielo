const db = require('../db');
const util = require('../util');


class RacerStore {
    constructor() {
        const racerQuery = {
            name: "racer",
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
        return this.racers
            // this is a quick hack for faster responses - limit the number of things we compute levenshtein distance on
            .filter(x => x.first_name && x.first_name.toLowerCase().startsWith(queryLower[0]) ||
                x.last_name && x.last_name.toLowerCase().startsWith(queryLower[0]))
            // TODO levenshtein computation should be pulled out - reducing nlgn ops to yield n ops
            .sort((a, b) => {
                const aLower = `${a.first_name} ${a.last_name}`.toLowerCase();
                const bLower = `${b.first_name} ${b.last_name}`.toLowerCase();
                // since the search may include prefixes (autocomplete), we don't wish to penalize longer names when the
                // query is short - else short names would always rank highest
                // TODO subtraction yields funky search results for small strings. this should be smoothed on query
                // length or made a ratio
                const aEditDistanceAdjusted = util.levenshtein(aLower, queryLower) - Math.max(0, aLower.length - queryLower.length);
                const bEditDistanceAdjusted = util.levenshtein(bLower, queryLower) - Math.max(0, bLower.length - queryLower.length);

                return aEditDistanceAdjusted - bEditDistanceAdjusted;
            });

    }

    containsRacerId(id) {
        return this.racers.filter(x => x.racer_id === id).length > 0
    }
}

module.exports = {
    RacerStore: RacerStore,
};