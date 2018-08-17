<template>
  <v-container fluid>
    <v-slide-y-transition mode="out-in">
      <v-layout column align-left>
        <h1>ADS Scoring <i>Simulateur</i></h1>
    
    <p>Hi {{name}}! Pleasure to meet you.</p>

    <p>In here you can help improve quality of the search results at ADS. We will do so by running (few hundred thousands of) experiments
      and try to find best set of parameters for the relevance score used by our search engine.</p>

    
    <p>In order to run experiments, we'd like to ask you to do following:</p>

    <ol>
      <li>make (arbitrary) query</li>
      <li>review returned results and select papers that are most relevant <b>to you</b></li>
      <li>(optionally) re-order the selected papers, to have the most relevant papers on top</li>
    </ol>

    <p>You will be able to see the results in real time. As we gather more data, we'll be able to converge and update our search engine.</p>

      </v-layout>
    </v-slide-y-transition>
  </v-container>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
