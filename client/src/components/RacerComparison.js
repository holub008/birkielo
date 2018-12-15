import React from 'react';

import {
    Grommet,
    Box,
    Text,
    DataTable,
} from "grommet";

import Spinner from './Spinner';
import SearchBar from './SearchBar';

import {callBackend, isEmpty} from "../util/data";

// TODO if a woman & man are compared, it would be a good idea to note that they aren't compared on equal footing
class RacerComparison extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            racers:[],
            maxRacers: props.maxRacers ? props.maxRacers : 2,
        }
    }

    addRacer(racerId) {
        // TODO there is no mutex on this update, so a fast double click could race condition past both checks
        // could use the double check pattern after the API call to make this a lot less likely (but still possible
        const existingRacerIds = this.state.racers.map(racer => racer.racerId);
        if (this.state.racers.length < this.state.maxRacers && !existingRacerIds.includes(racerId)) {
            callBackend(`/api/racer/${racerId}`)
                .then(data => {
                    const racersCopy = this.state.racers.slice();
                    racersCopy.push({
                        racerId: racerId,
                        data: data,
                    });
                    this.setState({racers: racersCopy});
                })
                // TODO dumping to console isn't a great long term solution
                .catch(error => {
                    console.log(error);
                });
        }
    }

    componentDidMount() {
        // note we wish this component to be used without a referenceRacerId, so this is not a superfluous null check
        if (this.props.referenceRacerId) {
            this.addRacer(parseInt(this.props.referenceRacerId));
        }
    }

    racerSelectDecorator(racerId, content) {
        return(
            <Box onClick={() => this.addRacer(racerId)} >
                {
                    content
                }
            </Box>
        );
    }

    racerSelectHandler(event) {
        this.addRacer(parseInt(event.suggestion.value));
    }

    render() {
        if (this.state.racers.length === 0 && this.props.referenceRacerId) {
            return(<Spinner/>);
        }

        return(
            <Box margin={{top:"medium", left:"small"}}>
                <Box direction="row-responsive">
                    <Box width="medium">
                        <Text>
                            Pick racers for comparison:
                        </Text>
                        <Box margin={{top:"small"}}>
                            <SearchBar maxResults={20}
                                       suggestionDecorator={(racerId, content) => this.racerSelectDecorator(racerId, content)}
                                       selectHandler={(event) => this.racerSelectHandler(event)}/>
                        </Box>
                    </Box>
                    <Box>
                        <DataTable/>
                    </Box>
                </Box>
                {
                    JSON.stringify(this.state.racers.map(racer=> racer.racerId))
                }
            </Box>
        )
    }
}

export default RacerComparison;