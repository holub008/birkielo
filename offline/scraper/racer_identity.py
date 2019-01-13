import re
from enum import Enum
from datetime import datetime
from datetime import timedelta
from string import digits


class RacerSource(Enum):
    PreviousUnmatch = 1 # previously unknown identity in the database
    RecordIngestion = 2 # something currently being ingested


class Gender(Enum):
    Male = "male"
    Female = "female"


class RacerIdentity:
    """
    represents a singular racer- either a previously matched identity, or a race record that we seek to match
    i.e. multiple race results may belong to this identity
    """
    def __init__(self, first_name, middle_name, last_name, age_lower, age_upper, gender,
                 racer_id=None):
        self._first_name = first_name
        self._middle_name = middle_name
        self._last_name = last_name
        self._age_range_lower = age_lower
        self._age_range_upper = age_upper
        self._gender = _gender_from_string(gender)
        self._racer_id = racer_id

    def get_first_name(self):
        return self._first_name

    def get_last_name(self):
        return self._last_name

    def get_middle_name(self):
        return self._middle_name

    def get_age_lower(self):
        return self._age_range_lower

    def get_age_upper(self):
        return self._age_range_upper

    def get_gender(self):
        return self._gender

    def shared_name(self, other,
                    include_middle = False):
        if self.get_first_name().lower() == other.get_first_name().lower():
            if self.get_last_name().lower() == other.get_last_name().lower():
                # handle this case somewhat carefully, since middle names are often missing
                if not include_middle:
                    return True
                elif self.get_middle_name() is None:
                    # this is a questionable choice -
                    return True
                else:
                    if other.get_middle_name() is None:
                        # same choice as above
                        return True
                    return self.get_middle_name().lower == other.get_middle_name.lower()
            else:
                return False
        else:
            return False

    def get_racer_id(self):
        """
        :return: None if the identity is not a previous match, else the racer_id for the previous match
        """
        return self._racer_id

    # TODO how to appropriately represent location?


def extract_name(name_string):
    """
    employ a variety of strategies to decompose a name to its parts
    note this is a very euro-centric approach to structuring names... but then again, skiers are very european!
    :param name_string: a string of unknown format
    :return: a tuple of first name, middle name, and last name. any may be None
    """
    # removing any numbers and weird characters
    name_string = name_string.replace(u'\xa0', u' ')\
        .replace(u'\x8e', u' ')\
        .translate({ord(k): None for k in digits})

    # TODO should write tests on this, since regression is so likely
    # match "first last" - this obviously isn't an all encompassing
    fl_matches = re.search(r"^([a-zA-Z\-\.]+) +([a-zA-Z\-\']+) *$", name_string)
    if fl_matches:
        return fl_matches.group(1), None, fl_matches.group(2)

    # match "first middle last" where middle could be a single letter or abbreviation
    fml_matches = re.search(r"^([a-zA-Z\-\.]+) +(\(?\"?[a-zA-Z\.]+\.?\"?\)?) +([a-zA-Z\-\']+) *$", name_string)
    if fml_matches:
        return fml_matches.group(1), fml_matches.group(2), fml_matches.group(3)

    # match "last, first"
    lf_matches = re.search(r"^([a-zA-Z\-\' ]+), *([a-zA-Z\-\.]+)$", name_string)
    if lf_matches:
        return lf_matches.group(2), None, lf_matches.group(1)

    # match "last, first middle"
    lfm_matches = re.search(r"^([a-zA-Z\-\' ]+), *([a-zA-Z\-\.]+) +([a-zA-Z\-]+\.?) *$", name_string)
    if lfm_matches:
        return lfm_matches.group(2), lfm_matches.group(3), lfm_matches.group(1)

    print('Supplied name string "%s" does conform to known name formats' % (name_string, ))
    return None, None, None


def _parse_time_millis(time_unparsed,
                       time_format='%H:%M:%S',
                       time_format_fallback = '%M:%S'):
    """
    :param time_unparsed: a string expected to represent time like format
    :param time_format: a datetime format string
    :param time_format_fallback: a alternative time format string
    :return: the number of milliseconds in the input time
    """
    # note this breaks on > 24 hours. to prevent the added dependency for a better lib, live with it
    dt = None
    try:
        dt = datetime.strptime(time_unparsed, time_format)
    except:
        try:
            dt = datetime.strptime(time_unparsed, time_format_fallback)
        except:
            try:
                dt = datetime.strptime(time_unparsed, time_format_fallback_fallback)
            except:
                print('Failed to parse a race time from "%s"' % (time_unparsed,))

    delta = timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
    return delta.total_seconds() * 1000


def _gender_from_string(gender_string):
    if gender_string.lower() == 'male' or gender_string.lower() == 'm':
        return Gender.Male
    elif gender_string.lower() == 'female' or gender_string.lower() == 'f':
        return Gender.Female
    else:
        raise ValueError('Supplied gender string "%s" does not match expected formats' % (gender_string,))


def _extract_age_range(unparsed_range):
    """
    :param unparsed_range: an unparsed age group
    :return: a tuple containing the min & max of the range
    """
    matches = re.search(r"([0-9]+)\-([0-9]+)", unparsed_range)
    if matches:
        return (int(x) for x in matches.groups())
    else:
        matches = re.search(r"([0-9]+)", unparsed_range)

        if matches:
            return int(matches.group(1)), int(matches.group(1))
        else:
            return None, None


class RaceRecord(RacerIdentity):
    """
    An individual race record.
    Extends an identity in that all may correspond to one
    """
    def __init__(self, unformatted_name, unformatted_age_range, gender,
                 duration, overall_place, gender_place,
                 race_id, racer_source):
        parsed_name = extract_name(unformatted_name)
        age_range = (None, None) if (unformatted_age_range is None) else _extract_age_range(unformatted_age_range)

        super().__init__(parsed_name[0], parsed_name[1], parsed_name[2], age_range[0], age_range[1], gender)

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
