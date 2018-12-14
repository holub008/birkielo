import React from 'react';

import {
    Grommet,
    Anchor,
    Box,
    Heading
} from "grommet";
import {grommet} from "grommet/themes/index";

import Spinner from "./Spinner";
import RacerList from "./RacerList";

import {callBackend, isEmpty, properGender} from "../util/data";


class RankedRacerList extends React.Component {

    constructor(props) {
       super(props);
       this.state = {
           gender: props.gender,
           rankings: {}
       }
    }

    loadData(gender) {
        if (gender === 'male' || gender === 'female') {
            // note API gives us a fixed page size of 50 (or less)
            callBackend(`/api/racers?minRank=${this.props.minRank}&gender=${gender}`)
                .then(data => this.setState({
                    rankings: data.rankings,
                    gender: gender,
                }))
                // TODO dumping to console isn't a great long term solution
                .catch(error => console.log(error));
        }
    }

    componentDidMount() {
        this.loadData(this.props.gender)
    }

    render() {
        if (isEmpty(this.state.rankings)) {
            return(
                <Spinner/>
            );
        }

        return(
            <Grommet theme={grommet}>
                <Box>
                    <Box direction="row-responsive">
                        <Heading margin="xsmall">{`Top ${properGender(this.state.gender)}`}</Heading>
                        <Anchor alignSelf="end"
                                onClick={() => {
                                    const updatedGender= this.state.gender === 'male' ? "female" : "male";
                                    this.loadData(updatedGender);
                                }}>
                                    {
                                        this.state.gender === 'male' ? "Women" : "Men"
                                    }
                        </Anchor>
                    </Box>
                    <Box style={{maxWidth:"700px"}}>
                        <RacerList racers={this.state.rankings}/>
                    </Box>
                </Box>
            </Grommet>);
    }
}

export default RankedRacerList;