import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import * as _ from 'lodash'

Vue.use(Vuex)


// a kludge for development
if (window && window.location.toString().indexOf(':8080') > -1) {
  axios.defaults.baseURL = 'http://localhost:4000/';
} else if (window && window.location.toString().indexOf('adsabs.harvard.edu/scorer') > -1) {
  axios.defaults.baseURL = 'http://adsabs.harvard.edu/scorer';
}

axios.defaults.headers.common['Accept'] = 'application/json';
axios.defaults.headers.post['Content-Type'] = 'application/json';

const massagePapers = function(payload) {
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
  return docs;
}

const dataDefaults = {
  dashboard: [
    {
      eid: 0,
      query: '',
      reporter: '',
      info: '34000/300/20'
    }
  ],
  experiment: {
      eid: '',
      query: '',
      extra_params: 'sort=score+desc&fl=classic_factor,title,bibcode',
      description: '',
      reporter: '',
      
      useK: true,
      kRange: [0.01, 1.8, 0.1],
      kStepSize: 0.1,
      
      useB: true,
      bRange: [0.01, 1.0, 0.05],
      bStepSize: 0.1,
      
      useBoost: false,
      fieldBoost: ['classic_factor', 'cite_read_boost'],
      boostSelection: '',
      
      useDocLen: false,
      docLenRange: [10, 50, 10],
      docStepSize: 10,
      
      useNormalization: false,
      normalizeWeight: true,
      
      useConstant: true,
      constFields: ['first_author', 'author', 'title', 'abstract', 'keyword', 'identifier', 'bibstem', 'year'],
      constSelection: [],
      constRange: [0, 10, 1],
      constStepSize: 1,
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
  relevant: [],
  experiment_results: {
    progress: 0,
    message: '',
    runs: 0,
    results: {},
    papers: []
  }
}

export default new Vuex.Store({
  strict: false,
  
  state: function() {
    return {
      dashboard: _.clone(dataDefaults.dashboard),
      experiment: _.clone(dataDefaults.experiment),
      papers: _.clone(dataDefaults.papers),
      relevant: _.clone(dataDefaults.relevant),
      experiment_results: _.clone(dataDefaults.experiment_results)
    }
  },

  mutations: {
    resetExperiment(state, payload) {
      state.experiment = _.clone(dataDefaults.experiment),
      state.papers = _.clone(dataDefaults.papers),
      state.relevant = _.clone(dataDefaults.relevant),
      state.experiment_results = _.clone(dataDefaults.experiment_results)
    },

    updateDashboard(state, payload) {
      state.dashboard = payload.results
    },

    updateExperiment(state, payload) {
      const picks = _.pick(payload.experiment_params, _.keys(dataDefaults.experiment))
      
      const parameters = _.defaults(picks, _.pick(payload, ['eid', 'reporter', 'query', 'description']), dataDefaults.experiment)
      
      
      state.experiment = parameters
      console.log('updating experiment/papers store', parameters)

      this.commit('updatePapers', payload);      
      this.commit('updateResults', payload);      
    },

    updatePapers(state, payload) {
      state.query_results = payload.query_results
      state.relevant = payload.relevant

      if (payload.query_results && payload.query_results.response) {
        state.papers = massagePapers(payload)
      }
      else {
        state.papers = []
      }
    },

    updateSimulatedPapers(state, payload) {
      if (payload.message) {
        state.experiment_results.progress = payload.progress;
        state.experiment_results.message = payload.message;
      }
      else {
        state.experiment_results.papers = massagePapers(payload);
        state.experiment_results.progress = 1.0;
        state.experiment_results.message = '';
      }
      
    },

    updateRelevant(state, payload) {
      state.relevant = payload.relevant
    },

    updateResults(state, payload) {
      
      state.experiment_results = _.defaults(payload.experiment_results, dataDefaults.experiment_results);
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
      // first reset all values
      context.commit('resetExperiment');
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
        
        data.data['kRange'][2] = data.data['kStepSize']
        data.data['bRange'][2] = data.data['bStepSize']
        data.data['docLenRange'][2] = data.data['docStepSize']
        data.data['constRange'][2] = data.data['constStepSize']

        // remove some defaults
        delete data.data['fieldBoost']
        delete data.data['constFields']
        

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
    },

    getResults(context, {eid: eid}) {
      return new Promise((resolve) => {
        axios.post('/results/' + eid).then((response) => {
          context.commit('updateResults', response.data);
          resolve();
        });
      });
    },

    getSimulatedResults(context, {eid: eid, setid: setid}) {
      return new Promise((resolve) => {
        axios.get('/reorder/' + eid + '/' + setid).then((response) => {
          context.commit('updateSimulatedPapers', response.data);
          resolve(response.data);
        });
      });
    }

  }
  
})