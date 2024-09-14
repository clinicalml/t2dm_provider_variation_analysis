import numpy as np
from scipy.stats import chi2

def run_chi2_test(cont_table):
    '''
    Compute chi-squared statistic for contingency table
    @param cont_table: numpy array, contingency table
    '''
    assert len(cont_table.shape) == 2
    row_sums = cont_table.sum(axis = 1, keepdims = True)
    col_sums = cont_table.sum(axis = 0, keepdims = True)
    total = cont_table.sum()
    expected_table = row_sums * col_sums / total
    chi2_stat = np.sum(np.square(cont_table - expected_table))
    df = (cont_table.shape[0] - 1) * (cont_table.shape[1] - 1)
    pval = chi2.sf(chi2_stat, df)
    print('Chi-squared statistic: ' + str(chi2_stat))
    print('p-value: ' + str(pval))

if __name__ == '__main__':

    contingency_table = # TODO: put number of patients in each eGFR and treatment bin into a 2 x 5 numpy array
    # these numbers are printed by compute_cohort_stats.py
    # these are the numbers in Table 1 of the paper
    
    run_chi2_test(contingency_table)