
def _extract_name(name_string):
    """
    employ a variety of strategies to decompose a name to its parts
    note this is a very euro-centric approach to structuring names... but then again, skiers are very european!
    :param name_string: a string of unknown format
    :return: a tuple of first name, middle name, and last name. any may be None
    """
    pass


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

