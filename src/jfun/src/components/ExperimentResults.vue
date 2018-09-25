<template>
  <v-container>
  <v-layout row wrap>
    
    <v-flex>
        <v-data-table
            :headers="experimentsHeaders"
            :items="experiments"
            :loading="true"
            class="elevation-1"
            v-model="selected"
            hide-actions
            item-key="id"
            >

            <v-progress-linear slot="progress" color="blue" ></v-progress-linear>
            <template slot="items" slot-scope="props">
            <td>
                <v-checkbox
                v-model="props.selected"
                primary
                hide-details
                v-on:click="doClick"
                ></v-checkbox>
            </td>
            <td>{{ props.item.id }}</td>
            <td class="text-xs-right">{{ props.item.k1 }}</td>
            <td class="text-xs-right">{{ props.item.b }}</td>
            <td class="text-xs-right">{{ props.item.perfield_avgdoclen }}</td>
            <td class="text-xs-right">{{ props.item.idf_normalization }}</td>
            <td class="text-xs-right">{{ props.item.use_fieldboost }}</td>
            </template>
        </v-data-table>
    </v-flex>
    

    

    
    <v-flex>
        <component
            v-bind:is="simulatedPapers"
        ></component>
    </v-flex>
    
  </v-layout>
  </v-container>
</template>

<script>
import ListOfArticles from './ListOfSimulatedArticles'
import * as _ from 'lodash'

export default {
    data: () => ({
      selected: [],
      expandRow: null,
      experimentsHeaders: [
        { text: 'id', value: 'id', sortable: false },
        { text: 'Score', value: 'score', sortable: false },
        { text: 'k', value: 'k', sortable: false },
        { text: 'b', value: 'b', sortable: false },
        { text: 'Document Length', value: 'docLen', sortable: false },
        { text: 'Normalize Weight', value: 'normalizeWeight', sortable: false },
        { text: 'Document Boost', value: 'fieldBoost', sortable: false },
      ],
      simulatedPapers: function() {
          return ListOfArticles
      }
    }),

    mounted: function() {
        this.$store.dispatch('getSimulatedResults', {eid: this.$store.state.experiment.eid, setid: 0})
    },

    methods: {
        doClick: function() {
            if (this.$data.selected.length > 0)
                this.$store.dispatch('getSimulatedResults', {eid: this.$store.state.experiment.eid, setid: this.selected[0]})
        }
    },
    computed: {
      experiments: function() {
          debugger;
          let r = _.clone(this.$store.state.experiment_results.results)
          const out = []
          _.each(r, function(elem, i, list) {
              let o = {}
              o['id'] = i;
              o['score'] = elem[0]
              _.merge(o, elem[1])
              if (o.perdoc_boost !== {}) {
                o.use_fieldboost = true
              }
              else {
                o.use_fieldboost = false
              }
              out.push(o)
          })
          return out
          },
      
  },
}
</script>

<style>

</style>
