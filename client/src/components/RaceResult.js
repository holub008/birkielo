import React from 'react';

import {
    Grommet,
    Box,
    Heading,
    Text,
    TextInput,
    Table,
    TableBody,
    TableHeader,
    TableCell,
    TableRow,
} from "grommet";
import { grommet } from "grommet/themes";
import { CaretNext, CaretPrevious, ChapterNext, ChapterPrevious } from "grommet-icons";

import {Link} from 'react-router-dom';

import Spinner from './Spinner';
import NotFound from './NotFound';

import { callBackend, milliTimeRender } from "../util/data";

const PAGE_SIZE = 50;

const COLUMNS = [
    // TODO this could be duplicated in e.g. ties or the like
    {
        property: "overall_place",
        header: "Overall Place",
    },
    {
        property: "name",
        header: "Name",
        render: datum => datum.racer_id ?
            <Link to={`/racer/${datum.racer_id}`} style={{textDecoration: "none", color:"rgb(144,96,235)"}}>
                {datum.name}
            </Link>
            :
            datum.racer_id
    },
    {
        property: "gender",
        header: "Gender",
    },
    {
        property: "duration",
        header: "Time",
        render: datum => milliTimeRender(datum.duration),
    },
    {
        property: "gender_place",
        header: "Gender Place",
    },
];

class RaceResultSearchBar extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            suggestions: [],
            selectHandler: props.selectHandler || (x => {}),
        };
    }

    updateSuggestions(query) {
        if (query.length > 0) {
            const queryLower = query.toLowerCase();
            this.setState({
                suggestions: this.props.results.filter(result => result.nameLower.includes(queryLower)),
            });
        }
        else {
            this.setState({suggestions: []});
        }
    }

    renderSuggestions(maxResults=8) {
        return(this.state.suggestions
                .slice(0, maxResults)
                .map(suggestion => ({
                        label:
                            <Box fill>
                                {
                                    `${suggestion.name} (${suggestion.overall_place})`
                                }
                            </Box>,
                        value: suggestion.index,
                    })
                )
        );
    }

    // this is gross, but grommet does not seem to provide a method for handling "enter"
    checkForAndHandleEnter(event) {
        if (event.key === 'Enter' && this.state.suggestions.length) {
            this.state.selectHandler(this.state.suggestions[0].index);
        }
    }

    render() {
        return(
            <TextInput
                onChange={(event) => this.updateSuggestions(event.target.value)}
                onSelect={(event) => this.state.selectHandler(event.suggestion.value)}
                suggestions={this.renderSuggestions()}
                placeholder="Search within Race"
                style={{backgroundColor: "#e6f1f0"}}
                onKeyPress={(event) => this.checkForAndHandleEnter(event)}/>)
    }
}

class RaceResult extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            results: null,
            raceMetadata: null,
            callComplete: false,
            currentPage: 0,
        };
    }

    // mutates the input list and objects
    preprocessResults(results) {
        const resultsSorted = results.sort((a,b) => a.overall_place - b.overall_place)
        return resultsSorted
            .map((result, index) => {
                result['index'] = index;
                result['nameLower'] = result.name.toLowerCase();

                return result;
            })
    }

    componentDidMount() {
        callBackend(`/api/races/${this.props.raceId}`)
            .then(data => this.setState({
                results: this.preprocessResults(data.results),
                raceMetadata: data.raceMetadata,
            }))
            .catch(error => console.log(error))
            .finally(() => this.setState({callComplete: true}));
    }

    getCurrentPageResults() {
        const resultStartIndex = PAGE_SIZE * this.state.currentPage;
        const resultEndIndex = Math.min(PAGE_SIZE * (this.state.currentPage + 1), this.state.results.length);

        return this.state.results.slice(resultStartIndex, resultEndIndex);
    }

    renderCurrentLocation(){
        return(
            <Box direction="row" margin={{top: "small", bottom: "small"}} alignSelf="center">
                <ChapterPrevious
                    color="rgb(144,96,235)"
                    onClick={() => this.setState({currentPage: Math.max(0, this.state.currentPage - 10)})}
                    style={{cursor: "pointer" }}
                />
                <CaretPrevious
                    color="rgb(144,96,235)"
                    onClick={() => this.setState({currentPage: Math.max(0, this.state.currentPage - 1)})}
                    style={{cursor: "pointer" }}
                />
                <Text>
                    {
                        `Displaying
                                        ${this.state.currentPage * PAGE_SIZE + 1}-${Math.min(this.state.results.length,
                            (this.state.currentPage + 1) * PAGE_SIZE)}
                                        of ${this.state.results.length}`
                    }
                </Text>
                <CaretNext
                    color="rgb(144,96,235)"
                    onClick={() =>
                        this.setState({
                            currentPage: Math.min(Math.floor(this.state.results.length / PAGE_SIZE),
                                this.state.currentPage + 1)})}
                    style={{cursor: "pointer" }}
                />
                <ChapterNext
                    color="rgb(144,96,235)"
                    onClick={() =>
                        this.setState({
                            currentPage: Math.min(Math.floor(this.state.results.length / PAGE_SIZE),
                                this.state.currentPage + 10)})}
                    style={{cursor: "pointer" }}
                />
            </Box>
        );
    }

    render() {
        if (!this.state.results && this.state.callComplete) {
            return(<Grommet theme={grommet}> <NotFound /> </Grommet>)
        }

        if (!this.state.callComplete) {
            return(<Grommet theme={grommet}> <Spinner /> </Grommet>);
        }

        const currentPageResults = this.getCurrentPageResults();

        return(
            <Grommet theme={grommet}>
                <Box>
                    <Box direction="column">
                        <Box>
                            <Link to={`/event/${this.state.raceMetadata.eventId}`}
                                  style={{textDecoration: "none", color:"rgb(144,96,235)"}}>
                                <Heading margin="none" size="small">
                                    {this.state.raceMetadata.eventName}
                                </Heading>
                             </Link>
                        </Box>
                        <Box direction="row">
                            <Box border="right" margin={{right: "small"}} pad="small">
                                <Text>{(new Date(this.state.raceMetadata.date)).toISOString().split('T')[0]}</Text>
                            </Box>
                            <Box border="right" margin={{right: "small"}} pad="small">
                                <Text>{`${this.state.raceMetadata.distance} K`}</Text>
                            </Box>
                            <Box pad="small">
                                <Text>{this.state.raceMetadata.discipline}</Text>
                            </Box>
                        </Box>

                    </Box>
                    <Box margin={{left: "small", top: "small"}} style={{maxWidth: "500px"}}>
                        <RaceResultSearchBar
                            results={this.state.results}
                            selectHandler={index => this.setState({currentPage:  Math.floor(index / PAGE_SIZE)})}
                        />
                    </Box>
                    {
                        this.renderCurrentLocation()
                    }
                    <Box>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    {
                                        COLUMNS.map(col =>
                                            <TableCell key={col.header}>
                                                {
                                                    col.header
                                                }
                                            </TableCell>
                                        )
                                    }
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {
                                    currentPageResults.map(result =>
                                       <TableRow key={result.index}>
                                           {
                                               COLUMNS.map(col =>
                                                   <TableCell key={`${result.index}-${col.property}`}>
                                                       {
                                                           col.render ? col.render(result) : result[col.property]
                                                       }
                                                   </TableCell>
                                               )
                                           }
                                       </TableRow>
                                   )
                                }
                            </TableBody>
                        </Table>
                    </Box>
                    {
                        this.renderCurrentLocation()
                    }
                </Box>
            </Grommet>
        );
    }
}

export default RaceResult;