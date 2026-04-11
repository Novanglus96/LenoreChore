/**
 * plugins/webfontloader.js
 *
 * Self-hosted via @fontsource/roboto — no external HTTP requests,
 * works offline and avoids mixed-content issues on HTTPS origins.
 */

export async function loadFonts() {
  await import("@fontsource/roboto/100.css");
  await import("@fontsource/roboto/300.css");
  await import("@fontsource/roboto/400.css");
  await import("@fontsource/roboto/500.css");
  await import("@fontsource/roboto/700.css");
  await import("@fontsource/roboto/900.css");
}
