import os
import ibis
from ibis import _
import ibis.selectors as s
from cng.utils import *
from cng.h3 import *
from minio import Minio
import streamlit 
from datetime import timedelta
import re
duckdb_install_h3()

# con = ibis.duckdb.connect("duck.db",extensions = ["spatial", "h3"])
con = ibis.duckdb.connect(extensions = ["spatial", "h3"])
set_secrets(con)

# Get signed URLs to access license-controlled layers
key = st.secrets["MINIO_KEY"]
secret = st.secrets["MINIO_SECRET"]
client = Minio("minio.carlboettiger.info", key, secret)

tracts_z8 = con.read_parquet("https://minio.carlboettiger.info/public-social-vulnerability/2022-tracts-h3-z8.parquet").select('FIPS','h8').mutate(h8 = _.h8.lower()).rename(FIPS_tract = "FIPS")
pad_z8 = con.read_parquet("https://minio.carlboettiger.info/public-biodiversity/pad-us-4/pad-h3-z8.parquet")
mobi = con.read_parquet("https://minio.carlboettiger.info/public-mobi/hex/all-richness-h8.parquet").select("h8", "Z").rename(richness = "Z")
svi = con.read_parquet("https://minio.carlboettiger.info/public-social-vulnerability/2022/SVI2022_US_tract.parquet").select("FIPS", "RPL_THEMES").filter(_.RPL_THEMES > 0).rename(svi = "RPL_THEMES").rename(FIPS_tract = "FIPS")
# carbon = con.read_parquet("https://minio.carlboettiger.info/public-carbon/hex/us-vulnerable-total-carbon-2018-h8.parquet").select('carbon','h8')

carbon = con.read_parquet("https://minio.carlboettiger.info/public-carbon/hex/us-tracts-vuln-total-carbon-2018-h8.parquet").select('carbon','h8')

tpl_geom_url = "s3://shared-tpl/tpl.parquet"
tpl_table = con.read_parquet(tpl_geom_url).mutate(geom = _.geom.convert("ESRI:102039", "EPSG:4326")).rename(year = 'Close_Year', state_name = 'State', county = 'County')

county_bounds = con.read_parquet("https://minio.carlboettiger.info/public-census/2024/county/2024_us_county.parquet")
landvote_z8 = (con.read_parquet("s3://shared-tpl/landvote_h3_z8.parquet")
            .rename(FIPS_county = "FIPS", measure_amount = 'Conservation Funds Approved', 
                    measure_status = "Status", measure_purpose = "Purpose",)
            .mutate(measure_year = _.Date.year()).drop('Date','geom'))


landvote_table = (con.read_parquet("s3://shared-tpl/landvote_geom.parquet")
            .rename(FIPS_county = "FIPS", measure_amount = 'Conservation Funds Approved', 
                    measure_status = "Status", measure_purpose = "Purpose")
            .mutate(year = _.Date.year()).drop('Date'))


tpl_drop_cols = ['Reported_Acres','Close_Date','EasementHolder_Name',
        'Data_Provider','Data_Source','Data_Aggregator',
        'Program_ID','Sponsor_ID']
tpl_z8_url = "s3://shared-tpl/tpl_h3_z8.parquet"
tpl_z8 = con.read_parquet(tpl_z8_url).mutate(h8 = _.h8.lower()).drop(tpl_drop_cols)

select_cols = ['fid','TPL_ID','landvote_id',
'state','state_name','county',
 'FIPS_county', 'FIPS_tract',
 'city','jurisdiction',
 'Close_Year', 'Site_Name',
 'Owner_Name','Owner_Type',
 'Manager_Name','Manager_Type',
 'Purchase_Type','EasementHolder_Type',
 'Public_Access_Type','Purpose_Type',
 'Duration_Type','Amount',
 'Program_Name','Sponsor_Name',
 'Sponsor_Type','measure_year',
 'measure_status','measure_purpose',
 'measure_amount',
 'carbon',
 'richness','svi',
 'h8']



