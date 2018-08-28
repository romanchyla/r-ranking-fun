import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

// TODO: plug in ajax https://vuejsdevelopers.com/2017/08/28/vue-js-ajax-recipes/

export default new Vuex.Store({
  strict: debug,
  
  state: {
    experiments: [
        {
          id: 0,
          query: 'title:(foo bar)',
          reporter: 'rchyla@cfa.harvard.edu',
          numfound: 45000,
          numused: 300,
          numrelevant: 20,
        },
        {
          id: 1,
          query: 'title:(foo bar)',
          reporter: 'rchyla@cfa.harvard.edu',
          numfound: 45000,
          numused: 300,
          numrelevant: 20,
        },
      ],
    experiment: {
        parameters: {
            query: 'title:(foo bar)',
            params: 'sort=score+desc&fl=classic_factor,title,bibcode',
            normalizeWeight: true,
            fieldBoost: ['classic_factor', 'cite_read_bost'],
            kRange: [0.5, 1.5],
            bRange: [0.75, 1.0],
            docLenRange: [0, 50],
            useK: true,
            useB: true,
            useBoost: true,
            useNormalization: true,
            useDocLen: false
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
            },
            {
              hitid: 1,
              relevant: -1,
              bibcode: 'bibcode1',
              title: 'Example title 1',
              authors: 'John, D; Emil, E; Patrick, P',
              publication: 'ApJ 2005, vol 1',
              abstract: 'looooooooooooooooooooooong abstract...........'
            },
            {
              hitid: 2,
              relevant: -1,
              bibcode: 'bibcode1',
              title: 'Example title 2',
              authors: 'John, D; Emil, E; Patrick, P',
              publication: 'ApJ 2005, vol 1',
              abstract: 'looooooooooooooooooooooong abstract...........'
            },
            {
              hitid: 3,
              relevant: -1,
              bibcode: 'bibcode1',
              title: 'Example title 3',
              authors: 'John, D; Emil, E; Patrick, P',
              publication: 'ApJ 2005, vol 1',
              abstract: 'looooooooooooooooooooooong abstract...........'
            },
          ]
    }
  },

  mutations: {
    
  },

  actions: {
    
  }
  
})