from scripts.ingest import compute_start_date


def test_no_data_means_full_load():
    assert compute_start_date(None) is None


def test_lookback_window():
    assert compute_start_date('2025-01-10', 3) == '2025-01-07'


def test_lookback_crosses_month_boundary():
    assert compute_start_date('2025-03-02', 3) == '2025-02-27'