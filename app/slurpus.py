import json
import tidalapi
from lib import auth, cache
from collections import namedtuple

# a JSON file with playlist_id to import to, and an input_path to import from
PATH_TO_CONFIG = "slurpus_config.json"

Track = namedtuple("Track", "name artist album")

def find_track(name, artist, album, track_cache, session):
    key = track_cache.make_key(name, artist, album)
    if track_id := track_cache.get_track_id(key):
        return track_id

    if not (candidates := track_cache.get_candidates(key)):
        results = session.search(name, models=[tidalapi.media.Track])
        candidates = {
            r.id: Track(
                        name=r.name,
                        artist=r.artist.name,
                        album=r.album.name
                       )
            for r in results["tracks"]}

        track_cache.set_candidates(key, candidates)

    target = Track(name=name, artist=artist, album=album)

    for track_id, candidate in candidates.items():
        if candidate == target:
            track_cache.set_track_id(key, track_id)
            return track_id

    return None

def import_playlist(input_path, playlist_name, track_cache, session):
    # https://tidalapi.netlify.app/playlist.html#adding-to-a-playlist

    track_count, track_ids = 0, 0
    with open(input_path, "r", encoding="utf-8") as input_f:
        for line in input_f:
            track_count += 1
            if track_count % 100 == 0:
                print(".", end="", flush=True)
            track, album, artist = map(str.strip, line.split("\t"))

            # note argument order is not the same as input_f order
            track_id = find_track(track, artist, album, track_cache, session)
            if track_id:
                track_ids += 1
    print("")
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
    with cache.TrackCache(cache_path) as track_cache:
        import_playlist(input_path, tidal_playlist_name, track_cache, session)


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
