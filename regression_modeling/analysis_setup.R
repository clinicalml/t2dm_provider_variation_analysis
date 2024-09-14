library("lme4")
library("rms")
library("dplyr")

# Set location for output csvs
inpath <- # Set to match data_dir in config.py
outpath <- # Set to match output_dir in config.py
dir.create(file.path(outpath), showWarnings = FALSE)

# load data including only providers with >= 10 patients and normalize to mean 0 and standard deviation 1
df <- read.csv(paste(inpath, "t2dm_cohort_data_frequent_prv_only.csv", sep=""))
df$trt_date <- as.Date(df$first_treatment_date, format='%Y-%m-%d')
mu_egfr <- mean(df$egfr)
sd_egfr <- sd(df$egfr)
mu_age <- mean(df$age)
sd_age <- sd(df$age)
mu_trt_date <- mean(df$trt_date)
sd_trt_date <- sd(df$trt_date)
df %>% mutate(egfr_z = (egfr-mu_egfr)/sd_egfr,
              age_z = (age-mu_age)/sd_age,
              trt_date_z = as.numeric((trt_date-mu_trt_date)/sd_trt_date)) -> df

cat("A total of", length(unique(df$npi)), "providers and", nrow(df), "patients.\n")

# Create restricted cubic spline features
create_transformed_rcs_features <- function(df, col_name, knot_positions){
    num_knots <- length(knot_positions)
    norm_factor <- (knot_positions[num_knots] - knot_positions[1])^2
    cubic_with_last_knot <- (df[col_name] - knot_positions[num_knots])^3
    cubic_with_last_knot <- replace(cubic_with_last_knot, cubic_with_last_knot < 0, 0)
    cubic_with_second_to_last_knot <- (df[col_name] - knot_positions[num_knots - 1])^3
    cubic_with_second_to_last_knot <- replace(cubic_with_second_to_last_knot, cubic_with_second_to_last_knot < 0, 0)
    for (i in 1:(num_knots-2)){
        new_col <- paste(col_name, '_knot', i, 'of', num_knots, sep='')
        cubic_with_this_knot <- (df[col_name] - knot_positions[i])^3
        cubic_with_this_knot <- replace(cubic_with_this_knot, cubic_with_this_knot < 0, 0)
        df[new_col] <- (cubic_with_this_knot
                       - (cubic_with_second_to_last_knot
                          * (knot_positions[num_knots] - knot_positions[i])
                          / (knot_positions[num_knots] - knot_positions[num_knots - 1]))
                       + (cubic_with_last_knot
                          * (knot_positions[num_knots - 1] - knot_positions[i])
                          / (knot_positions[num_knots] - knot_positions[num_knots - 1])))/norm_factor
    }
    return(df)
}

# Use suggested knot positions in terms of quantiles from Harrell (2001)
quantiles_for_3knots <- c(.1, .5, .9)
quantiles_for_4knots <- c(.05, .35, .65, .95)
quantiles_for_5knots <- c(.05, .275, .5, .725, .95)
quantiles_for_6knots <- c(.05, .23, .41, .59, .77, .95)

# 3 knots for eGFR
egfr_quantiles_for_3knots <- quantile(df$egfr_z, probs = quantiles_for_3knots)
cat('3 knots for eGFR: ',
    egfr_quantiles_for_3knots*sd_egfr + mu_egfr,
    '\n')
df <- create_transformed_rcs_features(df, 'egfr_z', egfr_quantiles_for_3knots)

# 4 knots for eGFR
egfr_quantiles_for_4knots <- quantile(df$egfr_z, probs = quantiles_for_4knots)
cat('4 knots for eGFR: ',
    egfr_quantiles_for_4knots*sd_egfr + mu_egfr,
    '\n')
df <- create_transformed_rcs_features(df, 'egfr_z', egfr_quantiles_for_4knots)

# 5 knots for eGFR
egfr_quantiles_for_5knots <- quantile(df$egfr_z, probs = quantiles_for_5knots)
cat('5 knots for eGFR: ',
    egfr_quantiles_for_5knots*sd_egfr + mu_egfr,
    '\n')
