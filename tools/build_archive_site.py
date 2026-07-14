from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TRANSCRIPT_DIR = ROOT / "transcripts"


RECORDINGS = [
    {
        "id": "tape-1-side-a",
        "label": "Tape 1 Side A",
        "stem": "1-Tape_1_Side_A",
        "audio": "1-Tape_1_Side_A.mp3",
        "txt": "1-Tape_1_Side_A (transcribed on 07-Jul-2026 17-19-37).txt",
        "vtt": "1-Tape_1_Side_A (transcribed on 07-Jul-2026 17-19-37).vtt",
        "srt": "1-Tape_1_Side_A (transcribed on 07-Jul-2026 17-19-36).srt",
    },
    {
        "id": "tape-1-side-b",
        "label": "Tape 1 Side B",
        "stem": "2-Tape_1_Side_B",
        "audio": "2-Tape_1_Side_B (FF corrected).mp3",
        "alternateAudio": "2-Tape_1_Side_B.mp3",
        "txt": "2-Tape_1_Side_B (transcribed on 07-Jul-2026 19-39-22).txt",
        "vtt": "2-Tape_1_Side_B (transcribed on 07-Jul-2026 19-39-22).vtt",
        "srt": "2-Tape_1_Side_B (transcribed on 07-Jul-2026 19-39-22).srt",
    },
    {
        "id": "tape-2-side-a",
        "label": "Tape 2 Side A",
        "stem": "3-Tape_2_Side_A",
        "audio": "3-Tape_2_Side_A.mp3",
        "txt": "3-Tape_2_Side_A (transcribed on 07-Jul-2026 22-08-52).txt",
        "vtt": "3-Tape_2_Side_A (transcribed on 07-Jul-2026 22-08-52).vtt",
        "srt": "3-Tape_2_Side_A (transcribed on 07-Jul-2026 22-08-52).srt",
    },
    {
        "id": "tape-2-side-b",
        "label": "Tape 2 Side B",
        "stem": "4-Tape_2_Side_B",
        "audio": "4-Tape_2_Side_B.mp3",
        "txt": "4-Tape_2_Side_B (transcribed on 07-Jul-2026 23-33-02).txt",
        "vtt": "4-Tape_2_Side_B (transcribed on 07-Jul-2026 23-33-02).vtt",
        "srt": "4-Tape_2_Side_B (transcribed on 07-Jul-2026 23-33-02).srt",
    },
    {
        "id": "tape-3-side-a",
        "label": "Tape 3 Side A",
        "stem": "5-Tape_3_Side_A",
        "audio": "5-Tape_3_Side_A.mp3",
        "txt": "5-Tape_3_Side_A (transcribed on 08-Jul-2026 00-54-56).txt",
        "vtt": "5-Tape_3_Side_A (transcribed on 08-Jul-2026 00-54-56).vtt",
        "srt": "5-Tape_3_Side_A (transcribed on 08-Jul-2026 00-54-56).srt",
    },
    {
        "id": "tape-3-side-b",
        "label": "Tape 3 Side B",
        "stem": "6-Tape_3_Side_B",
        "audio": "6-Tape_3_Side_B.mp3",
        "txt": "6-Tape_3_Side_B (transcribed on 08-Jul-2026 01-17-54).txt",
        "vtt": "6-Tape_3_Side_B (transcribed on 08-Jul-2026 01-17-54).vtt",
        "srt": "6-Tape_3_Side_B (transcribed on 08-Jul-2026 01-17-54).srt",
    },
    {
        "id": "tape-4-side-a",
        "label": "Tape 4 Side A",
        "stem": "7-Tape_4_Side_A",
        "audio": "7-Tape_4_Side_A.mp3",
        "txt": "7-Tape_4_Side_A (transcribed on 08-Jul-2026 02-13-02).txt",
        "vtt": "7-Tape_4_Side_A (transcribed on 08-Jul-2026 02-13-02).vtt",
        "srt": "7-Tape_4_Side_A (transcribed on 08-Jul-2026 02-13-02).srt",
    },
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def time_to_seconds(value: str) -> float:
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def seconds_to_clock(seconds: float) -> str:
    seconds = int(round(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02}:{secs:02}"
    return f"{minutes}:{secs:02}"


def parse_vtt(path: Path) -> list[dict]:
    cues = []
    block: list[str] = []
    for line in read_text(path).split("\n"):
        if line.strip():
            block.append(line)
            continue
        if block:
            cue = parse_vtt_block(block)
            if cue:
                cues.append(cue)
            block = []
    if block:
        cue = parse_vtt_block(block)
        if cue:
            cues.append(cue)
    return cues


def parse_vtt_block(block: list[str]) -> dict | None:
    if block[0].strip() == "WEBVTT":
        return None
    timing_index = next((i for i, line in enumerate(block) if "-->" in line), None)
    if timing_index is None:
        return None
    start_raw, end_raw = [part.strip().split(" ")[0] for part in block[timing_index].split("-->", 1)]
    text = " ".join(line.strip() for line in block[timing_index + 1 :] if line.strip())
    text = re.sub(r"<[^>]+>", "", text)
    return {
        "start": round(time_to_seconds(start_raw), 3),
        "end": round(time_to_seconds(end_raw), 3),
        "startLabel": seconds_to_clock(time_to_seconds(start_raw)),
        "endLabel": seconds_to_clock(time_to_seconds(end_raw)),
        "text": html.unescape(text),
    }


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def file_size(path: Path) -> int:
    return path.stat().st_size


def page_url(filename: str) -> str:
    return quote(filename, safe="/")


def render_manifest_path(path: str) -> str:
    if path.startswith("Not published"):
        return f"<span class=\"unpublished-artifact\">{html.escape(path)}</span>"
    return f"<a href=\"{page_url(path)}\">{html.escape(path)}</a>"


def build_catalog() -> list[dict]:
    catalog = []
    for item in RECORDINGS:
        txt = read_text(ROOT / item["txt"]).strip()
        cues = parse_vtt(ROOT / item["vtt"])
        duration = max((cue["end"] for cue in cues), default=0)
        transcript_page = f"transcripts/{item['id']}.html"
        wav_name = Path(item["audio"]).with_suffix(".wav").name
        data = {
            "id": item["id"],
            "label": item["label"],
            "transcriptionOrigin": "Initial transcript generated in Buzz using Whisper Large-v3; later reviewed and edited with limited human ear-checking plus Codex/ChatGPT-assisted cleanup.",
            "initialTranscriber": "Buzz / Whisper Large-v3",
            "editorCredit": "Leonard Bogard, with Codex/ChatGPT assistance",
            "verificationStatus": "Partially reviewed; not a fully human-verified verbatim transcript.",
            "audio": item["audio"],
            "audioUrl": page_url(item["audio"]),
            "txt": item["txt"],
            "txtUrl": page_url(item["txt"]),
            "vtt": item["vtt"],
            "vttUrl": page_url(item["vtt"]),
            "srt": item["srt"],
            "srtUrl": page_url(item["srt"]),
            "transcriptPage": transcript_page,
            "transcriptPageUrl": page_url(transcript_page),
            "duration": duration,
            "durationLabel": seconds_to_clock(duration),
            "wordCount": word_count(txt),
            "audioBytes": file_size(ROOT / item["audio"]),
            "transcriptBytes": file_size(ROOT / item["txt"]),
            "wavTranscode": {
                "filename": wav_name,
                "directory": "wav-44.1khz-16bit/",
                "published": False,
                "note": "44.1 kHz / 16-bit WAV transcode generated for local waveform review; intentionally not published in the GitHub repository because of file size.",
            },
            "plainText": txt,
            "cues": cues,
        }
        if "alternateAudio" in item:
            data["alternateAudio"] = item["alternateAudio"]
            data["alternateAudioUrl"] = page_url(item["alternateAudio"])
            data["alternateWavTranscode"] = {
                "filename": Path(item["alternateAudio"]).with_suffix(".wav").name,
                "directory": "wav-44.1khz-16bit/",
                "published": False,
                "note": "Alternate 44.1 kHz / 16-bit WAV transcode generated for local waveform review; intentionally not published in the GitHub repository because of file size.",
            }
        catalog.append(data)
    return catalog


def render_transcript_page(item: dict) -> str:
    cue_markup = "\n".join(
        f'<p id="{item["id"]}-{index + 1:04}" data-start="{cue["start"]}">'
        f'<a class="time" href="../index.html#{item["id"]}?t={cue["start"]}">{cue["startLabel"]}</a> '
        f'{html.escape(cue["text"])}</p>'
        for index, cue in enumerate(item["cues"])
    )
    json_ld = {
        "@context": "https://schema.org",
        "@type": "AudioObject",
        "name": f"Killdozer Tapes - {item['label']}",
        "encodingFormat": "audio/mpeg",
        "contentUrl": f"../{item['audioUrl']}",
        "transcript": item["plainText"],
        "duration": f"PT{int(item['duration'])}S",
    }
    json_ld_text = json.dumps(json_ld, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Killdozer Tapes - {html.escape(item["label"])} Transcript</title>
  <meta name="description" content="Plain, crawlable transcript and source audio links for {html.escape(item["label"])}.">
  <link rel="canonical" href="../{item["transcriptPageUrl"]}">
  <link rel="stylesheet" href="../styles.css">
  <script type="application/ld+json">{json_ld_text}</script>
</head>
<body class="transcript-page">
  <main class="transcript-document">
    <nav class="crumbs"><a href="../index.html">Archive index</a></nav>
    <header>
      <p class="eyebrow">Killdozer Tapes transcript</p>
      <h1>{html.escape(item["label"])}</h1>
      <p class="lede">Duration {item["durationLabel"]}. {item["wordCount"]:,} words. This page exposes the transcript as plain HTML for search engines, scrapers, and AI assistants.</p>
      <p class="provenance-note"><strong>Transcript provenance:</strong> initial transcript generated in Buzz using Whisper Large-v3; later corrected through limited human review and Codex/ChatGPT-assisted editing. This is not presented as a fully human-verified verbatim transcript. See <a href="../provenance.html">process and authorship notes</a>.</p>
      <div class="resource-row">
        <a href="../{item["audioUrl"]}">MP3 audio</a>
        <a href="../{item["txtUrl"]}">TXT</a>
        <a href="../{item["vttUrl"]}">VTT</a>
        <a href="../{item["srtUrl"]}">SRT</a>
      </div>
    </header>
    <article class="crawler-transcript">
      {cue_markup}
    </article>
  </main>
</body>
</html>
"""


def render_index(catalog: list[dict]) -> str:
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Killdozer Tapes Archive",
        "hasPart": [
            {
                "@type": "AudioObject",
                "name": item["label"],
                "contentUrl": item["audioUrl"],
                "duration": f"PT{int(item['duration'])}S",
                "transcript": item["transcriptPageUrl"],
            }
            for item in catalog
        ],
    }
    json_ld_text = json.dumps(json_ld, ensure_ascii=False).replace("</", "<\\/")
    links = "\n".join(
        f'        <li><a href="{item["transcriptPageUrl"]}">{html.escape(item["label"])} transcript</a></li>'
        for item in catalog
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Killdozer Tapes Archive</title>
  <meta name="description" content="A searchable audio and transcript archive with synchronized playback, plain transcript pages, and direct text downloads.">
  <link rel="stylesheet" href="styles.css">
  <script type="application/ld+json">{json_ld_text}</script>
</head>
<body>
  <a class="skip-link" href="#transcript">Skip to transcript</a>
  <main id="app" class="archive-shell" data-ready="false">
    <section class="mast">
      <div>
        <p class="eyebrow">Audio transcript archive</p>
        <h1>Killdozer Tapes</h1>
        <p class="mast-copy">A structured public index of the recordings, synchronized transcripts, plain text files, caption files, and QA notes.</p>
        <p class="mast-copy provenance-callout"><strong>Transcript provenance:</strong> generated initially with Buzz/Whisper Large-v3, then edited through limited human review with Codex/ChatGPT assistance. The transcripts are useful research aids, not fully human-certified verbatim records.</p>
        <div class="resource-row mast-links">
          <a href="provenance.html">Process and authorship</a>
          <a href="Codex_Change_Report_2026-07-13.txt">Codex change report</a>
          <a href="Transcription_QA_Timestamp_Sample_Report.txt">QA timestamp report</a>
        </div>
      </div>
      <dl class="archive-stats" aria-label="Archive statistics">
        <div><dt>Recordings</dt><dd id="stat-recordings">{len(catalog)}</dd></div>
        <div><dt>Transcript words</dt><dd id="stat-words">0</dd></div>
        <div><dt>Total runtime</dt><dd id="stat-runtime">0:00</dd></div>
      </dl>
    </section>

    <section class="workbench" aria-label="Archive player and transcript">
      <aside class="rail">
        <div class="search-box">
          <label for="search">Search transcripts</label>
          <input id="search" type="search" autocomplete="off" placeholder="Search names, places, phrases">
        </div>
        <div id="recording-list" class="recording-list" aria-label="Recordings"></div>
      </aside>

      <section class="reader">
        <header class="reader-head">
          <div>
            <p class="eyebrow" id="active-kicker">Recording</p>
            <h2 id="active-title">Loading archive</h2>
            <p id="active-summary" class="muted">Preparing transcript index.</p>
          </div>
          <div class="resource-row" id="resource-links"></div>
        </header>

        <div class="player-panel">
          <audio id="player" controls preload="metadata"></audio>
          <div class="progress-line" aria-hidden="true"><span id="progress-fill"></span></div>
        </div>

        <div class="toolbar" aria-label="Transcript tools">
          <button id="jump-back" class="icon-button" title="Back 15 seconds" aria-label="Back 15 seconds">−15</button>
          <button id="jump-forward" class="icon-button" title="Forward 15 seconds" aria-label="Forward 15 seconds">+15</button>
          <button id="toggle-follow" class="tool-toggle" type="button" aria-pressed="true">Follow audio</button>
          <span id="match-count" class="muted"></span>
        </div>

        <article id="transcript" class="transcript" aria-live="polite"></article>
      </section>
    </section>

    <section class="bot-index" aria-label="Direct transcript index">
      <h2>Direct Transcript Pages</h2>
      <p>These pages contain the transcript text as server-readable HTML with timestamp anchors and source file links.</p>
      <ul>
{links}
      </ul>
    </section>

    <section class="bot-index" aria-label="Transcript provenance summary">
      <h2>Transcript Provenance</h2>
      <p>Initial transcript files were produced in Buzz using Whisper Large-v3. Later edits were made by Leonard Bogard with limited human ear-checking and Codex/ChatGPT-assisted review, cleanup, and report generation. Supporting files include original transcript backups, locally generated 44.1 kHz / 16-bit WAV transcodes that are intentionally not published because of file size, the Buzz conversion screenshot, QA notes, and the Codex change report.</p>
      <p><a href="provenance.html">Read the full process and authorship notes</a>.</p>
    </section>
  </main>
  <noscript>
    <main class="transcript-document">
      <h1>Killdozer Tapes Archive</h1>
      <p>JavaScript is required for synchronized playback. Direct transcript pages are available below.</p>
      <ul>
{links}
      </ul>
    </main>
  </noscript>
  <script src="app.js" defer></script>
</body>
</html>
"""


def render_provenance_page(catalog: list[dict]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    transcript_rows = "\n".join(
        f"<tr><td>{html.escape(item['label'])}</td><td><a href=\"{item['txtUrl']}\">TXT</a></td><td><a href=\"{item['vttUrl']}\">VTT</a></td><td><a href=\"{item['srtUrl']}\">SRT</a></td><td><a href=\"Original%20Transcriptions%20Backup/{page_url(item['txt'])}\">backup TXT</a></td></tr>"
        for item in catalog
    )
    file_manifest = [
        ("Buzz conversion screenshot", "Buzz conversion screenshot.png", "Screenshot retained as evidence of the Buzz conversion workflow."),
        ("QA timestamp report", "Transcription_QA_Timestamp_Sample_Report.txt", "Timestamped list of suspected Whisper/Buzz transcript issues, resolved items, and sample positions."),
        ("Codex change report", "Codex_Change_Report_2026-07-13.txt", "Best-effort report of Codex-assisted replacements and review recommendations."),
        ("Original transcription backups", "Original Transcriptions Backup/", "Backup copies of earlier transcript files before later cleanup passes."),
        ("44.1 kHz / 16-bit WAV transcodes", "Not published in repository", "WAV transcodes were generated for local waveform review and sample-count referencing, but are intentionally omitted from the public GitHub Pages repository because of file size."),
        ("Machine catalog", "data/catalog.json", "Machine-readable SPA catalog with transcript text, cue timing, and provenance metadata."),
        ("LLM guidance", "llms.txt", "Plain text guidance for AI assistants and scrapers."),
    ]
    manifest_rows = "\n".join(
        f"<tr><td>{html.escape(label)}</td><td>{render_manifest_path(path)}</td><td>{html.escape(note)}</td></tr>"
        for label, path, note in file_manifest
    )
    json_ld = {
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": "Killdozer Tapes Transcript Provenance",
        "dateModified": generated_at,
        "about": "Transcript origin, machine transcription credit, human-assisted editing notes, backups, QA reports, and supporting artifacts.",
    }
    json_ld_text = json.dumps(json_ld, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Killdozer Tapes - Transcript Provenance</title>
  <meta name="description" content="Authorship, process, and transparency notes for the Buzz/Whisper transcripts and later human-assisted Codex/ChatGPT edits.">
  <link rel="stylesheet" href="styles.css">
  <script type="application/ld+json">{json_ld_text}</script>
</head>
<body class="transcript-page">
  <main class="transcript-document provenance-document">
    <nav class="crumbs"><a href="index.html">Archive index</a></nav>
    <header>
      <p class="eyebrow">Process and authorship</p>
      <h1>Transcript Provenance</h1>
      <p class="lede">This archive should not imply that the transcripts were authored from scratch by a human. The initial transcript creation is credited to Buzz using Whisper Large-v3. Later work was limited human review, correction, formatting, and Codex/ChatGPT-assisted cleanup.</p>
    </header>

    <section>
      <h2>Short Attribution Statement</h2>
      <p><strong>Initial transcription:</strong> Buzz / Whisper Large-v3.</p>
      <p><strong>Later editing and publication preparation:</strong> Leonard Bogard, with Codex/ChatGPT assistance.</p>
      <p><strong>Status:</strong> partially reviewed and corrected, but not fully human-certified as a verbatim transcript.</p>
    </section>

    <section>
      <h2>Process Summary</h2>
      <ol>
        <li>Source MP3 recordings were gathered for seven tape sides. Tape 1 Side B also has a fast-forward-corrected audio file that is used as the primary web playback source.</li>
        <li>Audio was transcoded locally to 44.1 kHz / 16-bit WAV files for waveform review and sample-count references. Those generated WAV files are documented in the machine catalog but intentionally not published in this GitHub repository because of file size.</li>
        <li>Initial transcript outputs were generated with Buzz using Whisper Large-v3, producing TXT, SRT, and VTT transcript files.</li>
        <li>Original transcript copies were preserved in <a href="Original%20Transcriptions%20Backup/">Original Transcriptions Backup/</a> before later correction passes.</li>
        <li>A first QA pass identified obvious Whisper/Buzz failure modes, including prompt leaks, hallucinated text, mojibake/non-English garbage, duplicate captions, overrun after audio ended, and suspicious names or terms.</li>
        <li>Some segments were manually ear-checked in audio tools such as GoldWave or Audacity. The QA report records timestamp ranges, sample counts, and resolution notes where available.</li>
        <li>Codex/ChatGPT was used as an editing assistant for limited cleanup, consistency checks, report generation, and archive-site generation. The Codex change report lists later replacement-style edits and explicitly marks several as questionable without ear-checking.</li>
        <li>The present web archive was generated from the current edited transcript files. It exposes synchronized transcript cues, plain transcript pages, original text/caption files, reports, and machine-readable metadata.</li>
      </ol>
    </section>

    <section>
      <h2>Known Machine Transcription Issues</h2>
      <p>The QA report documents several common automatic speech recognition problems found in this set: prompt leakage from the instruction phrase "Transcribe verbatim.", hallucinated text during silence or noisy sections, mojibake/corrupted non-English output, repeated captions, and uncertain proper names. Resolved items are marked in the QA report where they were checked or corrected.</p>
      <p>Some later Codex-assisted edits normalized spelling, names, punctuation, or likely terms. The change report intentionally flags edits that may need ear-checking before being treated as final.</p>
      <p>A remaining example of this uncertainty is visible near the end of Tape 4 Side A, where the current transcript still contains a bracketed <code>[Whisper: ...]</code> phrase. That artifact is preserved because it exists in the current source transcript files; it should not be treated as independently verified speech without checking the audio.</p>
    </section>

    <section>
      <h2>Supporting Artifacts</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Artifact</th><th>Path</th><th>Purpose</th></tr></thead>
          <tbody>{manifest_rows}</tbody>
        </table>
      </div>
      <figure class="evidence-figure">
        <img src="Buzz%20conversion%20screenshot.png" alt="Buzz conversion screenshot">
        <figcaption>Screenshot retained with the archive as conversion-process evidence.</figcaption>
      </figure>
    </section>

    <section>
      <h2>Transcript File Map</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Recording</th><th>Plain text</th><th>VTT captions</th><th>SRT captions</th><th>Backup</th></tr></thead>
          <tbody>{transcript_rows}</tbody>
        </table>
      </div>
    </section>

    <section>
      <h2>Recommended Citation Note</h2>
      <p>When quoting or relying on the transcript, cite the tape side and timestamp, and preferably verify the quoted passage against the audio. A fair attribution is: "Transcript initially generated with Buzz/Whisper Large-v3 and later lightly corrected by Leonard Bogard with Codex/ChatGPT assistance."</p>
    </section>

    <section>
      <h2>Machine-Readable Access</h2>
      <p>AI assistants, crawlers, and scrapers can read <a href="data/catalog.json">data/catalog.json</a>, <a href="llms.txt">llms.txt</a>, and the standalone transcript pages under <a href="transcripts/">transcripts/</a>. Those surfaces include provenance language so downstream users can see that the transcripts originated from automatic speech recognition.</p>
    </section>
  </main>
</body>
</html>
"""


def render_app_js() -> str:
    return r"""const state = {
  catalog: [],
  activeId: "",
  follow: true,
  query: "",
};

const els = {
  app: document.querySelector("#app"),
  list: document.querySelector("#recording-list"),
  search: document.querySelector("#search"),
  player: document.querySelector("#player"),
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
  const current = decodeURIComponent(els.player.getAttribute("data-src") || "");
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

const syncActiveCue = () => {
  const item = activeItem();
  if (!item || !els.player.duration) return;
  els.progress.style.width = `${Math.min(100, (els.player.currentTime / els.player.duration) * 100)}%`;
  const cues = [...els.transcript.querySelectorAll(".cue")];
  const active = cues.find((cue) => {
    const start = Number(cue.dataset.start);
    const end = Number(cue.dataset.end);
    return els.player.currentTime >= start && els.player.currentTime <= end;
  });
  cues.forEach((cue) => cue.classList.toggle("active", cue === active));
  if (active && state.follow) active.scrollIntoView({ block: "center", behavior: "smooth" });
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
  render();
});

els.follow.addEventListener("click", () => {
  state.follow = !state.follow;
  els.follow.setAttribute("aria-pressed", String(state.follow));
  els.follow.textContent = state.follow ? "Follow audio" : "Free scroll";
});

els.back.addEventListener("click", () => {
  els.player.currentTime = Math.max(0, els.player.currentTime - 15);
});

els.forward.addEventListener("click", () => {
  els.player.currentTime = Math.min(els.player.duration || Infinity, els.player.currentTime + 15);
});

els.player.addEventListener("timeupdate", syncActiveCue);
window.addEventListener("hashchange", () => {
  const id = cleanHash();
  if (id && id !== state.activeId) setActive(id, getHashTime());
});

boot().catch((error) => {
  els.title.textContent = "Archive could not load";
  els.summary.textContent = error.message;
});
"""


def render_css() -> str:
    return r""":root {
  color-scheme: light;
  --ink: #181a1f;
  --muted: #626b78;
  --line: #d8dde5;
  --paper: #f7f5ef;
  --panel: #ffffff;
  --accent: #0f6b68;
  --accent-2: #8f3f28;
  --mark: #f5d36c;
  --shadow: 0 18px 55px rgba(26, 31, 39, 0.12);
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.5;
}

a {
  color: var(--accent);
  text-decoration-thickness: 0.08em;
  text-underline-offset: 0.16em;
}

button,
input {
  font: inherit;
}

.skip-link {
  left: 1rem;
  position: absolute;
  top: -4rem;
}

.skip-link:focus {
  top: 1rem;
  z-index: 10;
}

.archive-shell {
  min-height: 100vh;
}

.mast {
  align-items: end;
  background: linear-gradient(180deg, #fffaf0 0%, #ece8dc 100%);
  border-bottom: 1px solid var(--line);
  display: grid;
  gap: 2rem;
  grid-template-columns: minmax(0, 1fr) auto;
  padding: 3rem clamp(1rem, 4vw, 4rem) 2rem;
}

.eyebrow {
  color: var(--accent-2);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0;
  margin: 0 0 0.45rem;
  text-transform: uppercase;
}

h1,
h2 {
  letter-spacing: 0;
  line-height: 1.05;
  margin: 0;
}

h1 {
  font-size: clamp(2.4rem, 7vw, 5.8rem);
}

h2 {
  font-size: 1.6rem;
}

.mast-copy,
.lede {
  color: var(--muted);
  font-size: 1.02rem;
  max-width: 62rem;
}

.provenance-callout {
  border-left: 4px solid var(--accent-2);
  color: var(--ink);
  margin-top: 1rem;
  padding-left: 1rem;
}

.mast-links {
  margin-top: 1rem;
}

.archive-stats {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(3, minmax(7rem, 1fr));
  margin: 0;
}

.archive-stats div {
  border-left: 3px solid var(--accent);
  padding-left: 0.8rem;
}

.archive-stats dt {
  color: var(--muted);
  font-size: 0.8rem;
}

.archive-stats dd {
  font-size: 1.55rem;
  font-weight: 800;
  margin: 0;
}

.workbench {
  display: grid;
  grid-template-columns: minmax(18rem, 23rem) minmax(0, 1fr);
  min-height: 72vh;
}

.rail {
  background: #23272f;
  color: #f4f0e8;
  padding: 1rem;
}

.search-box {
  margin-bottom: 1rem;
}

.search-box label {
  display: block;
  font-size: 0.8rem;
  font-weight: 800;
  margin-bottom: 0.4rem;
}

.search-box input {
  background: #ffffff;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--ink);
  min-height: 2.75rem;
  padding: 0.7rem 0.8rem;
  width: 100%;
}

.recording-list {
  display: grid;
  gap: 0.55rem;
}

.recording-card {
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 7px;
  color: inherit;
  cursor: pointer;
  min-height: 4.2rem;
  padding: 0.75rem;
  text-align: left;
  width: 100%;
}

.recording-card.active,
.recording-card:focus-visible {
  background: #fff;
  color: var(--ink);
  outline: 2px solid var(--mark);
  outline-offset: 2px;
}

.recording-title,
.recording-meta {
  display: block;
}

.recording-title {
  font-weight: 800;
}

.recording-meta {
  color: currentColor;
  font-size: 0.82rem;
  opacity: 0.74;
}

.reader {
  display: grid;
  grid-template-rows: auto auto auto minmax(0, 1fr);
  min-width: 0;
}

.reader-head {
  align-items: start;
  background: var(--panel);
  border-bottom: 1px solid var(--line);
  display: grid;
  gap: 1rem;
  grid-template-columns: minmax(0, 1fr) auto;
  padding: 1.3rem clamp(1rem, 3vw, 2rem);
}

.muted {
  color: var(--muted);
}

.resource-row {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.resource-row a {
  background: #edf4f3;
  border: 1px solid #c7dcda;
  border-radius: 999px;
  color: #063f3d;
  font-size: 0.86rem;
  font-weight: 800;
  padding: 0.42rem 0.7rem;
  text-decoration: none;
}

.unpublished-resource,
.unpublished-artifact {
  color: var(--muted);
  font-size: 0.86rem;
}

.unpublished-resource {
  background: #f4f1ed;
  border: 1px dashed #cfc6ba;
  border-radius: 999px;
  display: inline-flex;
  font-weight: 800;
  padding: 0.42rem 0.7rem;
}

.player-panel {
  background: #101317;
  padding: 1rem clamp(1rem, 3vw, 2rem);
}

audio {
  display: block;
  width: 100%;
}

.progress-line {
  background: rgba(255, 255, 255, 0.16);
  height: 0.3rem;
  margin-top: 0.8rem;
  overflow: hidden;
}

#progress-fill {
  background: var(--mark);
  display: block;
  height: 100%;
  width: 0;
}

.toolbar {
  align-items: center;
  background: #fbfaf7;
  border-bottom: 1px solid var(--line);
  display: flex;
  gap: 0.55rem;
  min-height: 3.6rem;
  padding: 0.65rem clamp(1rem, 3vw, 2rem);
}

.icon-button,
.tool-toggle {
  border: 1px solid var(--line);
  border-radius: 6px;
  cursor: pointer;
  min-height: 2.35rem;
  padding: 0.45rem 0.7rem;
}

.icon-button {
  aspect-ratio: 1.45 / 1;
  background: var(--panel);
  font-weight: 800;
}

.tool-toggle {
  background: #eaf2f1;
  color: #063f3d;
  font-weight: 800;
}

.tool-toggle[aria-pressed="false"] {
  background: #f4ece8;
  color: #6d2b1d;
}

.transcript {
  background: var(--panel);
  overflow: auto;
  padding: 1rem clamp(1rem, 3vw, 2rem) 4rem;
}

.cue {
  border-left: 3px solid transparent;
  display: grid;
  gap: 1rem;
  grid-template-columns: 4.5rem minmax(0, 1fr);
  margin: 0;
  padding: 0.65rem 0.4rem;
}

.cue + .cue {
  border-top: 1px solid #eceff3;
}

.cue.active {
  background: #fff8df;
  border-left-color: var(--accent-2);
}

.cue-time {
  background: transparent;
  border: 0;
  color: var(--accent);
  cursor: pointer;
  font-variant-numeric: tabular-nums;
  font-weight: 800;
  padding: 0;
  text-align: left;
}

mark {
  background: var(--mark);
  color: inherit;
  padding: 0 0.08em;
}

.bot-index,
.transcript-document {
  margin: 0 auto;
  max-width: 72rem;
  padding: 2rem clamp(1rem, 4vw, 4rem);
}

.bot-index {
  border-top: 1px solid var(--line);
}

.bot-index ul {
  columns: 2;
  padding-left: 1.2rem;
}

.transcript-page {
  background: #fffdf8;
}

.transcript-document {
  background: var(--panel);
  min-height: 100vh;
}

.crumbs {
  margin-bottom: 2rem;
}

.crawler-transcript {
  border-top: 1px solid var(--line);
  margin-top: 1.5rem;
  padding-top: 1rem;
}

.provenance-note {
  background: #fff8df;
  border: 1px solid #ead592;
  border-radius: 7px;
  margin: 1rem 0;
  padding: 0.9rem 1rem;
}

.crawler-transcript p {
  margin: 0;
  padding: 0.55rem 0;
}

.crawler-transcript p + p {
  border-top: 1px solid #edf0f4;
}

.time {
  font-weight: 800;
  margin-right: 0.65rem;
}

.provenance-document section {
  border-top: 1px solid var(--line);
  margin-top: 2rem;
  padding-top: 1.4rem;
}

.provenance-document h2 {
  font-size: 1.35rem;
  margin-bottom: 0.8rem;
}

.provenance-document ol {
  padding-left: 1.35rem;
}

.provenance-document li + li {
  margin-top: 0.55rem;
}

.table-wrap {
  overflow-x: auto;
}

table {
  border-collapse: collapse;
  min-width: 46rem;
  width: 100%;
}

th,
td {
  border-bottom: 1px solid var(--line);
  padding: 0.65rem 0.7rem;
  text-align: left;
  vertical-align: top;
}

th {
  background: #f1eee6;
  font-size: 0.86rem;
}

.evidence-figure {
  margin: 1.5rem 0 0;
}

.evidence-figure img {
  border: 1px solid var(--line);
  display: block;
  height: auto;
  max-width: 100%;
}

.evidence-figure figcaption {
  color: var(--muted);
  font-size: 0.9rem;
  margin-top: 0.45rem;
}

@media (max-width: 900px) {
  .mast,
  .workbench,
  .reader-head {
    grid-template-columns: 1fr;
  }

  .archive-stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .rail {
    position: static;
  }

  .recording-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .mast {
    padding-top: 2rem;
  }

  .archive-stats,
  .recording-list,
  .cue {
    grid-template-columns: 1fr;
  }

  .bot-index ul {
    columns: 1;
  }

  .resource-row a,
  .unpublished-resource {
    flex: 1 1 auto;
    text-align: center;
  }
}
"""


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    catalog = build_catalog()
    (DATA_DIR / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "index.html").write_text(render_index(catalog), encoding="utf-8")
    (ROOT / "provenance.html").write_text(render_provenance_page(catalog), encoding="utf-8")
    (ROOT / "app.js").write_text(render_app_js(), encoding="utf-8")
    (ROOT / "styles.css").write_text(render_css(), encoding="utf-8")
    for item in catalog:
        (TRANSCRIPT_DIR / f"{item['id']}.html").write_text(render_transcript_page(item), encoding="utf-8")
    sitemap_entries = ["index.html", "provenance.html", *[item["transcriptPage"] for item in catalog]]
    (ROOT / "sitemap.xml").write_text(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        + "\n".join(f"  <url><loc>{html.escape(page_url(entry))}</loc></url>" for entry in sitemap_entries)
        + "\n</urlset>\n",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: sitemap.xml\n", encoding="utf-8")
    (ROOT / "llms.txt").write_text(
        "# Killdozer Tapes Archive\n\n"
        "Transcript provenance and authorship:\n"
        "- Initial transcription was generated with Buzz using Whisper Large-v3.\n"
        "- Later editing was performed by Leonard Bogard with limited human ear-checking and Codex/ChatGPT-assisted cleanup.\n"
        "- The transcripts are partially reviewed research aids, not fully human-certified verbatim transcripts.\n"
        "- See provenance.html, Codex_Change_Report_2026-07-13.txt, and Transcription_QA_Timestamp_Sample_Report.txt before treating the text as authoritative.\n\n"
        "This archive exposes synchronized audio transcripts in several forms:\n"
        "- Human SPA: index.html\n"
        "- Process and authorship notes: provenance.html\n"
        "- Machine catalog: data/catalog.json\n"
        "- Crawlable transcript pages: transcripts/*.html\n"
        "- Original transcript text/caption files: TXT, VTT, and SRT files in the archive root\n\n"
        "Supporting evidence retained with the archive includes Original Transcriptions Backup/, locally generated 44.1 kHz / 16-bit WAV transcodes that are intentionally not published because of file size, Buzz conversion screenshot.png, and QA/change reports.\n"
        "Prefer timestamped VTT/SRT cues when citing exact locations, and verify quotations against the audio when accuracy matters.\n",
        encoding="utf-8",
    )
    print(f"Generated {len(catalog)} recordings at {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
