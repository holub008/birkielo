import React from 'react';

import {
    Grommet,
    Box,
    Heading
} from "grommet";
import {grommet} from "grommet/themes/index";

import {Link} from 'react-router-dom';

import Spinner from "./Spinner";
import NotFound from "./NotFound";
import RacerList from "./RacerList";

import {callBackend, isEmpty, properGender} from "../util/data";


class RankedRacerList extends React.Component {

    constructor(props) {
       super(props);
       this.state = {
           rankings: {},
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
                // TODO dumping to console isn't a great long term solution
                .catch(error => console.log(error));
        }
    }

    render() {
        if (isEmpty(this.state.rankings) && !this.state.callComplete) {
            return(
                <Grommet theme={grommet}>
                    <Spinner/>
                </Grommet>
            );
        }
        else if (isEmpty(this.state.rankings)) {
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
                            <Link to={`/rankings/${this.props.gender === 'male' ? "women" : "men"}`}
                                  style={{textDecoration: "none", color:"rgb(144,96,235)"}}>
                                        {
                                            this.props.gender === 'male' ? "Women" : "Men"
                                        }
                            </Link>
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