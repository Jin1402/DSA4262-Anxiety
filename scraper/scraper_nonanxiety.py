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

TARGET_PER_SUBREDDIT = 70
OUTPUT_FILE = "reddit_job_nonanxiety.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (StudentResearchBot/1.0)"
}

BASE_URL = "https://www.reddit.com"

nonanxiety_posts = []
seen_ids = set()

# Track per-subreddit counts
subreddit_counts = {sub: 0 for sub in SUBREDDITS}

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
            time.sleep(10)
            return None
        r.raise_for_status()
        return r.json()
    except:
        return None

# ==========================
# MAIN COLLECTION
# ==========================

total_target = TARGET_PER_SUBREDDIT * len(SUBREDDITS)
pbar = tqdm(total=total_target, desc="Collecting Non-Anxiety Posts")

for subreddit in SUBREDDITS:

    print(f"\nScraping r/{subreddit}")
    
    for sort_type in ["new", "top"]:

        after = None

        while subreddit_counts[subreddit] < TARGET_PER_SUBREDDIT:

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

                # Must NOT contain anxiety keywords
                if contains_keyword(full_text, ANXIETY_KEYWORDS):
                    continue

                # Add to dataset
                nonanxiety_posts.append({
                    "subreddit": subreddit,
                    "title": title,
                    "selftext": selftext,
                    "label": 0
                })

                subreddit_counts[subreddit] += 1
                seen_ids.add(post_id)
                pbar.update(1)

                if subreddit_counts[subreddit] >= TARGET_PER_SUBREDDIT:
                    break

            after = data["data"].get("after")
            if after is None:
                break

            time.sleep(2)

        if subreddit_counts[subreddit] >= TARGET_PER_SUBREDDIT:
            break

    print(f"Finished subreddit: {subreddit}. Sleeping 20 seconds...")
    time.sleep(20) 
    
pbar.close()

# ==========================
# SAVE
# ==========================

df = pd.DataFrame(nonanxiety_posts)
df.to_csv(OUTPUT_FILE, index=False)

print("\nDone.")
print("Total collected:", len(nonanxiety_posts))
print("Per-subreddit counts:")
print(subreddit_counts)