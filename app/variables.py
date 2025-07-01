import os
import ibis
from ibis import _
import ibis.selectors as s
from cng.utils import *
from cng.h3 import *
from minio import Minio
import streamlit 
from datetime import datetime, timedelta
import streamlit
import re
duckdb_install_h3()

con = ibis.duckdb.connect(extensions = ["spatial", "h3"])
con.raw_sql("SET THREADS=100;")
set_secrets(con)

print('variables.py is executed')

# Get signed URLs to access license-controlled layers
key = st.secrets["MINIO_KEY"]
secret = st.secrets["MINIO_SECRET"]
client = Minio("minio.carlboettiger.info", key, secret)

tpl_z8 = con.read_parquet("s3://shared-tpl/conservation_almanac/z8/tpl_h3_z8.parquet", table_name = 'conservation_almanac')
landvote_z8 = con.read_parquet("s3://shared-tpl/landvote/z8/landvote_h3_z8.parquet", table_name = 'landvote')
mobi_z8 = con.read_parquet("https://minio.carlboettiger.info/public-mobi/hex/all-richness-h8.parquet", table_name = 'mobi')
svi_z8 = con.read_parquet("https://minio.carlboettiger.info/public-social-vulnerability/2022/SVI2022_US_tract_h3_z8.parquet",table_name = 'svi')
carbon_z8 = con.read_parquet("https://minio.carlboettiger.info/public-carbon/hex/us-tracts-vuln-total-carbon-2018-h8.parquet",table_name = 'carbon')

county_bounds = con.read_parquet("https://minio.carlboettiger.info/public-census/2024/county/2024_us_county.parquet")
landvote_table = con.read_parquet("s3://shared-tpl/landvote/landvote_geom.parquet")
tpl_table = con.read_parquet('s3://shared-tpl/conservation_almanac/tpl.parquet')

# @st.cache_data(ttl = timedelta(hours=2))
def get_pmtiles_url():
    return client.get_presigned_url(
        "GET",
        "shared-tpl",
        "conservation_almanac/tpl.pmtiles",
        expires=timedelta(hours=2),
    )

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
                ["get", "amount"],
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
            'property': 'manager_type',
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
        'property': 'access_type',
        'type': 'categorical',
        'stops': [
            ['OA', green],
            ['XA', red],
            ['UK', dark_grey],
            ['RA', orange]
        ]
    },
    "Purpose": {
        'property': 'purpose_type',
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
                'Acquisition Cost': 'amount',
                'Measure Cost': 'conservation_funds_approved',
             }

from langchain_openai import ChatOpenAI
import streamlit as st

## dockerized streamlit app wants to read from os.getenv(), otherwise use st.secrets
import os
api_key = os.getenv("NRP_API_KEY")
if api_key is None:
    api_key = st.secrets["NRP_API_KEY"]

llm_options = {
    "gemma3": ChatOpenAI(model = "gemma3", api_key=api_key, base_url = "https://llm.nrp-nautilus.io/",  temperature=0),
    "llama3.3": ChatOpenAI(model = "llama3-sdsc", api_key=api_key, base_url = "https://llm.nrp-nautilus.io/",  temperature=0),
    "watt": ChatOpenAI(model = "watt", api_key=api_key, base_url = "https://llm.nrp-nautilus.io/",  temperature=0),
}
