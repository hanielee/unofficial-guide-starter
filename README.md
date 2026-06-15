# The Unofficial Guide: UC Berkeley Dining — Project 1 RAG System

> This is a fully-functional Retrieval-Augmented Generation (RAG) system that answers student questions about UC Berkeley dining, food resources, and nearby restaurants using local embeddings and LLM generation.

---

## Domain

UC Berkeley campus dining and food experiences, including dining halls, on-campus eateries, nearby restaurants, and student food resources. This knowledge is valuable because official university websites provide basic information, but students rely on scattered reviews, Reddit discussions, and personal recommendations to learn which dining options are actually affordable, convenient, and worth visiting. An unofficial guide consolidates these diverse perspectives into one searchable system.

---

## Document Sources

| # | Source | Type | URL |
|---|--------|------|-----|
| 1 | Berkeleyside - Freshmen Food Guide | Article | https://www.berkeleyside.org/2025/08/26/where-to-eat-if-you-are-new-to-berkeley |
| 2 | UC Berkeley Dining Locations | Directory | https://dining.berkeley.edu/locations |
| 3 | Berkeley Life: Dining at UC Berkeley | Guide | https://life.berkeley.edu/dining-at-uc-berkeley-where-to-eat |
| 4 | UC Berkeley Foodscape Map | Interactive Map | https://food.berkeley.edu/foodscape-map |
| 5 | UC Berkeley Basic Needs Center | Resource | https://basicneeds.berkeley.edu |

---

## Chunking Strategy

**Chunk size:** 2,000 characters

**Overlap:** 200 characters

**Why these choices fit your documents:** Most sources contain short sections focused on specific restaurants, dining halls, or recommendations. The 2000-character size preserves complete thoughts while staying under token limits. Overlap ensures context isn't lost when information spans chunk boundaries.

**Final chunk count:** 23 chunks from 5 documents

**Preprocessing:** Removed HTML tags, navigation menus, cookie banners, ads, footers, scripts, and boilerplate using BeautifulSoup. Cleaned HTML entities and normalized whitespace while preserving substantive content (restaurant names, addresses, descriptions, student recommendations).

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 (384-dimensional, from sentence-transformers)

**Why chosen:** Lightweight, runs locally with no API key or rate limits, sufficient accuracy for domain-specific restaurant/dining content, 384-dim embeddings balance quality and speed for 23-chunk corpus.

**Production tradeoff reflection:** A larger model like BGE-large-en would improve retrieval accuracy on informal student-generated content (Reddit, Yelp reviews), especially for sentiment and recommendation extraction. However, the tradeoff is increased latency and compute cost. For this system's corpus size and question types (factual location/resource queries), all-MiniLM is appropriate. At scale with user feedback, re-ranking or a domain-tuned model would be justified.

---

---

## Quick Start

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up your .env file with Groq API key
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (get free key at https://console.groq.com)
```

### Run CLI (test queries)
```bash
python3 generation.py
# Type 'test' to run 3 evaluation queries
# Type 'quit' to exit
```

### Run Web Interface (Gradio)
```bash
python3 app.py
# Opens at http://localhost:7860
```

---

**System prompt grounding instruction:**
```
"You are a helpful guide for UC Berkeley students about dining and food options on campus.
Answer questions based on the provided context from UC Berkeley dining resources.
Be specific and cite sources when relevant.
If the context doesn't contain enough information to answer, say so clearly.
Keep answers concise and focused."
```

**How source attribution is surfaced in the response:**
- Each retrieved chunk is prefixed with `[Source: {document_name}, Chunk {index}]`
- Chunks are presented in context-block format separated by `---`
- Web interface displays sources below the answer with:
  - Document name and chunk index
  - Distance score (semantic similarity, 0=identical, 1=opposite)
  - Content preview (first 150 characters)
- Distance score color coding (green <0.35, orange <0.5, red >0.5) provides visual feedback on retrieval confidence

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
