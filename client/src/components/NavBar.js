import React, {Fragment} from 'react';

import { withRouter } from 'react-router-dom';

import {
    Grommet,
    Box,
    Image,
    Text,
    Menu
} from "grommet";
import { grommet } from "grommet/themes";
import { Menu as MenuIcon } from 'grommet-icons';

import SearchBar from './SearchBar';
import BirkieloLink from "./BirkieloLink";

import {getClickableColor} from "../util/data";

function UnWrappedMenuDrop(props) {
    return (
        <Box margin={{horizontal: "large"}}>
            <Menu
                dropAlign={{ top: "top"}}
                items={[
                    {
                        label:
                            <Text color={getClickableColor()}>
                                Home
                            </Text>,
                        // note onClick is supplied only to avoid transparency on the drop item :(
                        onClick: () => {props.history.push('/')},
                    },
                    {
                        label:
                            <Text color={getClickableColor()}>
                                About
                            </Text>,
                        onClick: () => {props.history.push('/about')},
                    },
                    {
                        label:
                            <Text color={getClickableColor()}>
                                Support
                            </Text>,
                        onClick: () => {props.history.push('/support')},
                    },
                    {
                        label:
                            <Text color={getClickableColor()}>
                                Privacy
                            </Text>,
                        onClick: () => {props.history.push('/privacy')},
                    },
                ]}
                icon={<MenuIcon color="#e6f1f0"/>}
            />
        </Box>
    );
}

const MenuDrop = withRouter(({history, ...forwardedProps}) =>
    <UnWrappedMenuDrop history={history} {...forwardedProps}/>);

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
                            <BirkieloLink to="/">
                                <Box align="center">
                                    <Image src="/images/logo.png" alt="" fit="cover"
                                           style={{height: "50%", width:"50%"}}/>
                                </Box>
                            </BirkieloLink>
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