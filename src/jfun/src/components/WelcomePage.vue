<template>
  <v-container>
  <div class="hello">
    <h1>ADS Scoring <i>Simulateur</i></h1>
    
    <p>Hi {{name}}! Pleasure to meet you.</p>

    <p>In here you can help improve quality of the search results at ADS. We will do so by running (few hundred thousands of) experiments
      and try to find best set of parameters for the relevance score used by our search engine.</p>

    
    <p>In order to run experiments, we'd like to ask of you the following:</p>

    <ol>
      <li>make (arbitrary) new request</li>
      <li>review returned results and select papers that are most relevant <b>to you</b></li>
      <li>(optionally) re-order the selected papers, to have the most relevant papers on top</li>
    </ol>

    <p>We will run our simulations and try to derive the best set of parameters that produce the best search results. It is no black
      magic and we do not promise miracles, but as we gather more data, we'll be able to do more and more. Oh, btw - we'll use the 
      derived parameters to reorder your existing search results - so you will be able to see them (almost real time).</p>

  </div>
  </v-container>
</template>

<script>
export default {
  name: 'WelcomePage',
  props: {
    name: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1 {
  margin: 40px 0 0;
  text-align: center;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
