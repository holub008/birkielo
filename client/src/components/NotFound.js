import React from 'react';

import {
    Box,
    Grommet,
    Text,
    Image,
} from 'grommet';
import { grommet } from "grommet/themes";

function NotFound() {
    return(
        <Grommet theme={grommet}>
            <Box align="center" margin={{top:"medium"}}>
                <Text style={{fontStyle: "italic"}}>
                    Page not found
                </Text>
                <Image src="/images/skier.gif" style={{width:"50%", maxWidth:"400px"}}/>
            </Box>
        </Grommet>
    );
}

export default NotFound;