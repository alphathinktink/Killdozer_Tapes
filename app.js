const state = {
  catalog: [],
  activeId: "",
  follow: true,
  query: "",
};

const els = {
  app: document.querySelector("#app"),
  list: document.querySelector("#recording-list"),
  search: document.querySelector("#search"),
  reader: document.querySelector(".reader"),
  player: document.querySelector("#player"),
  playbackBar: document.querySelector("#playback-bar"),
  title: document.querySelector("#active-title"),
  kicker: document.querySelector("#active-kicker"),
  summary: document.querySelector("#active-summary"),
  links: document.querySelector("#resource-links"),
  transcript: document.querySelector("#transcript"),
  progress: document.querySelector("#progress-fill"),
  follow: document.querySelector("#toggle-follow"),
  back: document.querySelector("#jump-back"),
  forward: document.querySelector("#jump-forward"),
  matches: document.querySelector("#match-count"),
  statWords: document.querySelector("#stat-words"),
  statRuntime: document.querySelector("#stat-runtime"),
};

const formatClock = (seconds) => {
  const rounded = Math.max(0, Math.round(seconds || 0));
  const h = Math.floor(rounded / 3600);
  const m = Math.floor((rounded % 3600) / 60);
  const s = rounded % 60;
  return h ? `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}` : `${m}:${String(s).padStart(2, "0")}`;
};

const cleanHash = () => location.hash.replace(/^#/, "").split("?")[0];

const getHashTime = () => {
  const [, query] = location.hash.split("?");
  const params = new URLSearchParams(query || "");
  return Number(params.get("t") || 0);
};

const escapeHtml = (value) => value.replace(/[&<>"']/g, (char) => ({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#039;",
}[char]));

const highlight = (text, query) => {
  if (!query) return escapeHtml(text);
  const pattern = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return escapeHtml(text).replace(new RegExp(pattern, "gi"), (match) => `<mark>${match}</mark>`);
};

const activeItem = () => state.catalog.find((item) => item.id === state.activeId) || state.catalog[0];

const setActive = (id, time = 0) => {
  const item = state.catalog.find((entry) => entry.id === id) || state.catalog[0];
  if (!item) return;
  returnToReaderStart();
  state.activeId = item.id;
  location.hash = item.id + (time ? `?t=${time}` : "");
  render();
  els.player.currentTime = time || 0;
};

const renderList = () => {
  els.list.innerHTML = state.catalog.map((item) => {
    const matches = state.query
      ? item.cues.filter((cue) => cue.text.toLowerCase().includes(state.query.toLowerCase())).length
      : 0;
    return `<button class="recording-card ${item.id === state.activeId ? "active" : ""}" data-id="${item.id}">
      <span class="recording-title">${item.label}</span>
      <span class="recording-meta">${item.durationLabel} · ${item.wordCount.toLocaleString()} words${matches ? ` · ${matches} hits` : ""}</span>
    </button>`;
  }).join("");
};

const renderLinks = (item) => {
  const links = [
    ["Transcript page", item.transcriptPageUrl],
    ["TXT", item.txtUrl],
    ["VTT", item.vttUrl],
    ["SRT", item.srtUrl],
    ["MP3", item.audioUrl],
  ];
  const wavLabel = item.alternateWavTranscode
    ? `WAV not published (${item.wavTranscode.filename}; ${item.alternateWavTranscode.filename})`
    : `WAV not published (${item.wavTranscode.filename})`;
  els.links.innerHTML = [
    ...links.map(([label, href]) => `<a href="${href}">${label}</a>`),
    `<span class="unpublished-resource" title="${item.wavTranscode.note}">${wavLabel}</span>`,
  ].join("");
};

const renderTranscript = (item) => {
  const query = state.query.trim();
  let matches = 0;
  const cues = query
    ? item.cues.filter((cue) => {
      const hit = cue.text.toLowerCase().includes(query.toLowerCase());
      if (hit) matches += 1;
      return hit;
    })
    : item.cues;

  els.matches.textContent = query ? `${matches} matching timestamp${matches === 1 ? "" : "s"}` : `${item.cues.length} timestamped segments`;
  els.transcript.innerHTML = cues.map((cue, index) => `<p class="cue" data-start="${cue.start}" data-end="${cue.end}" id="cue-${index}">
    <button class="cue-time" data-start="${cue.start}" title="Play from ${cue.startLabel}">${cue.startLabel}</button>
    <span>${highlight(cue.text, query)}</span>
  </p>`).join("");
};

const renderPlayer = (item) => {
  const current = els.player.getAttribute("data-src");
  if (current === item.audioUrl) return;
  els.player.innerHTML = `<source src="${item.audioUrl}" type="audio/mpeg"><track kind="captions" src="${item.vttUrl}" srclang="en" label="English transcript" default>`;
  els.player.setAttribute("data-src", item.audioUrl);
  els.player.load();
};

