

<script>
import ListOfArticles from './ListOfArticles'
import * as _ from 'lodash'

export default {
    extends: ListOfArticles,
    methods: {
        getRef: function() {
            return 'selectedArticles'
        },
        getSortKey: function() {
            return 'docid'
        },
        getItems: function() {
            let out = _.clone(this.items)
            
            _.remove(out, function(value, index, array) {
            if (value.relevant === 0)
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
