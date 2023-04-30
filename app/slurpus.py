import json
import tidalapi
import re
from lib import auth, cache
from collections import namedtuple, Counter
import time

# a JSON file with playlist_id to import to, and an input_path to import from
PATH_TO_CONFIG = "slurpus_config.json"

Track = namedtuple("Track", "name artist album artists")

def same_track(candidate, target, ignore_artist=False, ignore_album=False, desperation=False):
    c_artist = "" if ignore_artist else candidate.artist.lower()
    t_artist = "" if ignore_artist else target.artist.lower()

    c_album = "" if ignore_album else candidate.album.lower()
    t_album = "" if ignore_album else target.album.lower()

    # FIXME: cache in dataclass
    # FIXME: dataclass.__init__(scrub=True)
    def scrub(name):
        ttable = {ord(c): None for c in "-()[]"}
        name = re.sub(r'\d{0,4}\s*digital remaster', "", name, flags=re.I)
        name = re.sub(r'\d{0,4}\s*remaster', "", name, flags=re.I)
        return ' '.join(name.translate(ttable).split()).lower()

    candidate = Track(name=scrub(candidate.name), artist=c_artist, album=scrub(c_album), artists=candidate.artists)
    target = Track(name=scrub(target.name), artist=t_artist, album=scrub(t_album), artists=target.artists)

    if candidate.name == target.name \
            and c_album == t_album \
            and c_artist == t_artist:
        return True

    # FIXME: once Track is a dataclass, cache Counter(self.artists)
    if candidate.name == target.name \
            and c_album == t_album \
            and Counter(candidate.artists) == Counter(target.artists):
        return True

    if desperation:
        artists_equal = True if ignore_artist else Counter(candidate.artists) == Counter(target.artists)
        if (candidate.name in target.name or target.name in candidate.name) \
                and c_album == t_album \
               and artists_equal:
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

def find_track(name, artist, album, track_cache, session, ignore_artist=False, ignore_album=False, desperation=False, skip_matching=False):

    freshen_candidates = False

    key = track_cache.make_key(name, artist, album)
    if (track_id := track_cache.get_track_id(key)) or skip_matching:
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
        if same_track(Track(*candidate), target, ignore_artist=ignore_artist, ignore_album=ignore_album, desperation=True):
            track_cache.set_track_id(key, track_id)
            return track_id

    return None


def find_track_ids(input_path, track_cache, session, skip_matching=False):
    track_count, track_ids = 0, []
    with open(input_path, "r", encoding="utf-8") as input_f:
        for line in input_f:
            track_count += 1
            if track_count % 100 == 0:
                print(".", end="", flush=True)
            track, album, artist = map(str.strip, line.split("\t"))

            # note argument order is not the same as input_f order
            track_id = find_track(track, artist, album, track_cache, session, skip_matching=skip_matching)
            if not skip_matching:
                if not track_id:
                    track_id = find_track(track, artist, album, track_cache, session, ignore_album=True)
                if not track_id:
                    track_id = find_track(track, artist, album, track_cache, session, ignore_artist=True)
                if not track_id:
                    track_id = find_track(track, artist, album, track_cache, session, desperation=True)
                if not track_id:
                    track_id = find_track(track, artist, album, track_cache, session, ignore_artist=True, desperation=True)
                if not track_id:
                    track_id = find_track(track, artist, album, track_cache, session, ignore_artist=True, ignore_album=True, desperation=True)

            if track_id:
                track_ids.append(track_id)

    return track_count, track_ids

def import_playlist(tidal_playlist_name, track_ids, session):
    playlist = None
    for candidate in session.user.playlists():
        if candidate.name == tidal_playlist_name:
            playlist = candidate
            break

    if not playlist:
        print("Creating playlist")
        playlist = session.user.create_playlist(tidal_playlist_name, tidal_playlist_name)

    MAX_ADD = 100
    start, finish = 0, MAX_ADD
    while finish < len(track_ids):
        # print(f"adding {start}:{finish}: {track_ids[start:finish]}")
        print(f"adding {start}:{finish}")
        playlist.add(track_ids[start:finish])
        start, finish = finish, finish + MAX_ADD

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
        track_count, track_ids = find_track_ids(input_path, track_cache, session, skip_matching=True)

        print("")
        print(f"Found {len(track_ids)} ids for {track_count} tracks.")

        import_playlist(tidal_playlist_name, track_ids, session)
        print("Success, probably!")

# FIXME: match inexact tracks
#        - [ ] multi-artist tracks
# FIXME: use dataclasses instead of namedtuple
# FIXME: typing
# FIXME: probably need to page search results - but this is last resort
# FIXME: refactor find_tracks
# FIXME: refactor find_track
# FIXME: `make lint` works in devcontainer
# FIXME: shell in devcontainer defaults to same dir as Makefile
# FIXME: vscode `Python: Run Linting` works
# FIXME: vscode python linting uses same tools as Makefile
# FIXME: vscode python linting runs `make lint` ?
# FIXME: vscode `Python: Run in Terminal` works even though devcontainer defaults to same dir as Makefile
# REFER: https://github.com/microsoft/vscode-dev-containers/blob/main/containers/python-3/.devcontainer/devcontainer.json

if __name__ == "__main__":
    main()
