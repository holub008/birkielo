import React from "react";

import {
    Box,
    Grommet,
    Select,
    Heading,
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

    updateResults(query, maxResults) {
        callBackend(`/api/search?queryString=${query}&maxResults=${maxResults}`)
            .then(results => {
                this.setState({
                    results: results.candidates.slice(0, maxResults),
                    maxResults: maxResults,
                });
            })
            // TODO dumping to console isn't a great long term solution
            .catch(error => {
                console.log(error);
            });
    }

    componentDidMount() {
        this.updateResults(this.props.query, this.state.maxResults);
    }

    render() {
        if (isEmpty(this.state.results)) {
            // TODO differentiate unfinished request and no results (but current search is never empty)
            return(<Spinner />);
        }
        else {
            const query = this.props.query;
            return(
                <Grommet theme={grommet}>
                    <Box pad="small">
                        <Heading level={3} margin={"small"}>
                            {
                                `Results for search '${query}'`
                            }
                        </Heading>
                        <Box style={{width:"30%", minWidth:"300px"}}>
                            <RacerList racers={this.state.results} additionalColumns={[]} />
                        </Box>
                        <Box style={{width:"10%", minWidth:"100px", marginBottom:"5%"}}>
                            <Select
                                id="select"
                                name="select"
                                value={this.state.maxResults.toString()}
                                options={["10", "25", "50"]}
                                onChange={({ option }) => this.updateResults(query, option)}
                            />
                        </Box>
                    </Box>
                </Grommet>);
        }
    }
}

export default SearchResults;