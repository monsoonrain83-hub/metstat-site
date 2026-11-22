/* MetStat Tabler UI vNext — OPT-IN legacy fullscreen bridge, no automatic startup.
 * Move exactly the original #fsMods DOM element into the verified map canvas.
 * NEVER duplicate model buttons or replace the map, NWP core, auth or routes.
 * Precondition for production: current live DOM has been hashed and reviewed.
 */
(function () {
  'use strict';
  const states = new WeakMap();
  const validStatus = new Set(['ready', 'missing', 'partial', 'updating']);
  function mount() {
    const fs = document.getElementById('nvFs');
    if (!fs || fs.dataset.msVnextApproved !== '1') return false;
    if (fs.querySelectorAll('#fsMods').length !== 1) return false;
    // The map canvas marker must be added only after verifying its identity in
    // the LIVE site. Do not guess .fsMap/.map selectors or mount to the body.
    const canvas = fs.querySelector('[data-metstat-map-canvas="1"]');
    const chips = fs.querySelector('#fsMods');
    if (!canvas || !chips || !canvas.contains(chips) && !fs.contains(chips)) return false;
    if (states.has(fs)) return states.get(fs).chips === chips;
    if (!canvas.isConnected || canvas === chips || chips.contains(canvas)) return false;
    const oldParent = chips.parentElement;
    const oldNext = chips.nextSibling;
    if (!oldParent || oldParent === canvas) return false;
    const wasHorizontal = fs.getAttribute('data-original-chips-horizontal');
    const dock = document.createElement('div');
    dock.className = 'ms-vnext-model-dock';
    dock.setAttribute('role', 'group');
    dock.setAttribute('aria-label', 'مدل‌های هواشناسی');
    try {
      canvas.appendChild(dock);
      dock.appendChild(chips);  // MOVE original event-bound node; NEVER clone.
      fs.removeAttribute('data-original-chips-horizontal'); // retire r205 CSS
      fs.dataset.msVnextMounted = '1'; // activate only AFTER successful move
      states.set(fs, {chips, dock, oldParent, oldNext, wasHorizontal});
      return true;
    } catch (error) {
      if (oldNext && oldNext.parentNode === oldParent) oldParent.insertBefore(chips, oldNext);
      else oldParent.appendChild(chips);
      dock.remove();
      return false;
    }
  }
  function unmount() {
    const fs = document.getElementById('nvFs');
    const record = fs && states.get(fs);
    if (!record) return false;
    const {chips, dock, oldParent, oldNext, wasHorizontal} = record;
    if (oldParent.isConnected) {
      if (oldNext && oldNext.parentNode === oldParent) oldParent.insertBefore(chips, oldNext);
      else oldParent.appendChild(chips);
    } else {
      return false; // Never drop live buttons into a detached subtree.
    }
    dock.remove();
    if (wasHorizontal === null) fs.removeAttribute('data-original-chips-horizontal');
    else fs.setAttribute('data-original-chips-horizontal', wasHorizontal);
    delete fs.dataset.msVnextMounted;
    states.delete(fs);
    return true;
  }
  function applyVerifiedStatus(modelId, status) {
    if (!validStatus.has(status)) return false;
    const fs=document.getElementById('nvFs');
    if (!fs || !states.has(fs)) return false;
    // Only update a known button whose logical-model identifier is verified by
    // the existing frontend. No model IDs/availability are manufactured here.
    const found = Array.from(fs.querySelectorAll('#fsMods [data-logical-model]'))
      .filter(node => node.dataset.logicalModel === modelId);
    if (found.length !== 1) return false;
    found[0].dataset.msStatus = status;
    return true;
  }
  Object.defineProperty(window, 'MetStatTablerVnextBridge', {
    value: Object.freeze({mount, unmount, applyVerifiedStatus}),
    configurable: false,
    writable: false
  });
}());
