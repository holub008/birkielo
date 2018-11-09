from enum import Enum

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
