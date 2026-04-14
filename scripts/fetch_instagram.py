#!/usr/bin/env python3
"""
Fetch first image from each post of @guestsixonetwo using Instagram's API.
Uses Chrome cookies for authentication. Saves images to images/instagram/
and generates data/instagram.json manifest.
"""

import json
import sys
import time
from pathlib import Path

import requests
from pycookiecheat import chrome_cookies

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = PROJECT_ROOT / "images" / "instagram"
DATA_FILE = PROJECT_ROOT / "data" / "instagram.json"
PROGRESS_FILE = PROJECT_ROOT / "data" / ".ig_progress.json"

PROFILE = "guestsixonetwo"
USER_ID = "30324303709"


def get_session():
    """Create a requests session with Chrome's Instagram cookies."""
    cookies = chrome_cookies("https://www.instagram.com")
    s = requests.Session()
    s.cookies.update(cookies)
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/131.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "X-IG-App-ID": "936619743392459",
        "Referer": f"https://www.instagram.com/{PROFILE}/",
    })
    return s


def load_progress():
    """Load saved progress if any."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"posts": [], "max_id": "", "page": 0, "done": False}


def save_progress(state):
    """Save progress to disk."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(state, f)


def fetch_all_posts(session):
    """Paginate through all posts and collect metadata."""
    state = load_progress()

    if state["done"]:
        print(f"Already collected {len(state['posts'])} posts. Delete {PROGRESS_FILE} to re-fetch.")
        return state["posts"]

    posts = state["posts"]
    max_id = state["max_id"]
    page = state["page"]
    has_more = True

    # Build a set of already-collected shortcodes
    seen = {p["code"] for p in posts}

    print(f"Resuming from page {page}, {len(posts)} posts collected so far")

    while has_more:
        url = f"https://www.instagram.com/api/v1/feed/user/{USER_ID}/?count=33"
        if max_id:
            url += f"&max_id={max_id}"

        try:
            resp = session.get(url, timeout=15)

            if resp.status_code == 429:
                print(f"  Rate limited at page {page}. Waiting 30s...")
                save_progress({"posts": posts, "max_id": max_id, "page": page, "done": False})
                time.sleep(30)
                continue

            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  Error at page {page}: {e}. Saving progress and retrying in 10s...")
            save_progress({"posts": posts, "max_id": max_id, "page": page, "done": False})
            time.sleep(10)
            continue

        items = data.get("items", [])
        for item in items:
            code = item.get("code")
            if not code or code in seen:
                continue

            # Get first image URL
            image_url = None
            if item.get("carousel_media"):
                first = item["carousel_media"][0]
                if first.get("image_versions2"):
                    image_url = first["image_versions2"]["candidates"][0]["url"]
            elif item.get("image_versions2"):
                image_url = item["image_versions2"]["candidates"][0]["url"]

            if not image_url:
                continue

            posts.append({
                "code": code,
                "url": image_url,
                "ts": item.get("taken_at", 0),
                "caption": (item.get("caption", {}) or {}).get("text", "")[:200],
            })
            seen.add(code)

        has_more = data.get("more_available", False)
        max_id = data.get("next_max_id", "")
        page += 1

        if page % 5 == 0:
            save_progress({"posts": posts, "max_id": max_id, "page": page, "done": False})
            print(f"  Page {page}: {len(posts)} posts collected")

        time.sleep(0.8)

    save_progress({"posts": posts, "max_id": max_id, "page": page, "done": True})
    print(f"Collection complete: {len(posts)} posts across {page} pages")
    return posts


def download_images(session, posts):
    """Download first image for each post."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    skipped = 0
    failed = 0

    for i, post in enumerate(posts):
        filename = f"{post['code']}.jpg"
        filepath = IMAGES_DIR / filename
        post["image"] = f"images/instagram/{filename}"

        if filepath.exists() and filepath.stat().st_size > 0:
            skipped += 1
            continue

        try:
            resp = session.get(post["url"], timeout=30)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(resp.content)
            downloaded += 1
        except Exception as e:
            print(f"  Failed [{i+1}] {post['code']}: {e}")
            failed += 1
            continue

        if (downloaded + skipped) % 50 == 0:
            print(f"  Progress: {downloaded} downloaded, {skipped} skipped, {failed} failed / {len(posts)} total")
            time.sleep(1)

    print(f"\nDownloads complete: {downloaded} new, {skipped} existing, {failed} failed")


def write_manifest(posts):
    """Write the JSON manifest for the frontend."""
    # Sort newest first
    posts.sort(key=lambda x: x.get("ts", 0), reverse=True)

    manifest_posts = []
    for p in posts:
        filepath = IMAGES_DIR / f"{p['code']}.jpg"
        if not filepath.exists():
            continue
        manifest_posts.append({
            "shortcode": p["code"],
            "image": f"images/instagram/{p['code']}.jpg",
            "caption": p.get("caption", ""),
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(p.get("ts", 0))),
        })

    manifest = {
        "profile": PROFILE,
        "total": len(manifest_posts),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "posts": manifest_posts,
    }

    with open(DATA_FILE, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest written: {DATA_FILE} ({len(manifest_posts)} posts)")


def main():
    print(f"=== Fetching @{PROFILE} ===\n")

    session = get_session()

    # Step 1: Collect all post metadata
    print("Step 1: Collecting posts from API...")
    posts = fetch_all_posts(session)

    # Step 2: Download images
    print(f"\nStep 2: Downloading {len(posts)} images...")
    download_images(session, posts)

    # Step 3: Write manifest
    print("\nStep 3: Writing manifest...")
    write_manifest(posts)

    print("\nAll done!")


if __name__ == "__main__":
    main()
