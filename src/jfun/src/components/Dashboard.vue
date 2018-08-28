<template>
  <div>
  <v-data-table
    :headers="headers"
    :items="experiments"
    class="dashboard"
    v-model="selected"
  >
    <template slot="items" slot-scope="props">
      <td>
        <v-checkbox
          v-model="props.selected"
          primary
          hide-details
        ></v-checkbox>
      </td>
      <td v-on:click="doClick('show', props.item)">{{ props.item.query }}</td>
      <td>{{ props.item.reporter }}</td>
      <td>{{ props.item.numused }}</td>
      <td>{{ props.item.numfound }}</td>
      <td>{{ props.item.numrelevant }}</td>
    </template>
  </v-data-table>
    <div>
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
          { text: 'Selected', value: 'selected', 'sortable': false },
          {
            text: 'Query',
            align: 'left',
            sortable: true,
            value: 'query'
          },
          { text: 'Reporter', value: 'reporter' },
          { text: 'Size', value: 'numused' },
          { text: 'Total Size', value: 'numfound' },
          { text: 'Relevant', value: 'numrelevant' }
        ],
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
        ]
      }
    },

    methods: {
      doClick: function(action, item) {
        if (action === 'show') {
          if (!item) {
            if (this.selected.length > 0) {
              let item = this.selected[0];
              this.$router.push({path: '/experiment/overview/' + item.id})
            }
          }
          else {
            this.$router.push({path: '/experiment/overview/' + item.id})
          }
          
        }
      }
    }
}
</script>

<style>

</style>
