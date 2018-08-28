<template>
  <v-app>
    <v-navigation-drawer
      app
      persistent
      :clipped="clipped"
      :mini-variant="miniVariant"
      v-model="drawer"
      enable-resize-watcher
      fixed
    >
      <v-list class="pt-0" dense>
        <v-list-tile
          v-for="(item, i) in items"
          :key="i"
          :to="item.path == '#' ? '' : item.path + ($route.params.id ? $route.params.id : '')"
        >
          <v-list-tile-action>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>{{ item.title }}</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>

    

    
    <v-toolbar
      app
      :clipped-left="clipped"
    >
      <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
      <v-btn icon @click.stop="miniVariant = !miniVariant">
        <v-icon v-html="miniVariant ? 'chevron_right' : 'chevron_left'"></v-icon>
      </v-btn>
      <v-btn icon @click.stop="clipped = !clipped">
        <v-icon>web</v-icon>
      </v-btn>
    </v-toolbar>



    <v-content>
      <router-view></router-view>
    </v-content>



    <v-footer :fixed="fixed" app>
      <span>&copy; 2017</span>
    </v-footer>
  </v-app>
</template>

<script>


export default {
  name: 'App',
  data () {
    return {
      clipped: false,
      drawer: true,
      fixed: false,
      items: [{
        icon: 'bubble_chart',
        title: 'Scoring Simulateur',
        path: '/'
      },
        { title: 'Dashboard', icon: 'dashboard', path: '/dashboard' },
        { title: 'Query ADS', icon: 'description', path: '/experiment/overview/' },
        { title: 'Returned Documents', icon: 'view_headline', path: '/experiment/articles/' },
        { title: 'Selected Relevant Papers', icon: 'assessment', path: '/experiment/selection/' },
        { title: 'Experiment Results', icon: 'build', path: '/experiment/results/' },
      ],
      miniVariant: false,
      right: true,
      rightDrawer: false,
      title: ''
    }
  },
  methods: {
    handleMenuClick: function() {
      console.log('clicked!');
    }
  }
}
</script>
