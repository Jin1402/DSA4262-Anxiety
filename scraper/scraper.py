import requests
import time
import pandas as pd
from tqdm import tqdm

# ==========================
# CONFIG
# ==========================

SUBREDDITS = [
    "jobs",
    "cscareerquestions",
    "recruitinghell",
    "careerguidance",
    "nus",
    "NTU"
]

# University / early-career stage markers
UNIVERSITY_STAGE_KEYWORDS = [
    "internship",
    "intern",
    "fresh grad",
    "new grad",
    "recent grad",
    "undergrad",
    "final year",
    "y3",
    "y4",
    "gpa",
    "cap",
    "campus recruiting",
    "career fair",
    "return offer"
]

TARGET_POSTS = 1500
OUTPUT_FILE = "reddit_job_posts_stage_filtered.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (StudentResearchBot/1.0)"
}

BASE_URL = "https://www.reddit.com"

posts_collected = []
seen_ids = set()

# ==========================
# HELPER FUNCTIONS
# ==========================

def contains_keyword(text, keyword_list):
    text = text.lower()
    return any(k in text for k in keyword_list)

def word_count(text):
    return len(text.split())

def fetch(url, params):
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)

        if r.status_code == 429:
            print("Rate limited. Sleeping 10 seconds...")
            time.sleep(10)
            return None

        r.raise_for_status()
        return r.json()

    except:
        return None


# ==========================
# MAIN COLLECTION
# ==========================

pbar = tqdm(total=TARGET_POSTS, desc="Collecting Posts")

for subreddit in SUBREDDITS:

    for sort_type in ["new", "top"]:

        after = None

        while len(posts_collected) < TARGET_POSTS:

            url = f"{BASE_URL}/r/{subreddit}/{sort_type}.json"

            params = {
                "limit": 100,
                "after": after,
                "t": "year"
            }

            data = fetch(url, params)

            if not data:
                break

            posts = data["data"]["children"]

            if not posts:
                break

            for post in posts:

                pdata = post["data"]
                post_id = pdata["id"]

                if post_id in seen_ids:
                    continue

                title = pdata.get("title", "")
                selftext = pdata.get("selftext", "")

                full_text = f"{title} {selftext}".strip()

                # Skip empty / deleted
                if len(selftext.strip()) < 20:
                    continue

                # Word count filter (remove very short posts)
                if word_count(full_text) < 80:
                    continue

                # University stage filter
                if not contains_keyword(full_text, UNIVERSITY_STAGE_KEYWORDS):
                    continue

                posts_collected.append({
                    "id": post_id,
                    "subreddit": subreddit,
                    "title": title,
                    "selftext": selftext,
                    "num_comments": pdata.get("num_comments", 0),
                    "score": pdata.get("score", 0)
                })

                seen_ids.add(post_id)
                pbar.update(1)

                if len(posts_collected) >= TARGET_POSTS:
                    break

            after = data["data"].get("after")

            if after is None:
                break

            time.sleep(2)

        if len(posts_collected) >= TARGET_POSTS:
            break

    if len(posts_collected) >= TARGET_POSTS:
        break

    print(f"Finished subreddit: {subreddit}. Sleeping 20 seconds...")
    time.sleep(20)

pbar.close()

# ==========================
# SAVE
# ==========================

df = pd.DataFrame(posts_collected)
df.to_csv(OUTPUT_FILE, index=False)

print("\nDone.")
print("Posts collected:", len(posts_collected))