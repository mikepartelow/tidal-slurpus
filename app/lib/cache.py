import json
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
        self.cache = {}

        if Path(cache_path).exists():
            with open(cache_path, "r", encoding="utf-8") as cache_f:
                self.cache = json.load(cache_f)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.cache_path, "w", encoding="utf-8") as cache_f:
            json.dump(self.cache, cache_f, indent=2)

        return False

    def key_for(self, track, artist, album):
        return f"{track}::{artist}::{album}"
