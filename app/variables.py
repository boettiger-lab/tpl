import os
import ibis
from ibis import _
import ibis.selectors as s
from cng.utils import *
from cng.h3 import *
from minio import Minio
import streamlit as st
from datetime import datetime, timedelta
import streamlit
import re
duckdb_install_h3()

con = ibis.duckdb.connect(extensions = ["spatial", "h3"])
con.raw_sql("SET THREADS=100;")
set_secrets(con, "", "", "minio.carlboettiger.info")

# Get signed URLs to access license-controlled layers
key = st.secrets["MINIO_KEY"]
secret = st.secrets["MINIO_SECRET"]
client = Minio("minio.carlboettiger.info", key, secret)

pmtiles = "https://minio.carlboettiger.info/public-tpl/conservation_almanac/tpl.pmtiles"
tpl_z8_url = "https://minio.carlboettiger.info/public-tpl/conservation_almanac/z8/tpl_h3_z8.parquet"
landvote_z8_url = "https://minio.carlboettiger.info/public-tpl/landvote/z8/landvote_h3_z8.parquet"
tpl_table_url = "https://minio.carlboettiger.info/public-tpl/conservation_almanac/tpl.parquet"
landvote_table_url = "https://minio.carlboettiger.info/public-tpl/landvote/landvote_geom.parquet"
county_bounds_url = "https://minio.carlboettiger.info/public-census/2024/county/2024_us_county.parquet"

mobi_z8_url = "https://minio.carlboettiger.info/public-mobi/hex/all-richness-h8.parquet"
svi_z8_url = "https://minio.carlboettiger.info/public-social-vulnerability/2022/SVI2022_US_tract_h3_z8.parquet"
carbon_z8_url = "https://minio.carlboettiger.info/public-carbon/hex/us-tracts-vuln-total-carbon-2018-h8.parquet"
lower_chamber_z8_url = "s3://public-census/2024/sld/lower/z8/**"
upper_chamber_z8_url = "s3://public-census/2024/sld/upper/z8/**"

tpl_z8 = con.read_parquet(tpl_z8_url, table_name = 'conservation_almanac')
landvote_z8 = con.read_parquet(landvote_z8_url, table_name = 'landvote')
tpl_table = con.read_parquet(tpl_table_url)
landvote_table = con.read_parquet(landvote_table_url)
county_bounds = con.read_parquet(county_bounds_url)

mobi_z8 = con.read_parquet(mobi_z8_url, table_name = 'mobi')
svi_z8 = con.read_parquet(svi_z8_url,table_name = 'svi')
carbon_z8 = con.read_parquet(carbon_z8_url, table_name = 'carbon')
lower_chamber_z8 = con.read_parquet(lower_chamber_z8_url, table_name = 'lower_chamber')
upper_chamber_z8 = con.read_parquet(upper_chamber_z8_url, table_name = 'upper_chamber')

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
                # ['linear'], 
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

basemaps = ['CartoDB.DarkMatter', 'CartoDB.DarkMatterNoLabels', 
            'CartoDB.DarkMatterOnlyLabels','CartoDB.Positron', 
            'CartoDB.PositronNoLabels', 'CartoDB.PositronOnlyLabels',
            'CartoDB.Voyager', 'CartoDB.VoyagerLabelsUnder', 'CartoDB.VoyagerNoLabels',
            'CartoDB.VoyagerOnlyLabels', 'CyclOSM', 'Esri.NatGeoWorldMap',
            'Esri.WorldGrayCanvas', 'Esri.WorldPhysical', 'Esri.WorldShadedRelief',
            'Esri.WorldStreetMap', 'Gaode.Normal', 'Gaode.Satellite',
            'NASAGIBS.ASTER_GDEM_Greyscale_Shaded_Relief', 'NASAGIBS.BlueMarble', 
            'NASAGIBS.ModisTerraBands367CR','NASAGIBS.ModisTerraTrueColorCR',
            'NLCD 2021 CONUS Land Cover', 'OPNVKarte',
            'OpenStreetMap', 'OpenTopoMap', 'SafeCast',
            'TopPlusOpen.Color', 'TopPlusOpen.Grey', 'UN.ClearMap',
            'USGS Hydrography', 'USGS.USImagery', 'USGS.USImageryTopo',
            'USGS.USTopo']

# legend_labels = {
#     "Acquisition Cost":  [],
#     "Manager Type":  
#                 ['Federal', 'State', 'Local','District','Unknown','Joint','Tribal','Private', 'NGO'],
#     "Access": 
#             ['Open Access', 'Closed','Unknown','Restricted'],
#     "Purpose": 
#     ['Forestry','Historical','Unknown','Other','Farming','Recreation','Environment','Scenic','RAN'],
# }

help_message = '''
- ❌ Safari/iOS not fully supported. For Safari/iOS users, change the **Leafmap module** from MapLibre to Folium in **(Map Settings)** below. 
- 📊 Use this sidebar to color-code the map by different attributes **(Group by)**
'''