df <- create_transformed_rcs_features(df, 'egfr_z', egfr_quantiles_for_5knots)

# Also try 5 knots for eGFR at inflection points where changes are known to occur based on kidney disease stages
egfr_splits <- c(30, 45, 60, 75, 90)
egfr_5knots_by_kidney_disease <- (egfr_splits - mu_egfr)/sd_egfr
df['egfr_z_stage'] <- df$egfr_z
df <- create_transformed_rcs_features(df, 'egfr_z_stage', egfr_5knots_by_kidney_disease)

# 6 knots for eGFR
egfr_quantiles_for_6knots <- quantile(df$egfr_z, probs = quantiles_for_6knots)
cat('6 knots for eGFR: ',
    egfr_quantiles_for_6knots*sd_egfr + mu_egfr,
    '\n')
df <- create_transformed_rcs_features(df, 'egfr_z', egfr_quantiles_for_6knots)

# 3 knots for age
age_quantiles_for_3knots <- quantile(df$age_z, probs = quantiles_for_3knots)
cat('3 knots for age: ',
    age_quantiles_for_3knots*sd_age + mu_age,
    '\n')
df <- create_transformed_rcs_features(df, 'age_z', age_quantiles_for_3knots)

# 4 knots for age
age_quantiles_for_4knots <- quantile(df$age_z, probs = quantiles_for_4knots)
cat('4 knots for age: ',
    age_quantiles_for_4knots*sd_age + mu_age,
    '\n')
df <- create_transformed_rcs_features(df, 'age_z', age_quantiles_for_4knots)

# 5 knots for age
age_quantiles_for_5knots <- quantile(df$age_z, probs = quantiles_for_5knots)
cat('5 knots for age: ',
    age_quantiles_for_5knots*sd_age + mu_age,
    '\n')
df <- create_transformed_rcs_features(df, 'age_z', age_quantiles_for_5knots)

# 6 knots for age
age_quantiles_for_6knots <- quantile(df$age_z, probs = quantiles_for_6knots)
cat('6 knots for age: ',
    age_quantiles_for_6knots*sd_age + mu_age,
    '\n')
df <- create_transformed_rcs_features(df, 'age_z', age_quantiles_for_6knots)

# 3 knots for treatment date
trt_date_quantiles_for_3knots <- quantile(df$trt_date_z, probs = quantiles_for_3knots)
cat('3 knots for treatment date: ',
    paste(strptime(trt_date_quantiles_for_3knots*sd_trt_date + mu_trt_date, format='%Y-%m-%d')),
    '\n')
df <- create_transformed_rcs_features(df, 'trt_date_z', trt_date_quantiles_for_3knots)

# 4 knots for treatment date
trt_date_quantiles_for_4knots <- quantile(df$trt_date_z, probs = quantiles_for_4knots)
cat('4 knots for treatment date: ',
    paste(strptime(trt_date_quantiles_for_4knots*sd_trt_date + mu_trt_date, format='%Y-%m-%d')),
    '\n')
df <- create_transformed_rcs_features(df, 'trt_date_z', trt_date_quantiles_for_4knots)

# 5 knots for treatment date
trt_date_quantiles_for_5knots <- quantile(df$trt_date_z, probs = quantiles_for_5knots)
cat('5 knots for treatment date: ',
    paste(strptime(trt_date_quantiles_for_5knots*sd_trt_date + mu_trt_date, format='%Y-%m-%d')),
    '\n')
df <- create_transformed_rcs_features(df, 'trt_date_z', trt_date_quantiles_for_5knots)

# 6 knots for treatment date
trt_date_quantiles_for_6knots <- quantile(df$trt_date_z, probs = quantiles_for_6knots)
cat('6 knots for treatment date: ',
    paste(strptime(trt_date_quantiles_for_6knots*sd_trt_date + mu_trt_date, format='%Y-%m-%d')),
    '\n')
df <- create_transformed_rcs_features(df, 'trt_date_z', trt_date_quantiles_for_6knots)