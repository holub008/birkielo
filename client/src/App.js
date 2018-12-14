import React, { Component } from 'react';
import {BrowserRouter as Router, Route, Switch } from 'react-router-dom';

import NavBar from "./components/NavBar";
import Home from "./components/Home";
import About from "./components/About";
import Support from "./components/Support";
import RacerSummary from "./components/RacerSummary";

import './App.css';

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
                            <Route path="/about" exact component={About}/>
                            <Route path="/support" exact component={Support}/>
                        </Switch>
                    </div>
                </div>
            </Router>);
    }
}

export default App;
