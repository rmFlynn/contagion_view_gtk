# start
import pandas as pd
import geopandas as gpd
import numpy as np

# To many files not vary useful
# pd.read_csv('./COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/01-22-2020.csv')
cov = pd.read_csv('./covid_csse/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
# Check the numbers
# cov_d_raw[cov_d_raw['Country_Region'] != 'US']
cov.columns

#cov_d_raw = pd.read_csv('./ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp')
#cov_d_raw = pd.read_csv('./ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp')
pop_raw = pd.read_csv('./co-est2019-alldata.csv', encoding='latin-1')
pop = pop_raw[list(pop_raw.columns[:7])]
pop['pop'] = pop_raw['POPESTIMATE2019']



shapefile1 = './map2/tl_2017_us_county.shp'
shapefile2 = './map3/US_County_Boundaries.shp'
#state_name = pd.read_csv('state_code.csv')
gdf1 = gpd.read_file(shapefile1)#[['ADMIN', 'ADM0_A3', 'geometry']]#Rename columns.
gdf2 = gpd.read_file(shapefile2)#[['ADMIN', 'ADM0_A3', 'geometry']]#Rename columns.
gdf = gdf1#gpd.sjoin(gdf2, gdf1, how="inner", op='intersects')

#for i in gdf.columns:
#    gdf[i].head()
#
#for i in pop.columns:
#    pop[i].head()

pop.rename(columns = {'STATE': "state", 'COUNTY': "county"}, inplace=True)
gdf.rename(columns = {'STATEFP': "state", 'COUNTYFP': "county"}, inplace=True)
gdf['state'] = gdf['state'].values.astype('int64')
gdf['county'] = gdf['county'].values.astype('int64')
data = pd.merge(gdf, pop, on=["state", "county"])
#data['STNAME'].unique()
#
#for i in cov.columns[:10]:
#    cov[i].head()




cov = gpd.GeoDataFrame(cov, geometry=gpd.points_from_xy(cov['Long_'], cov['Lat']))
cov = cov[cov['Long_'] != 0]
#cov[['geometry','Province_State']]

data = data[data.columns[data.columns != 'index_right']]
data = gpd.sjoin(data, cov, how="inner", op='intersects')
#data['geometry'] 
#data[["Province_State",'STNAME']][data["Province_State"] == 'Michigan']

#data['STNAME'].unique()



#list(data.columns)
data = data[data['STNAME'] != "Alaska"]
#data = data[data['STNAME'] == "Michigan"]
data = data[data['STNAME'] != "Hawaii"]
data = data[data['STNAME'] != "Virgin Islands"]
data = data[data['STNAME'] != "Puerto Rico"]
obs = list(data.columns[35:])
for day in obs:
    data.rename(columns = {day: day.replace("/", "-")}, inplace=True)

obs = list(data.columns[35:])
data = data[data[obs[-1]] > 0]

for i in data.columns:
    data[i].head()

data.rename(columns = {'NAME': 'county_name'}, inplace=True)

data.to_file("data_set2/full_data.shp")
#data2 =gpd.read_file("full_data.shp")

