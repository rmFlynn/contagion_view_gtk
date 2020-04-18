# start
import pandas as pd
import geopandas as gpd
import numpy as np
import geoplot as gplt
import geoplot.crs as gcrs
import mapclassify
import matplotlib.pyplot as plt
import seaborn as sea



# data = gpd.read_file('./data_set2/full_data.shp')
data = pd.read_pickle('data_set3.pkl')
obs = list(data.columns[37:])
times = pd.DataFrame()
times['day_str'] = obs
times['day'] = pd.to_datetime(times.day_str, infer_datetime_format=True)
#counties = ['Denver', 'King', 'New York']
counties = ['Denver', 'New York']
dfs = []
for county in counties:
    t_data = data[data.county_name == county][obs].T
    t_data = t_data.reset_index()
    t_data.columns = ['day_str', 'cases']
    t_data = t_data[t_data['cases'] > 0]
    pop = data[data.county_name == county]['pop'].values[0]
    #t_data['cases'] = t_data['cases']/(pop / 100000)
    t_data['county'] = county 
    t_data['day'] = pd.to_datetime(t_data.day_str, infer_datetime_format=True)
    dfs.append(t_data.copy())

c_data = pd.concat(dfs)
times =  times[[i in c_data.day_str.values for i in times.day_str.values]]
plt.clf()
plt.figure(figsize=(20,9))
plot = sea.pointplot(y='cases', x='day', hue="county",  markers='o', data=c_data)
#plot = sea.lineplot(y='cases', x='day_str', hue="county",  markers='O', data=t_data)
#plot.set_xticklabels(plot.get_xticklabels(), rotation=45)
#plot.get_xticklabels()
plot.set_xticklabels(times.day_str, rotation=45)
plt.savefig("counties_over_time.png")#, transparent=True)

def state_cp(state, data, day, lable=False):
    dat = data[data['STNAME'] == state].copy()
    scheme = mapclassify.Quantiles(dat[day], k=20)
    plt.clf()
    gplt.choropleth(
                dat,
                hue=dat[day], 
                scheme=scheme,
                cmap='Reds', linewidth=0,
                edgecolor='white',
                legend=False
                )
    if lable:
        dat['coords'] = dat.geometry.centroid.apply(lambda x: x.representative_point().coords[:])
        dat['coords'] = [coords[0] for coords in dat['coords']]
        for idx, row in dat.iterrows():
            plt.annotate(s=row['county_nam'], xy=row['coords'],
                                 horizontalalignment='center')
    plt.savefig(state+day + ".png", bbox_inches='tight', pad_inches=0.1, transparent=True)

state_cp('Nevada', data ,data.columns[-2], lable=True)
state_cp('Colorado', data ,data.columns[-2], lable=True)

obs = list(data.columns[:35])
day = obs[-1]
case_per_n = data[day] / (data['pop'] / 1000)
#scheme = mapclassify.Quantiles(case_per_n, k=20)
datac = data[data[day] > 3]
datac['geometry'] = datac.geometry.centroid

ax = gplt.polyplot(contiguous_usa,projection=gcrs.WebMercator())
gplt.kdeplot(datac, clip = contiguous_usa, ax=ax)

def point_plot(data, day):
    contiguous_usa = gpd.read_file(gplt.datasets.get_path('contiguous_usa'))
    plt.clf()
    dat = data.copy()
    dat.geometry = dat.geometry.centroid
    point_kwargs = {
                 'edgecolor': 'black', 'linewidth': 0.5
                }
    ax = gplt.webmap(contiguous_usa, projection=gcrs.WebMercator())
    gplt.pointplot(
                dat, projection=gcrs.AlbersEqualArea(),
                scale=day,
                limits=(0,200),
                hue=day, 
                cmap='Reds',
                #legend=True,
                ax=ax,
                **point_kwargs
                )
    #dat = dat.sort_values(by=[day], ascending=False)
    #dat_max = dat.head(20).copy()
    #dat_max['coords'] = dat_max.geometry.centroid.apply(lambda x: x.representative_point().coords[:])
    #dat_max['coords'] = [coords[0] for coords in dat_max['coords']]
    #for idx, row in dat_max.iterrows():
    #    plt.annotate(s=row['county_nam'], xy=row['coords'],
    #                horizontalalignment='center')
    plt.savefig("nat_"+day + ".png", bbox_inches='tight', pad_inches=0.1)


state = "Colorado"
day = obs[-2]

dat = data[data['STNAME'] == state]
obs = list(dat.columns[35:-1])
scheme = mapclassify.Quantiles(dat[day], k=20)

ax = dat.plot(cmap='Reds', linewidth=0)
dat['coords'] = dat.geometry.centroid.apply(lambda x: x.representative_point().coords[:])
dat['coords'] = [coords[0] for coords in dat['coords']]
for idx, row in dat.iterrows():
    plt.annotate(s=row['CTYNAME'], xy=row['coords'],
                         horizontalalignment='center')

ax.figure.savefig(state+day + ".png", bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.clf()








contiguous_usa = gpd.read_file(gplt.datasets.get_path('contiguous_usa'))
ax = gplt.webmap(contiguous_usa)
gplt.pointplot(data.geometry.centroid, projection=gcrs.WebMercator(), ax=ax)
plt.savefig("boston-airbnb-kde.png", bbox_inches='tight', pad_inches=0.1)


exit(0)

obs = list(data.columns[35:-1])
day = obs[-1]
case_per_n = data[day] / (data['pop'] / 1000)
case_per_n.min() 
case_per_n.max()
day = day.replace("/", "-")
scheme = mapclassify.Quantiles(case_per_n, k=20)

gplt.choropleth(
            data,
            hue=case_per_n, 
            scheme=scheme,
            cmap='Reds', linewidth=0.5,
            edgecolor='white',
            legend=False
            )
plt.savefig("nation_"+day + ".png", bbox_inches='tight', pad_inches=0.1, transparent=True)

# Note: this code sample requires geoplot>=0.4.0.
ax = geoplot.choropleth(data, hue=case_per_n, scheme=scheme,
                cmap='Greens', figsize=(24, 15)
                )

ax.figure.savefig("nation_"+day, transparent=True, dpi=300)






import geopandas as gpd
import geoplot.crs as gcrs
import matplotlib.pyplot as plt
import mplleaflet


ax = gplt.kdeplot(
            data, cmap='viridis', projection=gcrs.WebMercator(), figsize=(12, 12),
                shade=True
                )
gplt.pointplot(data.geometry.centroid, s=1, color='black', ax=ax)
gplt.webmap(data, ax=ax)
plt.title('Boston AirBnB Locations, 2016', fontsize=18)

fig = plt.gcf()
plt.savefig("boston-airbnb-kde.png", bbox_inches='tight', pad_inches=0.1)







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



#shapefile = './ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp'#Read shapefile using Geopandas
shapefile1 = './map2/tl_2017_us_county.shp'
shapefile2 = './map3/US_County_Boundaries.shp'
#state_name = pd.read_csv('state_code.csv')
gdf1 = gpd.read_file(shapefile1)#[['ADMIN', 'ADM0_A3', 'geometry']]#Rename columns.
gdf2 = gpd.read_file(shapefile2)#[['ADMIN', 'ADM0_A3', 'geometry']]#Rename columns.
gdf = gpd.sjoin(gdf2, gdf1, how="inner", op='intersects')

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

#for i in data.columns:
#    data[i].head()
#
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
data.to_file("data_set1/full_data.shp")
#data2 =gpd.read_file("full_data.shp")
