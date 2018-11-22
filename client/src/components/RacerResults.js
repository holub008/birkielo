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

function RacerResults(props) {
    const columns = [
        {
            property: "event_name",
            header: <Text>Event Name</Text>,
            primary: true,
        },
        {
            property: "event_date",
            header: "Date",
            render: datum =>
                datum.event_date && new Date(datum.event_date).toLocaleDateString("en-US"),
            align: "end",
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
            header: "gender_place",
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

    const results = props.results.map( result => {
            const resultCopy = Object.assign({}, result);
            resultCopy.percent_placement = result.gender_place / result.race_size;
            return(resultCopy);
        }
    );

    console.log(results);

    // TODO need to safety check for missing columns
    return(
        <Grommet theme={grommet}>
            <DataTable columns={columns} data={results} />
        </Grommet>
    )
}

export default RacerResults;