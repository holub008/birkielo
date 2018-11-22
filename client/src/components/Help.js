import React from 'react';
import {
    Box,
    Text,
    Button
} from "grommet";
import { MailOption, Cli, Currency } from 'grommet-icons';

function Help() {
    return(
        <Box
            direction="row-responsive"
            justify="center"
            align="center"
            pad="medium"
            gap="medium"
        >
            <Box fill pad="small" align="center">
                <Box pad="medium" align="center" background="dark-3" round gap="small">
                    <Cli size="large"/>
                    <Text>Accepting pull requests & issues</Text>
                    <Button label="Contribute on GitHub" onClick={() =>
                        window.open("https://github.com/holub008/birkielo")
                    }/>
                </Box>
            </Box>
            <Box fill pad="small" align="center">
                <Box pad="medium" align="center" background="dark-3" round gap="small">
                    <MailOption size="large"/>
                    <Text alignSelf="center">Suggestions & result quality</Text>
                    <Button label="Email Karl" onClick={() =>
                        window.location.href = "mailto:karljholub@gmail.com"
                    } />
                </Box>
            </Box>
            <Box fill pad="small" align="center">
                <Box pad="medium" align="center" background="dark-3" round gap="small">
                    <Currency size="large"/>
                    <Text>Web hosting costs</Text>
                    <Button label="Free (for now)" onClick={() => {}} />
                </Box>
            </Box>
        </Box>
    );
}

export default Help;