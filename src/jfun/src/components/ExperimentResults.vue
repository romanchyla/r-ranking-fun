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
                @change="doClick"
                ></v-checkbox>
            </td>
            <td>{{ props.item.score }}</td>
            <td >{{ props.item.k1 }}</td>
            <td >{{ props.item.b }}</td>
            <td >{{ props.item.perfield_avgdoclen }}</td>
            <td >{{ props.item.idf_normalization }}</td>
            <td >{{ props.item.use_fieldboost }}</td>
            <td >{{ props.item.consts }}</td>
            </template>
        </v-data-table>
    </v-flex>
</v-layout>
    <p v-if="message"> {{message}} </p>
    <p v-else>Number of combinations explored: {{runs}}, Time elapsed: {{elapsed}} s., Progress: {{progress}}</p>
    <v-layout row wrap>
    <v-flex>
        <component
            v-bind:is="simulatedPapers"
            v-model="results"
        ></component>
    </v-flex>
    
  </v-layout>
  </v-container>
</template>

<script>
import ListOfArticles from "./ListOfSimulatedArticles";
import * as _ from "lodash";

export default {
  data: () => ({
    selected: [],
    expandRow: null,
    results: [],
    experimentsHeaders: [
      { text: "id", value: "id", sortable: false },
      { text: "Score", value: "score", sortable: false },
      { text: "k", value: "k", sortable: false },
      { text: "b", value: "b", sortable: false },
      { text: "Document Length", value: "docLen", sortable: false },
      { text: "Normalize Weight", value: "normalizeWeight", sortable: false },
      { text: "Document Boost", value: "fieldBoost", sortable: false },
      { text: "Constants", value: "consts", sortable: false }
    ]
  }),

  mounted: function() {
    this.$store.dispatch("getSimulatedResults", {
      eid: this.$store.state.experiment.eid,
      setid: 0
    });
  },

  methods: {
    doClick: function() {
      if (this.$data.selected.length > 0) {

        let s = this.$data.selected[this.$data.selected.length - 1];
        this.$store.dispatch("getSimulatedResults", {
          eid: this.$store.state.experiment.eid,
          setid: s.id
        });
        this.$data.selected.length = 0;
        this.$data.selected.push(s);
      }
    }
  },
  computed: {
    experiments: function() {

      let r = _.clone(this.$store.state.experiment_results.results);
      const out = [];
      _.each(r, function(elem, i, list) {
        let o = {};
        o["id"] = i;
        o["score"] = elem[0];
        _.merge(o, elem[1]);
        if (o.perdoc_boost !== {}) {
          o.use_fieldboost = true;
        } else {
          o.use_fieldboost = false;
        }
        out.push(o);
      });
      return out;
    },
    simulatedPapers: function() {
      return ListOfArticles;
    },
    elapsed: function() {return this.$store.state.experiment_results.elapsed},
    runs: function() {return this.$store.state.experiment_results.runs},
    progress: function() {return this.$store.state.experiment_results.progress},
    message: function() {return this.$store.state.experiment_results.message},
  }
};
</script>

<style>
</style>
