import React from 'react';

import {
    Grommet,
    Box,
} from "grommet";
import {grommet} from "grommet/themes/index";

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
                racers: data.rankings,
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
            <Grommet theme={grommet}>
                <Box>
                    <Box direction="row-responsive">
                        {this.props.racerId.toString() + " Neighborhood (TODO)"}
                    </Box>
                    <Box style={{maxWidth:"700px"}}>
                        <RacerList racers={this.state.racers}/>
                    </Box>
                </Box>
            </Grommet>);
    }
}

export default RacerNeighborhood;