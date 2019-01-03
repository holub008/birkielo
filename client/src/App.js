import React, { Component } from 'react';
import {BrowserRouter as Router, Route, Switch } from 'react-router-dom';

import NavBar from "./components/NavBar";
import Home from "./components/Home";
import About from "./components/About";
import Support from "./components/Support";
import RacerSummary from "./components/RacerSummary";
import RankedRacerList from "./components/RankedRacerList";

import {apiGender} from "./util/data";

import './App.css';
import SearchResults from "./components/SearchResults";

class App extends Component {
    render() {
        return (
            <Router>
                <div className="app">
                    <Switch>
                        <Route path="/" exact component={NavBar} />
                        <Route path="/" render={ () => <NavBar searchBar />} />
                    </Switch>

                    <div className="page">
                        <Switch>
                            <Route path="/" exact component={Home} />
                            <Route path={"/racer/:racer_id"} render={
                                (props) => <RacerSummary racerId={props.match.params.racer_id}
                                                         key={props.match.params.racer_id}/>
                            }/>
                            <Route path="/about/:feature?" render={
                                (props) => <About feature={props.match.params.feature}/>}/>
                            <Route path="/support" exact component={Support}/>
                            <Route path="/rankings/:sex" exact render={
                                (props) => <RankedRacerList gender={apiGender(props.match.params.sex)}
                                                            minRank={1}/>}/>
                            <Route path="/search/:query" exact render={
                                (props) => <SearchResults query={props.match.params.query}/>
                            }/>
                        </Switch>
                    </div>
                </div>
            </Router>);
    }
}

export default App;
