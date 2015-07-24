# Load panes data into memory.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
import code

"""
Given panes df of hourly data. Collapse to hourly frequency and extract
relevant data.
"""
def collapse_to_daily(df):
    mean_vars = ['panes','is_ran_reset_today']
    sum_vars = ['absd1panes','sqd1panes']

    means = df.groupby(lambda stamp: stamp.normalize())[mean_vars[:]].mean()
    sums  = df.groupby(lambda stamp: stamp.normalize())[sum_vars[:]].sum()
    df = pd.concat([means,sums],axis=1)

    df['dow'] = df.index.map(lambda val: val.dayofweek)
    df['is_workday'] = df['dow'] <= 4
    df['is_mon'] = df['dow'] == 0
    df['is_tue'] = df['dow'] == 1
    df['is_wed'] = df['dow'] == 2
    df['is_thu'] = df['dow'] == 3
    df['is_fri'] = df['dow'] == 4
    df['is_sat'] = df['dow'] == 5
    df['is_sun'] = df['dow'] == 6
    df.drop(['dow'],axis=1,inplace=True)

    return df

def add_variables(df):
    df['d1panes'] = df['panes'].diff()
    df['d2panes'] = df['d1panes'].diff()
    df['l1panes'] = df['panes'].shift()
    df['absd1panes'] = df['d1panes'].apply(np.abs)
    df['sqd1panes'] = df['d1panes'] ** 2

    # Is today a workday?
    df['day_of_week'] = df.index.weekday
    df['is_workday'] = df['day_of_week'] <= 4

    # Code for RAN reset.
    # Condition: panes_{t-1} > 0, panes_{t} = 0.
    df['is_ran_reset_now'] = df.apply(
            lambda row: row['panes'] == 0 and row['l1panes'] > 0, axis=1)
    # Was RAN reset at any point today?
    grouped = df.groupby(by=lambda stamp: stamp.normalize())
    df1 = pd.DataFrame(grouped['is_ran_reset_now'].aggregate(np.sum))
    df1.rename(columns={'is_ran_reset_now':'is_ran_reset_today'}, inplace=True)

    # Prepare for merge...create keys and create duplicate of left index
    df['key'] = df.index.normalize()
    df1['key'] = df1.index
    index_copy = df.index
    df = df.merge(right=df1, how='left', on='key')
    df.index = index_copy
    df.drop(['key'], axis=1, inplace=True)
    df['is_ran_reset_today'] = df.apply(
            lambda row: bool(row['is_ran_reset_today']),axis=1)

    return df

def load_data_panes(panes_file):
    # Import
    dfun = lambda x: pd.datetime.strptime(x,'%Y-%m-%d-%H-%M')
    df = pd.read_csv(panes_file,engine='python',sep=': ',header=None, 
            parse_dates=True,date_parser=dfun,index_col=0)

    # Clean
    df.columns = ['panes']
    df.index.name = 'date'
    nHours = 9
    
    # Restamp dates more logically
    # For each datestamp at 9:07, record as datestamp of previous day at 18:07.
    def restamp(stamp):
        if stamp.hour == 9:
            delta = pd.Timedelta(hours=-15)
            new_stamp = stamp + delta
            return new_stamp
        else:
            return stamp

    df = df.reset_index()
    df['date'] = df['date'].map(restamp)
    df = df.set_index('date')
    df = df.sort()
    return df

def load_data_serial(serial_file):
    dfun = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')
    df = pd.read_csv(serial_file, parse_dates=True,date_parser=dfun,index_col=3)

    return df

def merge_panes_serial(panes, serial):
    df = panes.merge(serial, how='left', left_index=True, 
            right_index=True)
    df.index.name = 'date'

    # Remove duplicates
    df = df.reset_index().drop_duplicates(subset='date',
            take_last=True).set_index('date').sort()

    # Rename 'episode', and refactor
    df.rename(columns={'episode':'has_episode_today'}, inplace=True)
    df['has_episode_today'] = ~df['has_episode_today'].map(np.isnan)

    return df

if __name__ == "__main__":
    home = '/Users/micahsmith/Development/workspace/panes/'

    panes_file = home+'Data/Raw/panesmdc.txt'
    panes = load_data_panes(panes_file)
    panes = add_variables(panes)
    panes = collapse_to_daily(panes)

    serial_file = home+'Data/Raw/serial_episodes.csv'
    serial = load_data_serial(serial_file)

    panes = merge_panes_serial(panes, serial)

    # Prepare data
    panes = panes[~panes['is_ran_reset_today']]
    panes = panes[panes['is_workday']]

    panes_train = panes[:'2015-04-01']
    panes_test = panes['2015-04-01':]

    labels_train = panes_train['has_episode_today']
    data_train = panes_train[['absd1panes','sqd1panes','is_mon','is_tue','is_wed','is_thu']]

    labels_test = panes_test['has_episode_today']
    data_test = panes_test[['absd1panes','sqd1panes','is_mon','is_tue','is_wed','is_thu']]

    # Train
    rng = np.random.RandomState(123)
    model = AdaBoostRegressor(DecisionTreeRegressor(max_depth=4),n_estimators=300,random_state=rng)
    model.fit(data_train,labels_train)

    # Test
    ind = data_test.index
    pred = model.predict(data_test)
    data_pred = pd.DataFrame(pred,index=ind,columns=['pred'])
    data_pred_high = data_pred[data_pred['pred']>0.5]

    # Output table
    format = lambda x: '{0:.2f}'.format(x)
    fname = home+'Results/Tables/pred_high.tex'
    with open(fname,'w') as f:
        f.write(data_pred_high.to_latex(float_format=format))

    print('done')
