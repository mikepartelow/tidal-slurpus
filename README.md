# Tidal Slurpus

Download a playlist from Tidal and store it in a local JSON file.

## How?

1. Create `app/slurpus_config.json`
2. `make run`
3. Playlist can be found in `app/$PLAYLIST_NAME.$DATESTAMP.json`

## app/slurpus_config.json

- `playlist_id` is the id from Tidal's `Share > Copy Playlist Link`
- `playlist_name` is the base name of the file that `tidal-slurpus` will create

```json
{
    "playlist_id": "4d056fb5-99f9-46ec-8ff3-f2dddd41821f",
    "playlist_name": "taylor_swift_essentials"
}
```

## app/slurpus_creds.json

After your initial login, reusable session credentials will be saved to `app/slurpus_creds.json`. Delete this file to login again.

## Credits

All the hard work was done by [tamland](https://github.com/tamland/python-tidal)
