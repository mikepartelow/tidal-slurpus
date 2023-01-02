import json
import tidalapi
from helpers import auth

# a JSON file with playlist_id to downloand and playlist_name base filename to write
PATH_TO_CONFIG = "slurpus_config.json"

def import_playlist(input_path, playlist_name, session, cache):
    # cache format: [{track, artist, album, tidal_id, import_status}]
    pass

def main():
    """Does the magic."""
    with open(PATH_TO_CONFIG, "r", encoding="utf-8") as config_f:
        config = json.load(config_f)

    session = tidalapi.Session()
    auth.login(session)

    input_path = config["input_path"]
    tidal_playlist_name = config["tidal_playlist_name"]

    cache_path = f"{input_path}.cache.json"

    with open(cache_path, "r", encoding="utf-8") as cache_f:
        cache = json.load(cache_f)

    try:
        import_playlist(input_path, tidal_playlist_name, session, cache)
    finally:
        with open(cache_path, "w", encoding="utf-8") as cache_f:
            json.dump(cache, cache_f)

# FIXME: `make lint` works in devcontainer
# FIXME: shell in devcontainer defaults to same dir as Makefile
# FIXME: vscode `Python: Run Linting` works
# FIXME: vscode python linting uses same tools as Makefile
# FIXME: vscode python linting runs `make lint` ?
# FIXME: vscode `Python: Run in Terminal` works even though devcontainer defaults to same dir as Makefile
# REFER: https://github.com/microsoft/vscode-dev-containers/blob/main/containers/python-3/.devcontainer/devcontainer.json

if __name__ == "__main__":
    main()
