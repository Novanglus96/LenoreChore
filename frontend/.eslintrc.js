module.exports = {
  root: true,
  env: {
    node: true, // Enable Node.js global variables and scope
    browser: true, // Enable browser global variables
    es2021: true, // Enable modern JavaScript syntax
    // Declares defineProps/defineEmits/defineExpose/withDefaults as globals.
    // They are compiler macros: importing them from "vue" makes the SFC
    // compiler warn on every build, but without this eslint reports them as
    // no-undef. Both are only satisfiable together.
    "vue/setup-compiler-macros": true,
  },
  extends: [
    "plugin:vue/vue3-essential", // Essential rules for Vue 3
    "eslint:recommended", // Recommended core rules
    "prettier", // Disables conflicting rules with Prettier
  ],
  // The accessibility rules below are listed individually rather than pulled in
  // via `plugin:vuejs-accessibility/recommended`. On eslint 7 that shorthand
  // resolves through the package's exports map to the FLAT config, which needs
  // eslint 9 machinery and dies with a module-resolution error. Enumerating
  // them also keeps the rule set and its severity visible here instead of
  // hidden behind a preset. Revisit when the eslint 7 -> 10 upgrade lands.
  plugins: ["vuejs-accessibility"],
  parserOptions: {
    ecmaVersion: 2021, // Support for ES2021 features
    sourceType: "module", // Use ECMAScript modules
  },
  rules: {
    // ── Accessibility ───────────────────────────────────────────────────────
    // WARN, not error, and deliberately so. vite-plugin-eslint fails the dev
    // transform on an eslint ERROR -- that is what put "Cannot access
    // 'useUserStore' before initialization" on screen instead of the app. The
    // UI currently has no aria attributes at all, so promoting these to error
    // would refuse to serve every component and block the very revamp that is
    // meant to fix them. Promote to error per-rule as each is driven to zero.
    // These rules match on NATIVE element names, so unmapped they see almost
    // nothing here -- the templates are Vuetify components end to end. Measured
    // on this repo: 0 findings before the mappings below, 22 after.
    //
    // The plugin has no "button must have an accessible name" rule, but
    // anchor-has-content mapped onto VBtn does the same job: it requires
    // screen-reader-reachable content. That is what surfaces the icon-only
    // action buttons, which was the largest finding in the accessibility audit.
    // The message it prints says "Anchors must have content" -- read that as
    // "this control has no accessible name".
    "vuejs-accessibility/alt-text": ["warn", { img: ["VImg"] }],
    "vuejs-accessibility/anchor-has-content": ["warn", { components: ["VBtn"] }],
    "vuejs-accessibility/form-control-has-label": [
      "warn",
      {
        labelComponents: ["VLabel"],
        controlComponents: [
          "VTextField",
          "VTextarea",
          "VSelect",
          "VAutocomplete",
          "VCombobox",
          "VCheckbox",
          "VRadio",
          "VSwitch",
          "VSlider",
          "VFileInput",
        ],
      },
    ],
    "vuejs-accessibility/aria-props": "warn",
    "vuejs-accessibility/aria-role": "warn",
    "vuejs-accessibility/aria-unsupported-elements": "warn",
    "vuejs-accessibility/click-events-have-key-events": "warn",
    "vuejs-accessibility/heading-has-content": "warn",
    "vuejs-accessibility/iframe-has-title": "warn",
    "vuejs-accessibility/interactive-supports-focus": "warn",
    "vuejs-accessibility/label-has-for": "warn",
    "vuejs-accessibility/media-has-caption": "warn",
    "vuejs-accessibility/mouse-events-have-key-events": "warn",
    "vuejs-accessibility/no-access-key": "warn",
    "vuejs-accessibility/no-autofocus": "warn",
    "vuejs-accessibility/no-distracting-elements": "warn",
    "vuejs-accessibility/no-redundant-roles": "warn",
    "vuejs-accessibility/no-static-element-interactions": "warn",
    "vuejs-accessibility/role-has-required-aria-props": "warn",
    "vuejs-accessibility/tabindex-no-positive": "warn",

    // ── Existing ────────────────────────────────────────────────────────────
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off", // Warn on console in production
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off", // Warn on debugger in production
    "vue/valid-v-slot": [
      "error", // Validate v-slot syntax
      {
        allowModifiers: true, // Allow modifiers like `slot:header.sortable`
      },
    ],
  },
};
