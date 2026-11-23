/* MetStat R5 Stage19: enhance, do not replace, the canonical R9 NWP controls.
 * No API calls; no new model/parameter state; idempotent after DOM rebuild.
 */
(() => {
  'use strict';
  const version = 'r5-stage19-controls-1';
  const doc = document;
  const stat = window.MetStatR5Stage19 = {version, mounts: 0, palette: 'waiting', layers: 'waiting'};
  const NS = 'http://www.w3.org/2000/svg';
  const svg = (tag, attrs) => {
    const n = doc.createElementNS(NS, tag);
    Object.entries(attrs || {}).forEach(([k, v]) => n.setAttribute(k, String(v)));
    return n;
  };
  function isEnglish() {
    try {if (typeof LANG !== 'undefined') return LANG === 'en';} catch (_) {}
    return doc.documentElement.lang.toLowerCase().startsWith('en');
  }
  function installPalette(card) {
    const legend = card.querySelector('#nvLg');
    const palette = card.querySelector('#msMapPalette, .nvCbDd');
    if (!legend || !palette) {stat.palette = 'waiting_for_map'; return;}
    // R5's own picker, if present, owns this interaction. Do not stack controls.
    if (card.querySelector('#paletteBtn, [data-r5-palette-native]')) {
      stat.palette = 'native_picker_present'; return;
    }
    legend.dataset.msR5Palette = version;
    const desc = isEnglish() ? 'Choose map color scale' : 'انتخاب رنگ‌بندی نقشه';
    legend.setAttribute('role', 'button');
    legend.setAttribute('tabindex', '0');
    legend.setAttribute('aria-label', desc);
    legend.setAttribute('aria-haspopup', 'true');
    legend.setAttribute('aria-expanded', String(palette.open));
    const open = () => {
      if (!legend.isConnected || !palette.isConnected) return;
      palette.open = !palette.open;
      legend.setAttribute('aria-expanded', String(palette.open));
      if (palette.open) palette.querySelector('summary')?.focus({preventScroll: true});
    };
    if (legend.dataset.msR5PaletteBound !== version) {
      legend.addEventListener('click', open);
      legend.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {e.preventDefault(); open();}
      });
      legend.dataset.msR5PaletteBound = version;
    }
    if (palette.dataset.msR5PaletteBound !== version) {
      palette.addEventListener('toggle', () => {
        if (legend.isConnected) legend.setAttribute('aria-expanded', String(palette.open));
      });
      palette.dataset.msR5PaletteBound = version;
    }
    palette.dataset.msR5PaletteMenu = version;
    stat.palette = 'connected_to_original';
  }
  function installLayerIcon(card) {
    const summary = card.querySelector('.nvLayDd > summary');
    if (!summary) {stat.layers = 'waiting_for_map'; return;}
    if (!summary.querySelector('svg, [data-ms-r5-layers-icon]')) {
      const s = svg('svg', {viewBox: '0 0 24 24', fill:'none', stroke:'currentColor',
        'stroke-width':'1.9', 'stroke-linecap':'round', 'stroke-linejoin':'round',
        'aria-hidden':'true', 'data-ms-r5-layers-icon':version});
      for (const d of ['M12 3 2 9l10 6 10-6-10-6Z','m2 13 10 6 10-6','m2 17 10 6 10-6']) {
        s.appendChild(svg('path', {d}));
      }
      summary.insertBefore(s, summary.firstChild);
    }
    summary.setAttribute('aria-label', isEnglish() ? 'Map layers and boundaries' : 'لایه‌ها و مرزهای نقشه');
    stat.layers = 'connected_to_original';
  }
  function localizeBorders(card) {
    const select = card.querySelector('#nvBm');
    if (!select) return;
    const dict = isEnglish() ? {
      prov:'Country and province', ctry:'Country only', cnty:'Country, province, county', none:'No boundaries'
    } : {
      prov:'مرز کشور و استان', ctry:'فقط مرز کشور', cnty:'کشور، استان و شهرستان', none:'بدون مرز'
    };
    for (const opt of select.options) {
      const target = dict[opt.value];
      if (target && opt.textContent !== target) opt.textContent = target;
    }
    select.setAttribute('aria-label', isEnglish() ? 'Boundary type' : 'نوع مرز');
  }
  function mount() {
    const card = doc.querySelector('.nvCard');
    if (!card) return;
    installPalette(card); installLayerIcon(card); localizeBorders(card);
    stat.mounts++;
  }
  let pending = false;
  const schedule = () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => {pending = false; mount();});
  };
  function start() {
    mount();
    const root = doc.getElementById('onApp') || doc.body;
    // Watch only replaced children, not attributes: avoids observer loops when
    // this adapter annotates the existing canvas and summary.
    new MutationObserver(mutations => {
      if (mutations.some(m => m.addedNodes.length || m.removedNodes.length)) schedule();
    }).observe(root, {childList:true, subtree:true});
    doc.addEventListener('change', e => {
      if (e.target?.id === 'lang' || e.target?.matches?.('[data-lang]')) schedule();
    });
    doc.addEventListener('click', e => {
      if (e.target?.closest?.('[data-lang],#langBtn,.langBtn')) schedule();
    });
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', start, {once:true});
  else start();
})();