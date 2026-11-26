/** Forecast frame lookup, shared by Middle East and European map views.
 * The manifest loader publishes replacement arrays. Call invalidate() if a
 * future caller changes the model/region/parameter of rows in-place.
 * Returned arrays are independent; the original frame objects/order are kept.
 */
export function createForecastFrameIndex(getManifest, isPrevious) {
  let owner, indexes = new WeakMap();
  const empty = [];
  function invalidate() { indexes = new WeakMap(); }
  function source(manifest, model, previous) {
    return (previous && isPrevious(model) ? manifest.items_prev : manifest.items) || empty;
  }
  function getIndex(manifest, rows) {
    if (owner !== manifest) { invalidate(); owner = manifest; }
    let index = indexes.get(rows);
    if (index && index.length === rows.length) return index;
    index = {length: rows.length, middleEast: [], middleEastByModel: new Map(), europeByModel: new Map()};
    for (const row of rows) {
      if (row.r === 'me' && !/L$/.test(row.p)) {
        index.middleEast.push(row);
        let list = index.middleEastByModel.get(row.m);
        if (!list) { list = []; index.middleEastByModel.set(row.m, list); }
        list.push(row);
      } else if (row.r === 'eu' && !/[LHVW]$/.test(row.p)) {
        let parameters = index.europeByModel.get(row.m);
        if (!parameters) { parameters = new Map(); index.europeByModel.set(row.m, parameters); }
        let list = parameters.get(row.p);
        if (!list) { list = []; parameters.set(row.p, list); }
        list.push(row);
      }
    }
    indexes.set(rows, index);
    return index;
  }
  return Object.freeze({
    middleEast(model) {
      const manifest = getManifest();
      if (!manifest) return [];
      const index = getIndex(manifest, source(manifest, model, Boolean(model)));
      return (model ? index.middleEastByModel.get(model) || empty : index.middleEast).slice();
    },
    europe(model, parameter) {
      const manifest = getManifest();
      if (!manifest) return [];
      const index = getIndex(manifest, source(manifest, model, true));
      return (index.europeByModel.get(model)?.get(parameter) || empty).slice();
    },
    invalidate
  });
}
