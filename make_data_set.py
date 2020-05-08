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
pop = pop_raw[list(pop_raw.columns[:7])].copy()
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
obs = list(data.columns[36:])
for day in obs:
    data.rename(columns = {day: day.replace("/", "-")}, inplace=True)

obs = list(data.columns[36:])
data = data[data[obs[-1]] > 0]

for day in obs:
    data[day] = data[day].values.astype('int32')

data.rename(columns = {'NAME': 'county_name'}, inplace=True)
data.rename(columns = {'STNAME': 'state_name'}, inplace=True)
data.geometry = data.geometry.centroid.representative_point()
data_pd = pd.DataFrame(data)
data_pd.geometry = data.geometry.apply(lambda x : x.coords[:][0])
data = data_pd

data = data.reset_index()

data[day] = data[day].values.astype('int32')
data.geometry = data.geometry.apply(lambda x: np.asarray(x).astype('float32'))

for i in data.columns:
    data[i].head()

# #print(self.days)
# max_case = np.amax(self.data[self.days].values)
# for day in self.days:
#     print(day)
#     sizes = []
#     for _, i in self.data.iterrows():
#         size = int(i[day]/(max_case/500))
#         if (size < 7) and (i[day] > 0):
#             size = 7
#         sizes.append(size)
#     self.data[day] = sizes
# self.make_marker_layer(self.view)
#print(self.days)
max_case = np.amax(data[obs].values)

data_total = data.copy()
for day in obs:
    print(day)
    sizes = []
    for _, i in data_total.iterrows():
        size = int(i[day]/(max_case/500))
        if (size < 7) and (i[day] > 0):
            size = 7
        sizes.append(size)
    data_total[day+"_size"] = sizes

data_total.to_pickle("data_state_total.pkl")

data_permi = data.copy()
for day in obs:
    print(day)
    sizes = []
    ipmis= []
    for _, i in data_permi.iterrows():
        ipmi = int((i[day]*1000000)/i['pop'])
        size = int((i[day]*10000)/i['pop'])
        if (size < 7) and (i[day] > 0):
            size = 7
        sizes.append(size)
        ipmis.append(ipmi)
    data_permi[day] = ipmis
    data_permi[day+"_size"] = sizes

data_permi.to_pickle("data_state_permi.pkl")

np.amax(data_permi[[i +"_size" for i in obs]].values)
np.amax(data_permi[obs].values)
np.amax(data_total[[i +"_size" for i in obs]].values)
np.amax(data_total[obs].values)

keep_state = []
keep_county = []
for day in obs:
    data_total = data_total.sort_values(by=day, ascending=False)
    ks = data_total[data_total[day] > 0].head(100)['state_name'].values
    kc = data_total[data_total[day] > 0].head(100)['county_name'].values
    keep_state = np.concatenate([keep_state, ks])
    keep_county = np.concatenate([keep_county, kc])

keep = pd.DataFrame({'state_name': keep_state, 'county_name': keep_county})
keep = keep.drop_duplicates()
data_total = pd.merge(data_total, keep , on = ['state_name', 'county_name'])
data_total.to_pickle("data_nation_total.pkl")

keep_state = []
keep_county = []
for day in obs:
    data_permi = data_permi.sort_values(by=day, ascending=False)
    ks = data_permi[data_permi[day] > 0].head(100)['state_name'].values
    kc = data_permi[data_permi[day] > 0].head(100)['county_name'].values
    keep_state = np.concatenate([keep_state, ks])
    keep_county = np.concatenate([keep_county, kc])

keep = pd.DataFrame({'state_name': keep_state, 'county_name': keep_county})
keep = keep.drop_duplicates()
data_permi = pd.merge(data_permi, keep , on = ['state_name', 'county_name'])

data_permi.to_pickle("data_nation_permi.pkl")
np.save("days.npy", obs)

i['county_name'], i['state_name']


#data.to_file("data_set2/full_data.shp")
#data2 =gpd.read_file("full_data.shp")

