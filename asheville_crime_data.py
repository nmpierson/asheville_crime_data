'''
Program to analyze crime patterns by location

Data downloaded from https://data-avl.opendata.arcgis.com/search?tags=publicsafety

Nicholas Pierson
'''

import requests
import urllib.parse
import pandas as pd
import geopy.distance

def load_data():

    # Read in arrest data, downloaded from https://data-avl.opendata.arcgis.com/search?tags=publicsafety
    df_arrests = pd.read_csv('source_files/APD_Arrests.csv')

    # Find total arrests per year via aggregation
    df_arrests['Year'] = [x.split('/')[0] for x in df_arrests['date_arrested']]
    total_arrests_per_year = df_arrests.groupby('Year').agg({'address': 'count'}).reset_index().rename(columns={'address':'Total Arrests'})

    df_arr_20_21 = df_arrests[df_arrests['Year'].isin(['2020', '2021'])]
    df_arr_20_21['offense_type'].unique()
    df_arr_20_21.to_csv('output/arrests_2020_2021.csv', index=False)

    # Read in past 5 years of 911 call data
    df_2017 = pd.read_csv('source_files/APD_CAD_911_Calls_2017.csv')
    df_2018 = pd.read_csv('source_files/APD_CAD_911_Calls_2018.csv')
    df_2019 = pd.read_csv('source_files/APD_CAD_911_Calls_2019.csv')
    df_2020 = pd.read_csv('source_files/APD_CAD_911_Calls_2020.csv')
    df_2021 = pd.read_csv('source_files/APD_CAD_911_Calls_2021.csv')

    # Create dataframe with total calls per year, prefilter
    d911_prefilter = {
        2017: len(df_2017),
        2018: len(df_2018),
        2019: len(df_2019),
        2020: len(df_2020),
        2021: len(df_2021)
    }

    # Standardize column names (pre-2020 included upper casing)
    dfs = [df_2017, df_2018, df_2019, df_2020, df_2021]
    for df in dfs:
        df.columns = df.columns.str.lower()


    call_resolutions= df_2021['call_disposition'].unique()
    print(len(call_resolutions))
    print(call_resolutions)
    # 73 different possible call resolutions; 12 involving cancellations/false alarms. 
    # Filter cancellations and false alarms

    cancel = [
        'CANCEL PER ALARM COMPANY',
        'FALSE ALARM', 
        'NO POLICE ACTION NEEDED',
        'CANCEL PER COMPLAINANT/CALLER',
        'CANCEL PER LAW ENFORCEMENT',
        'CANCEL PER EOC',
        'UNFOUNDED CALL',
        'CANCEL PER FIRE DEPARTMENT',
        'CANCEL OUTSIDE JURISDICTION',
        'FALSE ALARM SURGHARGE',
        'CANCEL - STUCK IN STACK',
        'FALSE ALARM WEATHER RELATED'
    ]

    for i, df in enumerate(dfs):
        dfs[i] = df[-df['call_disposition'].isin(cancel)]

    # Overwrite dfs
    df_2017 = dfs[0]
    df_2018 = dfs[1]
    df_2019 = dfs[2]
    df_2020 = dfs[3]
    df_2021 = dfs[4]

    d911 = {
        2017: len(df_2017),
        2018: len(df_2018),
        2019: len(df_2019),
        2020: len(df_2020),
        2021: len(df_2021)
    }

    df911 = pd.DataFrame.from_dict(d911, orient='index').reset_index()
    df911 = df911.rename(columns={'index': 'Year', 0: '911 Incidents'})

    # Integrate arrest data
    tapy_2017_2021 = total_arrests_per_year[total_arrests_per_year['Year'].isin(['2017', '2018', '2019', '2020', '2021'])]
    df911['Total Arrests'] = list(tapy_2017_2021['Total Arrests'])

    # Locate homeless camp 911 calls, add to dataframe

    homeless_reports = []
    for i, frame in enumerate(dfs):
        homeless_reports.append(len(frame[frame['call_nature']=='HOMELESS CAMP']))
    df911['Homeless Camp 911 Calls'] = homeless_reports

    df911.to_csv('output/Asheville 5 Year Crime Data.csv', index=False)
    

    call_types = df_2021['call_nature'].unique()
    print(len(call_types))
    # 207 distinct types of calls

    # Categories used in the police report
    violent = ['Rape', 'Robbery - Armed', 'Robbery - Common Law', 'Agg Assault']
    property = ['Arson', 'Burglary - Commercial', 'Burglary - Residential', 'Motor Vehicle Theft',
                'Larceny - CarBand E-Forcible', 'Larceny - CarBand E-NonForci', 
                'Larceny- Other', 'Larceny - Shoplifting']
    
    print(call_types)
    # Categories matched in the dataset
    keep_types = ['RAPE', 'COMMON LAW ROBBERY', 'ARMED ROBBERY', 
                 'ASSAULT / SEXUAL ASSAULT', 'ASSAULT ON FEMALE', 'SIMPLE ASSAULT', 'SEXUAL ASSAULT',
                 'DUMPSTER FIRE', 'HOMELESS CAMP', 'SHOPLIFTING', 
                 'LARCENY FROM VEHICLE', 'LARCENY IN PROGRESS',
                 'LARCENY MOTOR VEHICLE', 'LARCENY REPORT']

    # Filtered dataframes based on specified crimes
    filtered_dfs = []
    for frame in dfs:
        filtered_df = frame[frame['call_nature'].isin(keep_types)]
        filtered_dfs.append(filtered_df)
        print(len(filtered_df))

    for i, frame in enumerate(filtered_dfs):
        frame.to_csv('output/911_filtered_{}.csv'.format(2017+i), index=False)

    # Slight formatting differences from year to year; 2021 first
    # 2021

