// Brightspace capture snapshot — run in Jock's signed-in Chrome on any
// https://brightspace.vanderbilt.edu/d2l/le/lessons/670098 page (read-only GET).
// Builds window.__snap: a compact JSON list of every content topic. Share links are
// reduced to a kind (Zoom -> recording live/async, Box -> private-link); only public
// reading URLs are kept. Read it back in <=900-char slices: window.__snap.slice(a, b).
const toc = await fetch('/d2l/api/le/1.99/670098/content/toc').then(r => r.json());
const items = [];
function cls(t) {
  const title = (t.Title || '').trim();
  const url = (t.Url || '').split('?')[0].split('#')[0];
  if (t.TypeIdentifier === 'File') {
    const f = decodeURIComponent(url.split('/').pop());
    let k = 'file';
    if (/^\d{4}-\d{2}-/.test(f)) k = 'paper';
    else if (/transcript/i.test(f) || /transcript/i.test(title)) k = 'transcript';
    else if (/lecture|async|live|week\d/i.test(f) && /\.(pdf|pptx?)$/i.test(f)) k = 'slides';
    else if (/\.pdf$/i.test(f) && /^[A-Z][a-z]+ et al\.|\(\d{4}\)/.test(title)) k = 'paper';
    return { k, f };
  }
  let host = '';
  try { host = new URL(url, location.origin).host; } catch (e) {}
  if (/zoom\.us$/.test(host)) return { k: 'recording', s: /async/i.test(title) ? 'async' : 'live' };
  if (/quizzing/.test(url)) return { k: 'quiz' };
  if (/survey/.test(url)) return { k: 'survey' };
  if (/dropbox|assignment/i.test(url)) return { k: 'assignment' };
  if (/box\.com$/.test(host)) return { k: 'private-link' };
  if (host === location.host || host === '') return { k: 'brightspace' };
  return { k: 'link', u: url.trim() };
}
function walk(m, week) {
  const mm = (m.Title || '').match(/Week\s+(\d+)/i);
  const w = mm ? +mm[1] : week;
  for (const t of (m.Topics || [])) items.push(Object.assign({ id: t.TopicId, w, t: (t.Title || '').trim() }, cls(t)));
  for (const c of (m.Modules || [])) walk(c, w);
}
for (const m of toc.Modules) walk(m, 0);
window.__snap = JSON.stringify(items);
'items=' + items.length + ' chars=' + window.__snap.length;
