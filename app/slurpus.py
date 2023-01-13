import json
import tidalapi
from lib import auth, cache
from collections import namedtuple, Counter

# a JSON file with playlist_id to import to, and an input_path to import from
PATH_TO_CONFIG = "slurpus_config.json"

Track = namedtuple("Track", "name artist album artists")

def same_track(track_a, track_b):
    if track_a.name == track_b.name \
            and track_a.album == track_b.album \
            and track_a.artist == track_b.artist:
        return True

    # FIXME: once Track is a dataclass, cache Counter(self.artists)
    if track_a.name == track_b.name \
            and track_a.album == track_b.album \
            and Counter(track_a.artists) == Counter(track_b.artists):
        return True

    return False

def find_candidates(target, session):
    candidates = {}
    search_terms = [f"{target.name} {target.artist}", target.name]
    target_artists = Counter(map(str.strip, target.artist.split(',')))
    multi_artist_target = len(target_artists) > 1

    for search_term in search_terms:
        results = session.search(search_term, models=[tidalapi.media.Track])

        for result in results["tracks"]:
            artist_group = ', '.join(a.name for a in result.artists)
            candidate = Track(name=result.name, artist=result.artist.name, album=result.album.name, artists=artist_group)
            candidates.update({result.id: candidate})

            if same_track(candidate, target):
                return candidates, result.id

    return candidates, None

def find_track(name, artist, album, track_cache, session):

    freshen_candidates = False

    key = track_cache.make_key(name, artist, album)
    if track_id := track_cache.get_track_id(key):
        return track_id

    # Our data source has only one "artist" field which can contain a list of artists like
    # "The Comet Is Coming, Kae Tempest"
    target = Track(name=name, artist=artist, album=album, artists=artist)

    if freshen_candidates or not (candidates := track_cache.get_candidates(key)):
        candidates, track_id = find_candidates(target, session)
        track_cache.set_candidates(key, candidates)
        if track_id:
            return track_id

    for track_id, candidate in candidates.items():
        if same_track(Track(*candidate), target):
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


# FIXME: match inexact tracks
#        - [ ] multi-artist tracks
# FIXME: use dataclasses instead of namedtuple
# FIXME: typing
# FIXME: probably need to page search results - but this is last resort
# FIXME: `make lint` works in devcontainer
# FIXME: shell in devcontainer defaults to same dir as Makefile
# FIXME: vscode `Python: Run Linting` works
# FIXME: vscode python linting uses same tools as Makefile
# FIXME: vscode python linting runs `make lint` ?
# FIXME: vscode `Python: Run in Terminal` works even though devcontainer defaults to same dir as Makefile
# REFER: https://github.com/microsoft/vscode-dev-containers/blob/main/containers/python-3/.devcontainer/devcontainer.json

if __name__ == "__main__":
    main()
