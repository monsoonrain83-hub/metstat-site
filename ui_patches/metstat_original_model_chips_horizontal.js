/* MetStat r205 production-safe: move ONLY the existing fullscreen model chip group.
 * Fail closed on an unexpected DOM. No DOM cloning, timers, or interval polling.
 * The layout CSS is gated on a success marker and never hides the old menu first.
 */
(function () {
  'use strict';
  var MARKER = 'data-original-chips-horizontal';
  function relocate() {
    var fs = document.getElementById('nvFs');
    if (!fs) return false;
    var top = fs.querySelector('.fsRow.fsA');
    var chips = fs.querySelector('#fsMods');
    var oldMenu = fs.querySelector('.fsColR .fsModDd');
    if (!top || !chips || !oldMenu) return false;
    if (fs.querySelectorAll('#fsMods').length !== 1) return false;
    // Expected r157-r204 tree: the chips are either still in oldMenu or already in top.
    if (!oldMenu.contains(chips) && chips.parentElement !== top) return false;
    if (chips.parentElement !== top) top.appendChild(chips);
    if (chips.parentElement !== top) return false;
    fs.setAttribute(MARKER, '1');
    oldMenu.hidden = true;
    return true;
  }
  function start() {
    if (relocate()) return;
    if (!document.body || typeof MutationObserver === 'undefined') return;
    // The canonical nvfBuild appends #nvFs directly to document.body on first entry.
    // Avoid a subtree-wide observer on this large site, which would hurt map performance.
    var watch = new MutationObserver(function (records) {
      for (var i = 0; i < records.length; i++) {
        var nodes = records[i].addedNodes;
        for (var j = 0; j < nodes.length; j++) {
          if (nodes[j].id === 'nvFs' && relocate()) { watch.disconnect(); return; }
        }
      }
    });
    watch.observe(document.body, { childList: true });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else start();
  window.MetStatFixOriginalModelChips = relocate;
}());
