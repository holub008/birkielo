import React from 'react';

import {Link} from 'react-router-dom';

import {
    Grommet,
    Box,
    DataTable,
    Heading,
} from "grommet";
import { grommet } from "grommet/themes";

import Spinner from './Spinner';

import { callBackend } from "../util/data";

const COLUMNS = [
    {
        property: "event_name",
        header: "Event",
        render: datum =>
                <Link to={`/event/${datum.event_id}`} style={{textDecoration: "none", color:"rgb(144,96,235)"}}>
                    {datum.event_name}
                </Link>,
        primary: true,
        search: true
    }
];

class EventList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            events: [],
            callComplete: false,
        }
    }

    componentDidMount() {
        callBackend(`/api/events`)
            .then(data => this.setState({events: data.events}))
            .catch(error => {
                console.log(error);
            })
            .finally(() => this.setState({callComplete: true}));
    }

    render() {
        if (!this.state.callComplete) {
            return(<Spinner />);
        }

        return(
            <Grommet theme={grommet}>
                <Box margin={{left: "small"}}>
                    <Box margin="none">
                        <Heading margin="none">
                            All Events
                        </Heading>
                    </Box>
                    <Box margin="none" style={{maxWidth: 400}}>
                        <DataTable data={this.state.events} columns={COLUMNS}/>
                    </Box>
                </Box>
            </Grommet>
        );

    }
}

export default EventList;