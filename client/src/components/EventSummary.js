import React from 'react';

import {
    Grommet,
    Box,
    Heading,
    Accordion,
    AccordionPanel,
    Text,
} from "grommet";
import { grommet } from "grommet/themes";

import Spinner from './Spinner';
import NotFound from './NotFound';

import { callBackend } from "../util/data";
import RaceList from "./RaceList";
import MetricTimeline from "./MetricTimeline";

class EventSummary extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            callComplete: false,
            races: null,
            timeline: null,
            eventName: null,
            selectedTabIndex: -1,
        };
    }

    componentDidMount() {
        callBackend(`/api/events/${this.props.eventId}`)
            .then(data => this.setState({
                races: data.races,
                eventName: data.event_name,
                timeline: data.event_timeline,
            }))
            .catch(error => console.log(error))
            .finally(() => this.setState({callComplete: true}));
    }

    renderPanelHeader(title, active) {
        return(
            <Box direction="row" align="center" pad="medium" gap="small">
                <strong>
                    <Text>{title}</Text>
                </strong>
                <Text color="brand">{active ? "-" : "+"}</Text>
            </Box>
        );
    }

    render() {
        if (this.state.callComplete && !this.state.races) {
            return(<NotFound/>);
        }
        else if (!this.state.races) {
            return(<Spinner/>);
        }

        console.log(this.state.timeline)

        return(
            <Grommet theme={grommet}>
                <Box>
                    <Heading margin="none">
                        {this.state.eventName}
                    </Heading>
                </Box>
                <Accordion
                    activeIndex={this.state.selectedTabIndex}
                    onActive={newActiveIndex =>
                        this.setState({ selectedTabIndex: newActiveIndex })
                    }
                >
                    <AccordionPanel
                        header={this.renderPanelHeader("Results by Year", this.state.selectedTabIndex === 1)}
                    >
                        <Box>
                            <RaceList races={this.state.races} />
                        </Box>
                    </AccordionPanel>
                    <AccordionPanel header={this.renderPanelHeader("Statistics", this.state.selectedTabIndex === 2)}>
                        <MetricTimeline timelines={ [this.state.timeline] } names={[this.state.eventName]}/>
                    </AccordionPanel>
                </Accordion>
            </Grommet>
        )
    }
}

export default EventSummary;