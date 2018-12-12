import React from 'react';

import { Heading, Box, Grommet, Text } from 'grommet';
import { grommet } from "grommet/themes";
import { Elevator, Group, User } from "grommet-icons";

import Spinner from './Spinner';
import RacerResults from './RacerResults';
import RacerNeighborhood from './RacerNeighborhood';

import {callBackend, isEmpty} from "../util/data";
import MetricDistribution from "./MetricDistribution";
import MetricTimeline from "./MetricTimeline";

class RacerSummary extends React.Component {

    state = {
        racerData: {},
        profileState: "user",
    };

    componentDidMount() {
        callBackend("/api/racer/" + this.props.racerId)
            .then(data => this.setState({ racerData: data }))
            // TODO dumping to console isn't a great long term solution
            .catch(error => console.log(error));
    }

    renderProfile() {
        return(
            <div>
                <Box direction="row-responsive" justify="center" margin={{vertical: "large"}}>
                    <Box pad="medium" border="right" align="center" fill="horizontal">
                        <Text>
                            {
                                // TODO need to actually sort by date!
                                "Birkielo: " + this.state.racerData.metrics[0].elo.toFixed(1)
                            }
                        </Text>
                        <MetricTimeline timeline={this.state.racerData.metrics}/>

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
    }

    getIconColor(contentName) {
        if (contentName === this.state.profileState) {
            return (null);
        }
        else {
            return("rgb(144,96,235)");
        }
    }

    render() {
        if (isEmpty(this.state.racerData)) {
            return(
                <Spinner/>
            );
        }

        return(
            <Grommet theme={grommet}>
                <Box direction="row-responsive" gap="small">
                    <Box>
                        <Heading size="medium" margin="xsmall">
                            {this.state.racerData.racer.first_name + " " + this.state.racerData.racer.last_name}
                        </Heading>
                    </Box>
                    <Box pad="small" border="left" alignSelf="end">
                        {
                            this.state.racerData.racer.gender
                        }
                    </Box>
                    <Box pad="small" alignSelf="end" direction="row-responsive" gap="small" border="left">
                        <User onClick={() => this.setState({profileState:"user"})}
                              color={ this.getIconColor("user") }/>
                        <Elevator onClick={() => this.setState({profileState:"neighborhood"})}
                                  color={ this.getIconColor("neighborhood") }/>
                        <Group onClick={() => this.setState({profileState:"compare"})}
                               color={ this.getIconColor("compare") }/>
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