import requests
import os
import time
import sys
import json
import yt_dlp
import csv

# ------------------------- CONFIGURATION -------------------------
ZENODO_URL = "https://zenodo.org/api/deposit/depositions"
ZENODO_COLLECTION = "sarvamnaya-oral-tradition-archive"
CHANNEL_ID = "UC4wAYkt8_U1TJOfXkfpjAsw"
CREATOR_NAME = "Timalsina, Staneshwar"
ARCHIVE_CITATION = "Vimarsha Foundation. (2025). The Sarvāmnāya Oral Tradition Archive [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15188107"
ARCHIVE_DOI = "10.5281/zenodo.15188107"
DOWNLOAD_DIR = "downloaded_videos"
CSV_DB_PATH = "zenodo_registry.csv"
WAIT_BETWEEN_UPLOADS = 3

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ------------------------- CSV FUNCTIONS -------------------------

def initialize_csv():
    if not os.path.exists(CSV_DB_PATH):
        with open(CSV_DB_PATH, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["id", "youtube_id", "zenodo_id", "title", "doi", "zenodo_link", "youtube_link"])

def load_processed_youtube_ids():
    if not os.path.exists(CSV_DB_PATH):
        return set()
    with open(CSV_DB_PATH, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return set(row["youtube_id"] for row in reader)

def append_to_csv(youtube_id, zenodo_id, title, doi, youtube_link):
    with open(CSV_DB_PATH, mode='a', newline='', encoding='utf-8') as file:
        reader = csv.reader(open(CSV_DB_PATH))
        row_count = sum(1 for _ in reader) - 1  # Exclude header
        writer = csv.writer(file)
        zenodo_url = f"https://zenodo.org/record/{zenodo_id}"
        writer.writerow([row_count + 1, youtube_id, zenodo_id, title, doi, zenodo_url, youtube_link])

# ------------------------- YOUTUBE FUNCTIONS -------------------------
def get_channel_videos(channel_id, api_key):
    videos = []
    next_page_token = None

    while True:
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "maxResults": 50,
            "pageToken": next_page_token
        }
        response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
        if not response.ok:
            print(f"❌ Error fetching videos: {response.status_code} - {response.text}")
            break

        data = response.json()
        for item in data.get("items", []):
            if item["id"]["kind"] == "youtube#video":
                videos.append({
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "published_at": item["snippet"]["publishedAt"]
                })

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return videos

def get_video_details(video_id, api_key):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet",
        "id": video_id,
        "key": api_key
    }
    response = requests.get(url, params=params)
    if not response.ok:
        print(f"❌ Error fetching video details: {response.status_code}")
        return None

    items = response.json().get("items", [])
    if not items:
        return None

    snippet = items[0]["snippet"]
    return {
        "title": snippet["title"],
        "description": snippet["description"],
        "tags": snippet.get("tags", []),
        "published_at": snippet["publishedAt"],
        "url": f"https://www.youtube.com/watch?v={video_id}"
    }

# ------------------------- VIDEO DOWNLOAD -------------------------
def sanitize_filename(title):
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '.', '_')).rstrip()
    return safe_title[:100]

def download_video(video_url, video_title):
    safe_title = sanitize_filename(video_title)
    file_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")

    if os.path.exists(file_path):
        return file_path

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': os.path.join(DOWNLOAD_DIR, f'{safe_title}.%(ext)s'),
        'quiet': False,
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            return file_path
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

