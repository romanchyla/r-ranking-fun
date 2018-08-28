<template>
  <v-card>
    
    <v-card-text>
      <v-form v-model="valid" ref="form" lazy-validation>
        <v-layout row wrap>
          <v-flex lg12 sm12>
            <v-text-field label="Reporter" name="reporter" v-model="reporter">
            </v-text-field>
          </v-flex>
          <v-flex lg12 sm12>
            <v-text-field label="Query" name="query" v-model="query">
            </v-text-field>
          </v-flex>
          <v-flex lg12 sm12>
            <v-text-field label="Additional Parameters (url format)" name="params" v-model="params" hint="All parameters must be properly URL encoded">
            </v-text-field>
          </v-flex>
          <v-flex lg12 sm12>
            <v-text-field textarea clearable=true label="Description" hint="Please describe your intent while making the search, this helps us evaluate search results/selections">
                
            </v-text-field>
          </v-flex>                              
          <v-spacer></v-spacer>
        </v-layout>


        <div>
            
            <v-checkbox
            label="simulate k1 parameter"
            v-model="useK"
            ></v-checkbox>
        <v-layout row wrap >
            k1 parameter controls the steepness of the slope; it affects the "TF" components of the BM25 formula; a higher values might lead to a fast 
        raising length normalization (effectively disregarding difference between documents with different term frequencies; however it is not 
        constant). Typically, the value of k1 is around 1.2 - however, try experimenting with large ranges (it is the CPU that will do the computations
        anyway)
            <v-flex
                shrink
                style="width: 60px"
            >
                <v-text-field
                v-model="kRange[0]"
                class="mt-0"
                hide-details
                single-line
                type="number"
                ></v-text-field>
            </v-flex>

            <v-flex>
                <v-range-slider
                v-model="kRange"
                :max="10.0"
                :min="0.0"
                :step="0.1"
                ></v-range-slider>
            </v-flex>

            <v-flex
                shrink
                style="width: 60px"
            >
                <v-text-field
                v-model="kRange[1]"
                class="mt-0"
                hide-details
                single-line
                type="number"
                ></v-text-field>
            </v-flex>
            
        </v-layout>

        </div>

        <div>
            <v-checkbox
            label="simulate b parameter"
            v-model="useB"
            ></v-checkbox>
            <v-layout row wrap>
                b parameter influences how much of a length normalization bears onto the final score (in BM25 score). Lucene's default value is 0.75; 
                when b=0.0, length normalization is effectively disabled.
                <v-flex
                    shrink
                    style="width: 60px"
                >
                    <v-text-field
                    v-model="bRange[0]"
                    class="mt-0"
                    hide-details
                    single-line
                    type="number"
                    ></v-text-field>
                </v-flex>

                <v-flex>
                    <v-range-slider
                    v-model="bRange"
                    :max="1.0"
                    :min="0.0"
                    :step="0.05"
                    ></v-range-slider>
                </v-flex>

                <v-flex
                    shrink
                    style="width: 60px"
                >
                    <v-text-field
                    v-model="bRange[1]"
                    class="mt-0"
                    hide-details
                    single-line
                    type="number"
                    ></v-text-field>
                </v-flex>

            </v-layout>

        </div>

        <div>
            <v-checkbox
            label="simulate different document lengths"
            v-model="useDocLen"
            ></v-checkbox>

            Here we can try to experiment with document lengths - lucene will typically use arithmetical mean; but we could try to see what happens if we
            assume median values. The beauty of BM25 algorithm is in the nice document length normalizations so it might be worthwhile to play with the 
            length (becuase it is important). 

            This requires judicious application from your side - obviously, you should have some knowledge of document lengths (in the given index)
            and it should not be used for multi-field queries (unless we can assume the fields are roughly the same size). <br/>

            Note: in the future, we should give you options to specify doc lenghts for various fields.
            
            <v-layout row wrap
                >
                <v-flex
                    shrink
                    style="width: 60px"
                >
                    <v-text-field
                    v-model="docLenRange[0]"
                    class="mt-0"
                    hide-details
                    single-line
                    type="number"
                    ></v-text-field>
                </v-flex>

                <v-flex>
                    <v-range-slider
                    v-model="docLenRange"
                    :max="100"
                    :min="0"
                    :step="1"
                    ></v-range-slider>
                </v-flex>

                <v-flex
                    shrink
                    style="width: 60px"
                >
                    <v-text-field
                    v-model="docLenRange[1]"
                    class="mt-0"
                    hide-details
                    single-line
                    type="number"
                    ></v-text-field>
                </v-flex>
            </v-layout>

        </div>

        <v-layout row wrap>
            <v-flex lg12 sm12>
            <v-checkbox
                label="Normalize Weight"
                v-model="useNormalization"
                ></v-checkbox>
                <p>
                    Imagine TF*IDF scoring formula. The IDF component depends on the corpus and partially (but significantly) influences magnitude
                    of the resulting product (a high IDF - for a rare term - will lead to high score). Now imagine also, that your query searches
                    two fields - one of the fields has very high boost, say: <b>title^1000,abstract^1</b> -- any match in the title will be thousand
                    times stronger than the abstract. 
                </p>
                <p>
                    Normalization is Lucene's attempt to arrive at scores that could be compared (between queries). It will still make the title 
                    to be thousand times stronger, but the weight will now be 1/1000 as opposed to 1000 (just an example). It is done by collecting 
                    all weights (for every term) in a query, summing them and then dividing every weight by this quantity. However, do not think
                    that the final score is normalized. The final result still depends on product of TF*IDF - and TF is not normalized (and cannot
                    be, it depends on a document lenght/frequencies etc). It is only the <b>weight</b> (which roughly corresponds to IDF) which is
                    normalized.
                </p>
                <p>
                    Important note: Lucene implementation of BM25 does not have weight normalization (so, we can't test it in real life yet). But
                   do not be discouraged - if we find it interesting, we'll implement that missing parts.
                </p>
          </v-flex>
          <v-flex lg12 sm12>
              <v-checkbox
                label="Apply boost"
                v-model="useBoost"
                ></v-checkbox>
            <v-select
            :items="fieldBoost"
            label="Select field"
            solo
            ></v-select>

            This is how we can simulate document boost. You can select a field whose value will be added to the final score: TF*IDF*<b>boost</b>.
          </v-flex>   
        </v-layout>

        <p>
            TODO: find a way to configure per field k/b/doclen
        </p>
      </v-form>


    </v-card-text>
    <v-card-actions class="pb-3">
      <v-spacer></v-spacer>
      <v-btn color="primary">Save</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  data: function() {
      return this.$store.state.experiment.parameters
  },
  methods: {
    closeDialog () {
      this.$parent.isActive = false;
    }
  }
};
</script>