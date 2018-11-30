import React from 'react';

import {
    Box,
    Text,
    Anchor
} from "grommet";

import '../styles/About.css';

function About() {
    return (
      <Box>
          <br/>
          <Text margin="small">
              From the beginning of time, skier kind has desired to know who the strongest skier is. And today, we have
              the technology. Well, we <i>had</i> the technology for a long time, now we just have a weekend
              warrior willing to employ it.
          </Text>
          <Text margin="small">
              Birkielo is an application of the&nbsp;
              <Anchor href="https://en.wikipedia.org/wiki/Elo_rating_system">
                  Elo rating system
              </Anchor>
              &nbsp;(commonly used in chess) to cross country ski results. This is a fairly complex effort involving
              web scraping, algorithmics, & mathematical statistics, so please excuse any errors & omissions.
              While in its early stages no explanation of scores are provided, Birkielo will seek to be transparent in
              its methodologies.
          </Text>
          <br/>
        <img src="/images/birkie_hills.jpg" className="about-image" alt="trample"/>
      </Box>
    );
}

export default About;