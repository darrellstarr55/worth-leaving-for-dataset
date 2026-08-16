import datetime as dt
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_dataset import RELEASE, SCHEMA_VERSION, build_payload  # noqa: E402
from markets import MARKETS, daily_markets  # noqa: E402


class DatasetTests(unittest.TestCase):
    def test_all_52_jurisdictions_are_represented_once(self):
        codes = [item[1] for item in MARKETS]
        self.assertEqual(52, len(codes))
        self.assertEqual(52, len(set(codes)))
        self.assertIn("DC", codes)
        self.assertIn("PR", codes)

    def test_detroit_is_always_first_and_rotation_is_deterministic(self):
        first = daily_markets(dt.date(2026, 8, 16).toordinal())
        replay = daily_markets(dt.date(2026, 8, 16).toordinal())
        self.assertEqual(first, replay)
        self.assertEqual("Detroit", first[0]["city"])
        self.assertEqual("MI", first[0]["stateCode"])
        self.assertEqual(2, len(first))
        self.assertNotEqual("MI", first[1]["stateCode"])

    def test_payload_is_bounded_and_json_serializable(self):
        sample = [{"id": "place-1", "geometry": {"type": "Point", "coordinates": [-83.0, 42.3]}}]
        payload = build_payload(dt.date(2026, 8, 16), downloader=lambda _market: sample)
        self.assertEqual(SCHEMA_VERSION, payload["schemaVersion"])
        self.assertEqual(RELEASE, payload["release"])
        self.assertEqual(2, len(payload["markets"]))
        self.assertLessEqual(sum(len(item["records"]) for item in payload["markets"]), 700)
        json.dumps(payload)

    def test_empty_market_does_not_replace_last_good_dataset(self):
        with self.assertRaisesRegex(RuntimeError, "No qualifying records"):
            build_payload(dt.date(2026, 8, 16), downloader=lambda _market: [])


if __name__ == "__main__":
    unittest.main()
