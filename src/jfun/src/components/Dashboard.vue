<template>
  <div>
  <v-data-table
    :headers="headers"
    :items="experiments"
    class="dashboard"
    v-model="selected"
    item-key="eid"
  >
    <template slot="items" slot-scope="props">
      <td>{{ props.item.eid }}</td>
      <td>
        <v-checkbox
          v-model="props.selected"
          primary
          hide-details
        ></v-checkbox>
      </td>
      <td v-on:click="doClick('show', props.item)">{{ props.item.query }}</td>
      <td>{{ props.item.reporter }}</td>
      <td title="numFound/numUsed/numGolden">{{ props.item.info }}</td>
    </template>
  </v-data-table>
    <div>
      <v-btn color="green" v-on:click="doClick('create')">Create</v-btn>
      <v-btn color="info" v-on:click="doClick('show')">Show</v-btn>
      <v-btn color="warning" v-on:click="doClick('run')">(Re-)Run</v-btn>
      <v-btn color="success" v-on:click="doClick('copy')">Copy</v-btn>
    </div>
  </div>
</template>

<script>
export default {
    data () { //TODO: plugin api calls
      return {
        selected: [],
        headers: [
          { text: 'ID', value: 'eid', 'sortable': true },
          { text: 'Selected', value: 'selected', 'sortable': false },
          {
            text: 'Query',
            align: 'left',
            sortable: true,
            value: 'query'
          },
          { text: 'Reporter', value: 'reporter' },
          { text: 'Info', value: 'numused' }
        ]
      }
    },

    computed: {
      experiments: function() {return this.$store.state.dashboard}
    },

    mounted: function() {
      this.$store.dispatch("refreshDashboard");
    },

    methods: {
      doClick: function(action, item) {
        
        if (action === 'show') {
          if (!item) { // selected papers, show the first one
            if (this.selected.length > 0) {
              console.log(this.selected, this.$data.selected[0])
              const item = this.selected[0]
              this.$store.dispatch('loadExperiment', {eid: item.eid}).then(() => {
                this.$router.push({path: '/experiment/overview/' + item.eid})
              })
            }
          }
          else {
            this.$store.dispatch('loadExperiment', {eid: item.eid}).then(() => {
              this.$router.push({path: '/experiment/overview/' + item.eid})
            })
            
          }
          
        }
        else if (action === 'create') {
          this.$store.dispatch('createExperiment').then(() => {
            this.$router.push({path: '/experiment/overview/' + this.$store.state.experiment.eid})
          })
        }
        else if (action == 'run') {
          this.$store.dispatch('getResults', {eid: this.selected[0].eid}).then(() => {
            this.$router.push({path: '/experiment/results/' + this.$store.state.experiment.eid})
          })
        }
      }
    }
}
</script>

<style>

</style>
