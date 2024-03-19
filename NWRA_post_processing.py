"""
#NWRA post processing
#
# This notebook is intended to provide an analysis of the AAL data produced
# for the NWRA project, and to identify any trends in nationally or by state/territory.
#
# 15 return periodss were used from 1 year to 10,000 years.
# The AEP impact results for each return period were generated using HazImp,
# with return period wind speeds generated based on the definition of the wind regions
# and design wind speed values in AS/NZS 1170.2 (2021). AAL was calculated
# using the AAL calculations_NWRA.ipynb notebook.
"""

import os
import datetime
import sys
from os.path import join as pjoin
import matplotlib
from matplotlib import patheffects
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

matplotlib.use("Agg")
sns.set_context('talk',font_scale=1.5)
sns.set_style('ticks')

colours_wind = {'SMA_A0': "#00171f",
                'SMA_A1': "#03045e",
                'SMA_A2': "#0077b6",
                'SMA_A3': "#00b4d8",
                'SMA_A4': "#90e0ef",
                'SMA_A5': "#caf0f8",
                'SMA_B1': "#f77f00",
                'SMA_B2': "#fcbf49",
                'SMA_C': "#db3a34",
                'SMA_D': "#5c1010"}

colours_wind2 = {'A0': "#00171f",
                'A1': "#03045e",
                'A2': "#0077b6",
                'A3': "#00b4d8",
                'A4': "#90e0ef",
                'A5': "#caf0f8",
                'B1': "#f77f00",
                'B2': "#fcbf49",
                'C': "#db3a34",
                'D': "#5c1010"}

wind_region_list = ['A0','A1','A2','A3','A4','A5','B1','B2','C','D']

colours_site = {'SMA_N1': "#03045e",
                'SMA_N2': "#0077b6",
                'SMA_N3': "#00b4d8",
                'SMA_N4': "#caf0f8",
                'SMA_C1': "#d62828",
                'SMA_C2': "#f77f00",
                'SMA_C3': "#fcbf49",
                'SMA_unknown': "#9e9d9d"}

colours_site2 = {'N1': "#03045e",
                'N2': "#0077b6",
                'N3': "#00b4d8",
                'N4': "#caf0f8",
                'C1': "#d62828",
                'C2': "#f77f00",
                'C3': "#fcbf49",
                'unknown': "#9e9d9d"}

site_class_list = ['N1','N2','N3','N4','C1','C2','C3','unknown']

colours_build = {'SMA_1840 - 1890': "#5E6A71",
                 'SMA_1891 - 1913': "#006983",
                 'SMA_1914 - 1945': "#72C7E7",
                 'SMA_1946 - 1959': "#A33F1F",
                 'SMA_1960 - 1979': "#CA7700",
                 'SMA_1980 - 1995': "#A5D867",
                 'SMA_1996 - present': "#6E7645"}

colours_build2 = {'1840 - 1890': "#5E6A71",
                 '1891 - 1913': "#006983",
                 '1914 - 1945': "#72C7E7",
                 '1946 - 1959': "#A33F1F",
                 '1960 - 1979': "#CA7700",
                 '1980 - 1995': "#A5D867",
                 '1996 - present': "#6E7645"}

build_year_list = ['1840 - 1890',
                   '1891 - 1913',
                   '1914 - 1945',
                   '1946 - 1959',
                   '1960 - 1979',
                   '1980 - 1995',
                   '1996 - present']

build_1980_list = ['pre 1980', 'post 1980']

colours_state = {
    'ACT': '#084bc2',
    'NSW': '#5fa2eb',
    'NT': '#C75B12',
    'QLD': '#73182c',
    'SA': '#E4002B',
    'TAS': '#2e5945',
    'VIC': '#061e54',
    'WA': '#FFD100'
}

colours_state_list = [
    '#084bc2',
    '#5fa2eb',
    '#C75B12',
    '#73182c',
    '#E4002B',
    '#2e5945',
    '#061e54',
    '#FFD100'
]

# The output files for the impact scenarios are stored in the project
# directory, and are stored as csv files.

