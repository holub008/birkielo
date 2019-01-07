const db = require('../db');


/**
 * this is a really simple implementation
 * I do not imagine site traffic will ever justify a more complicated implementation, for instance batching writes
 * and rate limiting if the site is getting whammied
 */
class EventLogger {

    constructor() {
        const siteEventTypeQuery = {
            name: "site_event_types",
            text: `SELECT unnest(enum_range(NULL::site_event)) as site_event`,
            values: [],
        };

        this.allowedEventTypes = [];
        this.shouldSurfaceDisallowedEventTypes = true;

        db.query(siteEventTypeQuery)
            .then(rs => {
                this.allowedEventTypes = rs.rows.map(row => row.site_event);
            })
            .catch(e => {
               console.log("Failed to query allowed event types - no logging will be done");
               console.log(e);
               this.shouldSurfaceDisallowedEventTypes = false;
            });
    }

    /**
     * handles ELB specific data extraction before logging
     */
    logForELBForwardedRequest(request,
                              event,
                              racerId=null) {
        // note we fall back to standard headers in the event of dev testing logging
        const ipAddress = request.headers['x-forwarded-for'] || request.connection.remoteAddress;
        const userAgent = request.headers['user-agent'];

        this.log(ipAddress, userAgent, event, racerId);
    }

    log(ipAddress,
              userAgent,
              event,
              racerId=null) {
        if (!this.allowedEventTypes.includes(event)) {
            if (this.shouldSurfaceDisallowedEventTypes) {
                console.log(`Unknown event type supplied to EventLogger: "${event}"`);
            }
            return;
        }

        const eventInsert = {
            name: "event_insert",
            text:`
                INSERT INTO user_tracking 
                    (ip_address, user_agent, event, racer_id) 
                VALUES 
                    ($1, $2, $3, $4)`,
            values: [ipAddress, userAgent, event, racerId],
        };

        db.query(eventInsert)
            .catch(e => {
               console.log(e);
            });
    }
}


module.exports = {
    EventLogger: EventLogger,
};