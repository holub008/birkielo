const db = require('../db');


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

    getContents(){
        return this;
    }

    // performs a prefix scan for either a first or last name - use case being a simple autocomplete
    searchFirstOrLastName(query) {
        const queryLower = query.toLowerCase();
        return this.racers.filter(x => x.first_name && x.first_name.toLowerCase().startsWith(queryLower) ||
            x.last_name && x.last_name.toLowerCase().startsWith(queryLower));
    }

    // performs a scan for specifically a first name and a last name
    // if an exact match is made, returns just those. otherwise falls back to first name or last name match
    searchFirstAndLastName(firstName, lastName) {
        const firstNameLower = firstName.toLowerCase();
        const lastNameLower = lastName.toLowerCase();
        const fullMatches = this.racers.filter(x => x.first_name && x.first_name.toLowerCase() ===  firstNameLower &&
            x.last_name && x.last_name.toLowerCase() === lastNameLower);

        if (fullMatches.length) {
            return fullMatches;
        }

        return this.racers.filter(x => x.first_name && x.first_name.toLowerCase() === firstNameLower ||
            x.last_name && x.last_name.toLowerCase() === lastName.toLowerCase());
    }

    containsRacerId(id) {
        return this.racers.filter(x => x.racer_id === id).length > 0
    }
}

module.exports = {
    RacerStore: RacerStore,
};