# About
Scoring algorithms for race results. Currently only contains a naive Elo implementation.

## Naive Elo
Reduces each individual race to traditional 1v1 Elo, where all n racers are compared in n choose 2 1v1 competitions. Runs with configurable k_factor ("reactiveness" to change / strength of prior), scale parameter (how large of a point difference corresponds to a 10x increase in odds of winning), and min/max scores.


# Running
All scripts should be run the parent offline/ directory using pipenv:
```sh
pipenv run python scoring/elo_executor.py
```
