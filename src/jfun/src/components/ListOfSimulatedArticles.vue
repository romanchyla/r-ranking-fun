<template>
    <v-data-table
        v-bind:headers="headers"
        :items="getItems()"
        class="elevation-1"
        :ref="getRef()"
        item-key="docid"
        expand
        :rows-per-page-items="[25,50,{text:'all',value:-1}]"
        v-model="relevant"
        :pagination.sync="pagination"
        must-sort
      >
      <template slot="items" slot-scope="props">
        <tr :key="itemKey(props.item)" @click="props.expanded = !props.expanded"> 
          
          
          <td >{{ props.item.new_score }}</td>
          <td >{{ props.item.score }}</td>
          <td><v-checkbox
                :input-value="props.item.relevant !== 0"
                :value="props.item.docid"
                v-model="relevant"
                ></v-checkbox></td>
          <td >{{ props.item.title[0] }}</td>
          <td >{{ props.item.authors }}</td>
          <td >{{ props.item.pub_raw }}</td>

        </tr>
      </template>
      
      <template slot="expand" slot-scope="props" >
        <v-card flat :key="itemKey(props.item) + '_expand'">
         <ul>
          <li v-for="(value, key) in props.item">
            <b>{{ key }}</b>: {{ value }}
          </li>
        </ul>
        </v-card>
      </template>
      
    </v-data-table>
</template>

<script>

import * as _ from 'lodash'

export default {
  
  methods: {
    getRef: function() {
      return 'articleTable'
    },
    getSortKey: function() {
      return 'new_score'
    },
    getItems: function() {
      return this.items;
    },
    itemKey (item) {
      if (!this.itemKeys.has(item)) this.itemKeys.set(item, ++this.currentItemKey)
      return this.itemKeys.get(item)
    }
    
  },
  
  data: () => ({
      selected: [],
      expandRow: null,
      itemKeys: new WeakMap(),
      currentItemKey: 0,
      pagination: {
          'sortBy': 'new_score',
          'descending': true,
          'rowsPerPage': -1
      },
      headers: [
        { text: 'New Score', value: 'new_score', sortable: true },
        { text: 'Lucene Score', value: 'score', sortable: true },
        {
          text: 'Relevant',
          align: 'left',
          sortable: true,
          value: 'relevant'
        },
        {
          text: 'Title',
          align: 'left',
          sortable: false,
          value: 'title'
        },
        { text: 'Authors', value: 'authors', sortable: false },
        { text: 'Publication', value: 'publication', sortable: false },
        
      ]
    }),

  computed: {
    
      items: function() {return this.$store.state.experiment_results.papers},
      relevant: {
        get: function() {return this.$store.state.relevant},
        set: function(docids) {
          // pass
        }
      }
  },
}
</script>

<style>

</style>
