# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
**My domain is UC Berkeley campus dining and food experiences, including dining halls, on-campus eateries, nearby restaurants, and student food resources. This knowledge is difficult to find in one place because official university websites provide basic information, but students often rely on scattered reviews, Reddit discussions, Yelp ratings, and personal recommendations to learn which options are actually affordable, convenient, and worth visiting. An unofficial guide can bring together these diverse perspectives to help students make informed dining choices.**
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or Location |
|---|--------|-------------|-----------------|
| 1 | Berkeleyside - Nosh Article "Freshmen Food Guide" | One of the most-read food guides for Berkeley newcomers. | [https://www.berkeleyside.org/2025/08/26/where-to-eat-if-you-are-new-to-berkeley](https://www.berkeleyside.org/2025/08/26/where-to-eat-if-you-are-new-to-berkeley) |
| 2 | UC Berkeley Dining Locations | Directory of dining halls, cafes, markets, and restaurants operated by Berkeley Dining. | [https://dining.berkeley.edu/locations](https://dining.berkeley.edu/locations) |
| 3 | Berkeley Life: Dining at UC Berkeley | Student-focused guide introducing dining options and food resources on campus. | [https://life.berkeley.edu/dining-at-uc-berkeley-where-to-eat](https://life.berkeley.edu/dining-at-uc-berkeley-where-to-eat) |
| 4 | UC Berkeley Foodscape Map | Interactive map of food resources, groceries, food pantries, and dining locations near campus. | [https://food.berkeley.edu/foodscape-map](https://food.berkeley.edu/foodscape-map) |
| 5 | r/berkeley (Reddit) | Student discussions, reviews, recommendations, and opinions about dining options around Berkeley. | https://www.reddit.com/r/berkeley |
| 6 | @tasteofberkeley | Instagram account featuring Berkeley food recommendations. | [https://www.reddit.com/r/CalDiningHall](https://www.instagram.com/tasteofberkeley/) |
| 7 | Yelp Berkeley Restaurants | User reviews and ratings of restaurants, cafes, and food spots near UC Berkeley. | [https://www.yelp.com/search?find_desc=Restaurants&find_loc=Berkeley%2C+CA](https://www.yelp.com/search?find_desc=Restaurants&find_loc=Berkeley%2C+CA) |
| 8 | Google Maps Restaurant Reviews | Reviews, ratings, photos, and location information for restaurants around campus. | [https://www.google.com/maps/search/restaurants+berkeley+ca](https://www.google.com/maps/search/restaurants+berkeley+ca) |
| 9 | Berkeley Student Food Collective | Student-run grocery store and food resource promoting affordable and sustainable food options. | [https://berkeleystudentfoodcollective.org](https://berkeleystudentfoodcollective.org) |
| 10 | The Daily Californian – Food & Drink Section | Student newspaper articles covering restaurant reviews, food trends, and dining news. | [https://www.dailycal.org/category/arts-life/food-drink](https://www.dailycal.org/category/arts-life/food-drink) |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
