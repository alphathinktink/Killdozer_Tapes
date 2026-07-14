# Killdozer Tapes Archive

This repository is a public archive of the Killdozer tape recordings, transcripts, caption files, provenance notes, QA reports, and related analysis material.

The goal of the archive is to make the recordings easier to inspect, cite, search, and verify without presenting machine-generated transcripts as unquestioned primary text. The audio remains the source of record. The transcripts, synchronized cue files, and analysis pages are research aids.

## Intentions

- Preserve the available tape-side audio files and associated transcript outputs in a structured repository.
- Provide a readable static archive site with synchronized audio playback, searchable transcript text, direct transcript pages, and machine-readable metadata.
- Keep transcription provenance visible so readers understand what was machine-generated, what was edited, and what still needs caution.
- Support careful citation by making tape-side labels, timestamps, TXT files, SRT/VTT captions, and QA notes available together.
- Separate primary archive materials from interpretive reports so downstream readers do not confuse analysis with transcript evidence.

## Methodologies

Initial transcript files were generated with Buzz using Whisper Large-v3. Those outputs produced TXT, SRT, and VTT files for the seven tape sides.

Later work included limited human ear-checking, correction of obvious automatic speech recognition failures, and Codex/ChatGPT-assisted cleanup, report generation, consistency checks, and static-site generation. The archive preserves original transcript backups where available so later edits can be compared against earlier machine outputs.

The QA process focused on known failure modes in automatic transcription, including prompt leakage, hallucinated text during silence or noisy passages, corrupted characters, duplicate captions, suspect names, and timing overrun after audio ended. Timestamp and sample-count notes are recorded in `Transcription_QA_Timestamp_Sample_Report.txt`.

The static archive is generated from the current transcript files and exposes:

- `index.html` for the main searchable audio/transcript interface.
- `transcripts/*.html` for crawlable standalone transcript pages.
- `data/catalog.json` for machine-readable transcript, cue, and provenance metadata.
- Original TXT, SRT, and VTT transcript files in the repository root.
- `provenance.html` for process and authorship notes.
- `Original Transcriptions Backup/` for retained earlier transcript outputs.
- `analysis/` for separate Codex/ChatGPT-generated interpretive reports.

The `analysis/` pages are not transcripts, not primary sources, and not part of the core transcript corpus. They summarize and organize transcript content as interpretive aids. When quoting or relying on the tapes, cite the tape side and timestamp, and verify against the audio when accuracy matters.

## Authors and Credits

- Archive editing, publication preparation, and repository authorship: `alphathinktink`.
- Initial machine transcription: Buzz using Whisper Large-v3.
- Assisted cleanup, analysis generation, and archive-site generation: Codex/ChatGPT, directed and reviewed by `alphathinktink`.

## Verification Status

The transcripts are partially reviewed and corrected, but they are not fully human-certified verbatim records. Treat uncertain passages, names, and bracketed machine-transcription artifacts as prompts for audio verification.

For the fullest process notes, see `provenance.html`, `Codex_Change_Report_2026-07-13.txt`, and `Transcription_QA_Timestamp_Sample_Report.txt`.
