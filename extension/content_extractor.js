// content_extractor.js
// This file defines a global function that can be executed inside any webpage.

// IMPORTANT: this must not use chrome.* APIs or import/export syntax.
// It must be pure browser JS so chrome.scripting can inject it.

// Wrap in a function and attach to window for clarity.
window.__policyExtract = (() => {

  const MAX_CHARS = 20000;
  const EXCLUDE = ['nav','header','footer','aside','form','svg','canvas','noscript','iframe'];

  function textLen(el) {
    try {
      const clone = el.cloneNode(true);
      clone.querySelectorAll('script,style,svg,canvas,iframe,noscript').forEach(n=>n.remove());
      clone.querySelectorAll(EXCLUDE.join(',')).forEach(n => { if (n !== clone) n.remove(); });
      return (clone.innerText || '').trim().length;
    } catch(e) { return 0; }
  }

  function extract(el) {
    if (!el) return '';
    const clone = el.cloneNode(true);
    clone.querySelectorAll('script,style,iframe,svg,canvas,noscript').forEach(n=>n.remove());
    clone.querySelectorAll('[class*="cookie"],[class*="consent"],[id*="cookie"]').forEach(n=>n.remove());
    let t = clone.innerText || '';
    t = t.replace(/\s{2,}/g, ' ').trim();
    return t.slice(0, MAX_CHARS);
  }

  return () => {

    // 1) user selection
    const sel = window.getSelection().toString().trim();
    if (sel && sel.length > 30)
      return { text: sel.slice(0,MAX_CHARS), source: "selection" };

    // 2) common semantic containers
    const base = [
      ...document.querySelectorAll("article"),
      ...document.querySelectorAll("main"),
      ...document.querySelectorAll("[role='main']"),
      ...document.querySelectorAll("#content, .content, .article, .page")
    ];

    for (const c of base) {
      const t = extract(c);
      if (t.length > 200) return { text: t, source: "semantic" };
    }

    // 3) largest text-containing element
    const all = [...document.querySelectorAll("div,section,article,main,p")];
    let best = null, bestLen = 0;

    for (const el of all) {
      const len = textLen(el);
      if (len > bestLen) { best = el; bestLen = len; }
    }

    if (best && bestLen > 200) {
      return { text: extract(best), source: "largest" };
    }

    // 4) fallback: body
    const fallback = extract(document.body);
    return { text: fallback, source: "body-fallback" };
  };

})();
