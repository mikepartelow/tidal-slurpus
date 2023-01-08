import json
import tidalapi
from pathlib import Path
from helpers import auth
from collections import namedtuple

# a JSON file with playlist_id to import to, and an input_path to import from
PATH_TO_CONFIG = "slurpus_config.json"

Track = namedtuple("Track", "name artist album")

# cache format
# {
#   cache_key(track, artist, album) : {
#     tidal_id: 123 or None,
#     candidates: {tidal_id: Track(), tidal_id: Track(), ...}
#   },
#   ...
# }

def cache_key(track, artist, album):
    return f"{track}::{artist}::{album}"

def find_track(name, artist, album, cache, session):
    key = cache_key(name, artist, album)
    if key in cache:
        if (track_id := cache[key]["track_id"]) is not None:
            return track_id
    else:
        cache[key] = {"track_id": None, "candidates": {}}


    if not (candidates := cache[key]["candidates"]):
        results = session.search(name, models=[tidalapi.media.Track])
        candidates = {
            r.id: Track(
                        name=r.name,
                        artist=r.artist.name,
                        album=r.album.name
                       )
            for r in results["tracks"]}

        cache[key]["candidates"] = candidates

    target = Track(name=name, artist=artist, album=album)

    for track_id, candidate in candidates.items():
        if candidate == target:
            cache[key]["track_id"] = track_id
            return track_id

    return None

def import_playlist(input_path, playlist_name, cache, session):
    # https://tidalapi.netlify.app/playlist.html#adding-to-a-playlist

    track_count, track_ids = 0, 0
    with open(input_path, "r", encoding="utf-8") as input_f:
        for line in input_f:
            track_count += 1
            track, album, artist = map(str.strip, line.split("\t"))

            # note argument order is not the same as input_f order
            track_id = find_track(track, artist, album, cache, session)
            if track_id:
                track_ids += 1

    print(f"Found {track_ids} ids for {track_count} tracks.")

def main():
    """Does the magic."""
    with open(PATH_TO_CONFIG, "r", encoding="utf-8") as config_f:
        config = json.load(config_f)

    session = tidalapi.Session()
    auth.login(session)

    input_path = config["input_path"]
    tidal_playlist_name = config["tidal_playlist_name"]

    cache_path = f"{input_path}.cache.json"

    if Path(cache_path).exists():
        with open(cache_path, "r", encoding="utf-8") as cache_f:
            cache = json.load(cache_f)
    else:
        cache = {}

    try:
        import_playlist(input_path, tidal_playlist_name, cache, session)
    finally:
        with open(cache_path, "w", encoding="utf-8") as cache_f:
            json.dump(cache, cache_f, indent=2)

# FIXME: refactor cache to an object in a lib
# FIXME: cache explorer app
# FIXME: match inexact tracks
# FIXME: `make lint` works in devcontainer
# FIXME: shell in devcontainer defaults to same dir as Makefile
# FIXME: vscode `Python: Run Linting` works
# FIXME: vscode python linting uses same tools as Makefile
# FIXME: vscode python linting runs `make lint` ?
# FIXME: vscode `Python: Run in Terminal` works even though devcontainer defaults to same dir as Makefile
# REFER: https://github.com/microsoft/vscode-dev-containers/blob/main/containers/python-3/.devcontainer/devcontainer.json

if __name__ == "__main__":
    main()
