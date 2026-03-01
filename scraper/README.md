# Reddit Job-Anxiety Dataset Collector

A streamlined toolset for scraping and labeling Reddit posts to study **job-related anxiety** among university students, with a specific focus on the **Singapore academic landscape**.

---

## 1. Research Objective
This pipeline constructs a "Silver Standard" balanced dataset for supervised NLP tasks:
* **Anxiety (Label 1):** Career-focused posts containing psychological distress markers.
* **Non-Anxiety (Label 0):** Neutral/informative career discussions (Control group).

---

## 2. Targeted Communities
We scrape specific subreddits to ensure a blend of local Singaporean context and disciplinary diversity.

| Category | Subreddits | Rationale |
| :--- | :--- | :--- |
| **Singapore Focus** | `r/nus`, `r/NTU`, `r/SGExams` | Captures local internship cycles and "Kiasu" culture stress. |
| **Major-Specific** | `r/csMajors`, `r/LawSchool`, etc. | Captures industry-specific anxiety (e.g., technical rounds). |
| **General** | `r/college` | Provides a high-volume baseline for student discourse. |

---

## 3. Data Collection Methodology

### Technical Implementation
The scripts utilize Reddit’s public `.json` endpoints, requiring **no API keys**. To ensure stability and bypass `429 Too Many Requests` errors, the following automated rate-limiting is implemented:
* **Request Interval:** 2-second cooldown between individual JSON fetches.
* **Subreddit Interval:** 20-second cooldown between subreddits to reset internal rate limits.
* **Dynamic Back-off:** Automatic 10-second sleep trigger if a rate limit is detected.

### Two-Stage Filtering Logic

1.  **Stage 1 (Relevance):** Posts must contain career-centric terms (*internship, interview, CV, recruiter*).
2.  **Stage 2 (Heuristic Labeling):**
    * **Anxiety:** Requires matches from an expanded 26-word distress lexicon (*burnout, panic, dread*).
    * **Non-Anxiety:** Strictly excludes these markers to maintain a clean control group.

### Balancing Strategy
* **Anxiety Scraper (`scrape_anxiety.py`):** Uses a **global target** (e.g., 600 posts) across all subreddits, as anxiety-specific content is naturally rarer and unevenly distributed.
* **Non-Anxiety Scraper (`scrape_nonanxiety.py`):** Enforces a **per-subreddit quota** to prevent high-traffic communities from introducing domain bias.


## 4. Usage

#### Installation
```bash
pip install requests pandas tqdm
```
#### Execution
```bash
# Collect anxiety-related posts
python scrape_anxiety.py

# Collect neutral job-related posts
python scrape_nonanxiety.py
```

## 5. Ethical Standards & Limitations
- **Privacy First**: No usernames, Profile IDs, or PII are stored. Only the `title` and `selftext` are collected.

- **Heuristic Noise**: Labeling is based on keyword presence; manual annotation is required to verify sentiment and filter out sarcasm or misclassifications.

- **API Constraints**: Public endpoints have lower historical depth than the official Reddit API; data is focused on recent and "Top" all-time posts.

- **Bias**: While subreddits are balanced, the dataset reflects the demographics of Reddit users, which may skew toward specific student profiles.