# ------------------------- ZENODO FUNCTIONS -------------------------
def build_metadata(video):
    metadata = {
        "title": video["title"],
        "upload_type": "presentation",
        "description": f"{video['description']}\n\nOriginal YouTube video: {video['url']}\n\nThis presentation is part of the Sarvāmnāya Oral Tradition Archive.\n{ARCHIVE_CITATION}",
        "creators": [{"name": CREATOR_NAME}],
        "access_right": "open",
        "license": "cc-by-4.0",
        "keywords": list(set([
            "sarvamnaya", "vimarsha-foundation", "sarvamnaya-oral-tradition-archive"
        ] + video.get("tags", []))),
        "publication_date": video["published_at"][:10],
        "communities": [{"identifier": ZENODO_COLLECTION}],
        "related_identifiers": [
            {
                "identifier": video["url"],
                "relation": "isIdenticalTo",
                "resource_type": "publication-other"
            },
            {
                "identifier": f"https://doi.org/{ARCHIVE_DOI}",
                "relation": "isPartOf",
                "resource_type": "dataset"
            }
        ],
        "series_title": "The Sarvāmnāya Oral Tradition Archive"
    }

    return {"metadata": metadata}

def create_deposition(metadata):
    headers = {
        "Authorization": f"Bearer {ZENODO_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(ZENODO_URL, json=metadata, headers=headers)
    if not response.ok:
        raise Exception(f"Deposition creation failed: {response.status_code}\n{response.text}")
    return response.json()

def upload_file_to_deposition(bucket_url, file_path):
    headers = {"Authorization": f"Bearer {ZENODO_TOKEN}"}
    file_name = os.path.basename(file_path)

    with open(file_path, "rb") as file:
        upload_response = requests.put(f"{bucket_url}/{file_name}", data=file, headers=headers)

    if not upload_response.ok:
        raise Exception(f"Upload failed: {upload_response.status_code} - {upload_response.text}")
    return upload_response.json()

def publish_deposition(deposition_id):
    headers = {"Authorization": f"Bearer {ZENODO_TOKEN}"}
    response = requests.post(f"{ZENODO_URL}/{deposition_id}/actions/publish", headers=headers)
    response.raise_for_status()
    return response.json()

# ------------------------- MAIN PROCESS -------------------------
def process_video(video):
    print(f"\n📦 Processing: {video['title']}")
    details = get_video_details(video["video_id"], YOUTUBE_API_KEY)
    if not details:
        print("❌ Skipping due to missing details.")
        return

    #confirm = input(f"Upload '{video['title']}' to Zenodo? (y/n): ").strip().lower()
    #if confirm != 'y':
    #   print("⏭️ Skipped.")
    #   return

    path = download_video(details["url"], details["title"])
    if not path:
        return

    metadata = build_metadata(details)
    dep = create_deposition(metadata)
    print("⬆️ Uploading video...")
    upload_file_to_deposition(dep["links"]["bucket"], path)
    print("🚀 Publishing...")
    pub = publish_deposition(dep["id"])
    print(f"✅ Published! DOI: {pub['metadata']['doi']}")
    append_to_csv(
        youtube_id=video["video_id"],
        zenodo_id=dep["id"],
        title=details["title"],
        doi=pub['metadata']['doi'],
        youtube_link=details["url"]
    )

def main():
    try:
        initialize_csv()
        processed_ids = load_processed_youtube_ids()

        print("📺 Fetching videos...")
        videos = get_channel_videos(CHANNEL_ID, YOUTUBE_API_KEY)
        print(f"Found {len(videos)} videos.")

        # Filter out already processed videos
        new_videos = [v for v in videos if v["video_id"] not in processed_ids]

        for i in range(0, len(new_videos), 10):
            batch = new_videos[i:i + 10]
            print("\n🔢 Upcoming batch:")
            for idx, v in enumerate(batch, start=1):
                print(f"  [{idx}] {v['title']}")

            choice = input("\n🚀 Upload this batch of 10 videos? (y/n): ").strip().lower()
            if choice != 'y':
                print("⏭️ Skipping this batch.\n")
                continue

            for v in batch:
                try:
                    process_video(v)
                    time.sleep(WAIT_BETWEEN_UPLOADS)
                except Exception as e:
                    print(f"⚠️ Error processing '{v['title']}': {e}")

        print("\n🎉 All batches complete!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()