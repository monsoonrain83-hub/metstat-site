/* Additive MetStat navigation entry: isolated from meteorological map workflows. */
(() => {
  'use strict';
  if (!/^\\/(?:index\\.html)?$/.test(location.pathname)) return;
  const path = 'toolbox.html';
  function insertToolboxEntry() {
    if (document.getElementById('metstat-weather-toolbox-link')) return true;
    const target = document.querySelector('header nav, nav[aria-label], #mainNav, #topNav, .top-nav, header');
    if (!target) return false;
    const link = document.createElement('a');
    link.id = 'metstat-weather-toolbox-link';
    link.href = path;
    link.textContent = 'جعبه ابزار هواشناسی';
    link.setAttribute('aria-label', 'جعبه ابزار هواشناسی: آوا استودیو');
    link.style.cssText = 'display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:7px 13px;margin:6px;border-radius:10px;border:1px solid currentColor;text-decoration:none;font:600 14px Tahoma,system-ui,sans-serif;white-space:nowrap';
    target.append(link);
    return true;
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', insertToolboxEntry, {once: true});
  } else {
    insertToolboxEntry();
  }
})();
