# This script assumes the variables in analysis_setup.R and generated_script_to_fit_glms.R are available

prepare_transformed_features <- function(df){
    df$trt_date <- as.Date(df$first_treatment_date, format='%Y-%m-%d')
    df %>% mutate(egfr_z = (egfr-mu_egfr)/sd_egfr,
                  age_z = (age-mu_age)/sd_age,
                  trt_date_z = as.numeric((trt_date-mu_trt_date)/sd_trt_date)) -> df

    # TODO: create features for the # of knots in the specified models below
    df <- create_transformed_rcs_features(df, 'egfr_z', egfr_quantiles_for_4knots)
    df <- create_transformed_rcs_features(df, 'age_z', age_quantiles_for_4knots)
    df <- create_transformed_rcs_features(df, 'trt_date_z', trt_date_quantiles_for_4knots)
    return(df)
}

best_model_without_random_effects <- model_without_random_effects_e4_a4_t4 # TODO: set to the model with highest log likelihood, name starts with model
best_model_with_random_effects <- model_with_random_slopes_e4_a4_t4 # TODO: set to the model with highest log likelihood, name starts with model

category_0_df <- read.csv(paste(outpath, "category_0_samples_for_plotting.csv", sep=""))
category_0_df <- prepare_transformed_features(category_0_df)
category_0_pred <- predict(best_model_without_random_effects, newdata = category_0_df)

category_0_npi_df <- read.csv(paste(outpath, "category_0_samples_with_npis_for_plotting.csv", sep=""))
category_0_npi_df <- prepare_transformed_features(category_0_npi_df)
category_0_npi_pred <- predict(best_model_with_random_effects, newdata = category_0_npi_df)

category_1_df <- read.csv(paste(outpath, "category_1_samples_for_plotting.csv", sep=""))
category_1_df <- prepare_transformed_features(category_1_df)
category_1_pred <- predict(best_model_without_random_effects, newdata = category_1_df)

category_1_npi_df <- read.csv(paste(outpath, "category_1_samples_with_npis_for_plotting.csv", sep=""))
category_1_npi_df <- prepare_transformed_features(category_1_npi_df)
category_1_npi_pred <- predict(best_model_with_random_effects, newdata = category_1_npi_df)

category_2_df <- read.csv(paste(outpath, "category_2_samples_for_plotting.csv", sep=""))
category_2_df <- prepare_transformed_features(category_2_df)
category_2_pred <- predict(best_model_without_random_effects, newdata = category_2_df)

category_2_npi_df <- read.csv(paste(outpath, "category_2_samples_with_npis_for_plotting.csv", sep=""))
category_2_npi_df <- prepare_transformed_features(category_2_npi_df)
category_2_npi_pred <- predict(best_model_with_random_effects, newdata = category_2_npi_df)

category_3_df <- read.csv(paste(outpath, "category_3_samples_for_plotting.csv", sep=""))
category_3_df <- prepare_transformed_features(category_3_df)
category_3_pred <- predict(best_model_without_random_effects, newdata = category_3_df)

category_3_npi_df <- read.csv(paste(outpath, "category_3_samples_with_npis_for_plotting.csv", sep=""))
category_3_npi_df <- prepare_transformed_features(category_3_npi_df)
category_3_npi_pred <- predict(best_model_with_random_effects, newdata = category_3_npi_df)

category_4_df <- read.csv(paste(outpath, "category_4_samples_for_plotting.csv", sep=""))
category_4_df <- prepare_transformed_features(category_4_df)
category_4_pred <- predict(best_model_without_random_effects, newdata = category_4_df)

category_4_npi_df <- read.csv(paste(outpath, "category_4_samples_with_npis_for_plotting.csv", sep=""))
category_4_npi_df <- prepare_transformed_features(category_4_npi_df)
category_4_npi_pred <- predict(best_model_with_random_effects, newdata = category_4_npi_df)

category_5_df <- read.csv(paste(outpath, "category_5_samples_for_plotting.csv", sep=""))
category_5_df <- prepare_transformed_features(category_5_df)
category_5_pred <- predict(best_model_without_random_effects, newdata = category_5_df)

category_5_npi_df <- read.csv(paste(outpath, "category_5_samples_with_npis_for_plotting.csv", sep=""))
category_5_npi_df <- prepare_transformed_features(category_5_npi_df)
category_5_npi_pred <- predict(best_model_with_random_effects, newdata = category_5_npi_df)

category_pred_df <- data.frame(category_0_pred, category_1_pred, category_2_pred, category_3_pred, category_4_pred, category_5_pred)
category_npi_pred_df <- data.frame(category_0_npi_pred, category_1_npi_pred, category_2_npi_pred, category_3_npi_pred, category_4_npi_pred, category_5_npi_pred)
write.csv(category_pred_df, paste(outpath, "category_predictions_for_plotting.csv", sep=""))
write.csv(category_npi_pred_df, paste(outpath, "category_predictions_with_npis_for_plotting.csv", sep=""))