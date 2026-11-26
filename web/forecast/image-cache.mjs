/** Byte- and count-bounded LRU for decoded forecast images.
 * The byte estimate is width*height*4, not total browser/GPU memory.
 * Active loads are separate from retained images and deduplicated by URL.
 * Eviction drops cache references only: images already used by a renderer or
 * export remain valid. No cancellation or forced image src mutation.
 */
export function createForecastImageCache(load, {maxEntries = 60, maxBytes = 64 * 1024 * 1024} = {}) {
  if (typeof load !== 'function' || !Number.isSafeInteger(maxEntries) || maxEntries < 1 || !Number.isSafeInteger(maxBytes) || maxBytes < 1) throw new TypeError('invalid image cache configuration');
  const retained = new Map(), pending = new Map();
  let bytes = 0, generation = 0;
  function drop(key) {
    const entry = retained.get(key);
    if (!entry) return;
    retained.delete(key); bytes -= entry.bytes;
  }
  function get(url) {
    if (retained.has(url)) {
      const entry = retained.get(url);
      retained.delete(url); retained.set(url, entry);
      return entry.promise;
    }
    if (pending.has(url)) return pending.get(url);
    const epoch = generation;
    const promise = Promise.resolve().then(() => load(url)).then(img => {
      if (!img || epoch !== generation) return img || null;
      const w = img.naturalWidth, h = img.naturalHeight, weight = w * h * 4;
      if (!Number.isSafeInteger(w) || !Number.isSafeInteger(h) || w <= 0 || h <= 0 || !Number.isSafeInteger(weight) || weight > maxBytes) return img;
      // Make space before insertion. The live entry may still be used by
      // nvResolve, overlays or GIF export; never mutate the image itself.
      while (retained.size >= maxEntries || bytes + weight > maxBytes) drop(retained.keys().next().value);
      retained.set(url, {promise, bytes: weight}); bytes += weight;
      return img;
    }, () => null).finally(() => {
      if (pending.get(url) === promise) pending.delete(url);
    });
    pending.set(url, promise);
    return promise;
  }
  return Object.freeze({get, clear() { generation++; retained.clear(); pending.clear(); bytes = 0; }, stats() { return {entries: retained.size, pending: pending.size, estimatedBytes: bytes}; }});
}
