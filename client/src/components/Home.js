import React from 'react';

import {
    Box,
    Grommet,
    DropButton,
    Text,
    Image,
} from "grommet";
import { grommet } from "grommet/themes";
import { Link } from 'react-router-dom';

import '../styles/Home.css';
import SearchBar from "./SearchBar";

const rotationImages = [
    {
        filename: "skier.gif",
        alt: "credit Walt Disney",
    },
    {
        filename: "back.JPG",
        alt: "fair use",
    },
    {
        filename: "baby.JPG",
        alt: "credit fasterskier.com"
    },
    {
        filename: "birkie_hills.jpg",
        alt: "credit star tribune"
    },
    {
        filename: "cheesin.jpg",
        alt: "cheesy"
    },
];

function getRandomImage() {
    const index = Math.floor(Math.random() * rotationImages.length);
    const image = rotationImages[index];
    return(
        <Image src={`/images/${image.filename}`} alt={image.alt} style={{width:"50%", maxWidth:"400px"}}/>
    )
}

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
                </Box>
                <Box align="center" margin={{top:"medium"}}>
                    {
                        getRandomImage()
                    }
                </Box>
            </Grommet>
        </div>
    );
}

export default Home;