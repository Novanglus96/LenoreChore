// Shared setup for component tests.
//
// happy-dom implements enough of the DOM for most work, but Vuetify reaches for
// a few browser APIs it does not provide. Each of these throws during mount
// rather than degrading, so they have to exist before any component renders.

// Several Vuetify components construct one on mount (VProgressLinear, VOverlay).
if (!global.ResizeObserver) {
  global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

// VOverlay's location strategies subscribe to visualViewport, which happy-dom
// does not define. Anything using VDialog or VMenu hits this.
if (!global.visualViewport) {
  global.visualViewport = {
    width: 1024,
    height: 768,
    scale: 1,
    offsetLeft: 0,
    offsetTop: 0,
    addEventListener() {},
    removeEventListener() {},
  };
  Object.defineProperty(window, "visualViewport", {
    value: global.visualViewport,
    writable: true,
  });
}

// Vuetify's display composable reads this during theme/breakpoint setup.
if (!window.matchMedia) {
  window.matchMedia = query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener() {},
    removeListener() {},
    addEventListener() {},
    removeEventListener() {},
    dispatchEvent: () => false,
  });
}
