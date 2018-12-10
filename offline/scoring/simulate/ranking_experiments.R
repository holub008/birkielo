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
  qnorm(1 - rank_percentile, prior_mean, prior_sd)
}

mean_elo <- function(results,
                     log_odds_oom_differential = 400,
                     k_factor = 10,
                     score_prior = function(x){mean_elo_prior(x, 1000, 200)}) {
  racers <- results %>%
    distinct(racer_id) %>%
    mutate(score = NA)
  
  score_history <- data.frame()
  
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

eds_prior <- function(rank_percentile, prior_mean = 1000, prior_sd = 400) {
  finite_q_percentile <- max(min(rank_percentile, .999), .001)
  score <- qnorm(1 - finite_q_percentile, prior_mean, prior_sd)
}

# I find this method simpler & more interprettable (in terms of parameterization) than Elo based methods. But it suffers several issues, relative to Elo: 
#  1. (without primes) assumes the range of talent is fixed over time; if you're the top racer in the race, the prime is your only incentive opportunity to improve your score
#  2. (if implementing primes) it becomes difficult / impossible to interpret scores over time; since the score distribution would be otherwise fixed over time
#      the prime can only have the effect of increasing the max attainable score
# TODO smoothing_factor > 0 suffers decay, shrinking variance in scores. this is because a 20% dop in score != a 20% increase in score in absolute terms.
empirical_distribution_smoothing <- function(results,
                                             smoothing_factor = .5,
                                             first_place_prime = 2,
                                             prior_threshold = .9, # if greater than 1-prior_threshold % of racers in a given race do not have a previous score, all racers are scored using the prior (but we still smooth)
                                             prior = eds_prior,
                                             # todo this is leaky (or poorly shared information) from the prior function
                                             prior_mean = 1000) {

  racers <- results %>%
    distinct(racer_id) %>%
    mutate(score = NA)
  
  score_history <- data.frame()
  
  for (ix in sort(unique(results$iteration))) {
    race_results <- results %>% 
      filter(iteration == ix) %>%
      mutate(
        race_rank = rank(time)
      ) %>%
      inner_join(racers, by = c('racer_id' = 'racer_id'))
    
    n_racers <- nrow(race_results)
    
    race_scorer <- prior
    if (mean(!is.na(race_results$score)) >= prior_threshold) {
      race_scorer <- function(percentile) {
        quantile(race_results$score, 1 - percentile, na.rm = TRUE)
      }
    }

    updated_racers <- race_results %>%
      mutate(
        # note that discrete rankings don't naturally map to an inclusive 0-1 range - the below makes that mapping
        uniform_rank_percentile = (race_rank - 1) / (n_racers -1),
        previous_score = ifelse(is.na(score), prior_mean, score),
        raw_score = sapply(uniform_rank_percentile, race_scorer),
        updated_score = (1 - smoothing_factor) * raw_score + smoothing_factor * previous_score
      ) %>%
      select(racer_id, updated_score)
    
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
all_results <- simulate_races(population, n_trials=200)

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

#####
eds_scores <- empirical_distribution_smoothing(all_results)
eds_scores %>%
  group_by(iteration) %>%
  summarize(
    mean_score = mean(score, na.rm = T),
    sd_score = sd(score, na.rm = T),
    min_score = min(score, na.rm=T),
    max_score = max(score, na.rm = T)
  ) %>% View()

eds_scores_joined <- eds_scores %>%
  filter(iteration == max(iteration)) %>%
  mutate(
    predicted_rank = rank(-score)
  ) %>%
  inner_join(population, by = c('racer_id' = 'racer_id'))
ggplot(eds_scores_joined) +
  geom_point(aes(true_rank, predicted_rank))

eds_scores %>%
  inner_join(population, by = c('racer_id' = 'racer_id')) %>%
  rank_correlation_over_time() %>%
  ggplot() +
  geom_point(aes(iteration, true_observed_rank_correlation))
