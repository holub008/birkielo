import numpy as np
from RacerIdentity import RacerIdentity

##########################
# The matching strategy I'm planning is heuristic & unsupervised (minus some human eyeballing) in this iteration.
# One could certainly imagine this could be turned into a supervised learning task with labelled data... another time!
#
# The planned method:
# Take a candidate set, X, of racer identities from results being ingested
# And a known set, Y, of racer identities we've previously built
# (Note we are ignoring a third set, Z, of racer identities from previously ingested results that we didn't match)
# Compare all pairs in the self-cartesian product of (X U Y). The comparison method returns a score, which we hope is
# proportional to the odds of the identities matching.
# If we imagine the comparisons implying an undirected graph (hopefully our comparison function is symmetric!),
# we hope our graph contains "disjoint" (for lack of a mathematical term) subgroups by edge weight distribution
# From these subgroups, we hope to either 1. merge all the identities to a single identity if all belong to X
# or 2. match all the identities to to a single y, if a y exists in the subgroup
# There are of course some difficulties - different people may have very high similarities!
# One give away: if a subgroup contains two records from the same race, at least two identities exist
# Or, stated as the pigeonhole principle, a subgroup is larger than the number of considered races
# How to resolve?
# We might look for even tighter sub-subgroups, or use a matching score with different sensitivities.
# At this point, it's easiest to give up and leave the identity unmatched for now.
# If a subgroup did satisfy our "easy" properties for matching or merging go for it!
##########################

def compute_similarity(record1, record2):
    """
    :param record1: a RacerIdentity instance for comparison
    :param record2: a RacerIdentity instance for comparison
    :return: a continuous valued similarity score
    """
    # this is an extremely simplistic start
    return 1 if (record1.shared_name(record2)) else 0


class RacerMatcher:

    # TODO, note that we don't currently take in previous identities
    def __init__(self, race_records):
        self._race_records = race_records

        similarity = np.zeros((len(race_records), len(race_records)))
        for ix1, race_record1 in enumerate(self._race_records):
            print(ix1)
            for ix2, race_record2 in enumerate(race_records[0:(ix1+1)]):
                similarity[ix1, ix2] = race_record1.shared_name(race_record2)

        self._similarity = similarity

    def merge_to_identity(self,
                          match_threshold=0):
        """

        :param match_threshold: the minimum threshold on similarity for a record to be matched to a another
        :return: a list of tuples. for each tuple, element 0 is the merged identity, element 1 is the race record
        indices (as input) of the match
        """
        merged_records = []
        for race_record_ix, race_record in enumerate(self._race_records):
            similarities = self._similarity[race_record_ix, ]
            # TODO need to validate our subgroup by checking for overlapped names
            subgroup = np.argwhere(similarities > match_threshold)
            # TODO our merge strategy is to just accept the first entry
            representative = subgroup[0]
            # TODO need to adjust age range based on year of race & current date
            ri = RacerIdentity(representative.get_first_name(), representative.get_middle_name(),
                               representative.get_last_name(), representative.get_age_lower(),
                               representative.get_age_upper(), representative.get_gender())

            merged_records.append((ri,subgroup))

        return merged_records