import re


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


class RacerIdentity:
    """
    represents a singular racer
    i.e. multiple race results will belong
    """
    def __init__(self):
        pass

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
        :return: None if the identity has yet to be matched, else the the racer id
        """

    # TODO how to appropriately represent location?

