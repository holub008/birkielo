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

naive_elo <- function(results,
                      log_odds_oom_differential = 400,
                      k_factor = 1,
                      default_score = 1000) {
  results$score <- 1000
  score_history <- data.frame()
  for (ix in sort(unique(results$iteration))) {
    race_results <- results %>% 
      filter(iteration == ix)%>%
      mutate(
        race_rank = rank(time)
      )
    
    updated_racers <- data.frame()
    for (update_racer_id in race_results$racer_id) {
      racer <- race_results %>% 
        filter(racer_id == update_racer_id) %>%
        mutate(
          linear_scale_score = 10 ^ (score / log_odds_oom_differential)
        ) 

      score_increment <- race_results %>%
        filter(racer_id != update_racer_id) %>%
        mutate(
          linear_scale_competitor_score = 10 ^ (score / log_odds_oom_differential),
          p_racer = racer$linear_scale_score / (linear_scale_competitor_score + racer$linear_scale_score),
          outcome = ifelse(race_rank < racer$race_rank, 1, 0),
          score_change = k_factor * (outcome - p_racer)
        ) %>%
        pull(score_change) %>%
        sum()
      
      racer$updated_score <- racer$score + score_increment
      
      updated_racers <- bind_rows(updated_racers, racer)
    }
    
    print(head(updated_racers))
    
    results <- results %>%
      left_join(updated_racers %>% select(racer_id, updated_score), by = c('racer_id' = 'racer_id')) %>%
      mutate(
        score = ifelse(!is.na(updated_score), updated_score, score)
      ) %>%
      select(-updated_score)
    score_history <- bind_rows(score_history, updated_racers %>% select(racer_id, updated_score))
  }
  
  list(race_results,
       score_history)
}

###########################
## start control flow
###########################
population <- generate_population()
all_results <- simulate_races(population)

elo_scores <- naive_elo(all_results)
