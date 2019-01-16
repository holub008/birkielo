import React from 'react';

import {
    Box,
    Text,
    RangeInput,
} from "grommet";

import Spinner from './Spinner';
import RacerList from './RacerList';

import {callBackend, isEmpty} from "../util/data";

const MAX_RACERS = 51;

class RacerNeighborhood extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            racers: [],
            nRacers: props.nRacers ? props.nRacers : 5,
        }
    }

    componentDidMount() {
        // note API gives us a fixed page size of 50 (or less)
        callBackend(`/api/racers?racerId=${this.props.racerId.toString()}&nRacers=${MAX_RACERS}`)
            .then(data => this.setState({
                racers: data.rankings.map(racer => {
                    if (racer.racer_id === parseInt(this.props.racerId)) {
                        racer.highlight = true;
                    }

                    return(racer);
                }),
            }))
            // TODO dumping to console isn't a great long term solution
            .catch(error => console.log(error));
    }

    onRangeChange = event => this.setState({ value: event.target.value });

    render() {
        if (isEmpty(this.state.racers)) {
            return(
                <Spinner/>
            );
        }

        const racersListMid = this.state.racers.length / 2;
        const interval = this.state.nRacers / 2;
        const racersForDisplay = this.state.racers.slice(racersListMid - interval,  racersListMid + interval);

        // TODO the DataTable render in RacerList is atrociously laggy - just use a DOM table
        return(
            <Box style={{maxWidth:"700px"}} margin={{top:"medium", left:"medium"}}>
                <Text size="large">
                    {`Neighboring ${this.state.nRacers - 1} Competitors`}
                </Text>
                <RangeInput
                    onChange={event => this.setState({ nRacers: event.target.value })}
                    value={this.state.nRacers}
                    step={2}
                    min={1}
                    max={MAX_RACERS}
                />
                <RacerList racers={racersForDisplay}/>
            </Box>);
    }
}

export default RacerNeighborhood;