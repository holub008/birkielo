import React from 'react';

import {
    Box,
    Button,
    Text,
} from "grommet";
import { Close } from "grommet-icons";

import Spinner from './Spinner';
import SearchBar from './SearchBar';

import {
    callBackend,
    isEmpty,
    getMetricHighlightColor } from "../util/data";
import MetricTimeline from "./MetricTimeline";
import RacerResultHeadToHead from "./RacerResultHeadToHead";

class RacerComparison extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            racerIdsToRacerData: {},
            maxRacers: props.maxRacers ? props.maxRacers : 5,
            selectedRacerId: null,
        }
    }

    addRacer(racerId) {
        const racerIdStr = racerId.toString();
        const selectedRacerId = this.props.referenceRacerId === racerId ? null : racerId;

        const currentRacerIds = Object.keys(this.state.racerIdsToRacerData);

        // there is no mutex on this update, so a fast set of clicks could race condition past both checks
        // could use the double check pattern after the API call to make this a lot less likely (but still possible
        if (currentRacerIds.length < this.state.maxRacers && !currentRacerIds.includes(racerIdStr)) {
            callBackend(`/api/racer/${racerId}`)
                .then(data => {
                    // as noted above, this is still not in mutex
                    if (!Object.keys(this.state.racerIdsToRacerData).includes(racerIdStr)) {
                        const racersCopy = Object.assign({}, this.state.racerIdsToRacerData);
                        racersCopy[racerIdStr] = data;
                        this.setState({
                            racerIdsToRacerData: racersCopy,
                            selectedRacerId: selectedRacerId,
                        });
                    }
                })
                .catch(error => {
                    console.log(error);
                });
        }
    }

    removeRacer(racerId) {
        const racersCopy = Object.assign({}, this.state.racerIdsToRacerData);
        delete racersCopy[racerId];
        const updatedState = {racerIdsToRacerData: racersCopy};

        if (this.state.selectedRacerId === racerId) {
            updatedState.selectedRacerId = null;
        }

        this.setState(updatedState);
    }

    toggleSelectedRacer(racerId) {
        if (this.state.selectedRacerId === racerId) {
            this.setState({selectedRacerId: null});
        }
        else {
            this.setState({selectedRacerId: racerId});
        }

    }

    componentDidMount() {
        // if the component is linked from a racer, always add in that racer first
        // note we wish this component to be used without a referenceRacerId, so this is not a superfluous null check
        if (this.props.referenceRacerId) {
            this.addRacer(this.props.referenceRacerId);
        }
    }

    renderMetricTimeline() {
        const racerIds = Object.keys(this.state.racerIdsToRacerData);
        const timelines = racerIds.map(racerId => this.state.racerIdsToRacerData[racerId].metrics);
        const names = racerIds.map(racerId => this.state.racerIdsToRacerData[racerId].racer.first_name + " " +
            this.state.racerIdsToRacerData[racerId].racer.last_name);

        return(<MetricTimeline timelines={timelines} names={names}/>);
    }

    renderDeleteRacerButtons() {
        const racerIds = Object.keys(this.state.racerIdsToRacerData).map(racerId => parseInt(racerId));
        return(
            racerIds
                .filter(racerId => racerId !== this.props.referenceRacerId)
                .map(racerId => {
                    const racer = this.state.racerIdsToRacerData[racerId].racer;

                    const maxWidth = racerIds.length > 1 ? 100/(racerIds.length - 1) : 100;

                    return (
                        <Button
                            icon={<Close onClick={() => this.removeRacer(racerId)} />}
                            label={
                                <Box onClick={() => this.toggleSelectedRacer(racerId)}>
                                    {racer.first_name + " " + racer.last_name}
                                    </Box>
                            }
                            size="small"
                            key={racerId}
                            margin={{bottom:"small"}}
                            style={{maxWidth:`${maxWidth}%`}}
                            primary={this.state.selectedRacerId === racerId}
                            color={getMetricHighlightColor()}
                        />);
                })
        );
    }

    render() {
        if (isEmpty(this.state.racerIdsToRacerData)) {
            return(<Spinner/>);
        }

        const leftRacerId = this.props.referenceRacerId;
        const rightRacerId = this.state.selectedRacerId;
        return(
            <Box margin={{top:"medium", left:"small", right:"small"}}>
                <Box direction="row" alignSelf="center">
                    <Box alignSelf="center" border round width="xlarge">
                        <Box margin="small" width="medium" alignSelf="center">
                            <SearchBar maxResults={20}
                                       selectHandler={event => this.addRacer(parseInt(event.suggestion.value))}
                                       enterHandler={racer => this.addRacer(racer.racer_id)}
                                       placeholder="Search racers for comparison"
                            />
                        </Box>
                        <Box direction="row">
                            {
                                this.renderDeleteRacerButtons()
                            }
                        </Box>
                    </Box>
                </Box>
                <Box direction="row-responsive" justify="center" margin={{vertical: "large"}}>
                    <Box align="center" fill="horizontal" border="right">
                        {
                            rightRacerId ?
                                <RacerResultHeadToHead
                                    racerLeft={this.state.racerIdsToRacerData[leftRacerId]}
                                    racerRight={this.state.racerIdsToRacerData[rightRacerId]}
                                />
                                :
                                <Text>
                                    Search and select racers to compare race by race results
                                </Text>
                        }
                    </Box>
                    <Box align="center" fill="horizontal">
                        {
                            this.renderMetricTimeline()
                        }
                    </Box>
                </Box>
            </Box>
        )
    }
}

export default RacerComparison;