<template>
  <v-data-table
    :headers="headers"
    :items="experiments"
    hide-actions
    class="elevation-1"
  >
    <template slot="items" slot-scope="props">
      <td>{{ props.item.query }}</td>
      <td>{{ props.item.reporter }}</td>
      <td>{{ props.item.numused }}</td>
      <td>{{ props.item.numfound }}</td>
      <td>{{ props.item.numrelevant }}</td>
    </template>
  </v-data-table>
</template>

<script>
export default {
    data () { //TODO: plugin api calls
      return {
        headers: [
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
        ]
      }
    }
}
</script>

<style>

</style>
