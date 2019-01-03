import React from "react";
import {callBackend} from "../util/data";

import {
    Anchor,
    TextInput,
    Box,
} from "grommet";

import { Link } from 'react-router-dom';

function defaultSuggestionDecorator(racerId, content) {
    return(
        <Link to={`/racer/${racerId}`} style={{textDecoration: "none"}}>
            { content }
        </Link>
    );
}

function defaultSelectHandler(event) {
    window.location.href = event.suggestion.label.props.to;
}

class SearchBar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            suggestions: [],
            suggestionDecorator: props.suggestionDecorator ? props.suggestionDecorator : defaultSuggestionDecorator,
            selectHandler: props.selectHandler? props.selectHandler : defaultSelectHandler,
            query:"",
        };
    }

    renderSuggestions() {
        return(this.state.suggestions.map(suggestion => {
            return({
                label:
                    this.state.suggestionDecorator(suggestion.racer_id,
                        <Box fill>
                            <Anchor>
                                {
                                    `${suggestion.first_name} ${suggestion.last_name}`
                                }
                            </Anchor>
                        </Box>
                    ),
                value:`${suggestion.racer_id}`
            })
        }));
    }

    updateSuggestions(query) {
        // TODO there should be a timeout (e.g. 500 millis to execute the search to avoid needless requests
        callBackend(`/api/search?queryString=${query}&maxResults=${this.props.maxResults}`)
            .then(results => {
                this.setState({ suggestions: results.candidates.slice(0, this.props.maxResults) });
            })
            // TODO dumping to console isn't a great long term solution
            .catch(error => {
                console.log(error);
            });
    }

    onChange(event) {
        const query = event.target.value;
        this.setState({query: query});

        if (query.length >= 3) {
            this.updateSuggestions(query);
        }
        else {
            this.setState({
                suggestions: [],
            });
        }
    }

    // this is gross, but grommet does not seem to provide a method for handling "enter"
    checkForAndHandleEnter(event) {
        if (event.key === 'Enter') {
            window.location.href = `/search?query=${this.state.query}`
        }
    }

    render() {
        return (
            <TextInput
                type="search"
                onChange={(event) => this.onChange(event)}
                onSelect={(event) => this.state.selectHandler(event)}
                suggestions={this.renderSuggestions()}
                placeholder="Skier Search"
                style={{color: "rgb(144,96,235)", backgroundColor: "#e6f1f0"}}
                onKeyPress={(event) => this.checkForAndHandleEnter(event)}
            />
        );
    }
}

export default SearchBar;