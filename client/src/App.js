import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Welcome to the future home of Birkielo, the site for ranking and quantitative
          analysis of cross country skiers!
        </p>
        <a
          className="source-link"
          href="https://github.com/holub008/birkielo"
          >
          Birkielo Github Repository
          </a>
        </header>
      </div>);
  }
}

export default App;
