const start = document.querySelector("#start");
const end = document.querySelector("#end");
const compareButton = document.querySelector("#compare");
const status = document.querySelector("#status");

const requested = new URLSearchParams(window.location.search);
let restorePending = false;
let restoreApplied = false;

function availableDates() {
  return new Set([...start.options].map((option) => option.value));
}

function prepareRestore() {
  if (restoreApplied || start.options.length === 0) return;
  restoreApplied = true;

  const dates = availableDates();
  const requestedStart = requested.get("start");
  const requestedEnd = requested.get("end");
  if (
    requestedStart &&
    requestedEnd &&
    dates.has(requestedStart) &&
    dates.has(requestedEnd) &&
    requestedStart < requestedEnd
  ) {
    start.value = requestedStart;
    end.value = requestedEnd;
    restorePending = true;
  }
}

function syncUrl() {
  if (!start.value || !end.value || start.value >= end.value) return;
  const url = new URL(window.location.href);
  url.searchParams.set("start", start.value);
  url.searchParams.set("end", end.value);
  window.history.replaceState(null, "", url);
}

function handleStatusChange() {
  prepareRestore();
  if (!status.textContent.includes("比較完了")) return;

  if (restorePending) {
    restorePending = false;
    compareButton.click();
    return;
  }
  syncUrl();
}

const observer = new MutationObserver(handleStatusChange);
observer.observe(status, { childList: true, characterData: true, subtree: true });

function waitForOptions() {
  prepareRestore();
  if (!restoreApplied) window.requestAnimationFrame(waitForOptions);
}

waitForOptions();