#maplibregl tooltip 
tooltip_cols = ['fid','state','site','sponsor','program','county','year','manager',
                'amount','acres']
tooltip_template = "<br>".join([f"{col}: {{{{ {col} }}}}" for col in tooltip_cols])


error_messages = {
    "bad_request": lambda llm, e, tb_str: f"""
**Error – LLM Unavailable** 

*The LLM you selected `{llm}` is no longer available. Please select a different model.*

**Error Details:**
`{type(e)}: {e}`

""",

    "internal_server_error": lambda llm, e, tb_str: f"""
**Error – LLM Temporarily Unavailable**

The LLM you selected `{llm}` is currently down due to maintenance or provider outages. It may remain offline for several hours.

**Please select a different model or try again later.**

**Error Details:**
`{type(e)}: {e}`

""",

    "unexpected_llm_error": lambda prompt, e, tb_str: f"""
🐞 **BUG: Unexpected Error in Application**

An error occurred while processing your query:

> "{prompt}"

**Error Details:**
`{type(e)}: {e}`

Traceback:

```{tb_str}```
---

🚨 **Help Us Improve!**

Please help us fix this issue by reporting it on GitHub:
[📄 Report this issue](https://github.com/boettiger-lab/CBN-taskforce/issues)

Include the query you ran and any other relevant details. Thanks!
""",

    "unexpected_error": lambda e, tb_str: f"""
🐞 **BUG: Unexpected Error in Application**


**Error Details:**
`{type(e)}: {e}`

Traceback:

```{tb_str}```

---

🚨 **Help Us Improve!**

Please help us fix this issue by reporting it on GitHub:
[📄 Report this issue](https://github.com/boettiger-lab/CBN-taskforce/issues)

Include the steps you took to get this message and any other details that might help us debug. Thanks!
"""
}

from langchain_openai import ChatOpenAI
import streamlit as st
from langchain_openai.chat_models.base import BaseChatOpenAI

## dockerized streamlit app wants to read from os.getenv(), otherwise use st.secrets
import os
api_key = os.getenv("NRP_API_KEY")
if api_key is None:
    api_key = st.secrets["NRP_API_KEY"]

openrouter_api = os.getenv("OPENROUTER_API_KEY")
if openrouter_api is None:
    openrouter_api = st.secrets["OPENROUTER_API_KEY"]

openrouter_endpoint="https://openrouter.ai/api/v1"
nrp_endpoint="https://ellm.nrp-nautilus.io/v1"

# don't use a provider that collects data
data_policy = {
    "provider": {
        "data_collection": "deny"
    }
}

llm_options = {
     "kat-coder-pro": ChatOpenAI(
        model="kwaipilot/kat-coder-pro:free",
        api_key=openrouter_api,
        base_url=openrouter_endpoint,
        temperature=0,
        extra_body=data_policy
    ),

    "llama-3.3-70b-instruct": ChatOpenAI(
        model="meta-llama/llama-3.3-70b-instruct:free",
        api_key=openrouter_api,
        base_url=openrouter_endpoint,
        temperature=0,
        extra_body=data_policy
    ),
        
    "gpt-oss-20b": ChatOpenAI(
        model="openai/gpt-oss-20b:free",
        api_key=openrouter_api,
        base_url=openrouter_endpoint,
        temperature=0,
        extra_body=data_policy
    ),
    
    "qwen3-coder": ChatOpenAI(
        model="qwen/qwen3-coder:free",
        api_key=openrouter_api,
        base_url=openrouter_endpoint,
        temperature=0,
        extra_body=data_policy
    ),  
    
    "dolphin-mistral-24b-venice-edition": ChatOpenAI(
        model="cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        api_key=openrouter_api,
        base_url=openrouter_endpoint,
        temperature=0,
        extra_body=data_policy
    ),

    "nemotron-nano-9b-v2": ChatOpenAI(
        model="nvidia/nemotron-nano-9b-v2:free",
        api_key=openrouter_api,
        base_url=openrouter_endpoint,
        temperature=0,
        extra_body=data_policy
    ),

    "gemma-3-27b-it": ChatOpenAI(
        model="gemma3",
        api_key=api_key,
        base_url=nrp_endpoint,
        temperature=0
    ),

    "gpt-oss-120b": ChatOpenAI(
        model="gpt-oss",
        api_key=api_key,
        base_url=nrp_endpoint,
        temperature=0
    ),

    "glm-4.6-gptq-int4-int8mix": ChatOpenAI(
        model="glm-4.6",
        api_key=api_key,
        base_url=nrp_endpoint,
        temperature=0
    ),

    "glm-4.5v-fp8": ChatOpenAI(
        model="glm-v",
        api_key=api_key,
        base_url=nrp_endpoint,
        temperature=0
    ),
}
