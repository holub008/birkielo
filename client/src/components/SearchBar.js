import React from "react";
import {callBackend, getClickableColor} from "../util/data";

import {
    Anchor,
    TextInput,
    Box,
} from "grommet";

import { withRouter } from 'react-router-dom';

// note that history is react-router history - this is tantamount to a redirect (SPA)
function defaultSelectHandler(event, history) {
    history.push(`/racer/${event.suggestion.value}`);
}

class UnwrappedSearchBar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            suggestions: [],
            selectHandler: props.selectHandler? props.selectHandler : defaultSelectHandler,
            allowRequests: true,
            query:"",
        };
    }

    renderSuggestions() {
        return(this.state.suggestions.map(suggestion => {
            return({
                label:
                    <Box fill>
                        <Anchor>
                            {
                                `${suggestion.first_name} ${suggestion.last_name}`
                            }
                        </Anchor>
                    </Box>,
                value:`${suggestion.racer_id}`
            })
        }));
    }

    updateSuggestions(query) {
        // note this is not mutex - but that's ok
        if (this.state.allowRequests) {
            this.setState({allowRequests: false});
            callBackend(`/api/search?queryString=${query}&maxResults=${this.props.maxResults}`)
                .then(results => {
                    this.setState({suggestions: results.candidates.slice(0, this.props.maxResults)});
                })
                .catch(error => {
                    console.log(error);
                })
                .finally(() => this.setState({allowRequests: true}));
        }
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
            this.props.enterHandler ?
                this.props.enterHandler(this.state.suggestions[0]) :
                this.props.history.push(`/search/${this.state.query}`);
        }
    }

    render() {
        return (
            <TextInput
                type="search"
                onChange={(event) => this.onChange(event)}
                onSelect={(event) => this.state.selectHandler(event, this.props.history)}
                suggestions={this.renderSuggestions()}
                placeholder={this.props.placeholder ? this.props.placeholder : "Skier Search"}
                style={{color: getClickableColor(), backgroundColor: "#e6f1f0"}}
                onKeyPress={(event) => this.checkForAndHandleEnter(event)}
            />
        );
    }
}

const SearchBar = withRouter(({history, ...forwardedProps}) =>
    <UnwrappedSearchBar history={history} {...forwardedProps}/>);

export default SearchBar;