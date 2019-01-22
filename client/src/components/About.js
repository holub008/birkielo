import React from 'react';

import {
    Box,
    Text,
    Anchor,
    Grommet,
    Tabs,
    Tab,
    Heading,
    Accordion,
    AccordionPanel,
    Image
} from "grommet";
import { grommet } from "grommet/themes";

import EventDonut from './EventDonut';
import BirkieloLink from "./BirkieloLink";

import '../styles/About.css';

const featureTabs = {
    concept:
        <Tab title="Concept" key="concept">
            <Box>
                <Text margin="small">
                    How do you find ski results? What do you hope do with them?
                </Text>
                <Text margin="small">
                    In all likellihood, the answer to the first question is some combination of trawling skinnyski &
                    googling. Answers to the second question may vary:
                    <ul>
                        <li>
                            Commit them to memory
                        </li>
                        <li>
                            Compare races and racers
                        </li>
                        <li>
                            Analyze how a racer's performance has changed over time
                        </li>
                    </ul>
                    All of these approaches are inefficient, imprecise & subject to bias, and non-reproducible.
                </Text>
                <Text margin="small">
                    Birkielo.com is both a web scraper and an application of the&nbsp;
                    <Anchor href="https://en.wikipedia.org/wiki/Elo_rating_system">
                        Elo rating system
                    </Anchor>
                    &nbsp;(commonly used in chess) to cross country ski results. It provides indexed and searchable
                    access to ski results and produces a rating system for comparison between racers, between races, and
                    with racers over time. To these ends, the site contains search tools and visualizations. The end
                    result is improved analysis & insight and saved time.
                </Text>
                <Text margin="small">
                    Chase trails, not links.
                </Text>
                <Box align="center">
                    <Image src="/images/birkie_hills.jpg"
                         style={{width:"75%", maxWidth: "500px"}}/>
                </Box>
            </Box>
        </Tab>,
    birkielo:
        <Tab title="Birkielo Computation" key="computation">
            <Box margin="medium">
                <Box align="center">
                    <Image src="/images/calc.jpg" style={{maxWidth:"150px"}}/>
                </Box>
                <Text>
                    Explain as if I'm:
                </Text>
                <Accordion>
                    <AccordionPanel label="A Child">
                        <Box margin="small">
                            <Text>
                                Every ski racer gets a score. Over time, if a skier races well & beats other skiers, they get
                                a higher score. If a skier does not race well, they get a lower score.
                            </Text>
                        </Box>
                    </AccordionPanel>
                    <AccordionPanel label="An Adult">
                        <Box margin="small">
                            <Text margin="small">
                                Every ski racer gets a score, with the average score around 1000. This score gives some
                                expectation for how well a skier should do in any given race. If the average score of racers
                                in a race is 1100 and my score is 1100, I should expect to beat half the competitors & lose
                                to half the competitors. Imagine the scenarios:
                                <ul>
                                    <li>I beat (and lose to) exactly half. My score must be just about right.</li>
                                    <li>I beat more than half. My score should be adjusted upwards a bit (but not too much,
                                        in case the race was a fluke).</li>
                                    <li>I beat less than half. My score should be adjusted downwards a bit (but not too much,
                                        in case the race was a fluke).</li>
                                    <li>I won the race. My score should be adjusted upwards substantially - it's clear I'm
                                    much better than my current score.</li>
                                </ul>
                            </Text>
                            <Text margin="small">
                                The key outcome to note is that score changes are relative to the competitiveness of race
                                the score is being updated for. A good skier winning a race of bad skiers doesn't say much
                                about their ability, and vice versa.
                            </Text>
                            <Text margin="small">
                                So, how are scores determined? For a given race & racer, take all other competitors in the
                                race that were beaten; for each competitor, add an amount to the racer score
                                inversely proportional to the score difference between the racer & competitor. Now take
                                all the competitors that beat the racer; for each competitor, subtract an amount from
                                the racer score inversely proportional to the score difference between the racer &
                                competitor.
                            </Text>
                        </Box>
                    </AccordionPanel>
                    <AccordionPanel label="A Computer Scientist">
                        <Box margin="small">
                            <Text>
                                The scoring algorithm has not been finalized. In the interest of not rewriting this section
                                with future changes it is left for a later date. Do feel free to read the&nbsp;
                                <Anchor href="https://github.com/holub008/birkielo/tree/master/offline/scoring">
                                code
                                </Anchor>
                                .
                            </Text>
                        </Box>
                    </AccordionPanel>
                    <AccordionPanel label="A Statistician">
                        <Box margin="small">
                            <Text>
                                The scoring algorithm has not been finalized. In the interest of not rewriting this section
                                with future changes it is left for a later date. The procedure is highly derivative of the&nbsp;
                                <Anchor href="https://en.wikipedia.org/wiki/Elo_rating_system#Theory">
                                    Elo rating
                                </Anchor>
                                &nbsp;as in chess and will share much of the math.

                                If you are interested in running some statistical simulations or seeing methods explored in
                                the development of Birkielo, see&nbsp;
                                <Anchor href="https://github.com/holub008/birkielo/blob/master/offline/scoring/simulate/ranking_experiments.R">
                                    here
                                </Anchor>
                                .
                            </Text>
                        </Box>
                    </AccordionPanel>
                </Accordion>
            </Box>
        </Tab>,
    results:
        <Tab title="Results" key="results">
            <Box margin="medium">
                <Text>
                    Birkielo is predicated on having access to consolidated ski results - both for providing a single
                    source of results to users as well as performing aggregate analysis (rankings).
                    As result inquisitors will surely verify, ski results are spread across a variety of
                    sources; even worse, these results often contain disparate content - different formatting, missing
                    data, data with different representations, etc. How does Birkielo jump these hurdles?
                </Text>
                <Heading size="small">The Result Graveyards</Heading>
                <Text>
                    In a period of history adjacent to the reign of three pin bindings, ski results were only
                    communicated in physical, paper format. As the internet rose in popularity in the early 2000s,
                    results were increasingly published in electronic formats (e.g. PDF & html in the form of web pages)
                    ; one only need look at the magnitude of&nbsp;
                    <Anchor href="http://www.skinnyski.com/racing/results/1997-1998/">
                        results published on skinnyski.com
                    </Anchor> to grasp this trend. Today, I am not aware of any large race that does not publish online.
                    Often the race website, a timing company (e.g. pttiming.com or mtecresults.com), or aggregators
                    like skinnyski.com will host the results.
                </Text>
                <br/>
                <Text>
                    But what happens to results once the post-race lust of result creepers has worn off? They sit in the
                    archives of web servers all over the internet, gathering dust & suffering&nbsp;
                    <Anchor href="http://lambda-diode.com/opinion/ecc-memory">
                        bit flips
                    </Anchor>
                    &nbsp;to the point that one day&nbsp;
                    <Anchor href="https://fasterskier.com/fsarticle/dubay-discusses-mistake-birkie-dq/">
                        Joe Dubay will be credited with winning the 2012 Birkie
                    </Anchor>
                    . This sad fate harkens the "graveyard" allusion; Birkielo is the gracious grave-robber,
                    indexing long dead race results & giving them new life.
                </Text>
                <Heading size="small">Scraping (not skis)</Heading>
                <Text>
                    Unlike the physical results graveyards, which are effectively unrecoverable (without substantial
                    human effort), these e-graveyards can be cheaply & quickly accessed. For the uninitiated, web
                    scraping is the process of extracting data from the internet; this frequently involves probing
                    websites and processing json & html - the text data underlying much of the content you see in a
                    browser. In fact, the majority of old race results that are not PDFs are structured as html
                    "tables"- html objects that have generally well-structured content (think excel spreadsheets for the
                    internet). Using simple web request & parsing tools (Birkielo utilizes&nbsp;
                    <Anchor href="https://www.crummy.com/software/BeautifulSoup/">
                        BeautifulSoup
                    </Anchor>
                    ), we can exhume this structured data.
                </Text>
                <Heading size="small">Formatting Hell</Heading>
                <Text>
                    If results are dead, they are surely in Hell. Imagine results you often see. While the high
                    level structure of the data may be strong (e.g.&nbsp;
                    <Anchor href="http://birkie.pttiming.com/results/2018/?page=1150&r_page=division&divID=2">
                        has consistent columns
                    </Anchor>
                    ), the attributes of the data may have arbitrary content . For example, a race time of 1 hour, 3
                    minutes, and 37 seconds may be reported as "1:03:37", "1:03:37.00", "1:04", "1:03.37", etc. A place
                    of 23 out of 100 may be reported as "23/100", "23" (where the total number of racers is in another
                    column, or implicit) - then add in the complexity introduced by including gender placement. Names
                    may be reported as "Karl Holub", "Karl J Holub", "Holub, Karl", or&nbsp;
                    <Anchor href="http://results.birkie.com/participant.php?event_id=38&bib=57">
                        "Karl 599 Hwy 20 Holub"
                    </Anchor>
                    . Results may or may not include the racer gender. How can we programmatically - that is, as if we
                    were writing a cooking recipe for data - express how to coerce this data to similar format?
                </Text>
                <br/>
                <Text>
                    To this stew of data, Birkielo sprinkles simple heuristics (e.g. scan for several common time formats,
                    look for several types of name ordering), algorithms (e.g. to derive gender from gender placement &
                    overall placement), and weakly structure text search tools - namely regular expressions - to produce
                    a unified, well structured data set.
                </Text>
                <Heading size="small">Matching</Heading>
                <Text>
                    Once results are consolidated, Birkielo seeks to make them attributable to a single racer
                    responsible for them- attach an "identity" to the result. I refer to this as matching results. The
                    simple approach employed at time of writing is to match on name equality. Certainly there are cases
                    where this fails - e.g. "Matthew Liebsch" sometimes gives his name as "Matt Liebsch" &
                    "Caitlin Compton" changed her name to "Caitlin Gregg" after marriage. Furthermore, the name
                    "Mark Johnson" undoubtedly corresponds to multiple racers because it is such a common name. Possible
                    solutions exist - what I will refer to as fuzzy matching techniques. Using age, location, average
                    rank, and other associated data often present in results, it may be possible to match results to
                    racers where names alone don't identify the racer. However, this represents a complex endeavour, and
                    has not yet been implemented.
                </Text>
                <Heading size="small">Which Races?</Heading>
                <Text>
                    Races are chosen for inclusion on the basis of
                    <ol>
                        <li>ease of scraping (how clean & well formatted the data is) </li>
                        <li>the number of racers in the race</li>
                    </ol>

                    These provide a measure of how time efficient programming a scraper will be. To date, a handful
                    of races have been scraped - see the below donut for a complete list of races from 2018. If you
                    would like to see other races added,&nbsp;
                    <BirkieloLink to="/support">
                        let me know or contribute results you've dug up!
                    </BirkieloLink>
                </Text>
                <Box alignSelf="center">
                    <EventDonut year={2018} />
                </Box>
            </Box>
        </Tab>,
};

function getTabs(referenceFeature) {
    let referenceTab = featureTabs[referenceFeature];
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