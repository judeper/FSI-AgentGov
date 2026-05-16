/**
 * _mermaid.mjs — shared Mermaid render-detection helper
 *
 * Material 9.7.6's mermaid integration renders into a *closed* shadow DOM
 * (`attachShadow({ mode: "closed" })`). That makes `.mermaid svg` return 0
 * even when rendering succeeds, because Playwright's locators cannot
 * traverse into closed shadow roots.
 *
 * To detect a successful render we use two layout-side signals:
 *   1. The `<div class="mermaid">` placeholder exists in the live DOM
 *      (Material consumed the original `<pre class="mermaid">`), AND
 *   2. The placeholder has non-zero bounding-box height — proving the
 *      shadow-rendered SVG is actually occupying layout space.
 *
 * For non-Material setups (or if Material ever switches to open shadow
 * DOM) we also count direct `svg` children of the placeholder as a
 * successful render. Both paths increment the same counter.
 *
 * Threshold of 10px is conservative — mermaid v11 always emits SVGs at
 * least ~30px tall for a one-node flowchart; an empty placeholder shows
 * 0px. 10px is well below the smallest legitimate render.
 */

/**
 * Count successfully-rendered Mermaid diagrams on the current page.
 *
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<number>}
 */
export async function countRenderedMermaid(page) {
  return await page.evaluate(() => {
    let count = 0;
    for (const el of document.querySelectorAll(".mermaid")) {
      const rect = el.getBoundingClientRect();
      const hasShadowSvg = rect.height > 10;
      const hasDirectSvg = el.querySelector("svg") !== null;
      if (hasShadowSvg || hasDirectSvg) count += 1;
    }
    return count;
  });
}
