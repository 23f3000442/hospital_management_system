import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Custom styles
import './assets/main.css'

const app = createApp(App)
app.use(router)
app.mount('#app')
