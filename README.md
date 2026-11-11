# alevelsociologytutor.com

Static Astro site for AQA A-level Sociology (7192) and AS (7191), deployed on Netlify. Built from the Economics site (economicsaleveltutor.com) with the `subject-revision-site` skill.

## Run locally
    npm install
    npm run dev        # http://localhost:4321
    npm run build      # writes dist/

## Deploy
Push to `main` of the linked GitHub repository; Netlify builds with `npm run build` and publishes `dist/`.
Set `CROPS=off` in Netlify's environment to replace every AQA crop with a link to AQA's site.

## Data
- `scripts/export.py --bank "<Question Bank folder>" --topics topics.json --config site.config.json [--images [--only <bundle>]]`
  reads the AQA Sociology question bank export (`data/index.js`, `data/img/*.js`) and writes `src/data/questions.json`, `papers.json`, `topics.json`, `spec.json`, `weighting.json`, and with `--images` the WebP crops under `public/img/<bundle>/`.
  `--only` rewrites the data files with a single paper: always follow it with the full run.
- The bank's `fmt` field gives the question type (Define, Brief explain, Outline, Outline and explain, Analyse, Methods in context, Essay). Each record also carries `area` (the paper/option block) and `item` (whether the part applies an Item); the Item is part of the question crop.
- `topics.json` (repo root) maps spec v1.2 bullets to the 59 site topics, grouped by paper and option (`GROUPS` in `src/lib/data.ts` sets badges, motifs and "where examined").
- `src/data/exams.json` (summer 2027 timetable) and `src/data/boundaries.json` (out of 240; AS out of 120) are AQA's figures.
- June 2016–2019 papers come from copies of AQA's originals (AQA no longer hosts them); the past-papers pages say so.

## Pages specific to Sociology
- `/mock/` builds AQA-shaped papers: A-level Papers 1 and 3 by section, Paper 2 by the two options taught, AS Papers 1 and 2; 90 seconds a mark.
- `/essays/` lists every 16-, 20- and 30-mark essay; self-marking uses the five AQA level bands (`LEVELS` in `src/scripts/player.js`).
- Question-type pages: definitions, brief explain, outline, outline and explain, analyse, Methods in Context, essays.
- `/practice/define/` drills the 2-mark AS define and brief-explain questions.
- Flashcards are key-term decks (`src/data/decks/*.json`, picked up by `src/lib/decks.ts`). Decks with `"checked": false` show a "being checked by our tutor" line.
- `src/data/tutors.json` holds Mark (photo `public/tutors/mark.webp`, fee £100 per hour, one Google review).

## Content that needs a tutor's check before launch
- The twelve key-term decks in `src/data/decks/`.