def analyze_data(df='output/arrests_2020_2021.csv'):
    '''
    Function to analyze data loaded and transformed in the previous function.
    The find_df_locations function and its helper function find_loc
    can be time-consuming due to API call limits on the open source
    Nominatim API.Utilizing the paid Google API would be approximately
    50 times faster if available.

    Inputs: 
        df (string, name of a dataframe to be read in)

    Outputs: 
        no function return; several CSVs written from df
    '''

    adf = pd.read_csv(df)
    
    # Format addresses for API call
    adf['address'] = format_address(adf['address'])

    # Find geo coordinates.
    adf['geo'] = find_df_locations(adf['address'])

    # Filtering out locations unable to be matched via Nominatim API
    adff = adf[-adf['geo'].isin(['Not found, Not found'])]
    print(len(adff)/len(adf))
    #88.5% of arrest addresses given were able to be matched via Nominatim

    # Matching camps to geo locations

    #   Commented block below includes original process of geotagging 
    #   the police's given locations

    # camp_df = pd.read_excel('source_files/camp_locations.xlsx')
    # for i in range(len(camp_df)):
    #     add = camp_df['Location'].iloc[i]
    #     add = add + ' Asheville North Carolina'
    #     camp_df['Geo'].iloc[i] = find_loc(add)
    # camp_df.to_csv('source_files/camp_locations.csv', index=False)

    camp_df = pd.read_csv('source_files/camp_locations.csv')

    # Creating column rename dictionary for convenience
    cd = {}
    for i in range(len(camp_df)):
        addy = camp_df['Location'].iloc[i]
        geo = camp_df['Geo'].iloc[i]
        cd[geo] = addy

    # Adding distance columns
    adff = evaluate_distances(cd, adff)

    # adff.to_csv('arrest_analysis_in_progress.csv', index=False)

    # Initializing new dataframe with Boolean columns
    adf2 = adff[['OBJECTID',
                 'date_arrested',
                 'time_arrested',
                 'address',
                 'offense_type',
                 'subject_race',
                 'subject_gender',
                 'agency',
                 'armainid',
                 'objectid_1',
                 'Year',
                 'geo']]

    new_cols = []
    for col in cd.keys():

        adf2[cd[col] + ' <= 1000'] = adff[col] < 1000
        adf2[cd[col] + ' <= 500'] = adff[col] < 500
        new_cols.append(cd[col] + ' <= 1000')
        new_cols.append(cd[col] + ' <= 500')

        # Check for duplicate counts.
    adf2
        
    
    base_cols = [
        'OBJECTID', 'date_arrested', 'time_arrested', 'address', 'offense_type',
        'subject_race', 'subject_gender', 'agency', 'armainid', 'objectid_1',
        'Year', 'geo'
    ]
    cols_500 = [
        col for col in adf2.columns if '500' in col
    ]
    ccols_500 = base_cols + cols_500

    cols_1000 = [
        col for col in adf2.columns if '1000' in col
    ]
    ccols_1000 = base_cols + cols_1000

    adf2_500 = adf2[ccols_500]
    adf2_1000 = adf2[ccols_1000]

    adf2_500['Duplicate Counts'] = adf2_500[cols_500].sum(axis=1)
    adf2_1000['Duplicate Counts'] = adf2_1000[cols_1000].sum(axis=1)

    adf2_500['Arrest Within 500'] = adf2_500['Duplicate Counts'] >= 1
    adf2_500['Arrest Within 500'] = adf2_500['Arrest Within 500'].astype(int)
    arr_within_500 = sum(adf2_500['Arrest Within 500'])
    print(arr_within_500)
    print(arr_within_500/len(adf2_500))
    # 14.7% of arrests occurring within 500 feet
    print(len(adf2_500[adf2_500['Duplicate Counts']>1]))
    print(len(adf2_500[adf2_500['Duplicate Counts']>=1]))
    # 492/1957 arrests within 500 feet were within more than one location
    # This would lead to a 25% overcount if locations are used as rows

    adf2_1000['Arrest Within 1000'] = adf2_1000['Duplicate Counts'] >= 1
    adf2_1000['Arrest Within 1000'] = adf2_1000['Arrest Within 1000'].astype(int)
    arr_within_1000 = sum(adf2_1000['Arrest Within 1000'])
    print(arr_within_1000)
    print(arr_within_1000/len(adf2_1000))
    # 27.1% of arrests occurring within 1000 feet
    dups = list(adf2_1000['Duplicate Counts'].unique())
    dups.sort()
    for dup in dups:
        if dup not in (0, 1):
            subdf = adf2_1000[adf2_1000['Duplicate Counts']==dup]
            print('Overcounts at {}: {}'.format(dup, len(subdf)))
            print('Percent overcounted: {}'.format(len(subdf)/len(adf2_1000[adf2_1000['Duplicate Counts']>=1])))
    adf2_1000['Overcount'] = adf2_1000['Duplicate Counts'] - adf2_1000['Arrest Within 1000']
    print(sum(adf2_1000['Overcount']))
    print(len(adf2_1000[adf2_1000['Duplicate Counts']>=1]))
    # With 3598 arrests, total overcounts reached 3848
    # This would lead to a 106.95% overcount if locations are used as rows

    # Filtering types used in the police's spreadsheet of 
    # certain violent and property crimes

    keep_types = [
        'SECOND DEGREE FORCIBLE RAPE',
        'SECOND DEGREE RAPE',
        'FIRST DEGREE FORCIBLE RAPE',
        'STATUTORY RAPE OF CHILD <= 15',
        'ASSAULT ON A FEMALE',
        'ROBBERY WITH DANGEROUS WEAPON',
        'ATTEMPTED COMMON LAW ROBBERY',
        'COMMON LAW ROBBERY',
        'ATT ROBBERY-DANGEROUS WEAPON',
        'ROBBERY - FREE TEXT',
        'ASSAULT WITH A DEADLY WEAPON',
        'MISDEMEANOR LARCENY',
        'SHOPLIFTING CONCEALMENT GOODS',
        'ASSAULT AND BATTERY',
        'LARC MERCHANT EXCH STOLEN PROP', 
        'SIMPLE ASSAULT',
        'ASSAULT INDIV W/ DISABILITY',
        'ASSAULT - FREE TEXT',
        'ASSAULT BY STRANGULATION',
        'ASSAULT BY POINTING A GUN',
        'ASSAULT INFLICT SERIOUS INJ(M)',
        'ARSON - FREE TEXT',
        'FIRST DEGREE ARSON',
        'FIRST DEGREE BURGLARY', 
        'SECOND DEGREE BURGLARY',
        'BURGLARY - FREE TEXT',
        'LARCENY OF MOTOR VEHICLE (F)',
        'LARCENY AFTER BREAK/ENTER',
        'FELONY LARCENY',
        'ATTEMPTED LARCENY (M)',
        'ATTEMPTED LARCENY (F)',
        'LARCENY OF A FIREARM',
        'LARCENY - FREE TEXT'
    ]

    adf500f = adf2_500[adf2_500['offense_type'].isin(keep_types)]
    gb500 = adf500f.groupby('offense_type').agg({'Arrest Within 500': 'sum'}).reset_index()
    gb500.to_csv('output/Arrests Within 500 ft.csv', index=False)
    arr500 = adf500f[adf500f['Arrest Within 500']>0]
    arr500['Duplicate Counts'].unique()
    len(arr500[arr500['Duplicate Counts']==2])
    # 67 total double counts
    len(arr500[arr500['Duplicate Counts']==2])/len(arr500)
    # 23.5 % of crimes were double counted

    adf1000f = adf2_1000[adf2_1000['offense_type'].isin(keep_types)]
    gb1000 = adf1000f.groupby('offense_type').agg({'Arrest Within 1000': 'sum'}).reset_index()
    gb1000.to_csv('output/Arrests Within 1000 ft.csv', index=False)
    arr1000 = adf1000f[adf1000f['Arrest Within 1000']>0]
    dups = list(arr1000['Duplicate Counts'].unique())
    dups.sort()
    for dup in dups:
        if dup != 1:
            subdf = arr1000[arr1000['Duplicate Counts']==dup]
            print('Overcounts at {}: {}'.format(dup, len(subdf)))
            print('Percent overcounted: {}'.format(len(subdf)/len(arr1000)))
    arr1000['Overcount'] = arr1000['Duplicate Counts'] - arr1000['Arrest Within 1000']
    sum(arr1000['Overcount'])

    # adf2.to_csv('adf.csv', index=False)

    # Repeating process with business locations
    bus_df = pd.read_excel('business_locations.xlsx')
    bd = {}
    for i in range(len(bus_df)):
        addy = bus_df['Address'].iloc[i]
        geo = bus_df['Geo'].iloc[i]
        geo = tuple(geo.split(', '))
        bd[geo] = addy


    adffb = evaluate_distances(bd, adff)
    new_cols_b = []
    for col in bd.keys():

        adffb[bd[col] + ' <= 1000'] = adffb[col] < 1000
        adffb[bd[col] + ' <= 500'] = adffb[col] < 500
        new_cols_b.append(bd[col] + ' <= 1000')
        new_cols_b.append(bd[col] + ' <= 500')

    base_cols = [
        'OBJECTID', 'date_arrested', 'time_arrested', 'address', 'offense_type',
        'subject_race', 'subject_gender', 'agency', 'armainid', 'objectid_1',
        'Year', 'geo'
    ]
    cols_500 = [
        col for col in adffb.columns if '500' in col
    ]
    ccols_500 = base_cols + cols_500

    cols_1000 = [
        col for col in adffb.columns if '1000' in col
    ]
    ccols_1000 = base_cols + cols_1000

    adffb_500 = adffb[ccols_500]
    adffb_1000 = adffb[ccols_1000]

    adffb_500['Duplicate Counts'] = adffb_500[cols_500].sum(axis=1)
    adffb_1000['Duplicate Counts'] = adffb_1000[cols_1000].sum(axis=1)

    adffb_500['Arrest Within 500'] = adffb_500['Duplicate Counts'] >= 1
    arr_within_500 = sum(adffb_500['Arrest Within 500'])
    print(arr_within_500)
    print(arr_within_500/len(adffb_500))
    # 14.1% of arrests occurring within 500 feet

    adffb_1000['Arrest Within 1000'] = adffb_1000['Duplicate Counts'] >= 1
    arr_within_1000 = sum(adffb_1000['Arrest Within 1000'])
    print(arr_within_1000)
    print(arr_within_1000/len(adffb_1000))
    # 26.2% of arrests occurring within 1000 feet

    # adffb.to_csv('adffb.csv', index=False)



