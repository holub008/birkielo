import React from 'react';

import {
    DataTable,
    Text,
    Box,
    Meter,
} from "grommet";

function milliTimeRender(millis){
    // TODO it's too late to figure this out elegantly :)
    const hours = Math.floor(millis / 1000 / 60 / 60);
    const minutes = Math.floor((millis - hours * 1000 * 60 * 60) / 1000 / 60);
    return hours + "h" + minutes + "m"
}

const columns = [
    {
        property: "event_name",
        header: <Text>Event Name</Text>,
    },
    {
        property: "event_date_deduped",
        header: "Date",
        primary: true,
    },
    {
        property: "discipline",
        header: "Discipline",
    },
    {
        property: "distance",
        header: "Distance (K)",
        render: datum =>
            datum.distance
    },
    {
        property: "duration",
        header: "Time",
        render: datum =>
            milliTimeRender(datum.duration)
    },
    {
        property: "gender_place",
        header: "Gender Place",
    },
    {
        property: "percent_placement",
        header: "Percent Placement",
        render: datum => (
            <Box pad={{ vertical: "xsmall" }}>
                <Meter
                    values={[{ value: 100 - datum.percent_placement * 100 }]}
                    thickness="small"
                    size="small"
                />
            </Box>
        )
    },
];

// although uncommon (or a data collection issue), some results may occur on the same date
// this happens to be the p key into the results table, which gives the table rows duplicate keys
// and leads to incorrect react behavior (rendering a row multiple times or not rendering)
// so here, we "dedupe" by attaching a postfix counter
function dedupeDates(raceResults) {
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

    var finalResults = [];
    Object.keys(groupedResults).forEach(dateKey => {
        const resultsOnDate = groupedResults[dateKey];
        finalResults = finalResults.concat(resultsOnDate);
    });

    return finalResults;
}

function RacerResults(props) {
    const resultsWithDedupedDates = dedupeDates(props.results.slice());
    const resultsForRender = resultsWithDedupedDates
        .sort((a,b) => new Date(b.event_date).getTime() - new Date(a.event_date).getTime())
        .map( result => {
            const resultCopy = Object.assign({}, result);
            resultCopy.percent_placement = result.gender_place / result.race_size;
            return(resultCopy);
        });

    // TODO I want this to be sortable, but grommet sometimes randomly adds rows to the table when it is sorted...
    return(
        <DataTable columns={columns} data={resultsForRender}
                   sortable size="medium" margin="small" />
    )
}

export default RacerResults;