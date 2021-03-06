#!/usr/bin/env python

from numpy import NaN
from sklearn.linear_model import LinearRegression
import argparse
import numpy as np
import os
import pandas as pd

class call_for_service_data:
    '''
    A class to load Call for Service data with member functions to
    answer TDI's questiona.
    '''
    def __init__(self, nrows):
        '''
        Constructor to load data.
        '''
        # there will be multiple datasets, so make a dictionary for storage
        self.dfs = dict()
        self.df_combined = None
        self.nrows = nrows
        # small nrows for testing purposes
        self.temp_fpn = '../data/response_time.csv' if nrows is None else f'../data/response_time_{nrows}.csv'

    def combine_data(self):
        # force datetime datatypes
        df = pd.concat(self.dfs.values())
        for col in ['TimeArrive', 'TimeDispatch']:
            df[col] = pd.to_datetime(df[col])
        
        # construct the combined dataframe and remove duplication
        self.df_combined = df.drop_duplicates('NOPD_Item')

    def load_data(self, id, infpn):
        '''
        Provide the data full pathname and an ID for access.
        '''
        # self.dfs[id] = pd.read_csv(infpn, dtype={'Zip': 'string'}, parse_dates=['TimeArrive', 'TimeDispatch'], nrows=self.nrows)
        self.dfs[id] = pd.read_csv(infpn, dtype={'Zip': 'string'}, nrows=self.nrows)
    
    def parse_location(self, x):
        '''
        A function to clean up the Location column.
        Some locations start with "POINT", which give latitude then longitude.
        Others start with '(', which have the coordinates reversed.
        '''
        loc_str = x['Location'].strip()
        if loc_str.startswith('POINT'):
            loc_str = loc_str.lstrip('POINT (').rstrip(')')
            locs = loc_str.split(' ')
            return locs[0].strip().strip('NEWS'), locs[1].strip().strip('NEWS')
        
        # loc_str.lstrip('(').rstrip(')')
        loc_str = loc_str.strip('()')
        if ',' in loc_str:
            locs = loc_str.split(',')
        else:
            locs = loc_str.split(' ')
        return locs[1].strip().strip('NEWS'), locs[0].strip().strip('NEWS')


    def q1_fraction_of_the_most_common_type(self, id):
        '''
        Return the fraction of calls that are of the most common type.
        '''
        print('{:.5f}'.format(self.dfs[id].Type.value_counts(normalize=True)[0]))
    
    def q2_compare_2016_2020(self):
        df2016 = self.dfs['2016'].TypeText.value_counts(normalize=True)
        df2020 = self.dfs['2020'].TypeText.value_counts(normalize=True)
        target_idx = df2016.subtract(df2020, fill_value=NaN).sort_values(ascending=False).index[0]

        print('{:.5f}'.format(self.dfs['2016'].TypeText.value_counts(normalize=True)[target_idx]))
    
    def q3_remove_duplicate(self):
        df = pd.concat(self.dfs.values())
        
        # solution 1: count the occurance of 2
        print(df.NOPD_Item.value_counts().value_counts())

        # solution 2: remove duplicated records and check the difference
        df_lens = [dfi.shape[0] for dfi in self.dfs.values()]
        print(sum(df_lens)-self.df_combined.shape[0])
    
    def q4_median_response_time(self):
        self.df_combined['response_time'] = (self.df_combined['TimeArrive'] - self.df_combined['TimeDispatch']).dt.total_seconds()
        df = self.df_combined
        df = df[df.response_time.notna()]
        df = df[df.response_time >= 0]
        print(df.response_time.median())

        # since this step takes so long, I want to save the results to answer further questions
        self.df_combined.to_csv(self.temp_fpn, index=False)
    
    def q5_response_time_difference(self):
        # since question 4 takes much time, once it finishes, buffer the results
        if os.path.exists(self.temp_fpn):
            self.df_combined = pd.read_csv(self.temp_fpn)
        else:
            self.df_combined['response_time'] = (self.df_combined['TimeArrive'] - self.df_combined['TimeDispatch']).dt.total_seconds()
        
        # clean up records with nonsensical response time, and select only the relevant columns
        df = self.df_combined[self.df_combined.response_time.notna() & (self.df_combined.response_time >= 0)][['PoliceDistrict', 'response_time']]
        longest_time_district = df.PoliceDistrict[df.response_time.idxmax()]
        shortest_time_district = df.PoliceDistrict[df.response_time.idxmin()]
        df2 = df.groupby('PoliceDistrict').mean()
        print('{:.5f}'.format((df2.iloc[longest_time_district] - df2.iloc[shortest_time_district]).values[0]))
    
    def q6_slope_response_vs_month_fit(self):
        # since question 4 takes much time, once it finishes, buffer the results
        if os.path.exists(self.temp_fpn):
            self.df_combined = pd.read_csv(self.temp_fpn)
        else:
            self.df_combined['response_time'] = (self.df_combined['TimeArrive'] - self.df_combined['TimeDispatch']).dt.total_seconds()
        # clean up records with nonsensical response time, and select only the relevant columns
        df = self.df_combined[self.df_combined.response_time.notna() & (self.df_combined.response_time >= 0)][['TimeDispatch', 'TimeArrive', 'response_time']]
        df['month'] = pd.DatetimeIndex(df.TimeArrive).month
        
        df2 = df.groupby('month').mean()
        df2.reset_index(level=0, inplace=True)
        
        # fit a line from df2
        regressor = LinearRegression()
        regressor.fit(df2.month.values.reshape(-1, 1), df2.response_time)
        print('{:.5f}'.format(regressor.coef_[0]))
    
    def q7_event_type_probability_ratio(self):
        # since question 4 takes much time, once it finishes, buffer the results
        if os.path.exists(self.temp_fpn):
            self.df_combined = pd.read_csv(self.temp_fpn)
        else:
            self.df_combined['response_time'] = (self.df_combined['TimeArrive'] - self.df_combined['TimeDispatch']).dt.total_seconds()
        # clean up records with nonsensical response time, and select only the relevant columns
        df = self.df_combined[self.df_combined.response_time.notna() & (self.df_combined.response_time >= 0)][['TypeText', 'PoliceDistrict', 'Location']]
        # df = self.df_combined[['TypeText', 'PoliceDistrict', 'Location']]
        # preprocess location
        df.Location.fillna(value='(0.0, 0.0)', inplace=True)
        df[['longitude', 'latitude']] = df.apply(self.parse_location, axis=1, result_type='expand')

        # remove rows with Location (0, 0)
        df = df[np.invert(np.isclose(df.longitude.astype(float), 0)) & np.invert(np.isclose(df.latitude.astype(float), 0))]
        
        # remove rows with type count < constraint
        # use a smaller value in a test run
        type_cut_val = 100 if self.nrows is None else 100*self.nrows/df.shape[0]
        print(f'Select only event types with counts larger than {type_cut_val}\n')
        df = df.groupby('TypeText').filter(lambda x: len(x) > type_cut_val)

        # make conditional frequency table
        df_cond = df.groupby(['PoliceDistrict'])['TypeText'].value_counts(normalize=True).to_frame('conditional_frequency')

        # make uncontional frequency table
        df_uncond = df.TypeText.value_counts(normalize=True).to_frame('unconditional_frequency')

        # combine the two tables on TypeText
        firsts = df_cond.index.get_level_values('TypeText')
        df_cond['unconditional_frequency'] = df_uncond.loc[firsts].values
        df_cond['ratio'] = df_cond['conditional_frequency']/df_cond['unconditional_frequency']
        print('{:.5f}'.format(df_cond.ratio.max()))
    
    def q8_district_size_estimate(self):
        # since question 4 takes much time, once it finishes, buffer the results
        if os.path.exists(self.temp_fpn):
            self.df_combined = pd.read_csv(self.temp_fpn)
        else:
            self.df_combined['response_time'] = (self.df_combined['TimeArrive'] - self.df_combined['TimeDispatch']).dt.total_seconds()

        # clean up response time
        df = self.df_combined[self.df_combined.response_time.notna() & (self.df_combined.response_time >= 0)]
        # df = self.df_combined
        # preprocess location and clean things up
        df.Location.fillna(value='(0.0, 0.0)', inplace=True)
        df[['longitude', 'latitude']] = df.apply(self.parse_location, axis=1, result_type='expand').astype(float)
        df = df[np.invert(np.isclose(df.longitude.astype(float), 0)) & np.invert(np.isclose(df.latitude.astype(float), 0))]
        df = df[['PoliceDistrict', 'longitude', 'latitude']]
        df_dist_summary = df.groupby('PoliceDistrict').agg({col:['mean','std'] for col in ['longitude', 'latitude']})

        # Each degree of latitude and longitude at the equator is 111 km.
        # Each degree of longitude at some latitude angle has an additional cos(latitude) factor.
        # The area of an ellipse is ??ab.
        df_dist_summary['area'] = np.pi*(df_dist_summary['longitude']['std']*111)*(df_dist_summary['latitude']['std']*111)*np.cos(df_dist_summary['latitude']['mean'])
        print('{:.5f}'.format(df_dist_summary.area.max()))