database = (
  tpl_z8.drop('State','County')
  .left_join(landvote_z8, "h8").drop('h8_right')
  .left_join(mobi, "h8").drop('h8_right')
  .left_join(carbon, "h8").drop('h8_right')
  .left_join(tracts_z8, "h8").drop('h8_right')
  .inner_join(svi, "FIPS_tract")
).select(select_cols).distinct()

database_geom = (database.drop('h8').distinct().inner_join(tpl_table.select('geom','TPL_ID','fid','Shape_Area'), [database.TPL_ID == tpl_table.TPL_ID, database.fid == tpl_table.fid])
            .mutate(acres = _.Shape_Area*0.0002471054)
           ).distinct()

pmtiles = client.get_presigned_url(
    "GET",
    "shared-tpl",
    "tpl_v2.pmtiles",
    expires=timedelta(hours=2),
)
# source_layer_name = re.sub(r'\W+', '', os.path.splitext(os.path.basename(pmtiles))[0]) #stripping hyphens to get layer name 
source_layer_name = 'tpl'


states = (
    "All", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
)

# Define color hex codes
darkblue = "#00008B"
blue = "#0096FF"
lightblue = "#ADD8E6"
darkgreen = "#006400"
grey = "#c4c3c3"
dark_grey = "#5a5a5a"
green = "#008000"
purple = "#800080"
darkred = "#8B0000"
orange = "#FFA500"
red = "#e64242"
yellow = "#FFFF00"
pink = '#FFC0CB'

style_options = {
    "Acquisition Cost":  
            ["interpolate",
                ['exponential', 1], 
                ["get", "Amount"],
                    0,	"#fde725",
                    36000,	"#b4de2c",
                    93000,	"#6ccd59",
                    156500,	"#35b779",
                    240000,	"#1f9e89",
                    335000,	"#26828e",
                    500000,	"#31688e",
                    796314,	"#3e4a89",
                    1634000,	"#482878",
                    308461380,	"#430154",
                    ] 
            ,
    "Manager Type":  {
            'property': 'Manager_Type',
            'type': 'categorical',
            'stops': [
                ['FED', darkblue],
                ['STAT', blue],
                ['LOC', lightblue],
                ['DIST', darkgreen],
                ['UNK', dark_grey],
                ['JNT', pink],
                ['TRIB', purple],
                ['PVT', darkred],
                ['NGO', orange]
            ]
            },
    "Access": {
        'property': 'Public_Access_Type',
        'type': 'categorical',
        'stops': [
            ['OA', green],
            ['XA', red],
            ['UK', dark_grey],
            ['RA', orange]
        ]
    },
    "Purpose": {
        'property': 'Purpose_Type',
        'type': 'categorical',
        'stops': [
            ['FOR', green],
            ['HIST', red],
            ['UNK', dark_grey],
            ['OTH', grey],
            ['FARM', yellow],
            ['REC', blue],
            ['ENV', purple],
            ['SCE', orange],
            ['RAN', pink]
        ]
    },
}

style_choice_columns = {'Manager Type': style_options['Manager Type']['property'],
              'Access' : style_options['Access']['property'],
              'Purpose': style_options['Purpose']['property'],
                'Acquisition Cost': 'Amount',
                'Measure Cost': 'measure_amount',
             }

# metric_columns = {'svi': 'svi', 'mobi': 'richness', 'landvote':'measure_status'}

from langchain_openai import ChatOpenAI
import streamlit as st

## dockerized streamlit app wants to read from os.getenv(), otherwise use st.secrets
import os
api_key = os.getenv("NRP_API_KEY")
if api_key is None:
    api_key = st.secrets["NRP_API_KEY"]

llm_options = {
    "llama3.3": ChatOpenAI(model = "llama3-sdsc", api_key=api_key, base_url = "https://llm.nrp-nautilus.io/",  temperature=0),
    "gemma3": ChatOpenAI(model = "gemma3", api_key=api_key, base_url = "https://llm.nrp-nautilus.io/",  temperature=0),
    "watt": ChatOpenAI(model = "watt", api_key=api_key, base_url = "https://llm.nrp-nautilus.io/",  temperature=0),
}
