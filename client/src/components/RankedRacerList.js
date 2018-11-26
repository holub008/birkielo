import React from 'react';

import {
    DataTable,
    Grommet,
    Anchor,
    Box,
    Heading,
    Button
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
            <Anchor>
                <Link to={`/racer/${datum.racer_id}`}>{
                `${datum.first_name} ${datum.middle_name ? datum.middle_name : ""} ${datum.last_name}`}
                </Link>
            </Anchor>,
        align: "left",
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
           minRank: props.minRank,
           rankings: {}
       }
    }

    componentDidMount() {
        // note API gives us a fixed page size of 100 (or less)
        callBackend(`/api/racers?minRank=${this.state.minRank}&gender=${this.props.gender}`)
            .then(data => this.setState({ rankings: data.rankings }))
            // TODO dumping to console isn't a great long term solution
            .catch(error => console.log(error));
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
                        <Heading margin="xsmall">{`${capitalizeProper(this.props.gender)} Ranking`}</Heading>
                        <Button>
                            <Link to={`/rank/${this.props.gender === 'female' ? 'male' : 'female'}`}>
                                {this.props.gender === 'female' ? 'Male' : 'Female'}
                            </Link>
                        </Button>
                    </Box>
                    <DataTable columns={columns} data={this.state.rankings} margin="small"/>
                </Box>
            </Grommet>);
    }
}

export default RankedRacerList;