# Worth Leaving For — Free National Place Dataset

This repository builds a small, bounded daily extract from the [Overture Maps Places theme](https://docs.overturemaps.org/guides/places/) for Worth Leaving For.

The workflow is intentionally credential-free:

- GitHub Actions downloads open Overture data for Detroit plus one rotating U.S. market.
- It writes only the latest validated public extract to `data/latest.json`.
- The private Worth Leaving For scheduler fetches that file, validates it again, and stores qualifying records in its separate Local WOW evidence layer.
- This runner cannot approve events, change event rankings, publish the site, activate affiliate links, or post to social media.

The schedule runs at 09:30 UTC, ahead of the private site research run. Detroit refreshes daily; the other 51 U.S. jurisdictions rotate so the national foundation grows continuously without a paid places API.

## Data and attribution

Overture data is provided under record-level open data licenses. Every exported record retains its Overture source dataset identifiers. See [Overture data licenses](https://docs.overturemaps.org/attribution/).

## Local verification

```bash
python -m unittest discover -s tests
python scripts/build_dataset.py --dry-run
```

`overturemaps==1.0.1` is pinned for reproducibility. No repository secrets are required.
