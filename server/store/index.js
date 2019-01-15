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

module.exports = {
    RacerStore: RacerStore,
};