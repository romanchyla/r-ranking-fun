<template>

  <v-data-table
    :headers="experimentsHeaders"
    :items="experiments"
    :loading="true"
    class="elevation-1"
  >
    <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
    <template slot="experiments" slot-scope="props">
      <td>{{ props.item.name }}</td>
      <td class="text-xs-right">{{ props.item.calories }}</td>
      <td class="text-xs-right">{{ props.item.fat }}</td>
      <td class="text-xs-right">{{ props.item.carbs }}</td>
      <td class="text-xs-right">{{ props.item.protein }}</td>
      <td class="text-xs-right">{{ props.item.iron }}</td>
    </template>
  </v-data-table>

  

</template>

<script>
export default {
    data: () => ({
      
      expandRow: null,
      experimentsHeaders: [
        { text: 'Score', value: 'score', sortable: false },
        { text: 'k', value: 'k', sortable: false },
        { text: 'b', value: 'b', sortable: false },
        { text: 'Document Length', value: 'docLen', sortable: false },
        { text: 'Normalize Weight', value: 'normalizeWeight', sortable: false },
        { text: 'Document Boost', value: 'fieldBoost', sortable: false },
      ]
    }),

  computed: {
      experiments: {
        get: function() {
            return this.$store.dispatch('getResults', {eid: this.$store.state.experiment.eid})
            },
        set: function(docids) {
          // noop
        }
      }
  },
}
</script>

<style>

</style>
