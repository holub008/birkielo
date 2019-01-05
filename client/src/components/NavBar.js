import React, {Fragment} from 'react';

import {Link} from 'react-router-dom';

import {
    Grommet,
    Box,
    Image,
    Menu
} from "grommet";
import { grommet } from "grommet/themes";
import { Menu as MenuIcon } from 'grommet-icons';

import SearchBar from './SearchBar';

class MenuDrop extends React.Component {
    render() {
        return (
            <Box margin={{horizontal: "large"}}>
                <Menu
                    dropAlign={{ top: "top"}}
                    items={[
                        { label: <Link to={"/"} style={{textDecoration: "none", color:"rgb(144,96,235)"}}>
                                    Home
                                 </Link>,
                          onClick: () => {} },
                        { label: <Link to={"/about"} style={{textDecoration: "none", color:"rgb(144,96,235)"}}>
                                    About
                                 </Link>,
                          onClick: () => {} },
                        { label: <Link to={"/support"} style={{textDecoration: "none", color:"rgb(144,96,235)"}}>
                                Support
                            </Link>,
                            onClick: () => {} },
                    ]}
                    icon={<MenuIcon color="#e6f1f0"/>}
                />
            </Box>
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
                        {
                            this.props.searchBar?
                                <SearchBar maxResults={5}/>
                            :
                                <Fragment/>
                        }
                    </Box>
                    <Box align="center" alignSelf="center" style={{width:"33%"}}>
                            <Link to="/">
                                <Box align="center">
                                    <Image src="/images/logo.png" alt="" fit="cover"
                                           style={{height: "50%", width:"50%"}}/>
                                </Box>
                            </Link>
                    </Box>
                    <Box alignSelf="center" style={{width:"33%"}} align="end">
                        <MenuDrop/>
                    </Box>
                </Box>
            </Grommet>
        );
    }
}

export default NavBar;