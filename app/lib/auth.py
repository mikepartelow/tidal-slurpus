from pathlib import Path
import json

# Tidal session credentials
PATH_TO_CREDS = "tidal.json"


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
