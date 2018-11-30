import React from 'react';

import {
    Box,
    Grommet,
    Tab,
    Tabs
} from "grommet";
import { grommet } from "grommet/themes";

import Help from "./Help";
import About from "./About";

import '../styles/Home.css';
import RankedRacerList from "./RankedRacerList";

function Home(props) {
    return(
        <div className="home">
            <Grommet theme={grommet}>
                <Box>
                    <Tabs flex>
                        <Tab title="About">
                            <About/>
                        </Tab>
                        <Tab title="Rankings">
                            <RankedRacerList minRank={1} gender={'male'}/>
                        </Tab>
                        <Tab title="Helping Out">
                            <Help/>
                        </Tab>
                    </Tabs>
                </Box>
            </Grommet>
        </div>
    );
}

export default Home;