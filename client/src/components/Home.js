import React from 'react';

import {
    Box,
    Grommet,
    DropButton,
    Text,
} from "grommet";
import { grommet } from "grommet/themes";

import '../styles/Home.css';
import SearchBar from "./SearchBar";
import EventSankey from "./EventSankey";
import EventDonut from "./EventDonut";
import BirkieloLink from "./BirkieloLink";

import {getClickableColor} from "../util/data";

const DropContent = ({ onClose }) => (
    <Box pad="small">
        <BirkieloLink to="/rankings/women">
            Women
        </BirkieloLink>
        <BirkieloLink to="/rankings/men">
            Men
        </BirkieloLink>
    </Box>
);

function Home(props) {
    // note the window.innerWidth conditional - critically, note that it isn't a listener & accompanying state update
    // if the user is on mobile screen less than 500px ----> show small graphic
    // if the user is on a big screen shrunk less than 500px and then sizes up -----> continue to show small graphic
    // if the user is on a big screen and shrinks it less than 500px -----> cruddy render until refresh
    return(
        <div className="home">
            <Grommet theme={grommet}>
                <Box margin={{top:"medium"}}>
                    <Box direction="row" alignSelf="center" gap="small">
                        <Box border="right" alignSelf="center">
                            <Text margin={{right:"small"}}> Search </Text>
                        </Box>
                        <Box border="right" style={{cursor: "pointer"}}>
                            <DropButton
                                dropContent={<DropContent/>}
                                dropAlign={{top:"bottom"}}>
                                <Text color={getClickableColor()} margin={{right: "small"}}>
                                    Rankings
                                </Text>
                            </DropButton>
                        </Box>
                        <Box border="right" style={{cursor: "pointer"}}>
                            <Box margin={{right: "small"}}>
                                <BirkieloLink to="/event/">
                                    Races
                                </BirkieloLink>
                            </Box>
                        </Box>
                        <Box style={{cursor: "pointer"}}>
                            <BirkieloLink to="/about/">
                                About
                            </BirkieloLink>
                        </Box>
                    </Box>
                    <Box margin="medium" width="large" alignSelf="center">
                        <SearchBar maxResults={20}/>
                    </Box>
                    <Box margin={{top: "small"}} alignSelf="center">
                        {
                            window.innerWidth > 550 ?
                                <EventSankey />
                                :
                                <EventDonut year={2018} />
                        }
                    </Box>
                </Box>
            </Grommet>
        </div>
    );
}

export default Home;