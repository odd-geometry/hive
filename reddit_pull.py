"""
Reddit Research Pipeline — read-only data collector

Purpose
-------
Pulls public posts and comments from a fixed list of computational-design-
related subreddits using Reddit's official Data API (read-only scope).

This script has NO write access. It does not post, comment, vote, or
message. It only reads public content for research purposes: identifying
recurring questions and pain points in parametric/computational design,
Grasshopper, Rhino, CAD, and 3D printing communities, to inform tutorials,
blog topics, and (optionally) manually-reviewed, manually-posted replies
from a human team member.

Setup
-----
1. Register a "script" type app at https://www.reddit.com/prefs/apps
2. Set the following environment variables (never commit these):
       REDDIT_CLIENT_ID
       REDDIT_CLIENT_SECRET
       REDDIT_USER_AGENT      e.g. "research-script:beegraphy-pipeline:v0.1 (by u/YOUR_USERNAME)"
3. pip install -r requirements.txt
4. python reddit_pull.py

Output
------
Writes a JSON file (reddit_pull_<timestamp>.json) containing post/comment
data from each target subreddit, ready for downstream scoring and
pain-point extraction steps (not included in this script).
"""

import os
import json
import sys
from datetime import datetime, timezone

try:
    import praw
except ImportError:
    sys.exit(
        "Missing dependency 'praw'. Install with: pip install -r requirements.txt"
    )

# ---- Config -----------------------------------------------------------

SUBREDDITS = [
    "grasshopper",
    "rhino",
    "3Dprinting",
    "CAD",
    "parametric_design",
]

POSTS_PER_SUBREDDIT = 25         # keep requests modest; respects rate limits
COMMENTS_PER_POST = 10           # top-level comments only, to limit volume
SORT = "new"                     # alternatives: "hot", "top", "new"


def get_reddit_client() -> "praw.Reddit":
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT")

    missing = [
        name
        for name, val in [
            ("REDDIT_CLIENT_ID", client_id),
            ("REDDIT_CLIENT_SECRET", client_secret),
            ("REDDIT_USER_AGENT", user_agent),
        ]
        if not val
    ]
    if missing:
        sys.exit(
            "Missing required environment variables: "
            + ", ".join(missing)
            + "\nSet these before running the script (see README.md)."
        )

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def pull_subreddit(reddit: "praw.Reddit", name: str) -> list[dict]:
    """Pull recent posts (and a handful of top comments each) from one subreddit."""
    results = []
    subreddit = reddit.subreddit(name)

    listing = {
        "new": subreddit.new,
        "hot": subreddit.hot,
        "top": subreddit.top,
    }[SORT]

    for submission in listing(limit=POSTS_PER_SUBREDDIT):
        submission.comments.replace_more(limit=0)  # drop "load more comments" stubs
        top_comments = [
            {
                "author": str(c.author) if c.author else "[deleted]",
                "body": c.body,
                "score": c.score,
            }
            for c in submission.comments[:COMMENTS_PER_POST]
        ]

        results.append(
            {
                "subreddit": name,
                "id": submission.id,
                "title": submission.title,
                "selftext": submission.selftext,
                "author": str(submission.author) if submission.author else "[deleted]",
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "url": f"https://reddit.com{submission.permalink}",
                "top_comments": top_comments,
            }
        )

    return results


def main():
    reddit = get_reddit_client()
    reddit.read_only = True  # enforce read-only; no write calls possible

    all_results = {}
    for sub in SUBREDDITS:
        print(f"Pulling r/{sub} ...")
        try:
            all_results[sub] = pull_subreddit(reddit, sub)
            print(f"  -> {len(all_results[sub])} posts collected")
        except Exception as e:
            print(f"  !! Failed to pull r/{sub}: {e}")
            all_results[sub] = []

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = f"reddit_pull_{timestamp}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    total = sum(len(v) for v in all_results.values())
    print(f"\nDone. {total} posts written to {out_path}")


if __name__ == "__main__":
    main()
