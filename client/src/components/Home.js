import React from 'react';

import {
    Box,
    Grommet,
    Tab,
    Tabs,
    Text,
    Anchor
} from "grommet";
import { grommet } from "grommet/themes";

import Help from "./Help";
import About from "./About";

import '../styles/Home.css';

function Home(props) {
    return(
        <div className="home">
            <Grommet theme={grommet}>
                <Box>
                    <Tabs flex>
                        <Tab title="About">
                            <About/>
                        </Tab>
                        <Tab title="Demos">
                            <Text>
                                Check out a few racer demos (in absence of a list page at present):
                            </Text>
                            <Box>
                                <Anchor href="/racer/9264">Caitlin Gregg</Anchor>
                                <Anchor href="/racer/22952">Matt Liebsch</Anchor>
                                <Anchor href="/racer/8858">Brain Gregg</Anchor>
                                <Anchor href="/racer/24222">Molly Watkins</Anchor>
                                <Anchor href={"/racer/28450"}>Spencer Davis</Anchor>
                                <Anchor href={"/racer/17162"}>Jessie Diggins</Anchor>
                                <Anchor href={"/racer/18226"}>Jonah Gilbert</Anchor>
                                <Anchor href={"/racer/30652"}>Tyler Gilbert</Anchor>
                                <Anchor href={"/racer/19588"}>Keith Gilbert</Anchor>
                                <Anchor href={"/racer/24482"}>Nate Rhode</Anchor>
                                <Anchor href={"/racer/10110"}>Chris Torvi</Anchor>
                                <Anchor href="/racer/19117">Karl Holub</Anchor>
                            </Box>
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