import React from 'react';

import {
    Grommet,
    Box,
    Heading,
    Text,
    DataTable,
} from "grommet";
import { grommet } from "grommet/themes";
import {Link} from 'react-router-dom';

import Spinner from './Spinner';
import NotFound from './NotFound';

import { callBackend } from "../util/data";

const COLUMNS = [
    // TODO this could be duplicated in e.g. ties or the like
    {
        property: "overall_place",
        header: "Overall Place",
        primary: true,
    },
    {
        property: "name",
        header: "Name",
        search: true,
    },
    {
        property: "gender",
        header: "Gender",
    },
    {
        property: "duration",
        header: "Time",
    },
    {
        property: "gender_place",
        header: "Gender Place",
    },
];

class RaceResult extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            results: null,
            raceMetadata: null,
            callComplete: false,
        };
    }

    componentDidMount() {
        callBackend(`/api/races/${this.props.raceId}`)
            .then(data => this.setState({
                results: data.results.sort((a,b) => a.overall_place - b.overall_place),
                raceMetadata: data.raceMetadata,
            }))
            .catch(error => console.log(error))
            .finally(() => this.setState({callComplete: true}));
    }

    render() {
        if (!this.state.results && this.state.callComplete) {
            return(<Grommet theme={grommet}> <NotFound /> </Grommet>)
        }

        if (!this.state.callComplete) {
            return(<Grommet theme={grommet}> <Spinner /> </Grommet>);
        }

        return(
            <Grommet theme={grommet}>
                <Box>
                    <Box direction="column">
                        <Box>
                            <Link to={`/event/${this.state.raceMetadata.eventId}`}
                                  style={{textDecoration: "none", color:"rgb(144,96,235)"}}>
                                <Heading margin="none" size="small">
                                    {this.state.raceMetadata.eventName}
                                </Heading>
                            </Link>
                        </Box>
                        <Box direction="row">
                            <Box border="right" margin={{right: "small"}} pad="small">
                                <Text>{(new Date(this.state.raceMetadata.date)).toISOString().split('T')[0]}</Text>
                            </Box>
                            <Box border="right" margin={{right: "small"}} pad="small">
                                <Text>{`${this.state.raceMetadata.distance} K`}</Text>
                            </Box>
                            <Box pad="small">
                                <Text>{this.state.raceMetadata.discipline}</Text>
                            </Box>
                        </Box>

                    </Box>
                    <Box>
                        <DataTable data={this.state.results} columns={COLUMNS} sortable size="large"/>
                    </Box>
                </Box>
            </Grommet>
        );
    }
}

export default RaceResult;