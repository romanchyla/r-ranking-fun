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
      >
      <template slot="items" slot-scope="props">
        <tr class="sortableRow" :key="itemKey(props.item)" @click="props.expanded = !props.expanded"> <!-- NOTE:  You'll need a unique ID, that is specific to the given item, for the key.   Not providing a unique key that's bound to the item object will break drag and drop sorting.  The itemKey method will return a uid for a given object using WeakMap.  You could just use a property in the object with a unique value, like "props.item.name" in this case, but often getting a unique value from the object's properties can be difficult, like when adding new rows, or when the unique field is open to editing, etc. -->
          <td class="px-1" style="width: 0.1%">
            <v-btn style="cursor: move" icon class="sortHandle"><v-icon>drag_handle</v-icon></v-btn>
          </td>
          <td >{{ props.item.docid }}</td>
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
         <div class="abstract" v-if="props.item.abstract"><b>abstract</b>: {{ props.item.abstract }} </div>
         <div v-if="props.item.formula"><b>formula</b>: {{ props.item.formula }} </div>
        </v-card>
      </template>
      
    </v-data-table>
</template>

<script>
import Sortable from 'sortablejs'
import * as _ from 'lodash'

export default {
  mounted () {
    /* eslint-disable no-new */
    let t = this.getRef()
    new Sortable(
      this.$refs[t].$el.getElementsByTagName('tbody')[0],
        {
          draggable: '.sortableRow',
          handle: '.sortHandle',
          onStart: this.dragStart,
          onEnd: this.dragReorder
        }
      )
    },

  methods: {
    getRef: function() {
      return 'articleTable'
    },
    getSortKey: function() {
      return 'docid'
    },
    getItems: function() {
      return this.items;
    },
    dragStart ({item}) {
      const nextSib = item.nextSibling
      if (nextSib &&
          nextSib.classList.contains('datatable__expand-row')) {
        this.expandRow = nextSib
      } else {
        this.expandRow = null
      }
    },
    dragReorder ({item, oldIndex, newIndex}) {
      const nextSib = item.nextSibling
      if (nextSib &&
          nextSib.classList.contains('datatable__expand-row') &&
          nextSib !== this.expandRow) {
        item.parentNode.insertBefore(item, nextSib.nextSibling)
      }
      const movedItem = this.items.splice(oldIndex, 1)[0]
      this.items.splice(newIndex, 0, movedItem)
    },
    itemKey (item) {
      if (!this.itemKeys.has(item)) this.itemKeys.set(item, ++this.currentItemKey)
      return this.itemKeys.get(item)
    },

    onClick: () => {
      debugger
      //this.$store.dispatch('updateRelevant', {selection: this.selection})
    },
    
  },
  
  data: () => ({
      selected: [],
      expandRow: null,
      itemKeys: new WeakMap(),
      currentItemKey: 0,
      headers: [
        {
          sortable: false
        },
        { text: 'Docid', value: 'docid', sortable: false },
        { text: 'Lucene Score', value: 'score', sortable: false },
        {
          text: 'Relevant',
          align: 'left',
          sortable: false,
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
    
      items: function() {return this.$store.state.papers},
      relevant: {
        get: function() {return this.$store.state.relevant},
        set: function(docids) {
          debugger;
          console.log(docids)
          this.$store.dispatch('updateRelevant', {docids: docids})
        }
      }
  },
}
</script>

<style>

</style>
