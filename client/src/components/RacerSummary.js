import React from 'react';

import Spinner from './Spinner';
import RacerResults from './RacerResults';

import { Heading, Box, Grommet, Text, Grid } from 'grommet';
import { grommet } from "grommet/themes";

import {callBackend, isEmpty} from "../util/data";
import MetricDistribution from "./MetricDistribution";
import MetricTimeline from "./MetricTimeline";

class RacerSummary extends React.Component {

    state = {
        racerData: {},
    };

    componentDidMount() {
        callBackend("/api/racer/" + this.props.racerId)
            .then(data => this.setState({ racerData: data }))
            // TODO dumping to console isn't a great long term solution
            .catch(error => console.log(error));
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
                    <Box pad="small" border="left">
                        {
                            this.state.racerData.racer.gender
                        }
                    </Box>
                </Box>
                <Grid columns={{count: 2, size: "auto"}} margin={{vertical: "large"}}>
                    <Box pad="medium" border="right" align="center">
                        <Text>
                        {
                            // TODO need to actually sort by date!
                            "Birkielo: " + this.state.racerData.metrics[0].elo.toFixed(1)
                        }
                        </Text>
                        <MetricTimeline timeline={this.state.racerData.metrics}/>

                    </Box>
                    <Box pad="medium" align="center">
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
                </Grid>
                <Box margin={{vertical: "large"}}>
                    <RacerResults results={this.state.racerData.results}/>
                </Box>
            </Grommet>
        )
    }
}

export default RacerSummary;