export async function callBackend(endpoint) {
    const response = await fetch(endpoint);
    var data = {};
    try {
        data = await response.json();
    }
    catch (error) {
        console.log(error);
        console.log(response);
    }
    if (response.status !== 200) throw Error(response);

    return data;
}

export function isEmpty(obj) {
    return !obj || (Object.keys(obj).length === 0 && obj.constructor === Object);
}

export function capitalizeProper(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

export function properGender(str) {
    return str === 'male' ? "Men": "Women";
}

export function apiGender(str) {
    if (str) {
        return str.toLowerCase() === 'men' ? 'male' : "female";
    }

    return str;
}

/**
 * although uncommon (or a data collection issue), some results may occur on the same date
 * this happens to be the p key into the results table, which gives the table rows duplicate keys
 * and leads to incorrect react behavior (rendering a row multiple times or not rendering)
 * so here, we "dedupe" by attaching a postfix counter
 */
export function dedupeDates(raceResults) {
    const groupedResults = raceResults.reduce(
        (groupedResults, item) => {
            const resultsOnDate = groupedResults[item['event_date']];
            const postfix = resultsOnDate ? `(${resultsOnDate.length})` : "";

            const updatedItem = Object.assign({}, item);
            const dateString = new Date(item.event_date).toISOString().split('T')[0];
            updatedItem.event_date_deduped = postfix ? `${dateString} ${postfix}` : dateString;

            return ({
                ...groupedResults,
                [updatedItem['event_date']]: [
                    ...(resultsOnDate || []),
                    updatedItem,
                ],
            });
        },
        {},
    );

    let finalResults = [];
    Object.keys(groupedResults).forEach(dateKey => {
        const resultsOnDate = groupedResults[dateKey];
        finalResults = finalResults.concat(resultsOnDate);
    });

    return finalResults;
}