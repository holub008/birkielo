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


class RacerMatcher:

    # TODO, note that we don't currently take in previous identities
    def __init__(self, race_records):
        if len(race_records) < 1:
            raise ValueError('Cannot match an empty list of race records')

        self._race_records = race_records

    def merge_to_identities(self):
        """
        TODO this method shows somewhat poor modularity in combining the similarity, validation, and merge steps
        :return: a list of tuples. for each tuple, element 0 is the merged identity, element 1 is the race record
        indices (as input) of the match
        """
        similarity = np.zeros((len(self._race_records), len(self._race_records)))
        # as a quick heuristic to avoid n^2 scanning, build minimally viable subgroups on first name and last name
        match_propensity_ordered_racers = sorted(self._race_records,
                                                 key=lambda rr: (rr.get_first_name().lower(),
                                                                   rr.get_last_name().lower()))
        ranks = sorted(range(len(self._race_records)), key=lambda ix: (self._race_records[ix].get_first_name().lower(),
                                                                 self._race_records[ix].get_last_name().lower()))
        merged_records = []
        current_subgroup = [ranks[0]]
        representative = match_propensity_ordered_racers[0]
        for sorted_ix in range(1, len(match_propensity_ordered_racers)):
            rank_ix = ranks[sorted_ix]
            racer = match_propensity_ordered_racers[sorted_ix]
            if representative.shared_name(racer):
                current_subgroup.append(rank_ix)
            else:
                # TODO need to handle overlapped names - when several identities in a subgoup where in the same race
                # TODO just using the first representative for the identity is suboptimal
                ri = RacerIdentity(representative.get_first_name(), representative.get_middle_name(),
                                   representative.get_last_name(), representative.get_age_lower(),
                                   representative.get_age_upper(), representative.get_gender().value)
                merged_records.append((ri, current_subgroup))

                current_subgroup = [rank_ix]
                representative = racer

        return merged_records
