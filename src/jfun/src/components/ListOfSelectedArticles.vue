

<script>
import ListOfArticles from './ListOfArticles'
import * as _ from 'lodash'

export default {
    extends: ListOfArticles,
    methods: {
        getRef: function() {
            debugger
            return 'selectedArticles'
        },
        getSortKey: function() {
            return 'relevant'
        },
        getItems: function() {
            debugger;
            let out = _.clone(this.items)
            
            _.remove(out, function(value, index, array) {
            if (value.relevant < 0)
                return true
            })
            
            // re-sort by relevancy
            out = _.orderBy(out, ['relevant'])
            return out;
        }
    }
}
</script>

<style>

</style>
