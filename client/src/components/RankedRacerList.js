import React from 'react';

import {
    DataTable,
    Grommet,
    Anchor,
    Box,
    Heading
} from "grommet";
import {grommet} from "grommet/themes/index";
import {Link} from 'react-router-dom';

import Spinner from "./Spinner";
import {callBackend, isEmpty, capitalizeProper} from "../util/data";

const columns = [
    {
        property: "rank",
        header: "Rank",
        primary: true,
    },
    {
        property: "first_name",
        header: "Racer",
        render: datum =>
            <Anchor align="center">
                <Link to={`/racer/${datum.racer_id}`}
                      style={{color:"rgb(144,96,235)"}}>{
                `${datum.first_name} ${datum.middle_name ? datum.middle_name : ""} ${datum.last_name}`}
                </Link>
            </Anchor>,
    },
    {
        property: "elo",
        header: "Birkielo",
        render: datum =>
            datum.elo.toFixed(1)
    },
];

class RankedRacerList extends React.Component {

    constructor(props) {
       super(props);
       this.state = {
           gender: props.gender,
           rankings: {}
       }
    }

    loadData(gender) {
        // note API gives us a fixed page size of 50 (or less)
        callBackend(`/api/racers?minRank=${this.props.minRank}&gender=${gender}`)
            .then(data => this.setState({
                rankings: data.rankings,
                gender: gender,
            }))
            // TODO dumping to console isn't a great long term solution
            .catch(error => console.log(error));
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
                        <Heading margin="xsmall">{`${capitalizeProper(this.state.gender)} Ranking`}</Heading>
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
                        <DataTable columns={columns} data={this.state.rankings} size="large"/>
                    </Box>
                </Box>
            </Grommet>);
    }
}

export default RankedRacerList;