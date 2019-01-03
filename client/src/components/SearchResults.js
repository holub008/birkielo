import React from "react";
import {callBackend} from "../util/data";

import { DataTable } from "grommet";

class SearchResults extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            results: [],
            maxResults: this.props.maxResults ? this.props.maxResults : 10,
        };
    }

    updateResults(query) {
        callBackend(`/api/search?queryString=${query}&maxResults=${this.props.maxResults}`)
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
        return(<DataTable />);
    }
}

export default SearchResults;