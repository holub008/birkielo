import React, { Component } from 'react';
import {BrowserRouter as Router, Route} from 'react-router-dom';

import NavBar from "./components/NavBar";
import Home from "./components/Home";
import RacerSummary from "./components/RacerSummary";
import RankedRacerList from "./components/RankedRacerList";

import './App.css';

class App extends Component {
    render() {
        return (
            <Router>
                <div className="app">
                    <NavBar />
                    <div className="page">
                        <Route path="/" exact component={Home} />
                        <Route path={"/racer/:racer_id"} render={
                            (props) => (<RacerSummary racerId={props.match.params.racer_id}
                                                      key={props.match.params.racer_id}/>)
                        }/>
                        <Route path="/rank/:gender" render={
                            (props) => (<RankedRacerList minRank={1} gender={props.match.params.gender}
                                                         key={props.match.params.gender}/>)
                        }/>
                    </div>
                </div>
            </Router>);
    }
}

export default App;
