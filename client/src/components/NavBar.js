import React from 'react';

import {Link} from 'react-router-dom';

import {
    Grommet,
    Box,
    Image,
} from "grommet";
import { grommet } from "grommet/themes";
import { Menu } from 'grommet-icons';

import NavBarSearch from './NavBarSearch';


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
                        <NavBarSearch maxResults={5}/>
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