import React from 'react';

import {
    DataTable,
    Text,
    Box,
    Meter,
} from "grommet";
import { Contract, Expand } from 'grommet-icons';

import { Link } from 'react-router-dom';

import { dedupeDates, milliTimeRender } from "../util/data";

const LINK_COLOR = "rgb(144,96,235)";


const columns = [
    {
        property: "event_date_deduped",
        header: "Date",
        primary: true,
    },
    {
        property: "event_name",
        header: "Event Name",
        render: datum =>
            <Link to={`/event/${datum.event_id}`}
                  style={{textDecoration: "none", color: "rgb(144,96,235)", cursor: "pointer"}}>
                {
                    datum.event_name
                }
            </Link>,
    },
    {
        property: "discipline",
        header: "Discipline",
    },
    {
        property: "distance",
        header: "Distance (K)",
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
                    values={[
                        {
                            value: 100 - datum.percent_placement * 100,
                            color: "rgb(17,147,154)"
                        }
                    ]}
                    thickness="small"
                    size="small"
                />
            </Box>
        )
    },
];


// produces a limited (higher importance) set of columns from input columns
function shrinkColumns(columns) {
    const columnSubset = columns
        .filter(col => ['event_name', 'event_date_deduped', 'duration', 'gender_place'].includes(col.property));
    const shrunkenColumns = columnSubset.map(
        col => {
            const colCopy = Object.assign({}, col);
            colCopy.render = col.property === 'event_name' ?
                datum =>
                    datum.event_name.split(/[ ]+/).map(str => str.slice(0,7)).join(" ")
                :
                colCopy.render;
            return colCopy;
        }
    );

    return shrunkenColumns;
}

class RacerResults extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            shrinkTable: window.innerWidth < 650,
        };
    }

    render() {
        const resultsWithDedupedDates = dedupeDates(this.props.results.slice());
        const resultsForRender = resultsWithDedupedDates
            .sort((a, b) => new Date(b.event_date).getTime() - new Date(a.event_date).getTime())
            .map(result => {
                const resultCopy = Object.assign({}, result);
                resultCopy.percent_placement = result.gender_place / result.gender_racers;
                return (resultCopy);
            });

        const columnsForRender = this.state.shrinkTable ? shrinkColumns(columns) : columns;

        return (
            <Box>
                <Box
                    margin={{left: "small"}}
                    onClick={() => this.setState({shrinkTable: !this.state.shrinkTable})}
                    style={{cursor: "pointer" }}
                >
                    {
                        !this.state.shrinkTable ?
                            <Box direction="row">
                                <Text color = {LINK_COLOR}
                                      size="xsmall"
                                      margin={{right:"xsmall"}}>
                                    Trouble viewing?
                                </Text>
                                < Contract color={LINK_COLOR} size="small" />
                            </Box> :
                            <Box direction="row">
                                <Text color = {LINK_COLOR}
                                      size="xsmall"
                                      margin={{right:"xsmall"}}>
                                    View more columns?
                                </Text>
                                <Expand color = {LINK_COLOR} size="small" />
                            </Box>
                    }
                </Box>
                <DataTable columns={columnsForRender} data={resultsForRender}
                           sortable size="medium" margin="small"/>
            </Box>
        );
    }
}

export default RacerResults;