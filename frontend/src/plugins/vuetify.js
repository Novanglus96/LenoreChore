import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { aliases, mdi } from "vuetify/iconsets/mdi";
import "@mdi/font/css/materialdesignicons.css";

const myCustomLightTheme = {
  dark: false,
  colors: {
    primary: "#2196f3",
    secondary: "#1782aa",
    accent: "#ffeb3b",
    error: "#FF3407",
    warning: "#ffc107",
    info: "#795548",
    success: "#4caf50",
    area1: "#BBDEFB",
    area2: "#90CAF9",
    area3: "#64B5F6",
    area4: "#42A5F5",
    area5: "#1E88E5",
    area6: "#1976D2",
    user1: "#E91E63",
    user2: "#3F51B5",
    user3: "#009688",
    user4: "#CDDC39",
  },
};

const myCustomDarkTheme = {
  dark: true,
  colors: {
    primary: "#90CAF9",
    secondary: "#4FC3F7",
    accent: "#ffeb3b",
    error: "#FF5252",
    warning: "#FFB300",
    info: "#BCAAA4",
    success: "#69F0AE",
    area1: "#1A237E",
    area2: "#283593",
    area3: "#303F9F",
    area4: "#3949AB",
    area5: "#3F51B5",
    area6: "#5C6BC0",
    user1: "#E91E63",
    user2: "#3F51B5",
    user3: "#009688",
    user4: "#CDDC39",
  },
};

export default createVuetify({
  theme: {
    defaultTheme: "myCustomLightTheme",
    themes: {
      myCustomLightTheme,
      myCustomDarkTheme,
    },
  },
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: {
      mdi,
    },
  },
  components,
  directives,
});
