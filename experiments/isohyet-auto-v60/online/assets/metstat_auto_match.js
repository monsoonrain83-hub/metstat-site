/* MetStat auto-resolution engine. No geographic guess is treated as sensor identity.
 * CommonJS for Node tests, global MetStatAutoMatch in browsers. No external dependencies.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.MetStatAutoMatch = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const CHAR_REPLACE = {'ي':'ی','ى':'ی','ك':'ک','ة':'ه','ۀ':'ه','ؤ':'و','إ':'ا','أ':'ا','ٱ':'ا','آ':'ا','ئ':'ی','ء':'','ـ':''};
  const DIGITS = '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩';
  const TYPE_MAP = {
    synoptic: 0, synop: 0, 'سینوپتیک': 0, 'ایستگاه سینوپتیک': 0, 'همدیدی': 0,
    climatology: 1, climatological: 1, climate: 1, 'اقلیم شناسی': 1, 'اقلیم‌شناسی': 1,
    raingauge: 2, 'rain gauge': 2, rainfall: 2, 'باران سنجی': 2, 'باران‌سنجی': 2, 'باران سنج': 2,
    geographic_place: 3, geographic_reference: 3, geographic: 3, place: 3, 'آبادی': 3, 'مکان جغرافیایی': 3
  };
  function normalize(v) {
    let s = String(v == null ? '' : v).trim();
    s = s.replace(/[يىكةۀؤإأٱآئءـ]/g, ch => CHAR_REPLACE[ch] || '');
    s = s.replace(/[\u064b-\u065f\u0670\u06d6-\u06ed]/g, '').replace(/[\u200c\u200d_#\-./،,؛:()[\]{}]/g, ' ');
    s = s.replace(/[۰-۹٠-٩]/g, ch => String(DIGITS.indexOf(ch) % 10));
    return s.replace(/\s+/g, ' ').trim().toLocaleLowerCase('fa-IR');
  }
  function variantNames(x) {
    const keys = [x.name, x.name_fa, x.station_name, x.original_name, ...(Array.isArray(x.aliases) ? x.aliases : []),
      ...(Array.isArray(x.alternative_names) ? x.alternative_names : [])];
    return [...new Set(keys.map(normalize).filter(Boolean))];
  }
  function typeRank(x) {
    const raw = normalize(x.station_type || x.network || x.type || '');
    return Object.prototype.hasOwnProperty.call(TYPE_MAP, raw) ? TYPE_MAP[raw] : 99;
  }
  function coords(x) {
    const lat = Number(x.lat ?? x.latitude); const lon = Number(x.lon ?? x.longitude ?? x.lng);
    return Number.isFinite(lat) && Number.isFinite(lon) && lat >= 24 && lat <= 41 && lon >= 43 && lon <= 64 ? {lat,lon} : null;
  }
  function sameAdmin(input, candidate, key) {
    const lhs = normalize(input[key]), rhs = normalize(candidate[key]);
    // Unknown is not a conflicting administration; it can never itself verify a match.
    return lhs && rhs ? lhs === rhs : null;
  }
  function stationCompare(a,b) {return a.rank-b.rank || String(a.id).localeCompare(String(b.id));}
  function outcome(status, chosen, candidates, method, reason) {
    return {status,chosen:chosen || null,candidates:candidates || [],method:method || null,reason:reason || null};
  }
  /**
   * Resolve one textual rainfall station against the existing sensor DB + gazetteer.
   * Does not authorize creation of a new meteorological sensor from a gazetteer point.
   */
  function resolveOne(input, stations, places = [], opts = {}) {
    const wanted = normalize(input.name); const province = normalize(input.province || opts.province);
    const county = normalize(input.county || opts.county);
    if (!wanted) return outcome('invalid',null,[],null,'نام ایستگاه خالی است');
    const valid = (o) => {
      const p = normalize(o.province), c = normalize(o.county);
      if (province && province !== p) return false;
      if (county && county !== c) return false;
      return true;
    };
    const exact = (stations || []).filter(s => valid(s) && variantNames(s).includes(wanted)).map(s => ({...s,rank:typeRank(s)}));
    // A name at a different county is NOT a fallback even if it has a better network type.
    if (exact.length) {
      const sorted = exact.sort(stationCompare);
      const first = sorted[0];
      const best = sorted.filter(x => x.rank === first.rank);
      const verified = best.filter(x => {
        const p = sameAdmin({province},x,'province'), c = sameAdmin({county},x,'county');
        return p !== false && c !== false && coords(x);
      });
      // Distinct same-priority stations require disambiguation; this is deliberate.
      if (best.length > 1)
        return outcome('ambiguous',null,best,'station_db','چند ایستگاه هم‌نام با اولویت برابر');
      const chosen = best[0];
      if (chosen.rank === 99) return outcome('review',null,sorted,'station_db','نوع شبکه مشخص نیست');
      if (!coords(chosen)) return outcome('review',null,sorted,'station_db','مختصات ایستگاه معتبر نیست');
      // Without a supplied province/county, only unique global names can be auto accepted.
      if (!province && !county && exact.length !== 1) return outcome('ambiguous',null,sorted,'station_db','محدوده جغرافیایی نامشخص');
      return outcome('auto_station',chosen,sorted,'station_db',null);
    }
    const locs = (places || []).filter(s => valid(s) && variantNames(s).includes(wanted));
    if (locs.length === 1) {
      const p = locs[0];
      if (coords(p)) return outcome('auto_geographic',{...p,station_type:'geographic_reference',not_sensor:true},locs,'gazetteer','مختصات آبادی؛ نه سنسور');
      return outcome('needs_geocoding',null,locs,'gazetteer','نام و تقسیمات کشوری مشخص؛ مختصات نیازمند جست‌وجو');
    }
    if (locs.length > 1) return outcome('ambiguous',null,locs,'gazetteer','نام آبادی در چند مکان تکرار شده');
    return outcome('needs_geocoding',null,[],null,'در بانک ایستگاه و آبادی یافت نشد');
  }
  function summary(rows) {
    const counts = {total:rows.length, auto_station:0,auto_geographic:0,needs_geocoding:0,ambiguous:0,review:0,unresolved:0,invalid:0};
    for (const r of rows) counts[r?.status in counts ? r.status : 'unresolved']++;
    counts.mapped=counts.auto_station+counts.auto_geographic;
    counts.pending=counts.total-counts.mapped;
    return counts;
  }
  /** Async geocoder only for unresolved rows. Injection avoids tying the matcher to any vendor. */
  async function resolveBatch(rows, stations, opts={}) {
    const out=[];const places=opts.places || [];
    for(let i=0;i<rows.length;i++) {
      const row=rows[i]; let r=resolveOne(row,stations,places,opts);
      if(r.status==='needs_geocoding' && typeof opts.geocode==='function') {
        try {
          const g=await opts.geocode({name:row.name,province:row.province || opts.province || '',county:row.county || opts.county || ''});
          if(g?.status==='exact' && coords(g) && g.admin_verified === true && g.unique === true) {
            r=outcome('auto_geographic',{...g,station_type:'geographic_reference',not_sensor:true},[g],'geocoding','مرجع مکانی تأییدشده؛ نه سنسور');
          } else if(g?.status==='ambiguous' || (Array.isArray(g?.candidates) && g.candidates.length)) {
            r=outcome('ambiguous',null,g.candidates || [],'geocoding','نتیجه جست‌وجو یکتا نیست');
          } else {r=outcome('unresolved',null,[], 'geocoding',g?.reason || 'مرجع معتبر پیدا نشد');}
        } catch(e) {r=outcome('unresolved',null,[],'geocoding','سرویس جست‌وجوی جغرافیایی در دسترس نیست');}
      }
      out.push({...r,input:row,index:i});
      if(typeof opts.onProgress==='function')opts.onProgress(i+1,rows.length,summary(out));
    }
    return {records:out,counts:summary(out)};
  }
  return Object.freeze({normalize,variantNames,typeRank,coords,resolveOne,resolveBatch,summary});
});
