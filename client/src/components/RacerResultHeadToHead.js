import React from 'react';

import {
    DataTable,
    Box,
    Text,
} from 'grommet';
import { Contract, Expand } from 'grommet-icons';

import { dedupeDates, milliTimeRender, shortenDiscipline } from "../util/data";
import VennIcon from "./VennIcon";

const LINK_COLOR = "rgb(144,96,235)";

function racesMatch(raceLeft, raceRight) {
    return (raceLeft.event_name === raceRight.event_name &&
        raceLeft.event_date === raceRight.event_date &&
        raceLeft.distance === raceRight.distance &&
        raceLeft.discipline === raceRight.discipline);
}

function outerJoinRaceLists(racesLeft, racesRight,
                            nullFieldRender="") {
    /**
     * this belongs as a library call with hash/merge joins, but it's simple & avoids a dependency to roll own n^2
     * returns the outer join of the 2 race lists, with 2 added fields per race:
     * "racer_left_result" & "racer_right_result"
     */

    const distinctRaces=[];
    racesLeft.forEach(lr => {
        const matchingRaces = distinctRaces.filter(candidate => racesMatch(lr, candidate));
        if (!matchingRaces.length) {
            distinctRaces.push(Object.assign({}, lr));
        }
    });

    racesRight.forEach(rr => {
        const matchingRaces = distinctRaces.filter(candidate => racesMatch(rr, candidate));
        if (!matchingRaces.length) {
            distinctRaces.push(Object.assign({}, rr));
        }
    });

    const racesJoined = distinctRaces.map(distinctRace => {
       const matchingLeftRace = racesLeft.filter(rl => racesMatch(rl, distinctRace));
       const matchingRightRace = racesRight.filter(rr => racesMatch(rr, distinctRace));

       distinctRace['racer_left_result'] =  matchingLeftRace.length ?
           `${milliTimeRender(parseInt(matchingLeftRace[0].duration))} (${matchingLeftRace[0].overall_place} / ${matchingLeftRace[0].total_racers})`
           : nullFieldRender;
       distinctRace['racer_right_result'] =  matchingRightRace.length ?
           `${milliTimeRender(parseInt(matchingRightRace[0].duration))} (${matchingRightRace[0].overall_place} / ${matchingRightRace[0].total_racers})`
           : nullFieldRender;

       return distinctRace;
    });

    return racesJoined;
}

function innerJoinRaceLists(racesLeft, racesRight,
                            nullFieldRender="") {
    const racesJoined = [];
    racesLeft.forEach(rl => {
        const rightMatch = racesRight.filter(rr => racesMatch(rr, rl));
        if (rightMatch.length) {
            const rr = rightMatch[0];
            const raceCopy = Object.assign({}, rl);

            raceCopy['racer_left_result'] = `${milliTimeRender(parseInt(rl.duration))} (${rl.overall_place} / ${rl.total_racers})`;
            raceCopy['racer_right_result'] = `${milliTimeRender(parseInt(rr.duration))} (${rr.overall_place} / ${rr.total_racers})`;

            racesJoined.push(raceCopy);
        }
    });

    return racesJoined;
}

const BASE_COLUMNS = [
    {
        // note that this column has the unique event date for keying, which is unrelated to the actual render
        // this just prevents react weirdness if we, e.g., make the table sortable
        property: "event_date_deduped",
        header: "Event",
        render: datum => `${new Date(datum.event_date).getFullYear()} ${datum.event_name}`,
        primary: true,
    },
    {
        property: "discipline",
        header: "Race",
        render: datum => `${datum.discipline} ${datum.distance}K`,
    },
];

class RacerResultHeadToHead extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            join: "outer",
            shrinkTable: window.innerWidth < 600,
        }

    }

    getData(joinMethod="outer") {

        let joinedData;
        if (joinMethod === "outer") {
            joinedData = outerJoinRaceLists(this.props.racerLeft.results, this.props.racerRight.results);
        }
        else {
            joinedData = innerJoinRaceLists(this.props.racerLeft.results, this.props.racerRight.results);
        }

        const resultsForRender = dedupeDates(joinedData)
            .sort((a, b) => new Date(b.event_date).getTime() - new Date(a.event_date).getTime());

        return resultsForRender;
    }

    getStaticColumns() {
        if (this.state.shrinkTable) {
            return [{
                property: "event_date_deduped",
                header: "Event",
                render: datum => `${new Date(datum.event_date).getFullYear()} 
                    ${datum.event_name.split(/[ ]+/).map(str => str.slice(0,7)).join(" ")} 
                    ${shortenDiscipline(datum.discipline)} ${datum.distance}K`
            }];
        }
        else {
            return BASE_COLUMNS.slice();
        }
    }

    getDynamicColumns() {
        return(
            [
                {
                    property: "racer_left_result",
                    header: `${this.props.racerLeft.racer.first_name} ${this.props.racerLeft.racer.last_name} Finish`,
                },
                {
                    property: "racer_right_result",
                    header: `${this.props.racerRight.racer.first_name} ${this.props.racerRight.racer.last_name} Finish`,
                },
            ]
        );
    }

    render() {
        const columns = this.getStaticColumns().concat(this.getDynamicColumns());
        const data = this.getData(this.state.join);

        return(
            <Box>
                <Box direction="row" justify="center">
                    <Box
                        direction="row"
                        margin={{left:"small"}}
                        fill="horizontal"
                    >
                        <Box
                            border="right"
                            onClick={() => this.setState({join: "outer"})}
                            style={{cursor: this.state.join !== "outer" ? "pointer" : "auto" }}
                        >
                            <VennIcon join="outer" highlight={this.state.join !== "outer"}/>
                        </Box>
                        <Box
                            onClick={() => this.setState({join: "inner"})}
                            style={{cursor: this.state.join !== "inner" ? "pointer" : "auto" }}
                        >
                            <VennIcon join="inner" highlight={this.state.join !== "inner"}/>
                        </Box>
                    </Box>
                    <Box
                        margin={{right: "small"}}
                        onClick={() => this.setState({shrinkTable: !this.state.shrinkTable})}
                        style={{cursor: "pointer" }}
                        alignSelf="end"
                        align="end"
                        alignContent="end"
                        fill="horizontal"
                    >
                        {
                            !this.state.shrinkTable ?
                                <Box direction="row">
                                    <Text color = {LINK_COLOR}
                                          size="xsmall"
                                          margin={{right:"xsmall"}}
                                    >
                                        Trouble viewing?
                                    </Text>
                                    <Contract color={LINK_COLOR} size="small" />
                                </Box> :
                                <Box direction="row">
                                    <Text color = {LINK_COLOR}
                                          size="xsmall"
                                          margin={{right:"xsmall"}}
                                    >
                                        View more?
                                    </Text>
                                    <Expand color = {LINK_COLOR} size="small" />
                                </Box>
                        }
                    </Box>
                </Box>
                <DataTable columns={columns} data={data}
                       size="medium" margin="small"/>
            </Box>
        );
    }
}

export default RacerResultHeadToHead;