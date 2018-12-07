library(dplyr)

# assumes the underlying distribution of skier skill is normal
# TODO would be interesting to experiment with other distributions (particularly other exponential family)
generate_population <- function(n_racers=1e4) {
  skill <- rnorm(n_racers, 1000, 400)
  
  data.frame(true_score = skill,
             racer_id = 1:n_racers) %>%
    mutate(true_rank = rank(-true_score))
}

# assumes that times are normally distributed, with expectation of finish time correlated with racer skill
# TODO is normal a reasonable assumption?
# note that currently, the time is not reasonably interpretted
execute_race <- function(population,
                         sample_fraction = .1,
                         # this function gives every racer equal probability of selection
                         sample_weight_function=function(scores){runif(length(scores))},
                         # note this is the sd on normal distribution, but may change
                         individual_racer_time_spread = 1) {

  population %>%
    mutate(
      sample_weight = sample_weight_function(true_score)
    ) %>%
    sample_frac(sample_fraction) %>%
    mutate(
      standardized_scores = scale(true_score),
      time = sapply(standardized_scores, function(ss) rnorm(1, ss, individual_racer_time_spread))
    ) %>%
    select(racer_id, time)
}

simulate_races <- function(population,
                           n_trials = 20,
                           ...) {
  total_results <- data.frame()
  lapply(1:n_trials, function(ix) {
    race_results <- execute_race(population, ...)
    race_results$iteration <- ix
    race_results}) %>%
  bind_rows()
}

###########################
## start control flow
###########################
population <- generate_population()
all_results <- simulate_races(population)
