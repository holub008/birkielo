from racer_identity import RacerIdentity
from db import get_connection

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


def mode_or_random(lst):
    """
    this implementation is a suboptimal n^2
    NOTE: None does not count towards towards the mode! this is desirable for the matching use case where missing data
    truly does imply "no vote" towards the truth
    :param lst: a list of any comparable objects
    :return:  the mode, or, if lst is multi-modal, an arbitrary choice among the multi-modes. None if no non-none elements
    """
    lst_present = [x for x in lst if x]
    if not len(lst_present):
        return None
    return max(set(lst_present), key=lst_present.count)


def load_existing_racer_identities(connection_supplier=lambda: get_connection()):
    cursor = connection_supplier().cursor()
    query = "SELECT id, first_name, middle_name, last_name, age_lower, age_upper, gender FROM racer"
    cursor.execute(query)
    results = cursor.fetchall()
    racer_identities = [RacerIdentity(x[1], x[2], x[3], x[4], x[5], x[6], x[0]) for x in results]

    return racer_identities


class RacerMatcher:

    def __init__(self, race_records, existing_identities_supplier=lambda: load_existing_racer_identities()):
        if len(race_records) < 1:
            raise ValueError('Cannot match an empty list of race records')

        self._race_records = race_records
        self._existing_racer_identities = existing_identities_supplier()

    def merge_to_identities(self):
        """
        match new newly supplied race records to either existing or new racer identities
        TODO this method doesn't implement all of the desired functionality in matching or use all available signals
        TODO this method doesn't communicate when an existing identity should be updated (vs. just newly inserted)
        :return: a list of tuples. for each tuple, element 0 is the merged identity, element 1 is the race record
        indices (as input) of the match
        """
        # it's critical that the input race records come first
        all_records = self._race_records + self._existing_racer_identities
        # as a quick heuristic to avoid n^2 scanning, build minimally viable subgroups on first name and last name
        # note that these two lists need to be generated from the exact same
        match_propensity_ordered_racers = sorted(all_records,
                                                 key=lambda rr: (rr.get_first_name().lower(),
                                                                   rr.get_last_name().lower()))
        ranks = sorted(range(len(all_records)), key=lambda ix: (all_records[ix].get_first_name().lower(),
                                                                all_records[ix].get_last_name().lower()))
        merged_records = []
        current_subgroup = [ranks[0]]
        representative = match_propensity_ordered_racers[0]
        for sorted_ix in range(1, len(match_propensity_ordered_racers)):
            rank_ix = ranks[sorted_ix]
            racer = match_propensity_ordered_racers[sorted_ix]
            if representative.shared_name(racer):
                current_subgroup.append(rank_ix)
            else:
                subgroup_racers = [all_records[x] for x in current_subgroup]
                racer_id = mode_or_random([r.get_racer_id() for r in subgroup_racers])

                # TODO just using the first representative for the identity is suboptimal. ideally we merge to consensus
                # doing something similar to what is done for racer id
                ri = RacerIdentity(representative.get_first_name(), representative.get_middle_name(),
                                   representative.get_last_name(), representative.get_age_lower(),
                                   representative.get_age_upper(), representative.get_gender().value,
                                   racer_id=racer_id)

                # filters out identities already stored in DB - those we don't wish to insert
                current_subgroup_for_insert = [rank_ix for rank_ix in current_subgroup
                                               if rank_ix < len(self._race_records)]
                merged_records.append((ri, current_subgroup_for_insert))

                current_subgroup = [rank_ix]
                representative = racer

        # if the identity has 0 new race records, it was an existing identity & there's nothing to do
        return [mr for mr in merged_records if len(mr[1]) > 0]