AAL_PATH = r"X:\georisk\HaRIA_B_Wind\projects\acs\2. DATA\1. Work Unit Assessment\NWRA\impact\AAL\20231206_run_1"
AEP_PATH = r"X:\georisk\HaRIA_B_Wind\projects\acs\2. DATA\1. Work Unit Assessment\NWRA\impact\AEP\20231206_run_1"
AS4055_PATH = r"X:\georisk\HaRIA_B_Wind\projects\acs\2. DATA\1. Work Unit Assessment\NWRA\exposure"
OUT_FOLDER = r"X:\georisk\HaRIA_B_Wind\projects\acs\2. DATA\1. Work Unit Assessment\NWRA\impact\post processing\method5"

events = ['ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']

AS4055 = {
     'ACT': ['N1', 'N2', 'unknown'],
     'NSW': ['N1', 'N2', 'N3', 'N4','unknown'],
     'NT': ['N1', 'N2', 'N3', 'N4','C1', 'C2','unknown'],
     'QLD': ['N1', 'N2', 'N3', 'N4','C1', 'C2', 'C3','unknown'],
     'SA': ['N1', 'N2', 'N3','unknown'],
     'TAS': ['N1', 'N2', 'N3','unknown'],
     'VIC': ['N1', 'N2', 'N3','unknown'],
     'WA': ['N1', 'N2', 'N3', 'C1', 'C2','unknown']
     }

AS1170 = {
     'ACT': ['A3'],
     'NSW': ['A0', 'A2', 'A3', 'A5', 'B1'],
     'NT': ['A0', 'B2', 'C'],
     'QLD': ['A0', 'B1', 'B2', 'C'],
     'SA': ['A0', 'A5'],
     'TAS': ['A4', 'A5'],
     'VIC': ['A0', 'A5'],
     'WA': ['A0', 'A1', 'A5', 'B2', 'C', 'D']
     }

YEARS = {
     'ACT': ['1914 - 1945', '1946 - 1959', '1960 - 1979', '1980 - 1995', '1996 - present'],
     'NSW': ['1840 - 1890', '1891 - 1913', '1914 - 1945', '1946 - 1959', '1960 - 1979',
             '1980 - 1995', '1996 - present'],
     'NT': ['1960 - 1979', '1980 - 1995', '1996 - present'],
     'QLD': ['1840 - 1890', '1891 - 1913', '1914 - 1945', '1946 - 1959', '1960 - 1979',
             '1980 - 1995', '1996 - present'],
     'SA': ['1840 - 1890', '1891 - 1913', '1914 - 1945', '1946 - 1959', '1960 - 1979',
            '1980 - 1995', '1996 - present'],
     'TAS': ['1840 - 1890', '1891 - 1913', '1914 - 1945', '1946 - 1959', '1960 - 1979',
             '1980 - 1995', '1996 - present'],
     'VIC': ['1840 - 1890', '1891 - 1913', '1914 - 1945', '1946 - 1959', '1960 - 1979',
             '1980 - 1995', '1996 - present'],
     'WA': ['1840 - 1890', '1891 - 1913', '1914 - 1945', '1946 - 1959', '1960 - 1979',
            '1980 - 1995', '1996 - present']
     }

# AAL bins
AAL_bins = [0, 0.00125, 0.0025, 0.00375, 0.005, 0.00625, 0.0075, 0.00875,
            0.01, 0.01125, 0.0125, 0.01375, 0.015, 0.01625, 0.0175, 0.01875,
            0.02, 0.02125, 0.0225, 0.02375, 0.025, 0.02625, 0.0275, 0.02875,
            0.03, 0.03125, 0.0325, 0.03375, 0.035]

AAL_bins2 = [0, 0.0025, 0.005, 0.0075,
            0.01, 0.0125, 0.015, 0.0175,
            0.02, 0.0225, 0.025, 0.0275,
            0.03, 0.0325, 0.035]

AAL_bins2_labels = ['0 - 0.0025', '0.0025 - 0.005',
                    '0.005 - 0.0075', '0.0075 - 0.01',
                    '0.01 - 0.0125', '0.0125 - 0.015',
                    '0.015 - 0.0175', '0.0175 - 0.02',
                    '0.02 - 0.0225', '0.0225 - 0.025',
                    '0.025 - 0.0275', '0.0275 - 0.03',
                    '0.03 - 0.0325', '0.0325 - 0.035']

state_list = []
Aus_wind_region_list = []
Aus_site_class_list = []
Aus_building_age_list = []
all_aep = []

