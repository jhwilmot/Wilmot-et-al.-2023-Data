import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import re
import numpy as np
from matplotlib.patches import Rectangle

def presentation_style(show_palettes=False, figure_size = [30,20], bold_label=True):
    size_scalar = (sum(figure_size)/2)/25
    # figure and axes info
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rc('axes', facecolor = 'white', linewidth=4*size_scalar,
            labelsize=40*size_scalar, titlesize = 32*size_scalar,
            titleweight = 'bold', labelpad=5*size_scalar)

    if bold_label == True:
        plt.rc('axes', labelweight='bold')

    plt.rc('axes.spines', right=False, top=False)
    # plot-specific info
    plt.rcParams['lines.linewidth'] = 4*size_scalar
    # tick info
    plt.rcParams['xtick.labelsize'] = 32*size_scalar
    plt.rcParams['ytick.labelsize'] = 44*size_scalar
    plt.rcParams['xtick.major.size'] = 10*size_scalar
    plt.rcParams['ytick.major.size'] = 10*size_scalar
    plt.rcParams['xtick.major.width'] = 4*size_scalar
    plt.rcParams['ytick.major.width'] = 4*size_scalar
    # legend info
    plt.rc('legend', fontsize=32*size_scalar, frameon=False)

    #color palettes
    sns.set_palette('muted')


# plot trace fear training data; default = bins
def tfc_plot(df, figsize=(30,20), xvar='Component Name', yvar='Pct Component Time Freezing',
             hue=None, xlab='Time (mins)', ylab='Freezing (%)',
             tone_squares=True, shock_line=True, min_bins=True, tone_only=False, 
             ylim=(0,100), scale=1.25, errwidth=10, marker_size=800, **kwargs):
    
    fig = plt.figure(figsize=figsize)  # create a figure object
    ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure

    if tone_only == False:
        df_plot = df        
    if tone_only == True:
        df_plot = df.loc[df['Component Name'].str.contains('tone')]
        xlab = ''
    
    # draw rectangles around tone periods
    if tone_squares == True and tone_only == False:
        tones, traces = get_tones(df)
        [ ax.axvspan(to, to+1, facecolor="grey", alpha=0.15) for to in tones ]
    
    # draw line where shock occurs (at the end of the trace)
    if shock_line == True and tone_only == False:
        tones,traces = get_tones(df)
        [ ax.axvspan(tr+1, tr+1.15, facecolor='#ffb200') for tr in traces ]

    ax = sns.pointplot(x=xvar, y=yvar, capsize=0.05,
                       ci=68, ax=ax, data=df_plot, errwidth=errwidth, scale=scale, hue=hue,
                       **kwargs)

    # change x-axis labels to mins
    if min_bins == True:
        min_bins = [i for i in range(len(df_plot['Component Name'].unique())) if (i+1) % 3 == 0]
        min_labs = [ i+1 for i in range(len(min_bins)) ]
        plt.xticks(min_bins, min_labs)

    # plot aesthetics
    ax.set_ylim(ylim)
    ax.set_ylabel(ylab, size=60)
    ax.set_xlabel(xlab, size=40)
    ax.tick_params('x',labelsize = 40)
    ax.tick_params('y',labelsize = 60)
    plt.setp(ax.collections, sizes=[marker_size])
    # remove legend title
    if hue != None:
        l = ax.legend(markerscale=0.6)
        l.set_title('')

    sns.despine()