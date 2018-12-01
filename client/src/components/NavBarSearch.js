import React from "react";
import {callBackend} from "../util/data";

import {
    Anchor,
    TextInput,
    Box,
} from "grommet";

import { Link } from 'react-router-dom';

class NavBarSearch extends React.Component {
    state = {
        query: "",
        suggestions: [],
    };

    renderSuggestions() {
        return(this.state.suggestions.map(suggestion => {
            return({
                label:
                    <Link to={`/racer/${suggestion.racer_id}`} style={{textDecoration: "none"}}>
                        <Box fill>
                        <Anchor>
                        {
                            `${suggestion.first_name} ${suggestion.last_name}`
                        }
                        </Anchor>
                        </Box>
                    </Link>,
                value:`${suggestion.first_name} ${suggestion.last_name}`
            })
        }));
    }

    updateSuggestions(query) {
        callBackend(`/api/search?queryString=${query}&maxResults=${this.props.maxResults}`)
            .then(results => {
                this.setState({ suggestions: results.candidates, query: query });
            })
            // TODO dumping to console isn't a great long term solution
            .catch(error => {
                console.log(error);
                this.setState({query: query});
            });
    }

    onChange(event) {
        const query = event.target.value;

        if (query.length >= 3) {
            this.updateSuggestions(query);
        }
        else {
            this.setState({
                query: query,
                suggestions: [],
            });
        }
    }

    onSelect(event) {
        this.setState({query: event.suggestion.value});
    }

    handleKeyPress(event) {
        alert(event.charCode);
        if (event.charCode === 13 || event.keyCode === 13){
            alert('Should search here');
        }
    }

    render() {
        const query = this.state.query;
        return (
            <TextInput
                type="search"
                onChange={(event) => this.onChange(event)}
                onSelect={(event) => this.onSelect(event)}
                suggestions={this.renderSuggestions()}
                placeholder="Skier Search"
                style={{color: "rgb(144,96,235)", backgroundColor: "#e6f1f0", width:"50%"}}
            />
        );
    }
}

export default NavBarSearch;