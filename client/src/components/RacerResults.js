import React from 'react';

import {
    DataTable,
    Grommet,
    Text,
    Box,
    Meter,
} from "grommet";
import { grommet } from "grommet/themes";

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
        property: "event_date",
        header: "Date",
        render: datum =>
            datum.event_date && new Date(datum.event_date).toISOString().split('T')[0],
        align: "end",
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
        align: "end",
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

function RacerResults(props) {

    const results = props.results.slice()
        .sort((a,b) => new Date(b.event_date).getTime() - new Date(a.event_date).getTime())
        .map( result => {
            const resultCopy = Object.assign({}, result);
            resultCopy.percent_placement = result.gender_place / result.race_size;
            return(resultCopy);
        });

    // TODO I want this to be sortable, but grommet sometimes randomly adds rows to the table when it is sorted...
    return(
        <Grommet theme={grommet}>
            <DataTable columns={columns} data={results}
                       size="medium" margin="small" />
        </Grommet>
    )
}

export default RacerResults;