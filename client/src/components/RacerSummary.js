import React from 'react';

import { Heading, Box, Grommet, Text } from 'grommet';
import { grommet } from "grommet/themes";
import { Elevator, Group, User, StatusUnknown, StatusCritical } from "grommet-icons";

import Spinner from './Spinner';
import RacerResults from './RacerResults';
import RacerNeighborhood from './RacerNeighborhood';
import BirkieloLink from './BirkieloLink';
import MetricDistribution from "./MetricDistribution";
import MetricTimeline from "./MetricTimeline";
import RacerComparison from "./RacerComparison";
import NotFound from "./NotFound";

import {callBackend, isEmpty, getClickableColor, } from "../util/data";

const LINK_COLOR = getClickableColor();
const VALID_PROFILE_STATES = ['user', 'neighborhood', 'compare'];

class RacerSummary extends React.Component {
    constructor(props){
        super(props);

        const validatedProfileState = VALID_PROFILE_STATES.includes(props.view) ? props.view : "user";
        this.state = {
            racerData: {},
            profileState: validatedProfileState,
        };
    }

    componentDidMount() {
        callBackend("/api/racer/" + this.props.racerId)
            .then(data => this.setState({ racerData: data }))
            .catch(error => console.log(error));
    }

    getName() {
        return this.state.racerData.racer.first_name + " " + this.state.racerData.racer.last_name;
    }

    renderProfile() {
        return(
            <div>
                <Box direction="row-responsive" justify="center" margin={{vertical: "large"}}>
                    <Box pad="medium" border="right" align="center" fill="horizontal">
                        <Box direction="row" align="center" gap="small">
                            <Text>
                                {
                                    "Birkielo: " + this.state.racerData.metrics
                                        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())[0].elo
                                        .toFixed(1)
                                }
                            </Text>
                            <BirkieloLink to="/about/computation">
                                <StatusUnknown color={LINK_COLOR}/>
                            </BirkieloLink>
                        </Box>
                        {
                            this.state.racerData.metrics.length > 1 ?
                                <MetricTimeline timelines={ [this.state.racerData.metrics] } names={[this.getName()]}/>
                                : <StatusCritical size="large"/>
                        }
                    </Box>
                    <Box pad="medium" align="center" fill="horizontal">
                        <Text>
                            {
                                "Birkielo ranking: " + this.state.racerData.relativeStatistics.ranking +
                                " / " + this.state.racerData.relativeStatistics.totalCompetitors
                            }
                        </Text>
                        <MetricDistribution totalDistribution=
                                                {this.state.racerData.relativeStatistics.totalDistribution}
                                            racerScore={this.state.racerData.metrics[0].elo}/>
                    </Box>
                </Box>
                <Box margin={{vertical: "large"}} align="center">
                    <RacerResults results={this.state.racerData.results}/>
                </Box>
            </div>
        );
    }

    getDisplayContent() {
        if (this.state.profileState === "user") {
            return(this.renderProfile());
        }
        else if (this.state.profileState === 'neighborhood') {
            return(<RacerNeighborhood racerId={this.props.racerId}/>);
        }
        else if(this.state.profileState === 'compare') {
            return(<RacerComparison referenceRacerId={parseInt(this.props.racerId)}/>)
        }
    }

    getIconColor(contentName) {
        if (contentName === this.state.profileState) {
            return (null);
        }
        else {
            return(LINK_COLOR);
        }
    }

    render() {
        if (isEmpty(this.state.racerData)) {
            return(
                <Spinner/>
            );
        }
        else if (!this.state.racerData.valid) {
            return(<NotFound/>);
        }

        // TODO the icons need a proper tooltip / hover text
        return(
            <Grommet theme={grommet}>
                <Box direction="row-responsive" gap="small">
                    <Box direction="row">
                        <Box>
                            <Heading size="medium" margin="xsmall">
                                {
                                    this.getName()
                                }
                            </Heading>
                        </Box>
                        <Box pad="small" border="left">
                            <Text>
                            {
                                this.state.racerData.racer.gender
                            }
                            </Text>
                        </Box>
                    </Box>
                    <Box pad="small" align="center" direction="row" gap="small" border="left">
                        <div title="Skier Profile" style={{cursor: "pointer"}}>
                            <User onClick={() => this.setState({profileState:"user"})}
                                  color={ this.getIconColor("user") }
                            />
                        </div>
                        <div title="Nearest Competitors" style={{cursor: "pointer"}}>
                            <Elevator onClick={() => this.setState({profileState:"neighborhood"})}
                                      color={ this.getIconColor("neighborhood") }
                            />
                        </div>
                        <div title="Compare to Competitors" style={{cursor: "pointer"}}>
                            <Group onClick={() => this.setState({profileState:"compare"})}
                                   color={ this.getIconColor("compare") }
                            />
                        </div>
                    </Box>
                </Box>
                {
                    this.getDisplayContent()
                }
            </Grommet>
        )
    }
}

export default RacerSummary;