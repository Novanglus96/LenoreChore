import "vuetify/styles";
import "@/styles/tokens.css";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { aliases, mdi } from "vuetify/iconsets/mdi";
import "@mdi/font/css/materialdesignicons.css";

/* ===========================================================================
   Palette
   ===========================================================================
   Loosely Material, deliberately not stock Material Blue.

   The hue family is drawn from the app bar's existing pale cyan (#c8f0ff) and
   deepened into something with more conviction. Neutrals are tinted toward
   that hue rather than being pure grey — a neutral with a slight cast reads as
   chosen, where a pure mid-grey reads as a default nobody thought about.

   ── The colour model ──
   Area and member colours are user data and can be anything, so they are used
   as ACCENTS — a stripe, an icon tint, a chip — never as a surface that text
   sits on. Text always sits on a themed surface whose contrast is known. This
   sidesteps the contrast problem rather than managing it, and needs no
   migration of anyone's existing colour.

   ── Dirtiness ──
   clean/soiled/filthy replace the generic success/warning/error for the
   dirtiness bands. They still map to green/amber/red because that reading is
   near-universal, but they are named for what they mean so a future change of
   hue does not require renaming call sites. Colour is never the only signal:
   the bar also carries a label, and its stripe density changes with severity.
   =========================================================================== */

const myCustomLightTheme = {
  dark: false,
  colors: {
    background: "#F4F8FA",
    surface: "#FFFFFF",
    "surface-variant": "#E4EDF0",
    "on-surface-variant": "#3F4B4F",

    primary: "#00637A",
    "on-primary": "#FFFFFF",
    "primary-container": "#B4E9FB",
    "on-primary-container": "#001F27",

    secondary: "#4B6069",
    "on-secondary": "#FFFFFF",
    "secondary-container": "#CEE5EF",
    "on-secondary-container": "#061E25",

    // The warm pop. Used sparingly — celebration, and the single most
    // important call to action on a screen. Its scarcity is what gives it
    // weight; spreading it around would flatten the hierarchy.
    accent: "#B5551B",
    "on-accent": "#FFFFFF",
    "accent-container": "#FFDBC8",

    // Dirtiness bands.
    clean: "#2C6E4F",
    soiled: "#8A5A00",
    filthy: "#A03328",

    success: "#2C6E4F",
    warning: "#8A5A00",
    error: "#A03328",
    info: "#00637A",

    outline: "#6F797D",
    "outline-variant": "#C3CDD1",

    // ⚠️ These names are PERSISTED DATA, not just palette entries.
    // AreaGroup.group_color stores the literal string "area1".."area6" and
    // Vuetify resolves it as a theme colour at render time, so renaming or
    // removing a key silently breaks every existing area group. (User colours
    // are different again: CustomUser.user_color stores hex.)
    //
    // Re-tuned for the accent role — they are stripes, icon tints and chips
    // now rather than card fills, so they need enough saturation to read at
    // 4px wide, where the old pale blues were nearly invisible.
    area1: "#0277BD",
    area2: "#00838F",
    area3: "#2E7D32",
    area4: "#6A4FB6",
    area5: "#C2185B",
    area6: "#B26500",

    user1: "#C2185B",
    user2: "#3949AB",
    user3: "#00796B",
    user4: "#9E9D24",
  },
  variables: {
    "border-color": "#C3CDD1",
    "border-opacity": 1,
    "high-emphasis-opacity": 0.92,
    "medium-emphasis-opacity": 0.68,
  },
};

const myCustomDarkTheme = {
  dark: true,
  colors: {
    background: "#0D1417",
    surface: "#141D21",
    "surface-variant": "#1D272C",
    "on-surface-variant": "#BFCACE",

    primary: "#65D4EE",
    "on-primary": "#003543",
    "primary-container": "#004E5F",
    "on-primary-container": "#B4E9FB",

    secondary: "#B2CBD5",
    "on-secondary": "#1D343B",
    "secondary-container": "#334A52",
    "on-secondary-container": "#CEE5EF",

    accent: "#FFB68F",
    "on-accent": "#552100",
    "accent-container": "#8B3D06",

    // Lightened for a dark ground. The light-theme values fail contrast here,
    // which is the usual way a "dark mode" ends up unreadable: the palette gets
    // inverted but the semantic colours are carried over unchanged.
    clean: "#7EDCA8",
    soiled: "#F0BE55",
    filthy: "#FFB4AA",

    success: "#7EDCA8",
    warning: "#F0BE55",
    error: "#FFB4AA",
    info: "#65D4EE",

    outline: "#899397",
    "outline-variant": "#3F494D",

    // Same persisted-name constraint as the light theme — see the note there.
    // Lightened so they hold up as accents against a dark ground.
    area1: "#7FCFFF",
    area2: "#5BD8E4",
    area3: "#8DD98F",
    area4: "#C1B0FF",
    area5: "#FF9EC4",
    area6: "#FFC46B",

    user1: "#F48FB1",
    user2: "#9FA8DA",
    user3: "#80CBC4",
    user4: "#E6EE9C",
  },
  variables: {
    "border-color": "#3F494D",
    "border-opacity": 1,
    "high-emphasis-opacity": 0.94,
    "medium-emphasis-opacity": 0.72,
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
  // Global component defaults, so the shape language is set once here rather
  // than repeated as props on every instance — and so it stays consistent when
  // new screens get built.
  defaults: {
    VCard: { rounded: "lg" },
    VBtn: { rounded: "pill", variant: "text" },
    VTextField: { variant: "outlined", density: "comfortable" },
    VSelect: { variant: "outlined", density: "comfortable" },
    VTextarea: { variant: "outlined", density: "comfortable" },
    VChip: { rounded: "pill" },
    VAlert: { rounded: "lg", variant: "tonal" },
    VDialog: { transition: "dialog-bottom-transition" },
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