if __name__ == '__main__':
    # specify the number of rows to read in
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nrows', type=int, default=None)
    parser.add_argument('-q', '--questions', type=int, nargs='*', default=[1,2,3,4,5,6,7,8])
    args = parser.parse_args()

    # display more rows
    pd.set_option('display.max_rows', 500)

    my_data = call_for_service_data(args.nrows)
    my_data.load_data('2016', '../data/Calls_for_Service_2016.csv')
    my_data.load_data('2017', '../data/Calls_for_Service_2017.csv')
    my_data.load_data('2018', '../data/Calls_for_Service_2018.csv')
    my_data.load_data('2019', '../data/Calls_for_Service_2019.csv')
    my_data.load_data('2020', '../data/Call_for_Service_2020.csv')
    my_data.combine_data()

    # question 1
    if 1 in args.questions:
        print('Q1')
        my_data.q1_fraction_of_the_most_common_type('2020')

    # question 2
    if 2 in args.questions:
        print('Q2')
        my_data.q2_compare_2016_2020()

    # question 3
    if 3 in args.questions:
        print('Q3')
        my_data.q3_remove_duplicate()

    # question 4
    if 4 in args.questions:
        print('Q4')
        my_data.q4_median_response_time()
    
    # question 5
    if 5 in args.questions:
        print('Q5')
        my_data.q5_response_time_difference()
    
    # question 6
    if 6 in args.questions:
        print('Q6')
        my_data.q6_slope_response_vs_month_fit()
    
    # question 7
    if 7 in args.questions:
        print('Q7')
        my_data.q7_event_type_probability_ratio()
    
    # question 8
    if 8 in args.questions:
        print('Q8')
        my_data.q8_district_size_estimate()