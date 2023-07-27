import os
import scipy.signal as signal
import scipy.stats as stats
import numpy as np
import pandas as pd
import yaml
import statsmodels.api as sm

###############################################################################
def calc_pre_post(df, event, t_pre, t_post, measure='mean'):
    """
    Compute the average over a defined pre and post period.
    
    Parameters
    ----------    
    df : DataFrame
        Pandas DataFrame with data to calculate over.
    t_pre: tuple
        Time points for pre-event period (start, end)
    t_post : tuple
        Time points for pre-event period (start, end)
    measure : str, optional
        Specify metric used to calculate pre-post, by default 'mean'.
    
    Returns
    -------
    DataFrame
        Averaged data across the give t_pre and t_post
    """

    df_pre = df[df['time_trial'].between(
        t_pre[0], t_pre[1])].reset_index(drop=True)
    df_post = df[df['time_trial'].between(
        t_post[0], t_post[1])].reset_index(drop=True)
    # add `epoch` column
    df_pre['epoch'] = f'pre-{event}'
    df_post['epoch'] = f'post-{event}'
    # recombine values and groupby new epoch var
    df_prepost = pd.concat([df_pre, df_post])

    if measure == 'mean':
        return df_prepost.groupby(['Animal', 'epoch']).mean().reset_index()
    elif measure == 'max':
        df_prepost = df_prepost.groupby(
            ['Animal', 'time_trial', 'epoch']).mean().reset_index()
        return df_prepost.groupby(['Animal', 'epoch']).max().reset_index()


################################################################################

def pre_post_stats(df_prepost, yvar='465nm_dFF_znorm', values=False):
    """
    Compute a paired t-test for pre and post event.

    Parameters
    ----------
    df_prepost : DataFrame
        Output from calc_pre_post
    yvar : str
        Name of independent variable to compare, by default '465nm_dFF_znorm'.
    values : bool, optional
        Return the tstat and pval for the t-test, by default False.

    Returns
    -------
    (tstat, pval)
        Returns the t-statistic and the p-value from the paired t-test.
    """
    pre = df_prepost.loc[df_prepost['epoch'].str.contains('pre'), yvar]
    post = df_prepost.loc[df_prepost['epoch'].str.contains('post'), yvar]
    tstat, pval = stats.ttest_rel(post, pre)

    print(f't-statistic: {tstat}')
    print(f'p-value: {pval}')

    if values is True:
        return (tstat, pval)


################################################################################
