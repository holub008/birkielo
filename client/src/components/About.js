import React, {Fragment} from 'react';

import {
    Box,
    Text,
    Anchor,
    Grommet,
    Tabs,
    Tab,
} from "grommet";
import { grommet } from "grommet/themes";

import '../styles/About.css';

const featureTabs = {
    concept:
        <Tab title="Concept">
            <Box>
                <br/>
                <Text margin="small">
                    From the beginning of time, skier kind has desired to know who the strongest skier is.
                    And today, we have
                    the technology. Well, we <i>had</i> the technology for a long time, now we just have a
                    weekend
                    warrior willing to employ it.
                </Text>
                <Text margin="small">
                    Birkielo is an application of the&nbsp;
                    <Anchor href="https://en.wikipedia.org/wiki/Elo_rating_system">
                        Elo rating system
                    </Anchor>
                    &nbsp;(commonly used in chess) to cross country ski results. This is a fairly complex
                    effort involving
                    web scraping, algorithmics, & mathematical statistics, so please excuse any errors &
                    omissions.
                    While in its early stages no explanation of scores are provided, Birkielo will seek to
                    be transparent in
                    its methodologies.
                </Text>
                <br/>
                <img src="/images/birkie_hills.jpg" className="about-image" alt="trample"/>
            </Box>
        </Tab>,
    birkielo:
        <Tab title="Birkielo Computation">
            <Box>
            </Box>
        </Tab>,
    results:
        <Tab title="Results">
            <Box>
            </Box>
        </Tab>,
};

function getTabs(referenceFeature) {
    var referenceTab = featureTabs[referenceFeature];
    if (!referenceTab) {
        referenceFeature = 'concept';
        referenceTab = featureTabs[referenceFeature];
    }

    const tabs = [referenceTab];
    Object.keys(featureTabs)
        .filter(feature => feature !== referenceFeature)
        .forEach(feature => tabs.push(featureTabs[feature]));

    return tabs;
}

// NOTE: grommet does not correctly use activeTab when initially rendering the <Tabs> - it always renders activeTab=0
// regardless of how it is configured. the result is that we hack the tab ordering so that the props.feature tab
// is at index 0, and we leave the <Tabs> uncontrolled. if no props.feature is specified, we default to the concept tab
function About(props) {
    return (
        <Grommet theme={grommet}>
            <Tabs >
                {
                    getTabs(props.feature)
                }
            </Tabs>
        </Grommet>
    );
}

export default About;