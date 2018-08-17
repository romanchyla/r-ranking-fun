<template>
  <v-card>
    
    <v-card-text>
      <v-form v-model="valid" ref="form" lazy-validation>
        <v-layout row wrap>
          <v-flex lg12 sm12>
            <v-text-field label="Query" name="query" v-model="query">
            </v-text-field>
          </v-flex>
          <v-flex lg12 sm12>
            <v-text-field label="Additional Parameters (url format)" name="params" v-model="params">
            </v-text-field>
          </v-flex>
          <v-flex lg12 sm12>
            <v-text-field textarea label="Description">

            </v-text-field>
          </v-flex>                              
          <v-spacer></v-spacer>
        </v-layout>


        <v-layout row wrap>

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


        <v-layout row wrap
            >
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
                v-model="bRange[1]"
                class="mt-0"
                hide-details
                single-line
                type="number"
                ></v-text-field>
            </v-flex>

        </v-layout>

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
                :max="1000"
                :min="0"
                :step="10"
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

        <v-layout row wrap>
            <v-flex lg12 sm12>
            <v-switch
                label="Normalize Weight"
                v-model="normalizeWeight"
                ></v-switch>
          </v-flex>
          <v-flex lg12 sm12>
            <v-select
            :items="fieldBoost"
            label="Apply boost using field"
            ></v-select>
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
  data: () => ({
    query: 'title:(foo bar)',
    params: 'sort=score+desc&fl=classic_factor,title,bibcode',
    normalizeWeight: true,
    fieldBoost: ['none', 'classic_factor', 'cite_read_bost'],
    kRange: [0.5, 1.5],
    bRange: [0.75, 1.2],
    docLenRange: [0, 50]
  }),
  methods: {
    closeDialog () {
      this.$parent.isActive = false;
    }
  }
};
</script>