import json
from collections import defaultdict
from pathlib import Path

# cache format
# {
#   cache_key(track, artist, album) : {
#     tidal_id: 123 or None,
#     candidates: {tidal_id: Track(), tidal_id: Track(), ...}
#   },
#   ...
# }

class TrackCache:
    def __init__(self, cache_path):
        self.cache_path = cache_path
        self.cache = defaultdict(dict)

        if Path(cache_path).exists():
            with open(cache_path, "r", encoding="utf-8") as cache_f:
                self.cache = json.load(cache_f)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.cache_path, "w", encoding="utf-8") as cache_f:
            json.dump(self.cache, cache_f, indent=2)

        return False

    def make_key(self, track, artist, album):
        return f"{track}::{artist}::{album}"

    def get_track_id(self, key):
        if key in self.cache:
            return self.cache[key].get("track_id", None)
        return None

    def set_track_id(self, key, track_id):
        self.cache[key]["track_id"] = track_id

    def get_candidates(self, key):
        if key in self.cache:
            return self.cache[key].get("candidates", {})
        return {}

    def set_candidates(self, key, candidates):
        self.cache[key]["candidates"] = candidates


# FIXME: tests
