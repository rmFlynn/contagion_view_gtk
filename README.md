# Contagion View GTK

sudo apt install libgeos-dev libproj-dev proj-data proj-bina

## Get US county map data 

wget ftp://ftp2.census.gov/geo/tiger/TIGER2019/COUNTY/tl_2019_us_county.zip

unzip tl_2019_us_county.zip -d us_county_shapes

rm tl_2019_us_county.*

## Johns Hopkins University COVID-19 Data
This is the data repository for the 2019 Novel Coronavirus Visual Dashboard operated by the Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE). Also, Supported by ESRI Living Atlas Team and the Johns Hopkins University Applied Physics Lab (JHU APL). We use this data very difrently to that system.

unzip tl_2019_us_county.zip

git submodule update --init 
