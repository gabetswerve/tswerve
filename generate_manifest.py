import os
import json
import datetime

AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.flac']
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
CATEGORIES = ['Singles', 'EPs', 'Albums', 'Albums and Mixtapes', 'Albums and Mixtales', 'Features']

def pretty_name(file_name):
    base = os.path.splitext(file_name)[0]
    base = base.replace('-', ' ').replace('_', ' ')
    return base.title()

def scan_music():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    music_dir = os.path.join(base_dir, 'Music')
    manifest_path = os.path.join(base_dir, 'music-manifest.json')
    
    tracks = []
    
    if not os.path.exists(music_dir):
        print("Music directory does not exist!")
        return
        
    category_dirs = []
    for item in os.listdir(music_dir):
        item_path = os.path.join(music_dir, item)
        if os.path.isdir(item_path) and item in CATEGORIES:
            category_dirs.append(item)
                
    for cat in category_dirs:
        display_category = 'Albums' if cat in ['Albums', 'Albums and Mixtales', 'Albums and Mixtapes'] else cat
        cat_path = os.path.join(music_dir, cat)
        
        release_dirs = []
        for item in os.listdir(cat_path):
            item_path = os.path.join(cat_path, item)
            if os.path.isdir(item_path):
                release_dirs.append(item)
                
        for release in release_dirs:
            release_path = os.path.join(cat_path, release)
            files = os.listdir(release_path)
            
            audio_files = [f for f in files if os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS]
            image_files = [f for f in files if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS]
            
            for audio in audio_files:
                audio_base = os.path.splitext(audio)[0]
                
                metadata = {}
                specific_json = f"{audio_base}.json"
                generic_json = "metadata.json"
                
                json_file = None
                for f in files:
                    if f.lower() == specific_json.lower():
                        json_file = f
                        break
                if not json_file:
                    for f in files:
                        if f.lower() == generic_json.lower():
                            json_file = f
                            break
                    
                if json_file:
                    try:
                        with open(os.path.join(release_path, json_file), 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except Exception as e:
                        print(f"Error parsing JSON for {audio} in {release_path}: {e}")
                        
                cover_file = None
                if 'cover' in metadata and metadata['cover']:
                    candidate = next((f for f in files if f.lower() == metadata['cover'].lower()), None)
                    if candidate:
                        cover_file = candidate
                        
                if not cover_file:
                    cover_file = next((f for f in image_files if os.path.splitext(f)[0].lower() == audio_base.lower()), None)
                if not cover_file:
                    cover_file = next((f for f in image_files if 'cover' in f.lower()), None)
                if not cover_file:
                    cover_file = image_files[0] if image_files else None
                    
                rel_audio_path = f"Music/{cat}/{release}/{audio}"
                rel_cover_path = f"Music/{cat}/{release}/{cover_file}" if cover_file else ""
                
                stat = os.stat(os.path.join(release_path, audio))
                default_date = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat().split('T')[0]
                
                track = {
                    "title": metadata.get("title") or pretty_name(audio),
                    "artist": metadata.get("artist") or metadata.get("producer") or "T Swerve",
                    "album": metadata.get("album") or ("Single" if display_category == 'Singles' else release),
                    "category": display_category,
                    "audioUrl": rel_audio_path,
                    "coverUrl": rel_cover_path,
                    "path": rel_audio_path,
                    "date": metadata.get("date") or default_date,
                }
                
                if 'year' in metadata or 'releaseYear' in metadata:
                    track['year'] = metadata.get('year') or metadata.get('releaseYear')
                else:
                    track['year'] = default_date.split('-')[0]
                    
                if display_category != 'Singles':
                    track['trackNumber'] = metadata.get('trackNumber') or metadata.get('track') or 0
                    
                tracks.append(track)
                
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(tracks, f, indent=2, ensure_ascii=False)
    print(f"Generated manifest at {manifest_path} with {len(tracks)} tracks.")

if __name__ == '__main__':
    scan_music()
