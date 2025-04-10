
import requests
from datetime import datetime, timezone

# Configuration
ZENODO_API_URL = "https://zenodo.org/api/deposit/depositions"  # Use sandbox if testing

def get_all_drafts():
    """Retrieve all draft depositions"""
    headers = {"Authorization": f"Bearer {ZENODO_API_TOKEN}"}
    params = {"status": "draft"}
    
    try:
        response = requests.get(ZENODO_API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching drafts: {e}")
        return []

def delete_deposition(deposition_id):
    """Delete a single deposition"""
    headers = {"Authorization": f"Bearer {ZENODO_API_TOKEN}"}
    url = f"{ZENODO_API_URL}/{deposition_id}"
    
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"✅ Successfully deleted deposition {deposition_id}")
            return True
        else:
            print(f"⚠️ Unexpected status code {response.status_code} for deposition {deposition_id}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error deleting deposition {deposition_id}: {e}")
        return False

def filter_today_drafts(drafts):
    """Filter drafts created today"""
    today = datetime.now(timezone.utc).date()
    today_drafts = []
    
    for draft in drafts:
        created = datetime.strptime(draft['created'], '%Y-%m-%dT%H:%M:%S.%f%z').date()
        if created == today:
            today_drafts.append(draft)
    
    return today_drafts

def main():
    print("Fetching all draft depositions...")
    drafts = get_all_drafts()
    
    if not drafts:
        print("No draft depositions found.")
        return
    
    today_drafts = filter_today_drafts(drafts)
    
    if not today_drafts:
        print("No draft depositions created today found.")
        return
    
    print(f"Found {len(today_drafts)} draft depositions created today:")
    for i, draft in enumerate(today_drafts, 1):
        print(f"{i}. ID: {draft['id']} - Created: {draft['created']} - Title: {draft.get('metadata', {}).get('title', 'Untitled')}")
    
    confirmation = input("\nAre you sure you want to delete ALL these drafts created today? (y/n): ").strip().lower()
    if confirmation != 'y':
        print("Operation cancelled.")
        return
    
    print("\nDeleting today's drafts...")
    success_count = 0
    for draft in today_drafts:
        if delete_deposition(draft['id']):
            success_count += 1
    
    print(f"\nDeletion process completed. Successfully deleted {success_count} out of {len(today_drafts)} drafts.")

if __name__ == "__main__":
    main()