import React from 'react';

import {
    Box,
    Button,
} from "grommet";
import { Close } from "grommet-icons";


import Spinner from './Spinner';
import SearchBar from './SearchBar';

import {callBackend, isEmpty} from "../util/data";
import MetricTimeline from "./MetricTimeline";

// TODO if a woman & man are compared, it would be a good idea to note that they aren't compared on equal footing
class RacerComparison extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            racerIdsToRacerData: {},
            maxRacers: props.maxRacers ? props.maxRacers : 5,
        }
    }

    addRacer(racerId) {
        const racerIdStr = racerId.toString();

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
                        this.setState({racerIdsToRacerData: racersCopy});
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

        this.setState({racerIdsToRacerData: racersCopy});
    }

    componentDidMount() {
        // if the component is linked from a racer, always add in that racer first
        // note we wish this component to be used without a referenceRacerId, so this is not a superfluous null check
        if (this.props.referenceRacerId) {
            this.addRacer(parseInt(this.props.referenceRacerId));
        }
    }

    racerSelectHandler(event) {
        this.addRacer(parseInt(event.suggestion.value));
    }

    renderMetricTimeline() {
        const racerIds = Object.keys(this.state.racerIdsToRacerData);
        const timelines = racerIds.map(racerId => this.state.racerIdsToRacerData[racerId].metrics);
        const names = racerIds.map(racerId => this.state.racerIdsToRacerData[racerId].racer.first_name + " " +
            this.state.racerIdsToRacerData[racerId].racer.last_name);

        return(<MetricTimeline timelines={timelines} names={names}/>);
    }

    renderDeleteRacerButtons() {
        const racerIds = Object.keys(this.state.racerIdsToRacerData);
        return(
            racerIds
                .filter(racerId => racerId !== this.props.referenceRacerId)
                .map(racerId => {
                    const racer = this.state.racerIdsToRacerData[racerId].racer;

                    const maxWidth = racerIds.length > 1 ? 100/(racerIds.length - 1) : 100;

                    return (
                        <Button
                            icon={<Close/>}
                            label={racer.first_name + " " + racer.last_name}
                            onClick={() => this.removeRacer(racerId)}
                            size="small"
                            key={racerId}
                            margin={{bottom:"small"}}
                            style={{maxWidth:`${maxWidth}%`}}
                        />);
                })
        );
    }

    render() {
        if (isEmpty(this.state.racerIdsToRacerData)) {
            return(<Spinner/>);
        }

        return(
            <Box margin={{top:"medium", left:"small", right:"small"}}>
                <Box direction="row" alignSelf="center">
                    <Box alignSelf="center" border round width="xlarge">
                        <Box margin="small" width="medium" alignSelf="center">
                            <SearchBar maxResults={20}
                                       selectHandler={(event) => this.racerSelectHandler(event)}
                                       placeholder="Search racers for comparison"
                                       preventSearchRedirect/>
                        </Box>
                        <Box direction="row">
                            {
                                this.renderDeleteRacerButtons()
                            }
                        </Box>
                    </Box>
                </Box>
                {
                    this.renderMetricTimeline()
                }
            </Box>
        )
    }
}

export default RacerComparison;