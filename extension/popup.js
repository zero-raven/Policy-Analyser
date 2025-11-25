const LABELS = [
  "First Party Collection/Use","Third Party Sharing/Collection","User Choice/Control",
  "User Access, Edit & Deletion","Data Retention","Data Security","Policy Change",
  "Do Not Track","International & Specific Audiences","Miscellaneous and Other","Contact Information",
  "User Choices/Consent Mechanisms"
];

const DEFAULT_BACKEND = "http://localhost:8000/predict";

const textEl = document.getElementById('text');
const classifyBtn = document.getElementById('classify');
const clearBtn = document.getElementById('clear');
const analyzePageBtn = document.getElementById('analyzePage');
const copyBtn = document.getElementById('copyLabels');
const exportBtn = document.getElementById('exportJson');
const statusEl = document.getElementById('status');
const resultsSection = document.getElementById('results');
const labelsUl = document.getElementById('labels');
const evidenceDiv = document.getElementById('evidenceList');
const backendLink = document.getElementById('backendLink');
const modelState = document.getElementById('modelState');

const settingsModal = document.getElementById('settingsModal');
const backendInput = document.getElementById('backendUrl');
const saveSettings = document.getElementById('saveSettings');
const cancelSettings = document.getElementById('cancelSettings');

let currentBackend = DEFAULT_BACKEND;
let lastResponse = null;

function setStatus(msg, isError=false){
  statusEl.textContent = msg;
  statusEl.style.color = isError ? '#ffb4b4' : '#9fb2d6';
}

function setModelState(text, color){
  modelState.textContent = text;
  modelState.style.color = color || '#9fb2d6';
}

function loadBackendUrl(cb){
  if(typeof chrome !== 'undefined' && chrome.storage){
    chrome.storage.sync.get({backendUrl: DEFAULT_BACKEND}, items => {
      currentBackend = items.backendUrl || DEFAULT_BACKEND;
      backendLink.textContent = currentBackend;
      backendLink.href = currentBackend;
      backendInput.value = currentBackend;
      cb && cb(currentBackend);
    });
  } else { currentBackend = DEFAULT_BACKEND; backendLink.textContent = currentBackend; backendInput.value = currentBackend; cb && cb(currentBackend); }
}

function saveBackendUrl(url, cb){
  if(typeof chrome !== 'undefined' && chrome.storage){
    chrome.storage.sync.set({backendUrl: url}, cb || (()=>{}));
  } else cb && cb();
}

function showSpinner(msg){
  setStatus(msg);
  setModelState('loading...', '#ffd166');
}
function hideSpinner(){
  setModelState('local');
}

function clearResults(){
  labelsUl.innerHTML = '';
  evidenceDiv.innerHTML = '';
  resultsSection.classList.add('hidden');
  lastResponse = null;
}

function renderResults(data){
  lastResponse = data;
  const labels = data.labels || [];
  const scores = data.scores || [];
  labelsUl.innerHTML = labels.length ? labels.map(l=>`<li>${l}</li>`).join('') : '<li><em>None above threshold</em></li>';

  evidenceDiv.innerHTML = '';
  if(data.evidence && data.evidence.length){
    data.evidence.forEach(item=>{
      const div = document.createElement('div');
      div.className = 'item';
      div.innerHTML = `<div class="title"><strong>${item.label}</strong><span>${(item.score*100).toFixed(1)}%</span></div>
        <div class="snippet">${escapeHtml(item.snippet)}</div>`;
      evidenceDiv.appendChild(div);
    });
  } else {
    for(let i=0;i<LABELS.length;i++){
      const s = scores[i] || 0;
      const div = document.createElement('div');
      div.className = 'item';
      div.innerHTML = `<div class="title"><strong>${LABELS[i]}</strong><span>${(s*100).toFixed(1)}%</span></div>
        <div class="snippet">—</div>`;
      evidenceDiv.appendChild(div);
    }
  }
  resultsSection.classList.remove('hidden');
  resultsSection.setAttribute('aria-hidden','false');
}

function escapeHtml(s){ return String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'); }

async function classifyText(text){
  try{
    showSpinner('Sending to backend...');
    const resp = await fetch(currentBackend, {
      method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text})
    });
    if(!resp.ok){
      const txt = await resp.text();
      throw new Error(`Backend error: ${resp.status} ${txt}`);
    }
    const data = await resp.json();
    renderResults(data);
    setStatus('Done.');
  }catch(err){
    console.error(err);
    setStatus('Error: '+err.message, true);
  }finally{
    hideSpinner();
  }
}

textEl.addEventListener('keydown', (e)=>{
  if(e.ctrlKey && e.key === 'Enter'){ classifyBtn.click(); }
  setTimeout(()=> document.getElementById('charCount').textContent = `${textEl.value.length} chars`, 0);
});

classifyBtn.addEventListener('click', async ()=>{
  const text = textEl.value.trim();
  if(!text){ setStatus('Paste some text to classify.', true); return; }
  await classifyText(text);
});

clearBtn.addEventListener('click', ()=>{
  textEl.value=''; document.getElementById('charCount').textContent = '0 chars'; clearResults(); setStatus('Cleared.');
});

copyBtn.addEventListener('click', ()=>{
  const items = Array.from(labelsUl.querySelectorAll('li')).map(li=>li.textContent.trim());
  navigator.clipboard.writeText(items.join(', ')).then(()=> setStatus('Copied labels to clipboard.'));
});

exportBtn.addEventListener('click', ()=>{
  if(!lastResponse){ setStatus('Nothing to export', true); return; }
  const blob = new Blob([JSON.stringify(lastResponse,null,2)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'policy-analysis.json'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  setStatus('Exported JSON.');
});

analyzePageBtn.addEventListener('click', async () => {
  setStatus('Requesting page content...');

  try {
    const [tab] = await chrome.tabs.query({active:true, lastFocusedWindow:true});

    chrome.scripting.executeScript(
      {
        target: { tabId: tab.id },
        files: ["content_extractor.js"]  // <-- loads your external file
      },
      async (results) => {
        try {
          // After loading content_extractor.js, run the extractor
          chrome.scripting.executeScript(
            {
              target: { tabId: tab.id },
              func: () => window.__policyExtract()  // <-- run extractor
            },
            (finalResult) => {
              const r = finalResult[0].result;
              if (r && r.text && r.text.length > 20) {
                textEl.value = r.text;
                document.getElementById("charCount").textContent = `${r.text.length} chars`;
                setStatus(`Loaded from: ${r.source}`);
              } else {
                setStatus("Page extract failed or too small", true);
              }
            }
          );
        } catch(e) {
          setStatus("Error extracting page", true);
          console.error(e);
        }
      }
    );

  } catch (e) {
    setStatus(`Page analysis unavailable: ${e.message}`, true);
  }
});


loadBackendUrl((url)=>{
  currentBackend = url;
  setModelState('local', '#9fb2d6');
  setStatus('Ready');
});

