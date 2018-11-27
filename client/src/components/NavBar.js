import React from 'react';

import {Link} from 'react-router-dom';
import {Menu,Grommet,Box} from 'grommet';
import { grommet } from "grommet/themes";


import '../styles/NavBar.css';

function NavBar(props) {
    return(
        <Grommet theme={grommet}>
        <Box direction="row-responsive" justify="between"
        style={{backgroundColor:"rgba(57, 62, 69, 0.82)"}}>
                <Link to="/">
                    <img className="navbar-logo" src="/images/logo.png" alt=""/>
                </Link>
            <Menu
                label="Actions"
                items={[
                    { label: "Launch", onClick: () => {} },
                    { label: "Abort", onClick: () => {} }
                ]}
            />
        </Box>
        </Grommet>
    );
}

export default NavBar;