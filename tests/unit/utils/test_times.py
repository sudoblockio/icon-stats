from datetime import datetime

from icon_stats.utils.times import convert_str_date


def test_convert_str_date():
    timezone_aware = convert_str_date('2023-10-27T05:39:00.000Z')
    assert isinstance(timezone_aware, datetime)
