import React from 'react';

import {
    Grommet,
    Box,
    DataTable,
    Heading,
} from "grommet";
import { grommet } from "grommet/themes";

import {Link} from 'react-router-dom';

import Spinner from './Spinner';
import NotFound from './NotFound';


import { callBackend } from "../util/data";

class EventSummary extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            callComplete: false,
            races: null,
            eventName: null,
        };
    }

    componentDidMount() {
        callBackend(`/api/events/${this.props.eventId}`)
            .then(data => this.setState({
                races: data.races,
                eventName: data.event_name,
            }))
            .catch(error => console.log(error))
            .finally(() => this.setState({callComplete: true}));
    }

    render() {
        if (this.state.callComplete && !this.state.races) {
            return(<NotFound/>);
        }
        else if (!this.state.races) {
            return(<Spinner/>);
        }

        return(
            <Grommet theme={grommet}>
                <Box>
                    <Heading margin="none">
                        {this.state.eventName}
                    </Heading>

                </Box>
            </Grommet>
        )


    }
}

export default EventSummary;