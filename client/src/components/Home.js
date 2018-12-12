import React from 'react';

import {
    Box,
    Grommet,
    Tab,
    Tabs
} from "grommet";
import { grommet } from "grommet/themes";

import '../styles/Home.css';
import RankedRacerList from "./RankedRacerList";
import SearchBar from "./SearchBar";

function Home(props) {
    return(
        <div className="home">
            <Grommet theme={grommet}>
                <Box>
                    <Tabs flex>
                        <Tab title="Search">
                            <Box>
                            <Box margin="medium" width="large" alignSelf="center">
                                <SearchBar maxResults={20}/>
                            </Box>
                            </Box>
                        </Tab>
                        <Tab title="Rankings">
                            <RankedRacerList minRank={1} gender={'male'}/>
                        </Tab>
                    </Tabs>
                </Box>
            </Grommet>
        </div>
    );
}

export default Home;