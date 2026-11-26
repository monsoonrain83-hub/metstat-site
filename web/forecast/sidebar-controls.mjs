/** Own the mirrored forecast select options and R5 period/model rows.
 * Rebuild only when the actual structural view changes. No polling or observers.
 */
export function createSidebarControls() {
  const rendered = new WeakMap();
  function replace(host, view, build, valid = () => true) {
    const signature = JSON.stringify(view), previous = rendered.get(host);
    if (previous && previous.signature === signature && previous.html === host.innerHTML && valid()) return false;
    const fragment = host.ownerDocument.createDocumentFragment();
    build(fragment, host.ownerDocument);
    host.replaceChildren(fragment);
    rendered.set(host, {signature, html: host.innerHTML});
    return true;
  }
  return Object.freeze({
    options(host, options, selected) {
      const view = options.map(o => [String(o.value), String(o.label), Boolean(o.disabled)]);
      replace(host, view, (fragment, doc) => {
        for (const [value, label, disabled] of view) {
          const option = doc.createElement('option');
          option.value = value; option.textContent = label; option.disabled = disabled;
          fragment.append(option);
        }
      });
      if (host.value !== selected) host.value = selected;
    },
    periods(host, options, selected, labels) {
      const view = options.map(o => [o.value, labels[o.value] || o.textContent, o.disabled, o.value === selected]);
      replace(host, view, (fragment, doc) => {
        for (const [value, label, disabled, pressed] of view) {
          const b = doc.createElement('button'); b.type = 'button'; b.className = 'msR5-period';
          b.dataset.msr5Period = value; b.setAttribute('aria-pressed', String(pressed)); b.disabled = disabled; b.textContent = label;
          fragment.append(b);
        }
      });
    },
    models(host, options, selected) {
      const view = options.map(o => [o.value, o.textContent.replace(/\s*[（(]\s*اروپا\s*[）)]/g, ''), o.disabled, o.value === selected]);
      const valid = () => {
        const inputs = host.querySelectorAll('input[data-msr5-model]');
        return inputs.length === view.length && view.every(([value, , , checked], i) => inputs[i].value === value && inputs[i].checked === checked);
      };
      replace(host, view, (fragment, doc) => {
        for (const [value, labelText, disabled, checked] of view) {
          const label = doc.createElement('label'), input = doc.createElement('input'), txt = doc.createElement('span');
          label.className = 'msR5-model-row'; input.type = 'radio'; input.name = 'msR5ForecastModel'; input.value = value;
          input.dataset.msr5Model = value; input.checked = checked; input.disabled = disabled; txt.textContent = labelText;
          label.append(input, txt); fragment.append(label);
        }
      }, valid);
    }
  });
}
