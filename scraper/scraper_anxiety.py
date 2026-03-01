import requests
import time
import pandas as pd
from tqdm import tqdm

# ==========================
# CONFIG
# ==========================

SUBREDDITS = [
    "college",
    "nus",
    "NTU",
    "SGExams",
    "csMajors",
    "EngineeringStudents",
    "businessschool",
    "LawSchool",
    "MedicalSchool"
]

JOB_KEYWORDS = [
    "job", "internship", "interview",
    "resume", "offer", "application",
    "career", "hiring", "rejection",
    "cv", "recruiter"
]

ANXIETY_KEYWORDS = [
    "anxious", "anxiety", "stress", 
    "stressed", "overwhelmed", "panic",
    "burnout", "worried", "fear",
    "depressed", "nervous", 
    "restless", "overthink", "apprehensive",
    "fearful", "dread", "overwhelmed",
    "panicky", "helpless", "irritable",
    "insecure", "tense", "uneasy",
    "paranoid", "troubled", "worried"
]

TARGET_ANXIETY = 600
OUTPUT_FILE = "reddit_job_anxiety.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (StudentResearchBot/1.0)"
}

BASE_URL = "https://www.reddit.com"

anxiety_posts = []
seen_ids = set()

# ==========================
# HELPER
# ==========================

def contains_keyword(text, keyword_list):
    text = text.lower()
    return any(k in text for k in keyword_list)

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

pbar = tqdm(total=TARGET_ANXIETY, desc="Collecting Anxiety Posts")

for subreddit in SUBREDDITS:

    for sort_type in ["new", "top"]:

        after = None

        while len(anxiety_posts) < TARGET_ANXIETY:

            url = f"{BASE_URL}/r/{subreddit}/{sort_type}.json"

            params = {
                "limit": 100,
                "after": after,
                "t": "all"
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

                if len(selftext.strip()) < 20:
                    continue

                full_text = f"{title} {selftext}"

                # Must be job-related
                if not contains_keyword(full_text, JOB_KEYWORDS):
                    continue

                # Must contain anxiety keywords
                if not contains_keyword(full_text, ANXIETY_KEYWORDS):
                    continue

                anxiety_posts.append({
                    "subreddit": subreddit,
                    "title": title,
                    "selftext": selftext,
                    "label": 1
                })

                seen_ids.add(post_id)
                pbar.update(1)

                if len(anxiety_posts) >= TARGET_ANXIETY:
                    break

            after = data["data"].get("after")
            if after is None:
                break

            time.sleep(2)

        if len(anxiety_posts) >= TARGET_ANXIETY:
            break

    if len(anxiety_posts) >= TARGET_ANXIETY:
        break

    print(f"Finished subreddit: {subreddit}. Sleeping 20 seconds...")
    time.sleep(20) 

pbar.close()

# ==========================
# SAVE
# ==========================

df = pd.DataFrame(anxiety_posts)
df.to_csv(OUTPUT_FILE, index=False)

print("\nDone.")
print("Anxiety collected:", len(anxiety_posts))