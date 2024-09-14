import sys
from os.path import dirname, abspath

import numpy as np
import pandas as pd
from scipy.stats import chi2, rankdata, norm

sys.path.append(dirname(dirname(abspath(__file__))))
import config

def run_benjamini_hochberg(p_value_df,
                           fdr = .05):
    '''
    Run Benjamini-Hochberg multiple hypothesis correction 
    to identify which null hypotheses can be rejected while maintaining expected false discovery rate
    @param p_value_df: pandas dataframe, contains column called 'P-values' with float p-values from hypothesis tests,
                       will be modified and returned
    @param fdr: float, desired false discovery rate
    @return: pandas dataframe indicating which null hypotheses were rejected
    '''
    p_values = p_value_df['P-value'].values
    assert np.all(np.logical_and(p_values >= 0, p_values <= 1))
    assert fdr >= 0
    assert fdr <= 1
    
    p_value_ranks                  = rankdata(p_values, method = 'min')
    critical_vals                  = p_value_ranks / float(len(p_values)) * fdr
    p_value_df['Rank']             = p_value_ranks
    p_value_df['Critical value']   = critical_vals
    p_value_df.sort_values(by      = 'Rank',
                           inplace = True)
    reject_to_rank                 = p_value_df.loc[p_value_df['P-value'] < p_value_df['Critical value']]['Rank'].max()
    p_value_df['Reject null']      = np.where(p_value_df['Rank'] <= reject_to_rank, 1, 0)
    return p_value_df

def perform_glrts():
    '''
    Perform a GLRT for whether including provider-specific random effects results in better fit
    Then perform a GLRT for whether each provider differs from general policy
    '''
    sample_df      = pd.read_csv(config.data_dir + 't2dm_cohort_data_frequent_prv_only.csv')
    prediction_df  = pd.read_csv(config.output_dir + 'model_predictions.csv')
    num_params_df  = pd.read_csv(config.output_dir + 'glm_num_params.csv')
    m1_model_name  = config.best_model_without_random_effects
    m2_model_name  = config.best_model_with_random_effects
    m1_num_params  = 12 # if family includes up to 4 knots per feature, note this is maximum # of params in family not # params in best model
    m2_num_params  = 18 # if family includes up to 4 knots per feature, note this is maximum # of params in family not # params in best model
    print('Comparing ' + m1_model_name + ' from family with ' + str(m1_num_params) + ' parameters and '
          + m2_model_name + ' from family with ' + str(m2_num_params) + ' parameters')
    
    m1_logits = prediction_df[m1_model_name]
    m2_logits = prediction_df[m2_model_name]
    
    m1_probs = 1./(1. + np.exp(-1*m1_logits))
    m2_probs = 1./(1. + np.exp(-1*m2_logits))
    
    m1_log_likelihood_per_sample = np.where(sample_df['metformin'] == 1, np.log(m1_probs), np.log(1 - m1_probs))
    m2_log_likelihood_per_sample = np.where(sample_df['metformin'] == 1, np.log(m2_probs), np.log(1 - m2_probs))
    
    m1_log_likelihood = np.sum(m1_log_likelihood_per_sample)
    m2_log_likelihood = np.sum(m2_log_likelihood_per_sample)
    print('Log likelihood of model without random effects: ' + str(m1_log_likelihood))
    print('Log likelihood of model with random intercepts: ' + str(m2_log_likelihood))
    
    g_stat = 2 * (m2_log_likelihood - m1_log_likelihood)
    print('G-statistic: ' + str(g_stat))
    pval = 1. - chi2.cdf(g_stat, df = m2_num_params - m1_num_params)
    print('P-value: ' + str(pval))
    
    npis        = sample_df['npi'].values
    unique_npis = np.unique(npis)
    npi_gstats  = np.empty(len(unique_npis))
    npi_pvals   = np.empty(len(unique_npis))
    for i, npi in enumerate(unique_npis):
        npi_idxs = np.argwhere(npis == npi).flatten()
        npi_m1_log_likelihood_per_sample = m1_log_likelihood_per_sample[npi_idxs]
        npi_m2_log_likelihood_per_sample = m2_log_likelihood_per_sample[npi_idxs]
        npi_m1_log_likelihood = np.sum(npi_m1_log_likelihood_per_sample)
        npi_m2_log_likelihood = np.sum(npi_m2_log_likelihood_per_sample)
        g_stat = 2 * (npi_m2_log_likelihood - npi_m1_log_likelihood)
        pval   = 1. - chi2.cdf(g_stat, df = m2_num_params - m1_num_params)
        npi_gstats[i] = g_stat
        npi_pvals[i]  = pval
    
    npi_pval_df = pd.DataFrame(data    = {'NPI'    : unique_npis,
                                          'G-stat' : npi_gstats,
                                          'P-value': npi_pvals},
                               columns = ['NPI', 'G-stat', 'P-value'])
    npi_pval_df = run_benjamini_hochberg(npi_pval_df, fdr = .10)
    npi_pval_df.to_csv(config.output_dir + 'npi_glrt_pvalues.csv',
                       index = False)
    
if __name__ == '__main__':
    
    perform_glrts()