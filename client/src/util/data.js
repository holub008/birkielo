export async function callBackend(endpoint) {
    const response = await fetch(endpoint);
    var data = {};
    try {
        data = await response.json();
    }
    catch (error) {
        console.log(error);
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

export function milliTimeRender(millis, includeSeconds = true) {
    // in the !includeSeconds case, this has the effect of pushing any seconds >= 30 to the next minute
    const millisForRender = includeSeconds ? millis : (millis + 30 * 1000);

    const hours = Math.floor(millisForRender / 1000 / 60 / 60);
    const minutes = Math.floor((millisForRender - hours * 1000 * 60 * 60) / 1000 / 60);
    const seconds = Math.floor((millisForRender - hours * 1000 * 60 * 60 - minutes * 1000 * 60) / 1000);

    return includeSeconds ? `${hours}h${minutes}m${seconds}s` : `${hours}h${minutes}m`;
}

export function shortenDiscipline(discipline) {
    if (discipline === 'freestyle') {
        return 'fs';
    }
    else if (discipline === 'classic') {
        return 'cl';
    }
    else if (discipline === 'pursuit') {
        return 'pur';
    }
    else if (discipline === 'sitski') {
        return 'sit';
    }
    else {
        return discipline;
    }
}

export function getClickableColor() {
    return "rgb(144,96,235)";
}

export function getMetricHighlightColor() {
    return "rgb(17,147,154)";
}