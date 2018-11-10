import re
from enum import Enum

from datetime import datetime


def _extract_name(name_string):
    """
    employ a variety of strategies to decompose a name to its parts
    note this is a very euro-centric approach to structuring names... but then again, skiers are very european!
    :param name_string: a string of unknown format
    :return: a tuple of first name, middle name, and last name. any may be None
    """
    name_string = name_string.replace(u'\xa0', u' ')

    # TODO should write tests on this, since regression is so likely
    # TODO I'm pretty sure python caches compiled regexs
    # match "first last" - this obviously isn't an all encompassing
    fl_matches = re.search(r"^([a-zA-Z]+) +([a-zA-Z]+)$", name_string)
    if fl_matches:
        return fl_matches.group(1), None, fl_matches.group(2)

    # match "first middle last" where middle could be a single letter or abbreviation
    fml_matches = re.search(r"^([a-zA-Z]+) +([a-zA-Z]+\.?) +([a-zA-Z]+)$", name_string)
    if fml_matches:
        return fml_matches.group(1), fml_matches.group(2), fml_matches.group(3)

    # match "last, first"
    lf_matches = re.search(r"^([a-zA-Z]+), *([a-zA-Z]+)$", name_string)
    if lf_matches:
        return lf_matches.group(2), None, lf_matches.group(1)

    raise ValueError('Supplied name string "%s" does conform to known name formats' % (name_string, ))


class RacerSource(Enum):
    PreviousUnmatch = 1 # previously unknown identity in the database
    RecordIngestion = 2 # something currently being ingested


class Gender(Enum):
    Male = 1
    Female = 2


def _gender_from_string(gender_string):
    return Gender.Male if (gender_string.to_lower() == 'male') else Gender.Female


def _extract_age_range(unparsed_range):
    """
    :param unparsed_range: an unparsed age group
    :return: a tuple containing the min & max of the range
    """
    matches = re.search(r"([0-9]+)\-([0-9]+)", unparsed_range)
    if matches:
        return matches.groups()
    else:
        return None, None

class RacerIdentity:
    """
    represents a singular racer- either a previously matched identity, or a race record that we seek to match
    i.e. multiple race results may belong to this identity
    """
    def __init__(self, unformatted_name, age_range, gender, source,
                 racer_id = None):
        parsed_name = _extract_name(unformatted_name)
        self._first_name = parsed_name[0]
        self._middle_name = parsed_name[1]
        self._last_name = parsed_name[2]
        # TODO we'll want to parse this into somethiing...
        self._age_range = _extract_age_range(age_range)
        self._gender = _gender_from_string(gender)
        self._racer_source = source
        self._racer_id = racer_id

    def get_first_name(self):
        return self._first_name

    def get_last_name(self):
        return self._last_name

    def get_middle_name(self):
        return self._middle_name

    def get_age_range(self):
        return self._age_range

    def get_gender(self):
        return self._gender

    def get_racer_id(self):
        """
        :return: None if the identity is not a previous match, else the racer_id for the previous match
        """
        return self._racer_id


    # TODO how to appropriately represent location?


def _parse_time_millis(time_unparsed,
                       format='%H:%M:%S.%f'):
    """
    :param time_unparsed: a string expected to represent time like format
    :param format: a datetime format string
    :return: the number of milliseconds in the input time
    """
    # note this breaks on > 24 hours. to prevent the added dependency for a better lib, live with it
    dt = datetime.strptime(time_unparsed, format)
    delta = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
    return delta.total_seconds() * 1000


class RaceRecord(RacerIdentity):
    """
    An individual race record.
    Extends an identity in that all may correspond to one
    """
    def __init__(self, unformatted_name, age_range, gender, source,
                 duration, overall_place, gender_place,
                 race_id, racer_source):
        super().__init__(unformatted_name, age_range, gender, source)
        self._duration = _parse_time_millis(duration)
        self._overall_place = overall_place
        self._gender_place = gender_place
        self._race_id = race_id
        self._racer_source = racer_source

    def get_duration(self):
        return self._duration

    def get_overall_place(self):
        return self._overall_place

    def get_gender_place(self):
        return self._gender_place

    def get_race_id(self):
        return self._race_id

    def get_racer_source(self):
        """
        :return: a RacerSource enum value
        """
        return self._racer_source

