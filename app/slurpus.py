"""Fetch a Tidal playlist and write it to a JSON file."""
from datetime import datetime
from pathlib import Path
import json
import time
import tidalapi

# time to sleep between tracks() API calls to avoid rate limits
BATCH_SLEEP = 8

# slurpus.py maintains this file with Tidal session credentials
PATH_TO_CREDS = "slurpus_creds.json"

# a JSON file with playlist_id to downloand and playlist_name base filename to write
PATH_TO_CONFIG = "slurpus_config.json"


def store_creds(session):
    """Store Tidal session credentials to a JSON file."""
    creds = dict(
        token_type=session.token_type,
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        expiry_time=session.expiry_time,
    )

    with open(PATH_TO_CREDS, "w", encoding="utf-8") as creds_f:
        json.dump(creds, creds_f, default=str)


def load_creds():
    """Load Tidal session credentials from a JSON file."""
    if Path(PATH_TO_CREDS).exists():
        with open(PATH_TO_CREDS, "r", encoding="utf-8") as creds_f:
            return json.load(creds_f)
    return None


def login(session):
    """Login to Tidal with stored or fresh credentials."""
    if creds := load_creds():
        session.load_oauth_session(
            creds["token_type"],
            creds["access_token"],
            creds["refresh_token"],
            creds["expiry_time"],
        )
    else:
        session.login_oauth_simple()
        store_creds(session)


def write_playlist(session, playlist_id, playlist_path):
    """Writes the given playlist as JSON to the given path."""
    playlist = session.playlist(playlist_id)

    playlist_tracks = []

    offset = 0

    while tracks := playlist.tracks(offset=offset):
        offset += len(tracks)

        for track in tracks:
            playlist_tracks.append(
                dict(
                    name=track.name,
                    artist=track.artist.name,
                    album=track.album.name,
                    version=track.version,
                    num=track.track_num,
                    id=track.id,
                    artists=[a.name for a in track.artists],
                )
            )
        time.sleep(BATCH_SLEEP)

        with open(playlist_path, "w", encoding="utf-8") as tracks_f:
            json.dump(playlist_tracks, tracks_f, default=str)


def main():
    """Does the magic."""
    with open(PATH_TO_CONFIG, "r", encoding="utf-8") as config_f:
        config = json.load(config_f)

    session = tidalapi.Session()
    login(session)

    datestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    playlist_path = f"{config['playlist_name']}.{datestamp}.json"

    write_playlist(session, config['playlist_id'], playlist_path)
    print(f"Wrote Tidal Playlist to {playlist_path}")


if __name__ == "__main__":
    main()
