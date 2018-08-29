import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import * as _ from 'lodash'

Vue.use(Vuex)


axios.defaults.baseURL = 'http://localhost:4000/';
axios.defaults.headers.common['Accept'] = 'application/json';
axios.defaults.headers.post['Content-Type'] = 'application/json';


export default new Vuex.Store({
  strict: false,
  
  state: {
    experiments: [
        {
          eid: 0,
          query: 'example title:(foo bar)',
          reporter: 'rchyla@cfa.harvard.edu',
          info: '34000/300/20'
        }
      ],
    experiment: {
        eid: 0,
        parameters: {
            query: 'title:(foo bar)',
            extra_params: 'sort=score+desc&fl=classic_factor,title,bibcode',
            normalizeWeight: true,
            fieldBoost: ['classic_factor', 'cite_read_bost'],
            kRange: [0.5, 1.5],
            bRange: [0.75, 1.0],
            docLenRange: [0, 50],
            useK: true,
            useB: true,
            useBoost: true,
            useNormalization: true,
            useDocLen: false,
            reporter: '',
            query: ''
          },
        papers:  [
            {
              hitid: 0,
              relevant: 0,
              bibcode: 'bibcode1',
              title: 'Example title 0',
              authors: 'John, D; Emil, E; Patrick, P',
              publication: 'ApJ 2005, vol 1',
              abstract: 'looooooooooooooooooooooong abstract...........'
            }
          ]
    }
  },

  mutations: {
    updateDashboard(state, payload) {
      state.experiments = payload.results
    },

    updateExperiment(state, payload) {
      debugger;
      
      const defaults = {
        kRange: [0.01, 12, 0.1],
        bRange: [0.001, 1.0, 0.05],
        docLenRange: [10, 50, 5],
        fieldBoost: ['classic_factor', 'cite_read_boost'],
        useK: true,
        useB: true,
        useDocLen: false,
        useNormalization: false,
        useBoost: false,
        extra_params: ''
      }
      const picks = _.pick(payload.experiment_params,
        ['kRange', 'bRange', 'docLenRange', 'useK', 'useB', 
        'useDocLen', 'useNormalization', 'useBoost',
        'extra_params'])
      
      const parameters = _.defaults(picks, defaults, 
        _.pick(payload, ['reporter', 'query', 'description']))
      const m = {}
      _.each(payload.relevant, function(element, index, list) {
        m[element] = index+1
      })
      _.each(payload.query_results, function(element, index, list) {
        if (m[element.docid]) {
          element['relevant'] = m[element.docid]
        }
        else {
          element['relevant'] = false
        }
      })
      
      state.experiment = {
        eid: payload.eid,
        parameters: parameters,
        papers: payload.query_results
        }
    }
  },

  actions: {
    refreshDashboard(context) {
      return new Promise((resolve) => {
        axios.get('/dashboard').then((response) => {
          context.commit('updateDashboard', response.data);
          resolve();
        });
      });
    },

    createExperiment(context) {
      return new Promise((resolve) => {
        axios.get('/experiment/-1').then((response) => {
          context.commit('updateExperiment', response.data);
          resolve();
        });
      });
    },

    loadExperiment(context, {eid}) {
      debugger;
      return new Promise((resolve) => {
        axios.get('/experiment/' + eid).then((response) => {
          context.commit('updateExperiment', response.data);
          resolve();
        });
      });
    },

    saveExperiment(context) {
      debugger;
      return new Promise((resolve) => {
        const data = {
          verb: 'save-experiment',
          data: _.merge(this.state.experiment.parameters, 
            {reporter: this.state.experiment.parameters.reporeter,
              query: this.state.experiment.parameters.query,
              description: this.state.experiment.parameters.description
            })
        }
        axios.post('/experiment/' + this.state.experiment.eid, data).then((response) => {
          context.commit('updateExperiment', response.data);
          resolve();
        });
      });
    }
  }
  
})