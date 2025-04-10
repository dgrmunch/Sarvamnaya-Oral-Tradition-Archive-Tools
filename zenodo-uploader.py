import requests
import os
import time
import sys
import json
import yt_dlp

# ------------------------- CONFIGURATION -------------------------
ZENODO_URL = "https://zenodo.org/api/deposit/depositions"
ZENODO_COLLECTION = "vimarsha-foundation"
CHANNEL_ID = "UC4wAYkt8_U1TJOfXkfpjAsw"
CREATOR_NAME = "Timalsina, Staneshwar"
DOWNLOAD_DIR = "downloaded_videos"
WAIT_BETWEEN_UPLOADS = 3

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
        'no_warnings': False,
        'retries': 10,
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
        "description": f"{video['description']}\n\nOriginal YouTube video: {video['url']}",
        "creators": [{"name": CREATOR_NAME}],
        "access_right": "open",
        "license": "cc-by-4.0",
        "keywords": video.get("tags", []),
        "publication_date": video["published_at"][:10],
        "communities": [{"identifier": ZENODO_COLLECTION}],
        "related_identifiers": [
            {
                "identifier": video["url"],
                "relation": "isIdenticalTo",
                "resource_type": "publication-other"
            }
        ]
    }

    required_fields = ["title", "upload_type", "description", "creators", "access_right"]
    for field in required_fields:
        if not metadata.get(field):
            raise ValueError(f"Missing required metadata field: {field}")

    return {"metadata": metadata}

def create_deposition(metadata):
    headers = {
        "Authorization": f"Bearer {ZENODO_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(ZENODO_URL, json=metadata, headers=headers, timeout=30)
        if not response.ok:
            msg = f"Deposition creation failed: {response.status_code}"
            try:
                errors = response.json()
                msg += "\n" + json.dumps(errors, indent=2)
            except Exception:
                msg += f"\nRaw response: {response.text}"
            raise Exception(msg)
        return response.json()
    except Exception as e:
        print(f"❌ {e}")
        return None


def upload_file_to_deposition(bucket_url, file_path):
    """Upload a file to a Zenodo bucket URL"""
    headers = {
        "Authorization": f"Bearer {ZENODO_TOKEN}",
    }
    file_name = os.path.basename(file_path)
    
    with open(file_path, "rb") as file:
        upload_response = requests.put(
            f"{bucket_url}/{file_name}",
            data=file,
            headers=headers
        )

    if not upload_response.ok:
        print(f"Error uploading file: {upload_response.status_code} - {upload_response.text}")
        return None
    
    return upload_response.json()


def publish_deposition(deposition_id):
    headers = {"Authorization": f"Bearer {ZENODO_TOKEN}"}
    url = f"{ZENODO_URL}/{deposition_id}/actions/publish"

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error publishing deposition: {e}")
        return None

# ------------------------- MAIN PROCESS -------------------------
def process_video(video):
    print(f"\n📦 Processing: {video['title']}")

    details = get_video_details(video["video_id"], YOUTUBE_API_KEY)
    if not details:
        print("❌ Skipping due to missing details.")
        return

    confirm = input(f"Upload '{video['title']}' to Zenodo? (y/n): ").strip().lower()
    if confirm != 'y':
        print("⏭️ Skipped.")
        return

    path = download_video(details["url"], details["title"])
    if not path:
        print("❌ Download failed.")
        return

    try:
        metadata = build_metadata(details)
        dep = create_deposition(metadata)
        if not dep:
            return

        print("⬆️ Uploading video...")
        if not upload_file_to_deposition(dep["links"]["bucket"], path):
            return

        print("🚀 Publishing...")
        pub = publish_deposition(dep["id"])
        if pub:
            print(f"✅ Published! DOI: {pub['metadata']['doi']}")
    except Exception as e:
        print(f"❌ Error in processing: {e}")

def main():
    try:
        print("📺 Fetching videos...")
        videos = get_channel_videos(CHANNEL_ID, YOUTUBE_API_KEY)
        print(f"Found {len(videos)} videos.")

        for video in videos:
            process_video(video)
            time.sleep(WAIT_BETWEEN_UPLOADS)

        print("\n🎉 All done!")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
