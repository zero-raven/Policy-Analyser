
const LABELS = [
  "First Party Collection/Use","Third Party Sharing/Collection","User Choice/Control",
  "User Access, Edit & Deletion","Data Retention","Data Security","Policy Change",
  "Do Not Track","International & Specific Audiences","Miscellaneous and Other","Contact Information",
  "User Choices/Consent Mechanisms"
];

const textEl = document.getElementById('text');
const classifyBtn = document.getElementById('classify');
const clearBtn = document.getElementById('clear');
const statusEl = document.getElementById('status');
const resultsDiv = document.getElementById('results');
const labelsUl = document.getElementById('labels');
const chartCanvas = document.getElementById('chart');
let chartInstance = null;

function setStatus(msg, isError=false){
  statusEl.textContent = msg;
  statusEl.style.color = isError ? '#ffb4b4' : '#9fb2d6';
}

classifyBtn.addEventListener('click', async ()=>{
  const text = textEl.value.trim();
  if(!text){ setStatus('Paste some text to classify.', true); return; }
  setStatus('Sending text to backend...');
  resultsDiv.style.display='none';
  labelsUl.innerHTML='';
  try{
    const resp = await fetch('http://localhost:8000/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    });
    if(!resp.ok){
      const txt = await resp.text();
      throw new Error(`Backend error: ${resp.status} ${txt}`);
    }
    const data = await resp.json();
    const labels = data.labels || [];
    const scores = data.scores || [];
    // show detected labels
    labelsUl.innerHTML = labels.length? labels.map(l=>`<li>${l}</li>`).join('') : '<li><em>None above threshold</em></li>';
    // draw chart
    drawChart(scores);
    resultsDiv.style.display='block';
    setStatus('Done.');
  }catch(err){
    console.error(err);
    setStatus('Error: ' + err.message, true);
  }
});

clearBtn.addEventListener('click', ()=>{
  textEl.value='';
  labelsUl.innerHTML='';
  if(chartInstance){ chartInstance.destroy(); chartInstance = null; }
  resultsDiv.style.display='none';
  setStatus('Cleared.');
});

function drawChart(scores){
  if(!scores || !scores.length){ scores = Array(LABELS.length).fill(0); }
  const data = {
    labels: LABELS,
    datasets: [{ label: 'Probability', data: scores.map(s=>Number(parseFloat(s).toFixed(4))) }]
  };
  if(chartInstance){ chartInstance.destroy(); chartInstance = null; }
  chartInstance = new Chart(chartCanvas.getContext('2d'), {
    type: 'bar',
    data,
    options: {
      indexAxis: 'y',
      scales: { x: { beginAtZero: true, max: 1 } },
      plugins: { legend: { display: false } }
    }
  });
}
