import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h2>Welcome to ADS Relevancy Engine</h2>
        </div>
        <div className="App-intro">
        <p>Hi! It is a pleasure to meet you. </p>
      
        <p>In here you can help ADS improve quality of the search results. We will run series of experiments
          and automatically try to find best set of parameters (for the relevance score evaluation). </p>
          
          <p>Since this is the first time we are seeing each other, would you be so kind to provide your email?</p>

          <form><input></input><button >Submit</button></form>
          
          <p>In order to run experiments, we'd like to ask you to do following:</p>
          
          <ol>
            <li>make (arbitrary) query</li>
            <li>review returned results and <b>select</b> papers that are most relevant</li>
            <li>(optionally) re-order the selected papers, to have the most relevant papers on top</li>
          </ol>

        <p>Based on your section, we will run hundreds of thounsands of experiments. You will be able to see 
          the results in real time. As we gather more data, we'll be able to converge and update our search engine.
          </p>

        

        </div>
      </div>
    );
  }
}

export default App;