aeps = pd.read_csv(pjoin(AAL_PATH, 'NSW', "structural_mean_NSW_aeps.csv"))
aeps.drop(columns=aeps.columns[0], axis=1, inplace=True)
aeps.rename(columns = {list(aeps)[0]: 'aeps'}, inplace = True)
AEP = aeps["aeps"].to_numpy()

RES = 600
FMT = "png"
pe = patheffects.withStroke(foreground="white", linewidth=5)

# Import all AAL files and create graphs by state/territory in loop
for event_num in events:
    print("Processing event {0}".format(event_num))

    output_path = pjoin(OUT_FOLDER, event_num)
    try:
        os.makedirs(output_path)
    except Exception:
        pass

    AAL_file = pjoin(AAL_PATH, event_num, f"structural_mean_{event_num}_SA1.csv")
    AEP_file = pjoin(AEP_PATH, event_num, "RP1.csv")
    AS4055_file = pjoin(AS4055_PATH,
                        f"{event_num}_TILES_Residential_Wind_Exposure_202311_v13.12_TRCM_new_yr_range_AS4055.csv")
    AAL_mod_date = os.path.getmtime(AAL_file)
    AAL_mod_date = datetime.datetime.fromtimestamp(AAL_mod_date)

    try:
        df = pd.read_csv(AAL_file)
    except FileNotFoundError:
        print(f"Cannot find {AAL_file}")
        print("Check the file path is correct")

    try:
        df2 = pd.read_csv(AEP_file)
    except FileNotFoundError:
        print(f"Cannot find {AEP_file}")
        print("Check the file path is correct")
        sys.exit()

    try:
        AS4055_new = pd.read_csv(AS4055_file)
    except FileNotFoundError:
        print(f"Cannot find {AS4055_file}")
        print("Check the file path is correct")
        sys.exit()

    AS4055_new = AS4055_new.rename(columns={"AS4055_CLASS": "AS4055_CLASS_NEW"})

    df3 = pd.merge(df2, df, on='SA1_CODE')
    df3 = df3.fillna('unknown')
    df3 = pd.merge(df3, AS4055_new, on='LID')
    df3 = df3.drop(['SA1_CODE_y'], axis=1)
    df3 = df3.rename(columns={"SA1_CODE_x":"SA1_CODE"})
    df4 = df[['SA1_CODE','AAL']]

    state_aep = df.drop(['SA1_CODE'], axis=1)
    state_aep = df.mean(axis=0)
    state_aep['STATE'] = event_num
    all_aep.append(state_aep)

    df12 = df3.groupby('SA1_CODE').count().reset_index()
    df12 = df12[['SA1_CODE', 'AAL']]
    df12 = df12.rename(columns={"AAL": "total buildings"})

    # for analysis remove any SA1 which contains 10 or less buildings
    v = df3.SA1_CODE.value_counts()
    df3 = df3[df3.SA1_CODE.isin(v.index[v.gt(10)])]

    # add a new column which groups buildings as pre or post 1980
    df3['1980'] = 'pre 1980'
    df3.loc[df3['YEAR_BUILT'].str.contains('1980 - 1995'), '1980'] = 'post 1980'
    df3.loc[df3['YEAR_BUILT'].str.contains('1996 - present'), '1980'] = 'post 1980'

    # wind class df
    wind_region = pd.crosstab(df3['SA1_CODE'], df3['REGION_NEW'],
                              rownames=['SA1_CODE'],
                              colnames=['REGION_NEW'])
    wind_region = pd.merge(df4, wind_region, on='SA1_CODE')
    wind_region.sort_values(by=['AAL'], inplace=True)
    wind_region = pd.merge(wind_region, df12, on='SA1_CODE')
    wind_region['AAL_bin'] = pd.cut(wind_region['AAL'], bins=AAL_bins2, labels=AAL_bins2_labels)

    for wind_num in AS1170[event_num]:

        try:
            wind_region[f'prop_{wind_num}'] = wind_region[wind_num]/wind_region['total buildings']
            wind_region[f'SMA_{wind_num}'] = wind_region[f'prop_{wind_num}'].\
                                             rolling(100, min_periods=15).mean()
            Aus_wind_region_list.append(wind_region)
        except Exception:
            pass
    wind_prop_list=wind_region.columns[wind_region.columns.str.startswith('prop_')].tolist()

    # site class df
    site_class = pd.crosstab(df3['SA1_CODE'], df3['AS4055_CLASS'],
                              rownames=['SA1_CODE'],
                              colnames=['AS4055_CLASS'])
    site_class = pd.merge(df4, site_class, on='SA1_CODE')
    site_class.sort_values(by=['AAL'], inplace=True)
    site_class = pd.merge(site_class, df12, on='SA1_CODE')
    site_class['AAL_bin'] = pd.cut(site_class['AAL'], bins=AAL_bins2, labels=AAL_bins2_labels)

    for site_num in AS4055[event_num]:

        try:
            site_class[f'prop_{site_num}'] = site_class[site_num]/site_class['total buildings']
            site_class[f'SMA_{site_num}'] = site_class[f'prop_{site_num}'].\
                                            rolling(100, min_periods=15).mean()
        except Exception:
            pass

    # site class new df
    site_class2 = pd.crosstab(df3['SA1_CODE'], df3['AS4055_CLASS_NEW'],
                              rownames=['SA1_CODE'],
                              colnames=['AS4055_CLASS_NEW'])
    site_class2 = pd.merge(df4, site_class2, on='SA1_CODE')
    site_class2.sort_values(by=['AAL'], inplace=True)
    site_class2 = pd.merge(site_class2, df12, on='SA1_CODE')
    site_class2['AAL_bin'] = pd.cut(site_class2['AAL'], bins=AAL_bins2, labels=AAL_bins2_labels)

    for site_num in AS4055[event_num]:

        try:
            site_class2[f'prop_{site_num}'] = site_class2[site_num]/site_class2['total buildings']
            site_class2[f'SMA_{site_num}'] = site_class2[f'prop_{site_num}'].\
                                             rolling(100, min_periods=15).mean()
        except Exception:
            pass

    # building age df
    building_age = pd.crosstab(df3['SA1_CODE'], df3['YEAR_BUILT'],
                              rownames=['SA1_CODE'],
                              colnames=['YEAR_BUILT'])
    building_age = pd.merge(df4, building_age, on='SA1_CODE')
    building_age.sort_values(by=['AAL'], inplace=True)
    building_age = pd.merge(building_age, df12, on='SA1_CODE')
    building_age['post_1980'] = building_age['1980 - 1995']+building_age['1996 - present']
    building_age['pre_1980'] = building_age['total buildings']-building_age['post_1980']
    building_age['AAL_bin'] = pd.cut(building_age['AAL'], bins=AAL_bins2, labels=AAL_bins2_labels)
    building_age['prop_post_1980'] = building_age['post_1980']/building_age['total buildings']
    building_age['prop_pre_1980'] = building_age['pre_1980']/building_age['total buildings']
    building_age['SMA_post_1980'] = building_age['prop_post_1980'].\
                                    rolling(100, min_periods=15).mean()
    building_age['SMA_pre_1980'] = building_age['prop_pre_1980'].\
                                   rolling(100, min_periods=15).mean()

    for build_num in YEARS[event_num]:

        try:
            building_age[f'prop_{build_num}'] = building_age[build_num]/building_age['total buildings']
            building_age[f'SMA_{build_num}'] = building_age[f'prop_{build_num}'].\
                                               rolling(100, min_periods=15).mean()
        except Exception:
            pass


    wind_region.to_csv(pjoin(output_path, f"{event_num}_wind_region.csv"))
    site_class.to_csv(pjoin(output_path, f"{event_num}_site_class.csv"))
    site_class2.to_csv(pjoin(output_path, f"{event_num}_site_class_new.csv"))
    building_age.to_csv(pjoin(output_path, f"{event_num}_year_built.csv"))

    kwargs = {'fontsize':'9','alpha':0.7}

    # wind region graph
    fig, ax = plt.subplots(figsize=(16,9))
    for wind_num in AS1170[event_num]:

        try:
            wind_region.plot.scatter(x='AAL', y=f'prop_{wind_num}', alpha=0.05,
                                     s=7.5, c=colours_wind[f'SMA_{wind_num}'], ax=ax)
            wind_region.plot(x='AAL', y=f'SMA_{wind_num}', c=colours_wind[f'SMA_{wind_num}'], ax=ax)
        except Exception:
            pass

    ax.set_xlabel("AAL")
    ax.set_ylabel("proportion of buildings")
    ax.legend()
    plt.text(x=-0.0013, y=-0.18, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=-0.0013, y=-0.2, s=f'combined with exposure data extracted from {AEP_file}',
             **kwargs)
    plt.text(x=-0.0013, y=-0.22, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.xlim(0, 0.02)
    plt.ylim(0, 1)
    plt.title(f'{event_num}')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_wind_region.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    # wind region as box and violin
    fig, ax = plt.subplots(figsize=(16,9))
    sns.violinplot(data = df3,
                      x = 'AAL',
                      y = 'REGION_NEW',
                      order = wind_region_list,
                      palette = colours_wind2)
    ax.set_ylabel('wind region')
    plt.xlim(0, 0.035)
    plt.text(x=0, y=11, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=11.2, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=11.4, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.title(f'{event_num}')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_wind_region_violin.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16,9))
    sns.boxplot(data = df3,
                      x = 'AAL',
                      y = 'REGION_NEW',
                      order = wind_region_list,
                      palette = colours_wind2)
    ax.set_ylabel('wind region')
    plt.xlim(0, 0.035)
    plt.text(x=0, y=11, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=11.2, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=11.4, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.title(f'{event_num}')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_wind_region_box.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    # site class graph
    fig, ax = plt.subplots(figsize=(16,9))
    for site_num in AS4055[event_num]:

        try:
            site_class.plot.scatter(x='AAL', y=f'prop_{site_num}', alpha=0.05, s=7.5,
                                    c=colours_site[f'SMA_{site_num}'], ax=ax)
            site_class.plot(x='AAL', y=f'SMA_{site_num}', c=colours_site[f'SMA_{site_num}'], ax=ax)
        except Exception:
            pass
    ax.set_xlabel("AAL")
    ax.set_ylabel("proportion of buildings")
    ax.legend()
    plt.xlim(0, 0.02)
    plt.ylim(0, 1)
    plt.text(x=-0.0013, y=-0.18, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=-0.0013, y=-0.2, s=f'combined with exposure data extracted from {AEP_file}',
             **kwargs)
    plt.text(x=-0.0013, y=-0.22, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.title(f'{event_num}')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_site_class.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    # site class as box and violin
    fig, ax = plt.subplots(figsize=(16,9))
    sns.violinplot(data = df3,
                      x = 'AAL',
                      y = 'AS4055_CLASS',
                      order = site_class_list,
                      palette = colours_site2)
    ax.set_ylabel('site class')
    plt.xlim(0, 0.035)
    plt.text(x=0, y=8.8, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=9, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=9.2, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.title(f'{event_num}')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_site_class_violin.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16,9))
    sns.boxplot(data = df3,
                      x = 'AAL',
                      y = 'AS4055_CLASS',
                      order = site_class_list,
                      palette = colours_site2)
    ax.set_ylabel('site class')
    plt.xlim(0, 0.035)
    plt.text(x=0, y=8.8, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=9, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=9.2, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.title(f'{event_num}')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_site_class_box.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    # site class new graph
    fig, ax = plt.subplots(figsize=(16,9))
    for site_num in AS4055[event_num]:

        try:
            site_class2.plot.scatter(x='AAL', y=f'prop_{site_num}', alpha=0.05, s=7.5,
                                     c=colours_site[f'SMA_{site_num}'], ax=ax)
            site_class2.plot(x='AAL', y=f'SMA_{site_num}', c=colours_site[f'SMA_{site_num}'], ax=ax)
        except Exception:
            pass
    ax.set_xlabel("AAL")
    ax.set_ylabel("proportion of buildings")
    ax.legend()
    plt.xlim(0, 0.02)
    plt.ylim(0, 1)
    plt.text(x=-0.0013, y=-0.18, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=-0.0013, y=-0.2, s=f'combined with exposure data extracted from {AEP_file}',
             **kwargs)
    plt.text(x=-0.0013, y=-0.22, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.title(f'{event_num}')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_site_class_new.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    # site class new as box and violin
    fig, ax = plt.subplots(figsize=(16,9))
    sns.violinplot(data = df3,
                      x = 'AAL',
                      y = 'AS4055_CLASS_NEW',
                      order = site_class_list,
                      palette = colours_site2)
    ax.set_ylabel('site class')
    plt.xlim(0, 0.035)
    plt.text(x=0, y=8.8, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=9, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=9.2, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.title(f'{event_num}')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_site_class_new_violin.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16,9))
    sns.boxplot(data = df3,
                      x = 'AAL',
                      y = 'AS4055_CLASS_NEW',
                      order = site_class_list,
                      palette = colours_site2)
    ax.set_ylabel('site class')
    plt.xlim(0, 0.035)
    plt.text(x=0, y=8.8, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=9, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=9.2, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.title(f'{event_num}')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_site_class_new_box.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    # building age graph pre and post 1980
    fig, ax = plt.subplots(figsize=(16,9))
    building_age.plot.scatter(x='AAL', y='prop_pre_1980', alpha=0.05, s=7.5, ax=ax)
    building_age.plot(x='AAL', y='SMA_pre_1980', ax=ax)
    building_age.plot.scatter(x='AAL', y='prop_post_1980', alpha=0.05, s=7.5, ax=ax)
    building_age.plot(x='AAL', y='SMA_post_1980', ax=ax)
    ax.set_xlabel("AAL")
    ax.set_ylabel("proportion of buildings")
    ax.legend()
    plt.xlim(0, 0.02)
    plt.ylim(0, 1)
    plt.text(x=-0.0013, y=-0.18, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=-0.0013, y=-0.2, s=f'combined with exposure data extracted from {AEP_file}',
             **kwargs)
    plt.text(x=-0.0013, y=-0.22, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_building_age_1980.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    # building age as box and violin pre and post 1980
    fig, ax = plt.subplots(figsize=(16,9))
    sns.violinplot(data = df3,
                      x = 'AAL',
                      y = '1980',
                      order = build_1980_list)
    ax.set_ylabel('building age')
    plt.xlim(0, 0.035)
    plt.title(f'{event_num}')
    plt.text(x=0, y=2, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=2.1, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=2.2, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_building_age_violin_1980.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16,9))
    sns.boxplot(data = df3,
                      x = 'AAL',
                      y = '1980',
                      order = build_1980_list)
    ax.set_ylabel('building age')
    plt.xlim(0, 0.035)
    plt.title(f'{event_num}')
    plt.text(x=0, y=2, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=2.1, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=2.2, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_building_age_box_1980.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    # building age graph
    fig, ax = plt.subplots(figsize=(16,9))
    for build_num in YEARS[event_num]:

        try:
            building_age.plot.scatter(x='AAL', y=f'prop_{build_num}', alpha=0.05, s=7.5,
                                      c=colours_build[f'SMA_{build_num}'], ax=ax)
            building_age.plot(x='AAL', y=f'SMA_{build_num}',
                              c=colours_build[f'SMA_{build_num}'], ax=ax)
        except Exception:
            pass
    ax.set_xlabel("AAL")
    ax.set_ylabel("proportion of buildings")
    ax.legend()
    plt.xlim(0, 0.02)
    plt.ylim(0, 1)
    plt.text(x=-0.0013, y=-0.18, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=-0.0013, y=-0.2, s=f'combined with exposure data extracted from {AEP_file}',
             **kwargs)
    plt.text(x=-0.0013, y=-0.22, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_building_age.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    # building age as box and violin
    fig, ax = plt.subplots(figsize=(16,9))
    sns.violinplot(data = df3,
                      x = 'AAL',
                      y = 'YEAR_BUILT',
                      order = build_year_list,
                      palette = colours_build2)
    ax.set_ylabel('building age')
    plt.xlim(0, 0.035)
    plt.title(f'{event_num}')
    plt.text(x=0, y=8, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=8.2, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=8.4, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_building_age_violin.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16,9))
    sns.boxplot(data = df3,
                      x = 'AAL',
                      y = 'YEAR_BUILT',
                      order = build_year_list,
                      palette = colours_build2)
    ax.set_ylabel('building age')
    plt.xlim(0, 0.035)
    plt.title(f'{event_num}')
    plt.text(x=0, y=8, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0, y=8.2, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0, y=8.4, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_by_building_age_box.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    #age by site class
    fig, ax = plt.subplots(figsize=(16,9))
    sns.countplot(x='YEAR_BUILT',
                  hue='AS4055_CLASS_NEW',
                  data=df3,
                  order = build_year_list,
                  hue_order = site_class_list,
                  palette = colours_site2)
    ax.set_xlabel("year built")
    ax.legend()
    plt.yscale('log')
    plt.savefig(pjoin(output_path, f"{event_num}_age_site_class.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

    #ranking
    df2 = df2[['SA1_CODE', 'SA2_CODE', 'SA2_NAME', 'LGA_CODE', 'LGA_NAME']].copy().drop_duplicates()
    state_rank = pd.merge(df4, df2, on='SA1_CODE')
    state_rank['STATE'] = f"{event_num}"
    state_list.append(state_rank)
    state_rank_save = state_rank.sort_values(by=['AAL'], ascending=False)
    state_rank_save['rank'] = state_rank_save['AAL'].rank(ascending=False)
    state_rank_save.to_csv(pjoin(output_path, f"{event_num}_state_rank.csv"))

    # graph histogram AAL per state
    fig, ax = plt.subplots(figsize=(16,9))
    ax.hist(state_rank['AAL'], bins=AAL_bins ,histtype="bar")
    ax.set_xlabel("AAL")
    ax.set_ylabel("SA1 count")
    plt.text(x=0.0001, y=0.13, s=f'AAL data from {AAL_file}', **kwargs)
    plt.text(x=0.0001, y=0.1, s=f'combined with exposure data extracted from {AEP_file}', **kwargs)
    plt.text(x=0.0001, y=0.08, s=f'data last updated on {AAL_mod_date}', **kwargs)
    plt.xlim(0, 0.035)
    plt.yscale('log')
    plt.savefig(pjoin(output_path, f"{event_num}_AAL_hist.{FMT}"),
                dpi=RES, bbox_inches="tight")
    plt.close(fig)

Aus_rank = pd.concat(state_list)

Aus_rank.sort_values(by=['AAL'], ascending=False, inplace=True)
Aus_rank['rank'] = Aus_rank['AAL'].rank(ascending=False)
Aus_rank.to_csv(pjoin(OUT_FOLDER, "Aus_AAL_rank_by_SA1.csv"))

# graph histogram AAL in all Aus
fig, ax = plt.subplots(figsize=(16,9))
ax.hist(Aus_rank['AAL'], bins=AAL_bins ,histtype="bar")
ax.set_xlabel("AAL")
ax.set_ylabel("SA1 count")
plt.xlim(0, 0.035)
plt.yscale('log')
plt.text(x=0.0001, y=0.13, s='AAL data from all states and territories .\
         from files with the name format "structural_mean_STATE_SA1.csv"',
         **kwargs)
plt.text(x=0.0001, y=0.1, s=f'located in {AAL_PATH}\STATE', **kwargs)
plt.text(x=0.0001, y=0.08, s=f'data last updated on {AAL_mod_date}', **kwargs)
plt.savefig(pjoin(OUT_FOLDER, f"Aus_AAL_hist.{FMT}"),
            dpi=RES, bbox_inches="tight")
plt.close(fig)

plot_Aus_AAL = Aus_rank.pivot(columns='STATE')['AAL']

# graph histogram AAL all Aus by state
fig, ax = plt.subplots(figsize=(16,9))
ax.hist(plot_Aus_AAL, bins=AAL_bins2, histtype="bar", label=plot_Aus_AAL.columns,
        color=colours_state_list)
ax.legend()
ax.set_xlabel("AAL")
ax.set_ylabel("SA1 count")
plt.text(x=0.0001, y=0.13, s='AAL data from all states and territories .\
         from files with the name format "structural_mean_STATE_SA1.csv"',
         **kwargs)
plt.text(x=0.0001, y=0.1, s=f'located in {AAL_PATH}\STATE', **kwargs)
plt.text(x=0.0001, y=0.08, s=f'data last updated on {AAL_mod_date}', **kwargs)
plt.xlim(0, 0.035)
plt.yscale('log')
plt.savefig(pjoin(OUT_FOLDER, f"Aus_AAL_count_by_state.{FMT}"),
            dpi=RES, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(16,9))
sns.violinplot(data = Aus_rank,
                  x = 'AAL',
                  y = 'STATE',
                  order = events,
                  palette = colours_state)
plt.text(x=-0.002, y=9, s='AAL data from all states and territories .\
         from files with the name format "structural_mean_STATE_SA1.csv"',
         **kwargs)
plt.text(x=-0.002, y=9.2, s=f'located in {AAL_PATH}\STATE', **kwargs)
plt.text(x=-0.002, y=9.4, s=f'data last updated on {AAL_mod_date}', **kwargs)
plt.savefig(pjoin(OUT_FOLDER, f"violin_AAL_all_Aus.{FMT}"),
            dpi=RES, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(16,9))
sns.boxplot(data = Aus_rank,
                  x = 'AAL',
                  y = 'STATE',
                  order = events,
                  palette = colours_state)
plt.text(x=-0.002, y=9, s='AAL data from all states and territories .\
         from files with the name format "structural_mean_STATE_SA1.csv"',
         **kwargs)
plt.text(x=-0.002, y=9.2, s=f'located in {AAL_PATH}\STATE', **kwargs)
plt.text(x=-0.002, y=9.4, s=f'data last updated on {AAL_mod_date}', **kwargs)
plt.savefig(pjoin(OUT_FOLDER, f"box_AAL_all_Aus.{FMT}"),
            dpi=RES, bbox_inches="tight")
plt.close(fig)

# top 100 ranked SA1s by AAL
# what states are they in
top_100 = Aus_rank.iloc[:100]
top_100_state = top_100.groupby('STATE').\
    agg(AAL_min=('AAL','min'),
        AAL_mean=('AAL','mean'),
        AAL_max=('AAL','max'),
        SA1_count=('AAL','size'),
        SA2_list=('SA2_NAME',list),
        LGA_list=('LGA_NAME',list))
top_100_state.to_csv(pjoin(OUT_FOLDER, "stats_top_100_AAL_SA1.csv"))

# bottom 100 ranked SA1s by AAL
# what states are they in
bot_100 = Aus_rank.iloc[-100:]
bot_100_state = bot_100.groupby('STATE').\
    agg(AAL_min=('AAL','min'),
        AAL_mean=('AAL','mean'),
        AAL_max=('AAL','max'),
        SA1_count=('AAL','size'),
        SA2_list=('SA2_NAME',list),
        LGA_list=('LGA_NAME',list))
bot_100_state.to_csv(pjoin(OUT_FOLDER, "stats_bottom_100_AAL_SA1.csv"))

# AAL statistics for all states
Aus_rank_state = Aus_rank.groupby('STATE').\
    agg(AAL_min=('AAL','min'),
        AAL_mean=('AAL','mean'),
        AAL_max=('AAL','max'),
        SA1_count=('AAL','size'))
Aus_rank_state.to_csv(pjoin(OUT_FOLDER, "stats_AAL_by_state_all_Aus.csv"))

ALL_STATE_AEP = pd.DataFrame(all_aep).set_index('STATE')
ALL_STATE_AEP = ALL_STATE_AEP.drop('SA1_CODE', axis=1)

# AEP curves for all states/territories
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
for idx, row in ALL_STATE_AEP.iterrows():
    x = row.drop(["AAL"]).values
    ax.semilogy(x, AEP, path_effects=[pe], label=idx, c=colours_state[idx])
ax.grid(which='major', linestyle='-')
ax.grid(which='minor', linestyle='--', linewidth=0.5)
ax.legend()
plt.xlim(0, 0.55)
ax.set_ylabel("AEP")
ax.set_xlabel("Structural loss ratio")
plt.savefig(os.path.join(OUT_FOLDER, "structural_mean_EPcurve"), bbox_inches="tight")

# Expected loss curve for all states/territories
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
for idx, row in ALL_STATE_AEP.iterrows():
    x = row.drop(["AAL"]).values
    ax.semilogy(x*AEP, AEP, path_effects=[pe], label=idx, c=colours_state[idx])
ax.grid(which='major', linestyle='-')
ax.grid(which='minor', linestyle='--', linewidth=0.5)
ax.set_title("Expected loss curves (SLR)")
ax.legend()
ax.set_ylabel("AEP")
ax.set_xlabel("Expected loss ratio")
plt.savefig(os.path.join(OUT_FOLDER, "structural_mean_ELcurve"), bbox_inches="tight")
