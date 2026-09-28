chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "customLinkAction",
    title: "Open With Nannite",
    contexts: ["link"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId !== "customLinkAction") return;

  const workerBase = "https://YOUR-WORKER.workers.dev/";

  try {
    const url = new URL(info.linkUrl);
    const encodedHost = url.hostname.replace(/\./g, "+");
    const encodedPath = url.pathname.replace(/\//g, "-");
    const encodedQuery = url.search
      ? url.search.replace(/\//g, "-").replace(/\./g, "+")
      : "";

    const encodedUrl =
      workerBase +
      encodedHost +
      encodedPath +
      encodedQuery;

    console.log("Original URL:", info.linkUrl);
    console.log("Nannite URL:", encodedUrl);

    chrome.tabs.create({
      url: encodedUrl
    });

  } catch (err) {
    console.error("Failed to encode URL:", err);
  }
});