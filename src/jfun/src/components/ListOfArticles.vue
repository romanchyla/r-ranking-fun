<template>
    <v-data-table
        v-bind:headers="headers"
        :items="getItems()"
        hide-actions
        class="elevation-1"
        ref="articleTable"
        item-key="hitid"
        expand
      >
      <template slot="items" slot-scope="props">
        <tr class="sortableRow" :key="itemKey(props.item)" @click="props.expanded = !props.expanded"> <!-- NOTE:  You'll need a unique ID, that is specific to the given item, for the key.   Not providing a unique key that's bound to the item object will break drag and drop sorting.  The itemKey method will return a uid for a given object using WeakMap.  You could just use a property in the object with a unique value, like "props.item.name" in this case, but often getting a unique value from the object's properties can be difficult, like when adding new rows, or when the unique field is open to editing, etc. -->
          <td class="px-1" style="width: 0.1%">
            <v-btn style="cursor: move" icon class="sortHandle"><v-icon>drag_handle</v-icon></v-btn>
          </td>
          <td><v-checkbox
                :input-value="props.item.relevant > -1"
                ></v-checkbox></td>
          <td >{{ props.item.title }}</td>
          <td >{{ props.item.authors }}</td>
          <td >{{ props.item.publication }}</td>

        </tr>
      </template>
      
      <template slot="expand" slot-scope="props" >
        <v-card flat :key="itemKey(props.item) + '_expand'">
         {{ props.item.abstract }}
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
    new Sortable(
      this.$refs.articleTable.$el.getElementsByTagName('tbody')[0],
      {
        draggable: '.sortableRow',
        handle: '.sortHandle',
        onStart: this.dragStart,
        onEnd: this.dragReorder
      }
    )},

  methods: {
    getItems: function() {
      let out = _.clone(this.items)
      if (window.location.toString().indexOf('selection') > -1 ) {
        _.remove(out, function(value, index, array) {
          if (value.relevant < 0)
            return true
        })
      }
      return out;
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
    }
  },
  
  data () {
    
    return {
      expandRow: null,
      itemKeys: new WeakMap(),
      currentItemKey: 0,
      headers: [
        {
          sortable: false
        },
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
        
      ],
      items: [
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
  }
}
</script>

<style>

</style>
