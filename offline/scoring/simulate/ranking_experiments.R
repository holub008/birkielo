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
                         sample_fraction = .5,
                         # this function gives every racer equal probability of selection
                         sample_weight_function=function(scores){runif(length(scores))},
                         # note this is the sd on normal distribution, but may change
                         individual_racer_time_spread = .3) {

  population %>%
    mutate(
      sample_weight = sample_weight_function(true_score)
    ) %>%
    sample_frac(sample_fraction, weight = sample_weight) %>%
    mutate(
      standardized_scores = scale(-true_score),
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
  racers <- results %>%
    distinct(racer_id) %>%
    mutate(score = default_score)
  
  score_history <- data.frame()
  
  updated_racers <- data.frame()
  for (ix in sort(unique(results$iteration))) {
    race_results <- results %>% 
      filter(iteration == ix)%>%
      mutate(
        race_rank = rank(time)
      ) %>%
      inner_join(racers, by = c('racer_id' = 'racer_id'))
    
    # TODO it's likely faster to just do a self antijoin
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
          outcome = ifelse(racer$race_rank < race_rank, 1, 0),
          score_change = k_factor * (outcome - p_racer)
        ) %>%
        pull(score_change) %>%
        sum()
      
      racer$updated_score <- racer$score + score_increment
      
      updated_racers <- bind_rows(updated_racers, racer)
    }
    
    racers <- racers %>%
      left_join(updated_racers %>% select(racer_id, updated_score), by = c('racer_id' = 'racer_id')) %>%
      mutate(
        score = ifelse(!is.na(updated_score), updated_score, score)
      ) %>%
      select(-updated_score)
    score_history <- bind_rows(score_history, racers %>% 
                                 select(racer_id, score) %>%
                                 mutate(iteration = ix))
  }
  
  score_history
}

mean_elo_prior <- function(rank_percentile, prior_mean, prior_sd) {
  qnorm(rank_percentile, prior_mean, prior_sd)
}

mean_elo <- function(results,
                     log_odds_oom_differential = 400,
                     k_factor = 10,
                     score_prior = function(x){mean_elo_prior(x, 1000, 200)}) {
  racers <- results %>%
    distinct(racer_id) %>%
    mutate(score = NA)
  
  score_history <- data.frame()
  
  updated_racers <- data.frame()
  for (ix in sort(unique(results$iteration))) {
    race_results <- results %>% 
      filter(iteration == ix) %>%
      mutate(
        race_rank = rank(time)
      ) %>%
      inner_join(racers, by = c('racer_id' = 'racer_id'))
    
    n_racers <- nrow(race_results)
    
    # TODO it's likely faster to just do a self antijoin
    updated_racers <- data.frame()
    for (update_racer_id in race_results$racer_id) {
      racer <- race_results %>% 
        filter(racer_id == update_racer_id) %>%
        mutate(
          linear_scale_score = 10 ^ (score / log_odds_oom_differential)
        ) 
      
      if (is.na(racer$score)) {
        racer$updated_score <- score_prior(racer$race_rank / n_racers)
      }
      else {
        score_increment <- race_results %>%
          filter(racer_id != update_racer_id) %>%
          mutate(
            lost = racer$race_rank < race_rank
          ) %>%
          group_by(lost) %>%
          summarize(
            mean_score = mean(score)
          ) %>%
          mutate(
            linear_scale_competitor_score = 10 ^ (mean_score / log_odds_oom_differential),
            p_racer = racer$linear_scale_score / (linear_scale_competitor_score + racer$linear_scale_score),
            outcome = ifelse(lost, 1, 0),
            score_change = k_factor * (outcome - p_racer)
          ) %>%
          pull(score_change) %>%
          sum()
        
        racer$updated_score <- racer$score + score_increment 
      }
      
      updated_racers <- bind_rows(updated_racers, racer)
    }
    
    racers <- racers %>%
      left_join(updated_racers %>% select(racer_id, updated_score), by = c('racer_id' = 'racer_id')) %>%
      mutate(
        score = ifelse(!is.na(updated_score), updated_score, score)
      ) %>%
      select(-updated_score)
    score_history <- bind_rows(score_history, racers %>% 
                                 select(racer_id, score) %>%
                                 mutate(iteration = ix))
  }
  
  score_history
}

empirical_distribution_smoothing <- function() {
  
}

rank_correlation_over_time <- function(historical_scores_joined) {
  historical_scores_joined %>%
    group_by(iteration) %>%
    mutate(
      rank = rank(-score)
    ) %>%
    summarize(
      true_observed_rank_correlation = cor(rank, true_rank)
    )
}

###########################
## start control flow
###########################
population <- generate_population(n_racers=1e3)
all_results <- simulate_races(population)

all_results %>% 
  inner_join(population, by = 'racer_id') %>% 
  filter(iteration == 1) %>%
  ggplot(aes(true_score, time)) + 
    geom_point()

elo_scores <- naive_elo(all_results)
elo_scores_mean_algo <- mean_elo(all_results)

final_scores_joined <- elo_scores %>%
  filter(iteration == 20) %>%
  mutate(
    predicted_rank = rank(-score)
  ) %>%
  inner_join(elo_scores_mean_algo %>%
               filter(iteration == 20) %>%
               mutate(
                 predicted_rank = rank(-score)
               ), by = c('racer_id' = 'racer_id'),
             suffix = c('.naive', '.mean'))

ggplot(final_scores_joined) + geom_point(aes(predicted_rank.naive, predicted_rank.mean))

final_scores <- elo_scores_mean_algo %>%
  filter(iteration == 20) %>%
  mutate(
    predicted_rank = rank(-score)
  )

true_joined_scores <- population %>%
  inner_join(final_scores, by = 'racer_id')

ggplot(true_joined_scores) + geom_point(aes(predicted_rank, true_rank))
ggplot(true_joined_scores) + geom_point(aes(true_rank, score))

true_joined_history <- elo_scores %>%
  inner_join(population, by = c('racer_id' = 'racer_id'))

rank_correlation_over_time(true_joined_history) %>%
  ggplot() +
    geom_point(aes(iteration, abs(true_observed_rank_correlation)))
