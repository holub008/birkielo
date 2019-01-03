import React from "react";

import {
    Grommet,
} from "grommet";
import { grommet } from "grommet/themes";

import {callBackend, isEmpty} from "../util/data";

import RacerList from "./RacerList";
import Spinner from "./Spinner";

class SearchResults extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            results: [],
            maxResults: this.props.maxResults ? this.props.maxResults : 10,
        };
    }

    updateResults(query) {
        callBackend(`/api/search?queryString=${query}&maxResults=${this.state.maxResults}`)
            .then(results => {
                this.setState({ results: results.candidates.slice(0, this.state.maxResults) });
            })
            // TODO dumping to console isn't a great long term solution
            .catch(error => {
                console.log(error);
            });
    }

    componentDidMount() {
        this.updateResults(this.props.query);
    }

    render() {
        if (isEmpty(this.state.results)) {
            // TODO differentiate unfinished request and no results (but current search is never empty)
            return(<Spinner />);
        }
        else {
            return(
                <Grommet theme={grommet}>
                    <RacerList racers={this.state.results} additionalColumns={null} />
                </Grommet>);
        }
    }
}

export default SearchResults;