import React from 'react';
import {
    Box,
    Text,
    Button,
    Grommet,
} from "grommet";
import { MailOption, Github, Currency } from 'grommet-icons';
import { grommet } from "grommet/themes";

function Help() {
    return(
        <Grommet theme={grommet}>
            <Box>
                <Box
                    direction="row-responsive"
                    justify="center"
                    alignSelf="center"
                    pad="small"
                    gap="small"
                    width="xx-large">
                    <Box fill pad="small" align="center">
                        <Box pad="medium" align="center" background="dark-3" round gap="small">
                            <MailOption size="large"/>
                            <Text alignSelf="center">
                                Reach out with any suggestions, questions, & issues with result quality
                            </Text>
                            <Button label="Email Karl" onClick={() =>
                                window.location.href = "mailto:karljholub@gmail.com"
                            } />
                        </Box>
                    </Box>
                    <Box fill pad="small" align="center">
                        <Box pad="medium" align="center" background="dark-3" round gap="small">
                            <Github size="large"/>
                            <Text>Tech-capable & interested? Accepting pull requests & issues</Text>
                            <Button label="On GitHub" href="https://github.com/holub008/birkielo"/>
                        </Box>
                    </Box>
                    <Box fill pad="small" align="center">
                        <Box pad="small" align="center" background="dark-3" round gap="small">
                            <Currency size="large"/>
                            <Text>I cover the ~$30/month to host this site; if you enjoy it, please consider donating
                                to groups growing the ski community.</Text>
                            <Button label="Loppet Foundation" onClick={() =>
                                window.location.href = "https://www.loppet.org/donate/"
                            }/>
                        </Box>
                    </Box>
                </Box>
            </Box>
        </Grommet>
    );
}

export default Help;