from datetime import datetime, timedelta
from logger import logger


def now_in_interval(from_s: str, to_s: str, test_h=None, test_m=None):
        now = datetime.now().strftime('%H:%M')
        hours, minutes = now.split(':')
        hours = int(hours)
        minutes = int(minutes)
        if test_h is not None and test_m is not None:
            hours = test_h
            minutes = test_m
        logger.debug('Now: %s:%s' % (str(hours), str(minutes)))
        from_h, from_m = (int(x) for x in from_s.split(':'))
        to_h, to_m = (int(x) for x in to_s.split(':'))
        logger.debug('Lock from: %s:%s to %s:%s' % (str(from_h), str(from_m), str(to_h), str(to_m)))
        if (from_h < to_h and from_h < hours < to_h) \
                or (hours == from_h and hours == to_h and from_m <= minutes <= to_m) \
                or (hours == from_h and hours != to_h and minutes >= from_m) \
                or (hours == to_h and hours != from_h and minutes <= to_m) \
                or (from_h > to_h and (from_h < hours < 24 or 0 < hours < to_h)):
            return True
        return False

if __name__ == "__main__":
    # 1
    from_h, from_m, to_h, to_m = 22, 15, 6, 00
    from_s = '%d:%d' % (from_h, from_m)
    to_s = '%d:%d' % (to_h, to_m)
    assert now_in_interval(from_s, to_s, 21, 0) is False
    assert now_in_interval(from_s, to_s, 22, 0) is False
    assert now_in_interval(from_s, to_s, 22, 30) is True
    assert now_in_interval(from_s, to_s, 23, 0) is True
    assert now_in_interval(from_s, to_s, 1, 0) is True
    assert now_in_interval(from_s, to_s, 5, 45) is True
    assert now_in_interval(from_s, to_s, 6, 15) is False
    assert now_in_interval(from_s, to_s, 7, 45) is False
    # 2
    from_h, from_m, to_h, to_m = 16, 10, 18, 30
    from_s = '%d:%d' % (from_h, from_m)
    to_s = '%d:%d' % (to_h, to_m)
    assert now_in_interval(from_s, to_s, 15, 45) is False
    assert now_in_interval(from_s, to_s, 16, 0) is False
    assert now_in_interval(from_s, to_s, 16, 30) is True
    assert now_in_interval(from_s, to_s, 17, 45) is True
    assert now_in_interval(from_s, to_s, 18, 0) is True
    assert now_in_interval(from_s, to_s, 18, 45) is False
    assert now_in_interval(from_s, to_s, 19, 0) is False
    # 3
    from_h, from_m, to_h, to_m = 16, 10, 16, 30
    from_s = '%d:%d' % (from_h, from_m)
    to_s = '%d:%d' % (to_h, to_m)
    assert now_in_interval(from_s, to_s, 16, 0) is False
    assert now_in_interval(from_s, to_s, 16, 25) is True
    assert now_in_interval(from_s, to_s, 16, 45) is False
