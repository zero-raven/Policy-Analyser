chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyzeSelection",
    title: "Analyze selection with Policy Analyser",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "analyzeSelection" && info.selectionText) {
    chrome.scripting.executeScript({
      target: {tabId: tab.id},
      func: (sel) => alert('Selected text will be analysed by Policy Analyser: ' + (sel.slice(0,200) + '...')),
      args: [info.selectionText]
    });
  }
});
