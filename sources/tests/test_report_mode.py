"""The reported day, in its two modes: nominal and demo (governance.yml,
report.mode).

Block: B3.
Lot: B3-P4.
Competency: B3-C4.
Covers: B3-EE03.

NOMINAL IS THE SYSTEM AS DOCUMENTED: the calendar day, delivered at 06:00.
DEMO exists for an afternoon recording: noon to noon, delivered at 14:00. One
switch moves both, and every reader of a day -- the report, the dashboard, the
checker -- goes through report.span_for(), so they move together.
"""
from __future__ import annotations

import datetime as dt
import types
import zoneinfo

import pytest

from fraud import config, dashboard, report

PARIS = zoneinfo.ZoneInfo("Europe/Paris")


def _settings(day_start=None, schedule="0 6 * * *", mode="nominal"):
    s = types.SimpleNamespace(report_timezone="Europe/Paris", report_schedule=schedule, report_mode=mode)
    if day_start is not None:
        s.report_day_start = day_start
    return s


# --- the window ---------------------------------------------------------------

def test_nominal_is_midnight_to_midnight_even_without_the_setting():
    """A configuration that does not carry the start of day is the calendar
    day: every namespace built before report.mode existed stays right."""
    w = report.window_for(_settings(), dt.date(2026, 11, 23))
    assert w.start == dt.datetime(2026, 11, 23, 0, 0, tzinfo=PARIS)
    assert w.end == dt.datetime(2026, 11, 24, 0, 0, tzinfo=PARIS)
    assert report.day_bounds(_settings()) == ""


def test_demo_runs_from_noon_to_noon_and_keeps_its_name():
    w = report.window_for(_settings(dt.time(12, 0)), dt.date(2026, 11, 23))
    assert w.start == dt.datetime(2026, 11, 23, 12, 0, tzinfo=PARIS)
    assert w.end == dt.datetime(2026, 11, 24, 12, 0, tzinfo=PARIS)
    assert w.day == dt.date(2026, 11, 23)          # named by its first date


def test_a_demo_report_delivered_at_14_00_is_accepted():
    """The run that fires on the 24th at 14:00 knows the day that ended at
    noon. Delivered before noon, report.Window would refuse it."""
    s = _settings(dt.time(12, 0))
    at_14 = dt.datetime(2026, 11, 24, 14, 0, tzinfo=PARIS)
    assert report.window_for(s, dt.date(2026, 11, 23), knowledge_at=at_14)
    with pytest.raises(ValueError):
        report.window_for(s, dt.date(2026, 11, 23),
                          knowledge_at=dt.datetime(2026, 11, 24, 6, 0,
                                                   tzinfo=PARIS))


def test_a_period_spans_from_the_first_noon_to_the_noon_after_the_last():
    w = report.span_for(_settings(dt.time(12, 0)),
                        dt.date(2026, 11, 20), dt.date(2026, 11, 22))
    assert w.start == dt.datetime(2026, 11, 20, 12, 0, tzinfo=PARIS)
    assert w.end == dt.datetime(2026, 11, 23, 12, 0, tzinfo=PARIS)


# --- said wherever a day is named ---------------------------------------------

def test_the_demo_bounds_are_said():
    assert report.day_bounds(_settings(dt.time(12, 0))) == "de 12:00 à 12:00"


def test_the_report_title_states_its_bounds_in_demo_mode_only():
    """Built on test_report's own fixture, so the body renders for real."""
    import test_report as tr

    nominal = tr._settings()
    assert report.render(tr._data(), nominal).splitlines()[0] == ("# Revue : journée du 2026-11-16")
    demo = tr._settings()
    demo.report_day_start = dt.time(12, 0)
    window = report.window_for(demo, dt.date(2026, 11, 16))
    first = report.render(tr._data(window=window), demo).splitlines()[0]
    assert first == "# Revue : journée du 2026-11-16 (de 12:00 à 12:00)"


def test_the_dashboard_period_label_carries_the_bounds():
    day = dt.date(2026, 11, 23)
    assert dashboard.period_label(day, day) == "le 2026-11-23"
    assert dashboard.period_label(day, day, _settings(dt.time(12, 0))) == "le 2026-11-23 (de 12:00 à 12:00)"


def test_today_is_the_day_in_progress():
    """At 09:00 in demo mode, the noon-to-noon day in progress began
    yesterday: the alerts of this morning are on yesterday's page."""
    morning = dt.datetime(2026, 11, 24, 9, 0, tzinfo=PARIS)
    afternoon = dt.datetime(2026, 11, 24, 15, 0, tzinfo=PARIS)
    assert dashboard.today(_settings(), morning) == dt.date(2026, 11, 24)
    demo = _settings(dt.time(12, 0))
    assert dashboard.today(demo, morning) == dt.date(2026, 11, 23)
    assert dashboard.today(demo, afternoon) == dt.date(2026, 11, 24)


# --- the declaration ----------------------------------------------------------

def test_the_mode_selects_its_block():
    section = {"mode": "demo",
               "nominal": {"day_start": "00:00", "schedule": "0 6 * * *"},
               "demo": {"day_start": "12:00", "schedule": "0 14 * * *"}}
    assert config._report_mode(section) == ("demo", dt.time(12, 0),
                                            "0 14 * * *")
    section["mode"] = "nominal"
    assert config._report_mode(section) == ("nominal", dt.time(0, 0),
                                            "0 6 * * *")


@pytest.mark.parametrize("section", [
    {"mode": "weekend"},
    {"mode": "demo", "nominal": {"day_start": "00:00", "schedule": "0 6 * * *"}},
    {"mode": "nominal", "nominal": {"day_start": "noon", "schedule": "0 6 * * *"}},
])
def test_a_wrong_declaration_is_refused_and_named(section):
    with pytest.raises(ValueError):
        config._report_mode(section)


def test_the_declared_schedule_is_the_one_load_reads():
    """The DAG reads declared_report_schedule() at parse time, the checkers
    read load(): one declaration, whichever mode is in force."""
    import yaml
    section = yaml.safe_load(
        config.governance_path().read_text(encoding="utf-8"))["report"]
    assert config.declared_report_schedule() == config._report_mode(section)[2]


def test_the_alert_hours_are_written_in_the_declared_zone():
    """THE DEFECT OF THE 2026-11-22 REPORT: PostgreSQL hands txn_ts back in
    UTC, and section 2 showed 09:50 for a payment made at 10:50 in Paris."""
    import test_report as tr

    utc = dt.datetime(2026, 11, 23, 9, 50, tzinfo=dt.timezone.utc)
    alert = {**tr._alert(), "txn_ts": utc}
    text = report.render(tr._data(alerts=[alert]), tr._settings())
    assert "| 1 | 10:50 |" in text
