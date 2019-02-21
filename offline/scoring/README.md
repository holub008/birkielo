# About
Scoring algorithms for race results. Currently contains a Naive Elo implementation and several variants.

## Naive Elo
Reduces each individual race to traditional 1v1 Elo, where all n racers are compared in n choose 2 1v1 competitions. 
Runs with configurable k_factor ("reactiveness" to change / strength of prior), scale parameter (how large of a point 
difference corresponds to a 10x increase in odds of winning), and min/max scores.

## Nearest Neighbor Elo
Same as Naive Elo, but instead of comparing to all other n-1 racers for a given racer, only compare to the nearest
k * (n-1) racers.

## Mean Elo
For each racer, compute mean of beaten and beating racers. Perform standard elo update using these two aggregates.

# Running
All scripts should be run the parent offline/ directory using pipenv. To update scores in production:
```sh
pipenv run python scoring/elo_executor.py
```
