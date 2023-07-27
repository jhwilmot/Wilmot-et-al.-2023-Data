""" Visualize fiber photometry data."""
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

################################################################################
################################################################################

# define color palette:
kp_pal = ['#2b88f0', #blue
          '#EF862E', #orange
          '#00B9B9', #cyan
          '#9147B1', #purple
          '#28A649', #green
          '#F97B7B', #salmon
          '#490035', #violet
          '#bdbdbd'] #gray


def set_palette(color_pal=None, show=False):
    """Set default color palette."""
    color_pal = kp_pal if color_pal is None else color_pal
    sns.set_palette(color_pal)
    if show:
        sns.palplot(color_pal)
    else:
        return color_pal


################################################################################

def check_ax(ax, figsize=None):
    """Check whether a figure axes object is defined, define if not.
    Parameters
    ----------
    ax : matplotlib.Axes or None
        Axes object to check if is defined.
    Returns
    -------
    ax : matplotlib.Axes
        Figure axes object to use.
    """

    if not ax:
        _, ax = plt.subplots(figsize=figsize)

    return ax

################################################################################

def set_trialavg_aes(ax,
                     title=None,
                     cs_dur=20,
                     us_del=40,
                     us_dur=2):
    """
    Set aesthetics for trialavg plot.

    Parameters
    ----------
    ax : matplotib.axes
        Axes object to apply formatting to
    cs_dur : int, optional
        CS duration (specified in trialavg call), by default 20
    us_del : int, optional
        US delivery time (specified in trialavg call), by default 40
    us_dur : int, optional
        US duration (specified in trialavg call), by default 2

    Returns
    -------
    [type]
        [description]
    """
    # adjust x-axis margin to shift plot adjacent to y-axis
    ax.margins(x=0)
    # add dashed line at y=0, dashed lines for shock
    ax.axhline(y=0, linestyle='-', color='black', linewidth=0.6)
    # add rectangle to highlight CS period
    ax.axvspan(0, cs_dur, facecolor="grey", alpha=0.2)
    # add dashed black rectangle around shock interval
    if us_dur > 0:
        ax.axvspan(us_del, us_del+us_dur, facecolor='none', edgecolor='black', ls='--')    
    # change label size 
    ylab = r'Normalized $\Delta F/F %$' 
    xlab = 'Time from cue onset (s)'
    # changed from 20,20 to 22,28 on 8-5-2019
    tick_size = 22
    label_size = 28
    ax.tick_params(labelsize=tick_size, width=1, length=8)
    ax.set_ylabel(ylab, size=label_size)
    ax.set_xlabel(xlab, size=label_size)
    
    if title:
        ax.set_title(title)

    return ax



################################################################################

def plot_style(figure_size=None):
    """Set default plot style."""
    figure_size = [30, 20] if figure_size is None else figure_size
    size_scalar = (sum(figure_size)/2)/25
    # figure and axes info
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rc('axes', facecolor='white', linewidth=2*size_scalar,
           labelsize=40*size_scalar, titlesize=32*size_scalar,
           labelpad=5*size_scalar)

    plt.rc('axes.spines', right=False, top=False)
    # plot-specific info
    plt.rcParams['lines.linewidth'] = 2*size_scalar
    # tick info
    plt.rcParams['xtick.labelsize'] = 32*size_scalar
    plt.rcParams['ytick.labelsize'] = 30*size_scalar
    plt.rcParams['xtick.major.size'] = 10*size_scalar
    plt.rcParams['ytick.major.size'] = 10*size_scalar
    plt.rcParams['xtick.major.width'] = 2*size_scalar
    plt.rcParams['ytick.major.width'] = 2*size_scalar
    # legend info
    plt.rc('legend', fontsize=32*size_scalar, frameon=False)

################################################################################

