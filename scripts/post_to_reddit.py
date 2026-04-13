import os
from pathlib import Path
import praw

FLAIR_ID_MAP = {
    "major": "e3d63234-5dc6-11f0-b36f-0a5798591b21",
    "minor": "0bc44ae2-5dc7-11f0-8a26-9685ac3bddf0",
}


def main():
    raw_tag = os.environ["COMMIT_TAG"].lstrip("vV")
    version = Path("scripts/version.txt").read_text().strip()
    changelog = os.environ["RELEASE_NOTES"]

    try:
        major, minor, patch = (int(x) for x in raw_tag.split(".")[:3])
    except ValueError:
        print(f"⚠️ Could not parse version tag '{raw_tag}', skipping Reddit post.")
        return

    if patch != 0:
        print(f"⚠️ Patch release '{raw_tag}', skipping Reddit post.")
        return

    release_type = "major" if minor == 0 else "minor"
    flair_id = FLAIR_ID_MAP.get(release_type)
    if not flair_id:
        print(f"⚠️ No flair configured for release type '{release_type}', skipping Reddit post.")
        return

    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        username=os.environ["REDDIT_USERNAME"],
        password=os.environ["REDDIT_PASSWORD"],
        user_agent="LenoreAppsBot/1.0 by u/LenoreReleaseBot",
    )

    title = f"LenoreChore v{version} Released!"
    body_template = Path("scripts/reddit_post_template.md").read_text()
    body = body_template.format(version=version, changelog=changelog)

    submission = reddit.subreddit("LenoreApps").submit(
        title=title, selftext=body, flair_id=flair_id
    )

    print(f"✅ Posted to Reddit: {submission.shortlink}")


if __name__ == "__main__":
    main()
