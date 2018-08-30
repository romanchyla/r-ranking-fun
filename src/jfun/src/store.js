import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import * as _ from 'lodash'

Vue.use(Vuex)


axios.defaults.baseURL = process.env.API_URL || 'http://localhost:4000/';
axios.defaults.headers.common['Accept'] = 'application/json';
axios.defaults.headers.post['Content-Type'] = 'application/json';


export default new Vuex.Store({
  strict: false,
  
  state: {
    dashboard: [
        {
          eid: 0,
          query: 'example title:(foo bar)',
          reporter: 'rchyla@cfa.harvard.edu',
          info: '34000/300/20'
        }
      ],
    experiment: {
        eid: 0,
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
    },
    papers:  [
            {
              hitid: 0,
              docid: 23467,
              relevant: 0,
              bibcode: 'bibcode1',
              title: 'Example title 0',
              authors: 'John, D; Emil, E; Patrick, P',
              publication: 'ApJ 2005, vol 1',
              abstract: 'looooooooooooooooooooooong abstract...........'
            },
          ],
    relevant: []
    
  },

  mutations: {
    updateDashboard(state, payload) {
      state.dashboard = payload.results
    },

    updateExperiment(state, payload) {
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
        extra_params: '',
        description: '',
        query: '',
        reporter: '',
        eid: ''
      }
      const picks = _.pick(payload.experiment_params,
        ['kRange', 'bRange', 'docLenRange', 'useK', 'useB', 
        'useDocLen', 'useNormalization', 'useBoost',
        'extra_params'])
      
      const parameters = _.defaults(picks, _.pick(payload, ['eid', 'reporter', 'query', 'description']), defaults)
      
      
      state.experiment = parameters
      console.log('updating experiment/papers store', parameters)

      this.commit('updatePapers', payload);      
    },

    updatePapers(state, payload) {
      state.query_results = payload.query_results
      state.relevant = payload.relevant

      if (payload.query_results && payload.query_results.response) {
          // map of all relevant docids (preserving order)
          const m = {}
          _.each(payload.relevant, function(element, index, list) {
            m[element] = index+1
          })

          const docs = payload.query_results.response.docs
          _.each(docs, function(element, index, list) {
            element['hitid'] = index
            if (m[element.docid]) {
              element['relevant'] = m[element.docid]
            }
            else {
              element['relevant'] = 0
            }
            if (element.author) {
              element.authors = element.author.join('; ')
            }
          })
        state.papers = docs
      }
      else {
        state.papers = []
      }
    },

    updateRelevant(state, payload) {
      state.relevant = payload.relevant
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
      return new Promise((resolve) => {
        axios.get('/experiment/' + eid).then((response) => {
          context.commit('updateExperiment', response.data);
          resolve();
        });
      });
    },

    saveExperiment(context) {
      return new Promise((resolve) => {
        const data = {
          verb: 'save-experiment',
          data: this.state.experiment
        }
        axios.post('/experiment/' + this.state.experiment.eid, data).then((response) => {
          context.commit('updateExperiment', response.data);
          resolve();
        });
      });
    },

    updateRelevant(context, {docids}) {
      return new Promise((resolve) => {      
        const data = {
          verb: 'replace-relevant',
          data: docids
        }
        axios.post('/experiment/' + this.state.experiment.eid, data).then((response) => {
          context.commit('updatePapers', response.data);
          resolve();
        });
      });
    }
  }
  
})