def tfc_trial_avg(df,
                  hue=None,
                  title=None,
                  yvar='465nm_dFF_znorm',
                  xvar='time_trial',
                  cs_dur=20,
                  us_del=40,
                  us_dur=2,
                  fig_size=(12, 8), 
                  ax=None, **kwargs):
    """
        Plot trial-averaged dFF signal.

        Parameters
        ----------
        df : DataFrame
            Trial-level DataFrame from trials_df()
        yvar : str, optional
            Column containing fluorescence values to plot, by default '465nm_dFF_znorm'
        xvar : str, optional
            Column containing trial-level timepoints, by default 'time_trial'
        cs_dur : int, optional
            CS duration. Used to draw rectangle around CS time period, by default 20
        us_del : int, optional
            Time point of US delivery, by default 40
        us_dur : int, optional
            US duration. Used to Draw rectangle around US time period, by default 2
        fig_size : tuple, optional
            Size of figure, by default (12, 8)
        """    
        
    # initialize the plot and apply trialavg formatting
    ax = check_ax(ax, figsize=fig_size)
    set_trialavg_aes(ax, title, cs_dur, us_del, us_dur)
        
    if hue:
        hue_means = df.groupby([xvar, hue]).mean().reset_index()
        if hue in ['Animal', 'Trial']:         
            hue_stds = df.groupby([xvar, hue]).sem().reset_index()
        else:
            hue_stds = (df.groupby([xvar, hue, 'Animal']).mean()
                        .groupby([xvar, hue]).sem().reset_index())
        # plot the data for each hue level
        for hue_level in hue_means[hue].unique():
            x = hue_means.loc[hue_means[hue] == hue_level, xvar]
            y = hue_means.loc[hue_means[hue] == hue_level, yvar]
            yerr = hue_stds.loc[hue_stds[hue] == hue_level, yvar]
            line = ax.plot(x, y, label=f'{hue}: {hue_level}', **kwargs)
            ax.fill_between(x, y-yerr, y+yerr, facecolor=line[0].get_color(), alpha=0.15)
            ax.legend(fontsize=12)
    else:
        animal_means = df.groupby([xvar]).mean().reset_index()
        animal_stds = (df.groupby([xvar, 'Animal']).mean()
                       .groupby(xvar).sem().reset_index())
        # grab variables for plotting
        x = animal_means.loc[:, xvar]
        y = animal_means.loc[:, yvar]
        yerror = animal_stds.loc[:, yvar]
        # plot the data
        line = ax.plot(x, y, **kwargs)
        ax.fill_between(x, y-yerror, y+yerror, facecolor=line[0].get_color(), alpha=0.15)


################################################################################

def tfc_trials_heatmap(df, yvar='465nm_dFF_znorm', 
                       fig_size=(32, 6), label_size=16, **kwargs):
    """
    Plot heatmap of dFF across trials.

    Parameters
    ----------
    df : DataFrame
        Trial-level DataFrame from trials_df()
    yvar : str, optional
        Column containing fluorescence values to plot, by default '465nm_dFF_znorm'
    fig_size : tuple, optional
        Size of figure, by default (32, 6)
    label_size : int, optional
        Size of x-axis tick labels, by default 16
    """
    # pivot df for heatmap format
    df_group_agg = df.pivot_table(index='Trial',
                                  columns='time_trial',
                                  values=yvar,
                                  aggfunc='mean')
    plt.figure(1, figsize=fig_size)
    ax = sns.heatmap(df_group_agg, 
                     cbar_kws={'shrink': .75, 'ticks':None},
                     yticklabels=df_group_agg.index,
                     **kwargs)
    xlab = 'Time from CS onset (sec)'
    ylab = 'Trial'
    plt.ylabel(ylab, size=label_size)
    plt.xlabel(xlab, size=label_size)
    # set tick length and remove ticks on y-axis
    ax.tick_params(axis='x', labelsize=label_size, width=2, length=6)
    ax.tick_params(axis='y', which='major', labelsize=label_size, length=0, pad=5)
    # set tick label param size
    ax.tick_params(axis='both', which='major', labelsize=label_size, rotation='auto')
    cbar = ax.collections[0].colorbar
    # here set the labelsize by label_size
    cbar.ax.tick_params(labelsize=label_size, length=0)
    # rescale x-axis into 10-sec labels
    xmin = min(df['time_trial'])
    xmax = max(df['time_trial'])
    xloc = np.arange(0, len(df_group_agg.columns), 50)
    xlabs = np.arange(int(xmin), int(xmax), 5)
    plt.xticks(xloc, xlabs)#, rotation=45)

################################################################################


