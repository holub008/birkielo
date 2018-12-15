import React from 'react';

import {
    Box,
    Text,
    Anchor,
    Grommet,
    Tabs,
    Tab,
    Heading,
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
            <Box margin="medium">
                <Text>
                    This is a work in progress. It will contain layered descriptions of how Birkielo computation is
                    performed.
                </Text>
            </Box>
        </Tab>,
    results:
        <Tab title="Results">
            <Box margin="medium">
                <Text>
                    Birkielo is predicated on having & providing access to consolidated ski results - both for
                    performing aggregate analysis (rankings) as well as providing a single source of results to users.
                    As result inquisitors of the past will surely verify, ski results are spread across a variety of
                    sources; even worse, these results often contain disparate content - different formatting, missing
                    data, data with different representations, etc. More on this later. How does Birkielo jump these
                    hurdles?
                </Text>
                <Heading size="small">The Result Graveyards</Heading>
                <Text>
                    In a period of history not far from the invention of klister & the extinction of dinosaurs, ski
                    results were only communicated in physical, paper format. As the internet rose in popularity in the
                    early 2000s, results were increasingly published in electronic formats (e.g. PDF & html in the
                    form of web pages); one only need look at the magnitude of results published on skinnyski.com to grasp this
                    trend. Today, I am not aware of any large race that does not publish online. Often the race
                    website, a timing company (e.g. pttiming.com or mtecresults.com), or aggregators like skinnyski.com
                    will host the results.
                </Text>
                <br/>
                <Text>
                    But what happens to results once the post-race lust of result creepers has worn off? They sit in the
                    archives of web servers all over the internet, gathering dust & suffering quantum bit flips
                    to the point that one day Joe Dubay will be credited with winning the Birkie. This sad fate harkens
                    the "graveyard" allusion; Birkielo is the gracious grave-robber, indexing long dead race
                    results & giving them new life.
                </Text>
                <Heading size="small">Scraping (not skis)</Heading>
                <Text>
                    Unlike the physical results graveyards, which are effectively unrecoverable (without substantial
                    human effort), these e-graveyards can be cheaply & quickly accessed. For the uninitiated, web
                    scraping is the process of extracting data from the internet; this frequently involves parsing html,
                    the text data underlying most of the content you see in a browser. In fact, all race results I have
                    seen online that are not PDFs are structured as html "tables"- html objects that have
                    generally well structured content (think excel spreadsheets for the internet). Using simple web
                    request & parsing tools (in many cases so far, Birkielo has utilized BeautifulSoup successfully),
                    we can mine this structured data.
                </Text>
                <Heading size="small">Formatting Hell</Heading>
                <Text>
                    If results are dead, they are surely in Hell. Imagine results you often see. While the high
                    level structure of the data may be strong (e.g. has consistent columns), the attributes of the data
                    may have arbitrary content. For example, a race time of
                    1 hour, 3 minutes, and 37 seconds may be reported as "1:03:37", "1:03:37.00", "1:04", "1:03.37",
                    etc. A place of 23 out of 100 may be reported as "23/100", "23" (where the total number of racers is
                    in another column, or implicit) - then add in the complexity introduced by including gender
                    placement. Names may be reported as "Karl Holub", "Karl J Holub", "Holub, Karl". Results may or may
                    not include the racer gender. How would you programmatically - that is, as if you were writing
                    a cooking recipe for data - express how to coerce this data to similar format?
                </Text>
                <br/>
                <Text>
                    To this stew of data, Birkielo sprinkles simple heuristics (e.g. try several common time formats,
                    look for several types of name ordering), algorithms (e.g. to derive gender from gender placement &
                    overall placement), and variable text searching tools - namely regular expressions - to produce
                    a unified, well structured data set.
                </Text>
                <Heading size="small">Matching</Heading>
                <Text>
                    Once all results are consolidated, Birkielo seeks to make them searchable by indexing on the racer
                    responsible for the result. The simple approach employed at time of writing is match on name
                    equality. Certainly there are cases where this fails - e.g. "Matthew Liebsch" sometimes gives his
                    name as "Matt Liebch" & "Caitlin Compton" changed her name to "Caitlin Gregg". Furthermore, the name
                    "Mark Johnson" undoubtedly corresponds to multiple racers because it is such a common name. Possible
                    solutions exist - what I will refer to as fuzzy matching techniques. Using age, location, average
                    rank, and other associated data often present in results, it may be possible to match results to
                    racers where names don't tell the correct story. However, this represents a complex endeavour, and
                    has not yet been implemented.
                </Text>
                <Heading size="small">Which Races?</Heading>
                <Text>
                    Races are chosen to be consumed on the basis of 1. ease of scraping (how clean & well formatted the
                    data is) and 2. the number of racers in the race.
                    These are measures of how much utility the races provide. To date, only the Birkie & City of Lakes
                    Loppet have been consumed - they are the two lowest hanging fruits in this regard.
                </Text>
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