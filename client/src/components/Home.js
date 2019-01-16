import React from 'react';

import {
    Box,
    Grommet,
    DropButton,
    Text,
} from "grommet";
import { grommet } from "grommet/themes";
import { Link } from 'react-router-dom';

import '../styles/Home.css';
import SearchBar from "./SearchBar";
import EventSankey from "./EventSankey";
import EventDonut from "./EventDonut";

const DropContent = ({ onClose }) => (
    <Box pad="small">
        <Link to="/rankings/women" style={{textDecoration: "none", color: "rgb(144,96,235)"}}>
            Women
        </Link>
        <Link to="/rankings/men" style={{textDecoration: "none", color: "rgb(144,96,235)"}}>
            Men
        </Link>
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
                        <Box>
                            <DropButton
                                dropContent={<DropContent/>}
                                dropAlign={{top:"bottom"}}>
                                <Text color="rgb(144,96,235)">
                                    Rankings
                                </Text>
                            </DropButton>
                        </Box>
                    </Box>
                    <Box margin="medium" width="large" alignSelf="center">
                        <SearchBar maxResults={20}/>
                    </Box>
                    <Box margin={{top: "small"}} alignSelf="center">
                        {
                            // TODO the EventDonut has some left/right play on a 300px screen :(
                            window.innerWidth > 550 ?
                                <EventSankey />
                                :
                                <EventDonut />
                        }
                    </Box>
                </Box>
            </Grommet>
        </div>
    );
}

export default Home;