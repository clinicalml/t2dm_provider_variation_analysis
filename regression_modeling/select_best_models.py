import sys
from os.path import dirname, abspath

import numpy as np
import pandas as pd

sys.path.append(dirname(dirname(abspath(__file__))))
import config

def compute_aic_and_log_likelihood(model_name,
                                   prediction_df,
                                   sample_df,
                                   num_params):
    '''
    Compute AIC and log likelihood for model
    @param model_name: str, name of column in prediction_df
    @param prediction_df: pandas DataFrame, logits from models
    @param sample_df: pandas DataFrame, matches samples in prediction_df, metformin column is true binary label
    @param num_params: int, number of parameters in model
    @return: 1. float, AIC
             2. float, log likelihood
    '''
    model_logits = prediction_df[model_name]
    model_probs  = 1./(1. + np.exp(-1*model_logits))
    model_log_likelihood_per_sample = np.where(sample_df['metformin'] == 1, np.log(model_probs), np.log(1 - model_probs))
    model_log_likelihood = np.sum(model_log_likelihood_per_sample)
    return 2 * num_params - 2 * model_log_likelihood, model_log_likelihood
    
def identify_best_models():
    '''
    Print names of models with lowest AIC:
    1. model without random effect
    2. model with random intercept or slope
    @return: None
    '''
    num_params_df    = pd.read_csv(config.output_dir + 'glm_num_params.csv')
    num_params_df    = num_params_df.loc[np.logical_and.reduce((~num_params_df['model_name'].str.contains('e5'),
                                                                ~num_params_df['model_name'].str.contains('e6'),
                                                                ~num_params_df['model_name'].str.contains('a5'),
                                                                ~num_params_df['model_name'].str.contains('a6'),
                                                                ~num_params_df['model_name'].str.contains('t5'),
                                                                ~num_params_df['model_name'].str.contains('t6')))]
    prediction_df    = pd.read_csv(config.output_dir + 'model_predictions.csv')
    sample_df        = pd.read_csv(config.data_dir + 't2dm_cohort_data_frequent_prv_only.csv')
    model_names      = num_params_df['model_name'].values
    model_num_params = num_params_df['num_params'].values
    
    lowest_aic_without_random_effects = float('inf')
    lowest_aic_with_random_effects    = float('inf')
    highest_loglik_without_random_effects = float('-inf')
    highest_loglik_with_random_effects    = float('-inf')
    aics = []
    log_likelihoods = []
    for model_name, num_params in zip(model_names, model_num_params):
        aic, log_likelihood = compute_aic_and_log_likelihood(model_name,
                                                             prediction_df,
                                                             sample_df,
                                                             num_params)
        aics.append(aic)
        log_likelihoods.append(log_likelihood)
        if model_name.startswith('glm_without_random_effects_'):
            if aic < lowest_aic_without_random_effects:
                best_model_without_random_effects_by_aic    = model_name
                lowest_aic_without_random_effects           = aic
            if log_likelihood > highest_loglik_without_random_effects:
                best_model_without_random_effects_by_loglik = model_name
                highest_loglik_without_random_effects       = log_likelihood
        else:
            if aic < lowest_aic_with_random_effects:
                best_model_with_random_effects_by_aic       = model_name
                lowest_aic_with_random_effects              = aic
            if log_likelihood > highest_loglik_with_random_effects:
                best_model_with_random_effects_by_loglik    = model_name
                highest_loglik_with_random_effects          = log_likelihood
    
    num_params_df['AIC'] = aics
    num_params_df['loglik'] = log_likelihoods
    num_params_df.to_csv(config.output_dir + 'model_aics.csv',
                         index = False)
    print('Best model without random effects by AIC: ' + best_model_without_random_effects_by_aic 
          + ', AIC: ' + str(lowest_aic_without_random_effects))
    print('Best model with random effects by AIC: '    + best_model_with_random_effects_by_aic
          + ', AIC: ' + str(lowest_aic_with_random_effects))
    print('Best model without random effects by log likelihood: ' + best_model_without_random_effects_by_loglik
          + ', log likelihood: ' + str(highest_loglik_without_random_effects))
    print('Best model with random effects by log likelihood: ' + best_model_with_random_effects_by_loglik
          + ', log likelihood: ' + str(highest_loglik_with_random_effects))
    
if __name__ == '__main__':
    
    identify_best_models()