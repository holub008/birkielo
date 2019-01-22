import React from 'react';

import {
    Grommet,
    Box,
    Heading
} from "grommet";
import {grommet} from "grommet/themes/index";

import Spinner from "./Spinner";
import NotFound from "./NotFound";
import RacerList from "./RacerList";

import {callBackend, properGender} from "../util/data";
import BirkieloLink from "./BirkieloLink";


class RankedRacerList extends React.Component {

    constructor(props) {
       super(props);
       this.state = {
           rankings: [],
           callComplete: false,
       }
    }


    componentDidMount() {
        const gender = this.props.gender;
        if (gender === 'male' || gender === 'female') {
            // note API gives us a fixed page size of 50 (or less)
            callBackend(`/api/racers?minRank=${this.props.minRank}&gender=${gender}`)
                .then(data => this.setState({
                    rankings: data.rankings,
                }))
                .catch(error => console.log(error));
        }
    }

    render() {
        if (!this.state.rankings.length && !this.state.callComplete) {
            return(
                <Grommet theme={grommet}>
                    <Spinner/>
                </Grommet>
            );
        }
        else if (!this.state.rankings.length) {
            return(
                <Grommet theme={grommet}>
                    <NotFound />
                </Grommet>

            )
        }

        return(
            <Grommet theme={grommet}>
                <Box>
                    <Box direction="row">
                        <Heading margin="xsmall">
                            {`Top ${properGender(this.props.gender)}`}
                        </Heading>
                        <Box alignSelf="end" align="start">
                            <BirkieloLink to={`/rankings/${this.props.gender === 'male' ? "women" : "men"}`}>
                                {
                                    this.props.gender === 'male' ? "Women" : "Men"
                                }
                            </BirkieloLink>
                        </Box>
                    </Box>
                    <Box style={{maxWidth:"700px"}}>
                        <RacerList racers={this.state.rankings} />
                    </Box>
                </Box>
            </Grommet>);
    }
}

export default RankedRacerList;