def find_loc(address):
    '''
        Function to get geo coordinates for a location using
        the Nominatim API. Open use policy, but relatively slow.
        Nominatim caps queries at approximately 1 per second.

        Inputs: address (string)

        Outputs: coordinates (tuple of latitude and longitude floats, 
                              or Not Found string)
    '''

    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
    response = requests.get(url).json()
    try:
        lat, lon = response[0]['lat'], response[0]['lon']
    except:
        lat, lon = 'Not found', 'Not found'
        return (lat, lon)

    return (float(lat), float(lon))

def format_address(address_column):

    '''
    Formats addresses from police data into a format
    suitable for API calls.

        Inputs: address_column (list)

        Outputs: newadd (list)
    '''

    newadd = []
    for add in address_column:
        add = add.split(' ')
        add[0] = add[0].split('-')[0]
        s = ' '
        newadd.append(s.join(add))

    newadd = [x + ' Asheville North Carolina' for x in newadd]
    
    return newadd

def find_df_locations(address_column):
    '''
    Function to find all geo coordinates in a df column.

    Inputs:
        address_column (list, column from a df)
    
    Outputs:
        geo (list, column of coordinates)
    '''
    geo = []
    for i, addy in enumerate(address_column):
        print(i)
        geo.append(find_loc(addy))
    geo = [x if type(x[0])==float else ', '.join(list(x)) for x in geo]
    return geo

def evaluate_distances(cdict, df):
    '''
    Evaluates distances between a df and a camp dictionary

    Inputs:
        cdict (dictionary of locations and names)
        df (Pandas dataframe)
    
    Outputs:
        df (Pandas dataframe, modified to include new columns)
    '''

    for key in cdict:
        df[key] = None

    for i in range(len(df)):
        print(i)
        # Select crime coordinates
        ccoords = df['geo'].iloc[i]

        for col in cdict.keys():
            # Select location of purported encampment coordinates
            lcoords = list(col)
            lcoords = tuple([float(x) for x in lcoords])

            # Evaluate distance in feet
            d = geopy.distance.distance
            df[col].iloc[i] = d(ccoords, lcoords).feet

    # Once df has been modified in place, return df
    return df

