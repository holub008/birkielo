import React from 'react';

import {
    Box,
    Text,
} from "grommet";

import Spinner from './Spinner';
import RacerList from './RacerList';

import {callBackend, isEmpty} from "../util/data";

class RacerNeighborhood extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            racers: {}
        }
    }

    componentDidMount() {
        // note API gives us a fixed page size of 50 (or less)
        callBackend(`/api/racers?racerId=${this.props.racerId.toString()}`)
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

    render() {
        if (isEmpty(this.state.racers)) {
            return(
                <Spinner/>
            );
        }

        return(
            <Box style={{maxWidth:"700px"}} margin={{top:"medium", left:"medium"}}>
                <Text size="large">Surrounding 50 Competitors</Text>
                <RacerList racers={this.state.racers}/>
            </Box>);
    }
}

export default RacerNeighborhood;