import React from 'react';

import {Box} from 'grommet';
import {Nodes} from "grommet-icons";

import '../styles/Spinner.css';

function Spinner() {
    return(
        <Box align="center">
            <Nodes size="xlarge" className="spinner"/>
        </Box>
    )
}

export default Spinner;