# Reddit Research Pipeline

A small, **read-only** data collector for computational-design research.

## What this does

Pulls public posts and top-level comments from a fixed list of subreddits
related to parametric/computational design, Grasshopper, Rhino, CAD, and
3D printing:

- r/grasshopper
- r/rhino
- r/3Dprinting
- r/CAD
- r/parametric_design

The data is used to identify recurring questions, frustrations, and unmet
needs in these communities, which inform:

- Tutorial and blog topic ideas
- Internal product/content planning
- Occasionally, a manually-written, manually-posted reply from a human
  team member to a thread where we can genuinely help — this script
  never posts, comments, votes, or interacts with Reddit in any way.

## What this does NOT do

- No posting, commenting, voting, or messaging
- No automated replies of any kind
- No access beyond the standard read-only Data API scope
- No high-frequency polling — intended to run a few times per week, well
  within Reddit's rate limits

## Setup

1. Register a **script**-type app at
   [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Set environment variables (do **not** commit these anywhere):

   ```bash
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   export REDDIT_USER_AGENT="research-script:beegraphy-pipeline:v0.1 (by u/your_username)"
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run:

   ```bash
   python reddit_pull.py
   ```

Output is written to a timestamped JSON file
(`reddit_pull_<timestamp>.json`) containing post/comment data for
downstream analysis (topic clustering, pain-point extraction — not part
of this script).

## Status

Early-stage prototype. Scoring, clustering, and content-idea generation
are planned as separate, later steps once raw collection is validated.
