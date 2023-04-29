import json
from lib import cache

# a JSON file with playlist_id to import to, and an input_path to import from
PATH_TO_CONFIG = "slurpus_config.json"


def main():
    """Does the magic."""
    with open(PATH_TO_CONFIG, "r", encoding="utf-8") as config_f:
        config = json.load(config_f)

    input_path = config["input_path"]

    cache_path = f"{input_path}.cache.json"
    with cache.TrackCache(cache_path, read_only=True) as track_cache:
        for track in track_cache:
            if track.get("track_id", None) is None:
                if track['candidates']:
                    k = list(track['candidates'].keys())[0]
                    print(f"{track['key']} ~= {track['candidates'][k]}")
                else:
                    print(f"No candidates: {track['key']}")
                print("")
                # print(json.dumps(track, indent=2))


# FIXME: polish this

if __name__ == "__main__":
    main()
