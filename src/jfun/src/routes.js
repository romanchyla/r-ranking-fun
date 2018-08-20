import HelloWorld from './components/HelloWorld.vue'
import WelcomePage from './components/WelcomePage.vue'
import NotFound from './components/NotFound.vue'
import Dashboard from './components/Dashboard.vue'
import ExperimentOverview from './components/ExperimentOverview.vue'
import ListOfArticles from './components/ListOfArticles.vue'

const routes = [
  {
    path: '/',
    component: HelloWorld,
  },
  {
    path: '/dashboard',
    component: Dashboard,
  },

    {
    path: '/experiment/overview',
    name: 'overview',
    component: ExperimentOverview
    },
    {
    path: '/experiment/articles',
    name: 'articles',
    component: ListOfArticles
    },
    {
    path: '/experiment/selection',
    name: 'selection',
    component: ListOfArticles
    },
    {
    path: 'results',
    name: 'results',
    component: WelcomePage
    },
    
  { path: '*', component: NotFound }
]

/**
 * Asynchronously load view (Webpack Lazy loading compatible)
 * The specified component must be inside the Views folder
 * @param  {string} name  the filename (basename) of the view to load.
function view(name) {
   var res= require('../components/Dashboard/Views/' + name + '.vue');
   return res;
};**/

export default routes