const renderStats = () => {
  const words = state.catalog.reduce((sum, item) => sum + item.wordCount, 0);
  const duration = state.catalog.reduce((sum, item) => sum + item.duration, 0);
  els.statWords.textContent = words.toLocaleString();
  els.statRuntime.textContent = formatClock(duration);
};

const render = () => {
  const item = activeItem();
  if (!item) return;
  els.title.textContent = item.label;
  els.kicker.textContent = "Selected recording";
  els.summary.textContent = `${item.durationLabel} runtime. ${item.wordCount.toLocaleString()} transcript words.`;
  renderList();
  renderLinks(item);
  renderPlayer(item);
  renderTranscript(item);
  renderStats();
  els.app.dataset.ready = "true";
};

const setFollow = (follow) => {
  state.follow = follow;
  els.follow.textContent = follow ? "Pause follow" : "Resume follow";
  els.follow.classList.toggle("follow-paused", !follow);
};

let lastPageScroll = window.scrollY;

const scrollPageTo = (top) => {
  // Instant scrolling leaves no animation competing with the reader's next scroll.
  window.scrollTo({ top, behavior: "instant" });
  lastPageScroll = window.scrollY;
};

const returnToReaderStart = () => {
  const readerTop = els.reader.getBoundingClientRect().top;
  if (readerTop < 0) scrollPageTo(window.scrollY + readerTop);
};

const trackPageScroll = () => {
  // Scroll events arrive after scrollPageTo has recorded its new position.
  if (window.scrollY === lastPageScroll) return;
  lastPageScroll = window.scrollY;
  if (state.follow && !els.player.paused) setFollow(false);
};

const scrollToCue = (cue) => {
  const bar = els.playbackBar.getBoundingClientRect();
  const bounds = cue.getBoundingClientRect();
  const viewportHeight = document.documentElement.clientHeight;
  const visibleTop = Math.max(0, Math.min(bar.bottom, bar.height));
  const visibleCueHeight = Math.min(bounds.height, viewportHeight - visibleTop);
  if (bounds.top >= visibleTop && bounds.top + visibleCueHeight <= viewportHeight) return;

  const centeredTop = Math.max(bar.height, (viewportHeight + bar.height - bounds.height) / 2);
  scrollPageTo(window.scrollY + bounds.top - centeredTop);
};

const syncActiveCue = (recenter = false) => {
  const item = activeItem();
  if (!item || !els.player.duration) return;
  els.progress.style.width = `${Math.min(100, (els.player.currentTime / els.player.duration) * 100)}%`;
  const cues = [...els.transcript.querySelectorAll(".cue")];
  const active = cues.find((cue) => {
    const start = Number(cue.dataset.start);
    const end = Number(cue.dataset.end);
    return els.player.currentTime >= start && els.player.currentTime <= end;
  });
  const cueChanged = active && !active.classList.contains("active");
  cues.forEach((cue) => cue.classList.toggle("active", cue === active));
  trackPageScroll();
  if (active && state.follow && (cueChanged || recenter)) scrollToCue(active);
};

const boot = async () => {
  const response = await fetch("data/catalog.json");
  state.catalog = await response.json();
  state.activeId = cleanHash() || state.catalog[0]?.id || "";
  render();
  const hashTime = getHashTime();
  if (hashTime) els.player.currentTime = hashTime;
};

els.list.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-id]");
  if (button) setActive(button.dataset.id);
});

els.transcript.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-start]");
  if (!button) return;
  els.player.currentTime = Number(button.dataset.start);
  els.player.play();
});

els.search.addEventListener("input", () => {
  state.query = els.search.value;
  if (state.follow && !els.player.paused) setFollow(false);
  returnToReaderStart();
  render();
});

els.follow.addEventListener("click", () => {
  setFollow(!state.follow);
  if (state.follow) {
    lastPageScroll = window.scrollY;
    syncActiveCue(true);
  }
});

els.back.addEventListener("click", () => {
  els.player.currentTime = Math.max(0, els.player.currentTime - 15);
});

els.forward.addEventListener("click", () => {
  els.player.currentTime = Math.min(els.player.duration || Infinity, els.player.currentTime + 15);
});

els.player.addEventListener("timeupdate", () => syncActiveCue());
els.player.addEventListener("play", () => syncActiveCue(true));
window.addEventListener("scroll", trackPageScroll, { passive: true });
window.addEventListener("hashchange", () => {
  const id = cleanHash();
  if (id && id !== state.activeId) setActive(id, getHashTime());
});

boot().catch((error) => {
  els.title.textContent = "Archive could not load";
  els.summary.textContent = error.message;
});
