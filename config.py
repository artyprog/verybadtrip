# coding: utf-8
import yaml
from aenum import Enum
from datetime import datetime
from datetime import timedelta


class DayEnum(Enum):
    MONDAY = 'mon'
    TUESDAY = 'tue'
    WEDNESDAY = 'wed'
    THURSDAY = 'thu'
    FRIDAY = 'fri'
    SATURDAY = 'sat'
    SUNDAY = 'sun'


DAY_VALUE = {
    DayEnum.MONDAY.value: 0,
    DayEnum.TUESDAY.value: 1,
    DayEnum.WEDNESDAY.value: 2,
    DayEnum.THURSDAY.value: 3,
    DayEnum.FRIDAY.value: 4,
    DayEnum.SATURDAY.value: 5,
    DayEnum.SUNDAY.value: 6,
}


class DayRange(object):
    def __init__(self, start, end):
        """Takes two DayEnum as args.

        >>> DayRange(DayEnum.MONDAY, DayEnum.FRIDAY)

        """
        self.start = start.value
        self.end = end.value

    def check(self, dt):
        dt_day = DayEnum(dt.strftime('%a').lower()).value
        return DAY_VALUE.get(self.start) <= DAY_VALUE.get(dt_day) <= DAY_VALUE.get(self.end)


class Trip(object):
    def __init__(self, data):
        self._data = data

    def next_trip_date(self):
        if 'day_range' in self._data:
            day_start, day_end = self._data['day_range'].split('-')
            day_range = DayRange(DayEnum(day_start), DayEnum(day_end))
            for x in xrange(4):
                dt = datetime.now() + timedelta(days=x)
                if day_range.check(dt):
                    return dt.strftime('%Y%m%dT') + self._data['hour']
            return None
        else:
            raise Exception('bad rule')

    @property
    def headsign(self):
        return self._data.get('headsign')

    @property
    def from_(self):
        return self._data.get('from')

    @property
    def date_time(self):
        if not self.recurring:
            return self._data.get('date_time')
        return self.next_trip_date()

    @property
    def recurring(self):
        return self._data.get('recurring', False)


def load():
    trips = []
    with open('config.yaml') as f:
        data = yaml.load(f)
        for trip in data['trips']:
            trips.append(Trip(trip))
    return trips
