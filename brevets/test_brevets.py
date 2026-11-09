"""Nose-compatible tests using RUSA calculator examples and edge cases."""

import unittest

import acp_times
from flask_brevets import app


START = "2026-01-01T00:00:00+00:00"


class CalculationTests(unittest.TestCase):
    def test_start_opens_at_start(self):
        self.assertEqual(acp_times.open_time(0, 200, START), START)

    def test_start_closes_after_one_hour(self):
        self.assertEqual(acp_times.close_time(0, 200, START),
                         "2026-01-01T01:00:00+00:00")

    def test_early_control_uses_relaxed_closing_time(self):
        self.assertEqual(acp_times.open_time(20, 200, START),
                         "2026-01-01T00:35:00+00:00")
        self.assertEqual(acp_times.close_time(20, 200, START),
                         "2026-01-01T02:00:00+00:00")

    def test_sixty_km_boundary(self):
        self.assertEqual(acp_times.open_time(60, 200, START),
                         "2026-01-01T01:46:00+00:00")
        self.assertEqual(acp_times.close_time(60, 200, START),
                         "2026-01-01T04:00:00+00:00")

    def test_rusa_200_km_examples(self):
        for distance, opening, closing in [
            (120, "03:32", "08:00"),
            (175, "05:09", "11:40"),
            (205, "05:53", "13:30"),
        ]:
            self.assertEqual(acp_times.open_time(distance, 200, START),
                             "2026-01-01T" + opening + ":00+00:00")
            self.assertEqual(acp_times.close_time(distance, 200, START),
                             "2026-01-01T" + closing + ":00+00:00")

    def test_opening_accumulates_speed_bands(self):
        for distance, expected in [
            (200, "2026-01-01T05:53:00+00:00"),
            (350, "2026-01-01T10:34:00+00:00"),
            (400, "2026-01-01T12:08:00+00:00"),
            (550, "2026-01-01T17:08:00+00:00"),
            (600, "2026-01-01T18:48:00+00:00"),
            (890, "2026-01-02T05:09:00+00:00"),
            (1000, "2026-01-02T09:05:00+00:00"),
        ]:
            self.assertEqual(acp_times.open_time(distance, 1000, START),
                             expected)

    def test_rounds_total_once(self):
        self.assertEqual(acp_times.open_time(300, 300, START),
                         "2026-01-01T09:00:00+00:00")

    def test_half_minute_rounds_up(self):
        self.assertEqual(acp_times.open_time(8.5, 200, START),
                         "2026-01-01T00:15:00+00:00")

    def test_closing_after_six_hundred_km(self):
        self.assertEqual(acp_times.close_time(890, 1000, START),
                         "2026-01-03T17:23:00+00:00")

    def test_finish_uses_official_time_limits(self):
        for distance, expected in [
            (200, "2026-01-01T13:30:00+00:00"),
            (300, "2026-01-01T20:00:00+00:00"),
            (400, "2026-01-02T03:00:00+00:00"),
            (600, "2026-01-02T16:00:00+00:00"),
            (1000, "2026-01-04T03:00:00+00:00"),
        ]:
            self.assertEqual(acp_times.close_time(distance, distance, START),
                             expected)
            self.assertEqual(acp_times.close_time(distance + 5, distance, START),
                             expected)

    def test_overdistance_opening_is_capped(self):
        self.assertEqual(acp_times.open_time(609, 600, START),
                         "2026-01-01T18:48:00+00:00")

    def test_preserves_timezone_and_rolls_into_next_year(self):
        start = "2026-12-31T23:30:00-08:00"
        self.assertEqual(acp_times.open_time(60, 200, start),
                         "2027-01-01T01:16:00-08:00")
        self.assertEqual(acp_times.close_time(60, 200, start),
                         "2027-01-01T03:30:00-08:00")

    def test_rejects_invalid_distances(self):
        for distance in [-1, float("nan"), float("inf"), "bad"]:
            for calculate in [acp_times.open_time, acp_times.close_time]:
                with self.assertRaises(ValueError):
                    calculate(distance, 200, START)

    def test_rejects_unsupported_brevet(self):
        for distance in [0, 201, 200.5, 1200]:
            for calculate in [acp_times.open_time, acp_times.close_time]:
                with self.assertRaises(ValueError):
                    calculate(60, distance, START)

    def test_rejects_invalid_start(self):
        for calculate in [acp_times.open_time, acp_times.close_time]:
            with self.assertRaises(ValueError):
                calculate(60, 200, "not a date")


class RequestTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_page_loads(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_request_uses_selected_brevet_and_start(self):
        response = self.client.get("/_calc_times", query_string={
            "km": 400, "brevet": 400,
            "start": "2026-12-31T23:00:00-08:00",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"result": {
            "open": "2027-01-01T11:08:00-08:00",
            "close": "2027-01-02T02:00:00-08:00",
        }})

    def test_bad_requests_return_json_errors(self):
        valid = {"km": "60", "brevet": "200", "start": START}
        invalid = [
            ("km", ""), ("km", "oops"), ("km", "-1"),
            ("km", "nan"), ("km", "inf"),
            ("brevet", "201"), ("brevet", "200.5"),
            ("start", "not a date"),
        ]
        for key, value in invalid:
            query = dict(valid, **{key: value})
            response = self.client.get("/_calc_times", query_string=query)
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.get_json())
        for missing in valid:
            query = dict(valid)
            del query[missing]
            response = self.client.get("/_calc_times", query_string=query)
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.get_json())
