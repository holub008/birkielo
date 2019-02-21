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
import {withRouter} from "react-router-dom";

// note, I used http://hilite.me/ for code -> html creation, then a jsx converter
const featureTabs = [
        <Tab title="Concept" key="concept">
            <Box>
                <Text margin="small">
                    How do you find ski results? What do you hope to do with them?
                </Text>
                <Text margin="small">
                    In all likelihood, the answer to the first question is some combination of trawling skinnyski and
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
                    To these ends, tab juggling, Control+F, and other manual efforts are typically employed. All of
                    these approaches are inefficient, subject to bias, and non-reproducible.
                </Text>
                <Text margin="small">
                    Birkielo.com is both a web scraper and an application of the&nbsp;
                    <Anchor href="https://en.wikipedia.org/wiki/Elo_rating_system">
                        Elo rating system
                    </Anchor>
                    &nbsp;(commonly used in chess) to cross country ski results. It provides indexed and searchable
                    access to ski results and produces a rating system for comparison between racers, between races, and
                    with racers over time. The end result is improved analysis, deeper insight, and saved time.
                </Text>
                <Text margin="small">
                    Chase trails, not links!
                </Text>
                <Box align="center">
                    <Image src="/images/roerich_fire_blossom.jpg"
                         style={{width:"75%", maxWidth: "750px"}}/>
                </Box>
            </Box>
        </Tab>,
        <Tab title="Birkielo Score" key="computation">
            <Box margin="medium">
                <Box align="center">
                    <Image src="/images/calc.jpg" style={{maxWidth:"150px"}}/>
                </Box>
                <Text>
                    Explain birkielo scoring as if I'm:
                </Text>
                <Accordion>
                    <AccordionPanel label="A Child">
                        <Box margin="small">
                            <Text>
                                Every skier gets a score. Over time, if a skier races well and beats other skiers, they
                                get a higher score. If a skier does not race well and loses to other skiers, they get a
                                lower score. Skiers with higher scores will usually beat those with lower scores.
                            </Text>
                        </Box>
                    </AccordionPanel>
                    <AccordionPanel label="An Adult">
                        <Box margin="small">
                            <Text margin="small">
                                Birkielo ratings can approximately be interpreted as: "If skier A has a rating 200
                                points greater than skier B, skier A is 10 times as likely to beat skier B in a race
                                than to lose. At a 400 point differential, the odds of victory grow to 100:1, and so
                                on.
                            </Text>
                            <Text margin="small">
                                A layman's description of how scores are determined follows.
                            </Text>
                            <Text margin="small">
                                Every skier gets a score, with the average score around 1000. This score gives some
                                expectation for how well a skier should do in any given race. If the median score of
                                skiers in a race is 1100 and my score is 1100, I should expect to beat half the
                                competitors and lose to half the competitors. Imagine the scenarios:
                                <ul>
                                    <li>I beat (and lose to) exactly half. My score must be just about right.</li>
                                    <li>I beat more than half. My score should be adjusted upwards a bit (but not too much,
                                        in case the race was a fluke for me or my competitors).</li>
                                    <li>I beat less than half. My score should be adjusted downwards a bit (again, not
                                        too much).</li>
                                    <li>I won the race. My score should be adjusted upwards substantially because it's
                                        clear I'm much better than my current score.</li>
                                </ul>
                            </Text>
                            <Text margin="small">
                                This update can be iterated across all races a skier has participated in. The key
                                outcome to note is that score changes are relative to the competitiveness of the
                                race the score is being updated for. A good skier winning a race of bad skiers doesn't
                                say much about their ability.
                            </Text>
                            <Text margin="small">
                                So, how are scores determined? For a given race and skier, take all other competitors in
                                the race that were beaten; for each beaten competitor, add an amount to the skier score
                                inversely proportional to the score difference between the skier and competitor. Now take
                                all the competitors that beat the skier; for each winning competitor, subtract an amount
                                from the skier score inversely proportional to the score difference between the skier
                                and competitor.
                            </Text>
                        </Box>
                    </AccordionPanel>
                    <AccordionPanel label="A Programmer">
                        <Box margin="small">
                            <Text>
                                Expressing the "adult" tab precisely and in pseudocode, with a few added parameters:
                            </Text>
                            <Box>
                                <div style={{background: '#ffffff', overflow: 'auto', width: 'auto', border: 'solid gray', borderWidth: '.1em .1em .1em .8em', padding: '.2em .6em'}}>
                                    <pre style={{margin: 0, lineHeight: '125%'}}>
                                        <span style={{color: '#008800', fontWeight: 'bold'}}>for</span> race&nbsp;
                                        <span style={{color: '#000000', fontWeight: 'bold'}}>in</span> races{"\n"}{"    "}
                                        <span style={{color: '#008800', fontWeight: 'bold'}}>for</span> update_racer&nbsp;
                                        <span style={{color: '#000000', fontWeight: 'bold'}}>in</span> race{"\n"}{"        "}
                                        <span style={{color: '#008800', fontWeight: 'bold'}}>if</span>
                                        &nbsp;not update_racer
                                        <span style={{color: '#333333'}}>.</span>score{"\n"}{"            "}update_racer
                                        <span style={{color: '#333333'}}>.</span>score&nbsp;
                                        <span style={{color: '#333333'}}>=</span>&nbsp;default_score{"\n"}{"        "}scale_racer_score&nbsp;
                                        <span style={{color: '#333333'}}>=</span>&nbsp;
                                        <span style={{color: '#0000DD', fontWeight: 'bold'}}>10</span>&nbsp;
                                        <span style={{color: '#333333'}}>^</span> (update_racer
                                        <span style={{color: '#333333'}}>.</span>score&nbsp;
                                        <span style={{color: '#333333'}}>/</span> log_odds_differential){"\n"}{"        "}
                                        <span style={{color: '#008800', fontWeight: 'bold'}}>for</span> competitor&nbsp;
                                        <span style={{color: '#000000', fontWeight: 'bold'}}>in</span> setdiff(race, update_racer){"\n"}{"            "}scale_competitor_score&nbsp;
                                        <span style={{color: '#333333'}}>=</span>&nbsp;
                                        <span style={{color: '#0000DD', fontWeight: 'bold'}}>10</span>&nbsp;
                                        <span style={{color: '#333333'}}>^</span> (competitor
                                        <span style={{color: '#333333'}}>.</span>score&nbsp;
                                        <span style={{color: '#333333'}}>/</span> log_odds_differential){"\n"}{"            "}p_win&nbsp;
                                        <span style={{color: '#333333'}}>=</span> scale_racer_score&nbsp;
                                        <span style={{color: '#333333'}}>/</span> (scale_racer_score&nbsp;
                                        <span style={{color: '#333333'}}>+</span> scale_competitor_score){"\n"}{"            "}outcome&nbsp;
                                        <span style={{color: '#333333'}}>=</span>&nbsp;
                                        <span style={{color: '#0000DD', fontWeight: 'bold'}}>0</span>&nbsp;
                                        <span style={{color: '#008800', fontWeight: 'bold'}}>if</span> competitor
                                        <span style={{color: '#333333'}}>.</span>time&nbsp;
                                        <span style={{color: '#333333'}}>&lt;</span> update_racer
                                        <span style={{color: '#333333'}}>.</span>time&nbsp;
                                        <span style={{color: '#008800', fontWeight: 'bold'}}>else</span>&nbsp;
                                        <span style={{color: '#0000DD', fontWeight: 'bold'}}>1</span>{"\n"}{"            "}update_racer
                                        <span style={{color: '#333333'}}>.</span>score&nbsp;
                                        <span style={{color: '#333333'}}>+=</span> k_factor&nbsp;
                                        <span style={{color: '#333333'}}>*</span> (outcome&nbsp;
                                        <span style={{color: '#333333'}}>-</span> p_win){"\n"}
                                    </pre>
                                </div>

                            </Box>
                            <Text margin={{top:"small"}}>
                                Birkielo ratings run with the following parameterization:
                            </Text>
                            <Box>
                                <div style={{background: '#ffffff', overflow: 'auto', width: 'auto', border: 'solid gray', borderWidth: '.1em .1em .1em .8em', padding: '.2em .6em'}}>
                                    <pre style={{margin: 0, lineHeight: '125%'}}>default_score&nbsp;
                                        <span style={{color: '#333333'}}>=</span>&nbsp;
                                        <span style={{color: '#0000DD', fontWeight: 'bold'}}>1000</span>{"\n"}k_factor&nbsp;
                                        <span style={{color: '#333333'}}>=</span>&nbsp;
                                        <span style={{color: '#0000DD', fontWeight: 'bold'}}>2</span>{"\n"}log_odds_differential&nbsp;
                                        <span style={{color: '#333333'}}>=</span>&nbsp;
                                        <span style={{color: '#0000DD', fontWeight: 'bold'}}>200</span>{"\n"}
                                    </pre>
                                </div>
                            </Box>
                            <Text margin={{top:"small"}}>
                                For practical purposes, a per-race maximum score change is instituted (200 points). This
                                is to prevent corner cases such as a top racer sand-bagging one race only to sky rocket
                                their rating with a follow up top placement. It has the downside of reducing the speed
                                with which tail racers (both bad and good) reach their true ratings; slow and
                                conservative is acceptable, if not preferred, in this case because most top competitors
                                do many races.
                            </Text>
                            <Text margin={{top:"small"}}>
                                You can also read the actual implementation and several other attempted approaches&nbsp;
                                <Anchor href="https://github.com/holub008/birkielo/tree/master/offline/scoring">
                                    here.
                                </Anchor>
                            </Text>
                        </Box>
                    </AccordionPanel>
                    <AccordionPanel label="A Statistician">
                        <Box margin="small">
                            <Text margin="small">
                                The birkielo rating system is highly derivative of the&nbsp;
                                <Anchor href="https://en.wikipedia.org/wiki/Elo_rating_system#Theory">
                                    Elo rating
                                </Anchor>
                                &nbsp;as in chess. In that setting, all matches are of course 1 vs. 1. As in the
                                "programmer" tab above, if the log scale odds differential is parameterized as 200,
                                we expect that a score gap of 200 points between two competitors implies the higher
                                rated player is 10 times more likely to win than lose against the lower rated player.
                                I won't cover the math in further detail, but the above wikipedia link and&nbsp;
                                <Anchor href="https://math.stackexchange.com/a/1733081">
                                    this post
                                </Anchor>&nbsp;elucidate the model.
                            </Text>
                            <Text margin="small">
                                The birkielo rating system naively carries out the Elo rating system by deconstructing
                                a race (an n skier vs. n skier match) into n*(n-1) individual matchups. This has a couple statistical
                                implications that differ from traditional Elo:
                                <ul>
                                    <li>Score updates are correlated with one another within a competition</li>
                                    <li>The system will be more confident in the measured outcome from a single race
                                        vs. a single chess match, since the sample size has grown substantially
                                        (shrinking variance via Law of Large Numbers).</li>
                                </ul>
                                Both of these facts are not accounted for by the traditional Elo rating system; Birkielo
                                ratings weakly account for them by:
                                <ul>
                                    <li>Imposing a score update cap of 200 points on each race. This may be thought of
                                    as a hard regularization.</li>
                                    <li>Substantially shrinking the k-factor (reactivity) of the scoring system. This
                                    may be thought of as a soft regularization.</li>
                                </ul>
                                Both temper the overconfidence that traditional Elo rating systems would be subject to.
                            </Text>
                            <h4>
                                Model Development
                            </h4>
                            <Text margin="small">
                                Before arriving at the final model, several hypothesized rating models were developed:
                                <ul>
                                    <li>Naive Elo (the selected model): Break a race into n*(n-1) 1 vs. 1 matchups and
                                        perform standard Elo</li>
                                    <li>Mean Elo: For each racer, compute mean rating of defeated skiers and mean rating
                                        of winning skiers, then perform standard Elo for both averages</li>
                                    <li>Nearest Neighbor Elo: Similar to Naive Elo, but instead of considering all
                                        n-1 competitors, only consider the nearest k * (n-1) competitors for
                                        k &le; 1.</li>
                                    <li>Empirical Distribution Smoothing: Assume a prior distribution of skier skill.
                                        After a race completes, compute updated scores as a weighted average of the
                                        racer's previous rating and the empirical pre-race rating distribution quantile,
                                        or the prior quantile if it's the racer's first race.
                                    </li>
                                </ul>
                            </Text>
                            <Text margin="small">
                                As a first pass test, a toy data set was constructed, with "true" skier rating drawn
                                from a Gaussian distribution. Races in this set contain a subset of the entire
                                racer population and race outcomes are a Gaussian sampling with mean of the skier's true
                                rating. Skier outcomes are a stationary process in this data.
                            </Text>
                            <Text margin="small">
                                Several key properties of the model were assessed using this set:
                                <ul>
                                    <li>Convergence: Does the implied ranking converge reasonably close to the
                                        "true" ranking? Here, and throughout validation, Spearman's rank correlation
                                        (rho) is used. </li>
                                    <li>Speed of convergence: How many races does it take for the implied
                                        ranking to become reasonably close to the "true" ranking?</li>
                                    <li>Stability of score distribution: For human interpretability, it is desirable
                                        that the score distribution remains relatively stable over time (e.g. the
                                        mean and variance don't substantially shrink or grow over time).</li>
                                </ul>
                                Below is a visual example of rho convergence over time for a Naive Elo model. Predictions achieve
                                quite high correlation by 5 races, and have converged to practically perfect prediction
                                by 15 races.
                            </Text>
                            <Image src="/images/naive_elo_toy_rho.jpg"
                                   style={{margin:"auto", width: "90%", maxWidth:"700px"}}/>
                            <Text margin="small">
                                Using this first pass, the 3 Elo variants (Naive, Mean, & Nearest Neighbor) were found
                                to have desirable characteristics.
                            </Text>
                            <h4>
                                Model Selection & Validation
                            </h4>
                            <Text margin="small">
                                In reality, the toy data is missing several complexities present in real data:
                                <ul>
                                    <li>Stationarity: Skier skill is generally not constant over time (nor its variance)
                                    </li>
                                    <li>Sparsity: Most skiers do not race more than a few times</li>
                                    <li>Dropout: Below average skiers have a higher propensity to quit</li>
                                </ul>
                                So, we need an empirical method of validation to select a final model (and
                                parameterization). Forward chaining is a method of sequential cross validation that
                                may provide such inference. The method:
                                <ul>
                                    <li>build the model to time t</li>
                                    <li>predict the placements for the race at time t + 1</li>
                                    <li>compute accuracy of predictions using actual placements at time t + 1</li>
                                    <li>repeat from top</li>
                                </ul>
                                Using a grid search over the 3 model varieties and parameters, forward chaining produced
                                a picture of the most favorable models (filtered down for demonstration purposes):
                            </Text>
                            <Image src="/images/rater_search.jpg"
                                 style={{margin:"auto", width: "90%", maxWidth:"700px"}}/>
                            <Text margin="small">
                                The bottom red line is Mean Elo, which performed rather poorly, likely due to no
                                weighting on the number of racers beaten and lost to. The middle 3 purple lines are
                                Nearest Neighbor variants. They perform reasonably but worse than the top 5 green lines
                                &mdash;all flavors of Naive Elo. While they are mostly comparable, there appears to be
                                some improvement in smaller k (k=1,2), which generally suggests a less reactive model.
                            </Text>
                            <h4>
                                Implementation
                            </h4>
                            <Text margin="small">
                                If you are interested in running any of the simulations, seeing methods
                                explored in the development, or the final implementation, see&nbsp;
                                <Anchor href="https://github.com/holub008/birkielo/blob/master/offline/scoring/">
                                    here.
                                </Anchor>
                            </Text>
                        </Box>
                    </AccordionPanel>
                </Accordion>
            </Box>
        </Tab>,
        <Tab title="Results" key="results">
            <Box margin="medium">
                <Text>
                    Birkielo is predicated on access to consolidated ski results&mdash;both for providing a single
                    source of results to users as well as performing aggregate analysis (rankings).
                    As result inquisitors will surely verify, ski results are spread across a variety of
                    sources; even worse, these results often contain disparate content&mdash;different formatting,
                    missing data, data with different representations, etc. How does Birkielo jump these hurdles?
                </Text>
                <Heading size="small">The Result Graveyards</Heading>
                <Text>
                    In a period of history adjacent to the reign of three pin bindings, ski results were only
                    communicated in physical, paper format. As the internet rose in popularity in the early 2000s,
                    results were increasingly published in electronic formats (e.g. PDF and html in the form of web
                    pages); one need only look at the magnitude of&nbsp;
                    <Anchor href="http://www.skinnyski.com/racing/results/1997-1998/">
                        results published on skinnyski.com
                    </Anchor> to grasp this trend. Today, I am not aware of any large race that does not publish online.
                    Often the race website, a timing company (e.g. pttiming.com or mtecresults.com), or aggregators
                    like skinnyski.com will host the results.
                </Text>
                <br/>
                <Text>
                    But what happens to results once the post-race lust of result creepers has worn off? They sit in the
                    archives of web servers all over the internet, gathering dust and suffering&nbsp;
                    <Anchor href="http://lambda-diode.com/opinion/ecc-memory">
                        bit flips
                    </Anchor>
                    &nbsp;to the point that one day&nbsp;
                    <Anchor href="https://fasterskier.com/fsarticle/dubay-discusses-mistake-birkie-dq/">
                        Joe Dubay will be credited with winning the 2012 Birkie
                    </Anchor>
                    . This sad fate harkens the "graveyard" allusion; Birkielo is the gracious grave robber,
                    indexing long dead race results and giving them new life.
                </Text>
                <Heading size="small">Scraping (not skis)</Heading>
                <Text>
                    Unlike the physical results graveyards, which are effectively unrecoverable (without substantial
                    human effort), these e-graveyards can be cheaply and quickly accessed. For the uninitiated, web
                    scraping is the process of extracting data from the internet; this frequently involves probing
                    websites and processing json and html&mdash;the text data underlying much of the content you see in a
                    browser. In fact, the majority of old race results that are not PDFs are structured as html
                    "tables"&mdash;html objects that have generally well-structured content (think excel spreadsheets for the
                    internet). Using simple web request and parsing tools (Birkielo utilizes&nbsp;
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
                    of 23 out of 100 may be reported as "23/100" or "23" (where the total number of racers is in another
                    column, or implicit)&mdash;then add in the complexity introduced by including gender placement. Names
                    may be reported as "Karl Holub", "Karl J Holub", "Holub, Karl", or&nbsp;
                    <Anchor href="http://results.birkie.com/participant.php?event_id=38&bib=57">
                        "Karl 599 Hwy 20 Holub"
                    </Anchor>
                    . Results may or may not include the racer gender. How can we programmatically, that is, as if we
                    were writing a cooking recipe for data, express how to coerce this data to similar format?
                </Text>
                <br/>
                <Text>
                    To this stew of data, Birkielo sprinkles simple heuristics (e.g. scan for several common time formats,
                    look for several types of name ordering), algorithms (e.g. to derive gender from gender placement
                    and overall placement), and weakly structured text search tools&mdash;namely regular
                    expressions&mdash;to produce a unified, well-structured data set.
                </Text>
                <Heading size="small">Matching</Heading>
                <Text>
                    Once results are consolidated, Birkielo seeks to make them attributable to a single racer
                    responsible for them&mdash;attach an "identity" to the result. I refer to this as matching results.
                    The simple approach employed at time of writing is to match on name equality. Certainly there are
                    cases where this fails; e.g.&nbsp;
                    <BirkieloLink to="/racer/22952">
                        "Matthew Liebsch"
                    </BirkieloLink>
                    &nbsp;sometimes gives his name as "Matt Liebsch" and&nbsp;
                    <BirkieloLink to="/racer/9264">
                        "Caitlin Gregg"
                    </BirkieloLink>
                    &nbsp;changed her name from "Caitlin Compton" after marriage. Furthermore, the name
                    "Mark Johnson" undoubtedly corresponds to multiple racers because it is such a common name. Possible
                    solutions exist&mdash;what I will refer to as fuzzy matching techniques. Using age, location, average
                    rank, and other associated data often present in results, it may be possible to match results to
                    racers where names alone don't identify the racer. However, this represents a complex endeavour, and
                    has not yet been implemented.
                </Text>
                <Heading size="small">Which Races?</Heading>
                <Text>
                    Races are chosen for inclusion on the basis of
                    <ol>
                        <li>ease of scraping (how clean and well-formatted the data is) </li>
                        <li>the number of racers in the race</li>
                    </ol>

                    These provide a measure of how time-efficient programming a scraper will be. To date, a handful
                    of events have been scraped. See the below donut for a complete list of races from 2018. If you
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
];

function getActiveTabIndex(referenceFeature) {
    if (referenceFeature === 'computation') {
        return 1;
    }
    else if (referenceFeature === 'results') {
        return 2;
    }

    return 0;
}

function getTabKey(index) {
    if (index === 1) {
        return 'computation';
    }
    else if (index === 2) {
        return 'results';
    }

    return 'concept';
}

function AboutUnWrapped(props) {
    return (
        <Grommet theme={grommet}>
            <Tabs
                activeIndex={getActiveTabIndex(props.feature)}
                onActive={i => {
                    props.history.push(`/about/${getTabKey(i)}`);
                }}
            >
                {
                    featureTabs
                }
            </Tabs>
        </Grommet>
    );
}

const About = withRouter(({history, ...forwardedProps}) =>
    <AboutUnWrapped history={history} {...forwardedProps}/>);

export default About;