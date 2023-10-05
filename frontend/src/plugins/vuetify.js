import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const myCustomLightTheme = {
    dark: false,
    colors: {
        primary: '#2196f3',
        secondary: '#00bcd4',
        accent: '#ffeb3b',
        error: '#FF3407',
        warning: '#ffc107',
        info: '#795548',
        success: '#4caf50',
        area1: '#1B5E20',
        area2: '#795548',
        area3: '#607D8B',
        area4: '#009688',
        area5: '#03A9F4',
        area6: '#9C27B0',
        user1: '#E91E63',
        user2: '#3F51B5',
        user3: '#009688',
        user4: '#CDDC39',
    },
}

export default createVuetify({
    theme: {
      defaultTheme: 'myCustomLightTheme',
      themes: {
        myCustomLightTheme,
      },
    },
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: {
          mdi,
        },
    },
    components,
    directives,
  })