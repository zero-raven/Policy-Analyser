/***********************
 * CONFIG
 ***********************/
const DEFAULT_BACKEND = "http://localhost:8000/predict";
const ANALYZE_TEXT_ENDPOINT = "http://localhost:8000/analyze-text";
const CHAT_ENDPOINT = "http://localhost:8000/chat";

/***********************
 * ELEMENTS
 ***********************/
const textEl = document.getElementById("text");
const classifyBtn = document.getElementById("classify");
const clearBtn = document.getElementById("clear");
const analyzePageBtn = document.getElementById("analyzePage");

const statusEl = document.getElementById("status");
const modelState = document.getElementById("modelState");
const backendLink = document.getElementById("backendLink");

const modelSelect = document.getElementById("modelSelect");
const resultsSection = document.getElementById("results");

const labelsUl = document.getElementById("labels");
const evidenceDiv = document.getElementById("evidenceList");

const toggleDeepBtn = document.getElementById("toggleDeep");
const toggleChatBtn = document.getElementById("toggleChat");
const deepSection = document.getElementById("deepAnalysis");
const summaryText = document.getElementById("summaryText");

const chatSection = document.getElementById("chatSection");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendChatBtn = document.getElementById("sendChat");

const copyBtn = document.getElementById("copyLabels");

/***********************
 * STATE
 ***********************/
let policyChunks = [];
let summaryLoaded = false;

/***********************
 * HELPERS
 ***********************/
function setStatus(msg, isError = false) {
  statusEl.textContent = msg;
  statusEl.style.color = isError ? "#ef4444" : "#9aa7bd";
}

function setModelState(text) {
  modelState.textContent = text;
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function clearResults() {
  labelsUl.innerHTML = "";
  evidenceDiv.innerHTML = "";
  resultsSection.classList.add("hidden");
  deepSection.classList.add("hidden");
  chatSection.classList.add("hidden");
  chatMessages.innerHTML = "";
  summaryLoaded = false;
  policyChunks = [];
}

/***********************
 * RENDERING
 ***********************/
function renderResults(data) {
  const labels = data.labels || [];
  const scores = data.scores || [];
  const evidence = data.evidence || [];

  labelsUl.innerHTML = labels.length
    ? labels.map(l => `<li>${escapeHtml(l)}</li>`).join("")
    : "<li><em>No significant clauses detected</em></li>";

  evidenceDiv.innerHTML = "";

  if (evidence.length) {
    evidence.forEach(item => {
      const div = document.createElement("div");
      div.className = "item";
      div.innerHTML = `
        <div class="title">
          <strong>${escapeHtml(item.label)}</strong>
          <span>${(item.score * 100).toFixed(1)}%</span>
        </div>
        <div class="snippet">${escapeHtml(item.snippet)}</div>
      `;
      evidenceDiv.appendChild(div);
    });
  }

  policyChunks = data.chunks || [];
  resultsSection.classList.remove("hidden");
  deepSection.classList.add("hidden");
  chatSection.classList.add("hidden");
  summaryLoaded = false;
}

/***********************
 * BACKEND CALLS
 ***********************/
async function classifyText(text) {
  setStatus("Analyzing…");
  setModelState(modelSelect.value);

  try {
    const resp = await fetch(DEFAULT_BACKEND, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        model: modelSelect.value
      })
    });

    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

    const data = await resp.json();
    renderResults(data);
    setStatus("Analysis complete");
  } catch (err) {
    console.error(err);
    setStatus("Analysis failed", true);
  }
}

/***********************
 * EVENTS
 ***********************/
classifyBtn.addEventListener("click", async () => {
  const text = textEl.value.trim();
  const url = urlInput.value.trim();

  // Priority 1: URL provided → analyze-url endpoint
  if (url) {
    setStatus("Analyzing URL…");
    setModelState(modelSelect.value);

    try {
      const resp = await fetch("http://localhost:8000/analyze-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: url,
          model: modelSelect.value
        })
      });

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const data = await resp.json();
      renderResults(data);
      setStatus("URL analysis complete");
      return;
    } catch (err) {
      console.error(err);
      setStatus("URL analysis failed", true);
      return;
    }
  }

  // Priority 2: fallback → pasted/scanned text
  if (!text) {
    setStatus("Paste text, scan page, or enter a URL", true);
    return;
  }

  classifyText(text);
});


clearBtn.addEventListener("click", () => {
  textEl.value = "";
  document.getElementById("charCount").textContent = "0 chars";
  clearResults();
  setStatus("Cleared");
});

textEl.addEventListener("input", () => {
  document.getElementById("charCount").textContent =
    `${textEl.value.length} chars`;
});

/***********************
 * SCAN PAGE (FIXED)
 ***********************/
analyzePageBtn.addEventListener("click", async () => {
  setStatus("Scanning page…");

  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true
    });

    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content_extractor.js"]
    });

    const [{ result }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => window.__policyExtract?.()
    });

    if (!result || !result.text || result.text.length < 50) {
      setStatus("No policy-like content found", true);
      return;
    }

    textEl.value = result.text;
    document.getElementById("charCount").textContent =
      `${result.text.length} chars`;

    setStatus(`Scanned from ${result.source}`);
    classifyText(result.text); // 🔥 auto-analyze (this was missing)
  } catch (err) {
    console.error(err);
    setStatus("Page scan failed", true);
  }
});

/***********************
 * SUMMARY (ON DEMAND)
 ***********************/
toggleDeepBtn.addEventListener("click", async () => {
  deepSection.classList.toggle("hidden");

  if (summaryLoaded || deepSection.classList.contains("hidden")) return;

  summaryText.textContent = "Generating summary…";

  try {
    const resp = await fetch(ANALYZE_TEXT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: textEl.value,
        model: modelSelect.value
      })
    });

    const data = await resp.json();
    summaryText.textContent =
      data.summary || "No summary available.";
    summaryLoaded = true;
  } catch {
    summaryText.textContent = "Failed to generate summary.";
  }
});

/***********************
 * CHAT (ON DEMAND)
 ***********************/
toggleChatBtn.addEventListener("click", () => {
  chatSection.classList.toggle("hidden");
});

sendChatBtn.addEventListener("click", async () => {
  const msg = chatInput.value.trim();
  if (!msg) return;

  chatInput.value = "";

  chatMessages.innerHTML += `
    <div class="item user">${escapeHtml(msg)}</div>
  `;

  try {
    const resp = await fetch(CHAT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        chunks: policyChunks
      })
    });

    const data = await resp.json();

    chatMessages.innerHTML += `
      <div class="item bot">${escapeHtml(data.answer || "No response")}</div>
    `;
  } catch {
    chatMessages.innerHTML += `
      <div class="item bot">Chat failed.</div>
    `;
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
});

/***********************
 * COPY LABELS
 ***********************/
copyBtn.addEventListener("click", () => {
  const labels = Array.from(labelsUl.children)
    .map(li => li.textContent)
    .join(", ");
  navigator.clipboard.writeText(labels);
  setStatus("Copied labels");
});

/***********************
 * INIT
 ***********************/
backendLink.href = DEFAULT_BACKEND;
backendLink.textContent = "Local API";
setModelState("Ready");
setStatus("Ready");
