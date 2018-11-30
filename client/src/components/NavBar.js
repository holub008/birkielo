import React from 'react';

import {Link} from 'react-router-dom';

import {
    Grommet,
    Box,
    Image,
    TextInput,
} from "grommet";
import { grommet } from "grommet/themes";

import { Menu } from 'grommet-icons';

const suggestions = Array(5)
    .fill()
    .map((_, i) => `suggestion ${i + 1}`);

class SuggestionsTextInput extends React.Component {
    state = { value: "" };

    onChange = event => this.setState({ value: event.target.value });

    onSelect = event => this.setState({ value: event.suggestion });

    render() {
        const { value } = this.state;
        return (
            <TextInput
                value={value}
                onChange={this.onChange}
                onSelect={this.onSelect}
                suggestions={suggestions}
                placeholder="Skier Search"
                style={{color: "rgb(144,96,235)", backgroundColor: "#e6f1f0", width:"50%"}}
            />
        );
    }
}

class NavBar extends React.Component {
    constructor(props) {
        super(props);

        this.state = {};
    }

    render() {
        return(
            <Grommet theme={grommet}>
                <Box background="rgba(57, 62, 69, 0.82)"
                     direction="row"
                     justify="between">
                    <Box alignSelf="center"
                         width="33%"
                         align="start"
                         margin={{left:"small"}}
                    >
                        <SuggestionsTextInput/>
                    </Box>
                    <Box align="center" alignSelf="center" style={{width:"33%"}}>
                        <Link to="/">
                            <Image src="/images/logo.png" alt="" fit="cover"
                                   style={{height: "50%", width:"50%"}}/>
                        </Link>
                    </Box>
                    <Box alignSelf="center" style={{width:"33%"}} align="end">
                        <Box margin="medium">
                            <Menu color="#e6f1f0" />
                        </Box>
                    </Box>
                </Box>
            </Grommet>
        );
    }
}

export default NavBar;