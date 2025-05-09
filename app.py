# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# +
import leafmap.foliumap as leafmap
import streamlit as st
from minio import Minio
import os
from datetime import timedelta
import pandas as pd

# Get signed URLs to access license-controlled layers
key = st.secrets["MINIO_KEY"]
secret = st.secrets["MINIO_SECRET"]
client = Minio("minio.carlboettiger.info", key, secret)


pmtiles = client.get_presigned_url(
    "GET",
    "shared-tpl",
    "tpl.pmtiles",
    expires=timedelta(hours=2),
)

parquet = client.get_presigned_url(
    "GET",
    "shared-tpl",
    "tpl.parquet",
    expires=timedelta(hours=2),
)

geojson = client.get_presigned_url(
    "GET",
    "shared-tpl",
    "tpl.geojson",
    expires=timedelta(hours=2),
)

# -


basemaps = leafmap.basemaps.keys()

# +

## Protected Area polygon color codes 

style_options = {
    "Manager Type":  {
            'property': 'Manager_Type',
            'type': 'categorical',
            'stops': [
                ['FED', "darkblue"],
                ['STAT', "blue"],
                ['LOC', "lightblue"],
                ['DIST', "darkgreen"],
                ['UNK', "grey"],
                ['JNT', "green"],
                ['TRIB', "purple"],
                ['PVT', "darkred"],
                ['NGO', "orange"]
            ]
            },
    "Access": {
        'property': 'Public_Access_Type',
        'type': 'categorical',
        'stops': [
            ['OA', "green"],
            ['XA', "red"],
            ['UK', "grey"],
            ['RA', "orange"]
        ]
    },
    "Purpose": {
        'property': 'Purpose_Type',
        'type': 'categorical',
        'stops': [
            ['FOR', "green"],
            ['HIST', "red"],
            ['UNK', "grey"],
            ['OTH', "grey"],
            ['FARM', "yellow"],
            ['REC', "blue"],
            ['ENV', "purple"],
            ['SCE', "orange"],
            ['RAN', "pink"]
        ]
    }
}



notused = {
    "Amount": ["interpolate",
                ['exponential', 1], 
                ["get", "Amount"],
                       0,	"#FCE2DC",
                34273487,	"#F8C3BF",
                68546973,	"#F4A5A2",
                102820460,	"#F08785",
                137093947,	"#EB6968",
                171367433,	"#DB5157",
                205640920,	"#BE4152",
                239914407,	"#A0304C",
                274187893,	"#832047",
                308461380,	"#661042",
                ] 
}

# +
st.set_page_config(layout="wide",
                   page_title="TPL Conservation Almanac",
                   page_icon=":globe:")

'''
# TPL Conservation Almanac

A data visualization tool built for the Trust for Public Land

'''

m = leafmap.Map(center=[35, -100], zoom=5, layers_control=True, fullscreen_control=True)


def pad_style(paint, alpha):
    return {
    "version": 8,
    "sources": {
        "source1": {
            "type": "vector",
            "url": "pmtiles://" + pmtiles,
            "attribution": "TPL"}},
    "layers": [{
            "id": "TPL",
            "source": "source1",
            "source-layer": "tpl",
            "type": "fill",
            "paint": {
                "fill-color": paint,
                "fill-opacity": alpha
            }
        }]}



code_ex='''
m.add_cog_layer("https://data.source.coop/vizzuality/lg-land-carbon-data/natcrop_expansion_100m_cog.tif",
                palette="oranges", name="Cropland Expansion", transparent_bg=True, opacity = 0.7, zoom_to_layer=False)
'''
# -
## Map controls sidebar
with st.sidebar:

    if st.toggle("Protected Areas", True):
        alpha = st.slider("transparency", 0.0, 1.0, 0.5)
        style_choice = st.radio("Color by:", style_options)
        style = pad_style(style_options[style_choice], alpha)
        m.add_pmtiles(pmtiles, name="Conservation Protected Areas", style=style, overlay=True, show=True, zoom_to_layer=False)
        ## Add legend based on selected style?
        # m.add_legend(legend_dict=legend_dict)

    b = st.selectbox("Basemap", basemaps)
    m.add_basemap(b)

# And here we go!
m.to_streamlit(height=600)

st.divider()

import altair as alt
import ibis
from ibis import _
import ibis.selectors as s


# +
@st.cache_resource
def tpl_database(parquet):
    df = ibis.read_parquet(parquet)  
    return df

df = tpl_database(parquet)


# +
@st.cache_data
def tpl_summary(_df):
    summary = _df.group_by(_.Manager_Type).agg(Amount = _.Amount.sum())
    public_dollars = round( summary.filter(_.Manager_Type.isin(["FED", "STAT", "LOC", "DIST"])).agg(total = _.Amount.sum()).to_pandas().values[0][0] )
    private_dollars = round( summary.filter(_.Manager_Type.isin(["PVT", "NGO"])).agg(total = _.Amount.sum()).to_pandas().values[0][0] )
    tribal_dollars = round( summary.filter(_.Manager_Type.isin(["TRIB"])).agg(total = _.Amount.sum()).to_pandas().values[0][0] )
    total_dollars = round( summary.agg(total = _.Amount.sum()).to_pandas().values[0][0] )
    return public_dollars, private_dollars, tribal_dollars, total_dollars

public_dollars, private_dollars, tribal_dollars, total_dollars = tpl_summary(df)

# +
# areas actively managed / owned / sponsored by TPL
# tpl = (df
#     .filter(_.Sponsor_Name.lower().re_search("trust for public land") | _.Owner_Name.lower().re_search("trust for public land") | _.Manager_Name.lower().re_search("trust for public land"))
#     .agg(Amount = _.Amount.sum(), 
#          area_hectares = _.Shape_Area.sum() / 10000)
#     .order_by(_.Amount.desc())
#     .to_pandas() 
#    )
# -





# +
@st.cache_data
def calc_delta(_df):
    deltas = (_df
     .group_by(_.Manager_Type, _.Close_Year)
     .agg(Amount = _.Amount.sum())
     #.filter(_.Manager_Type.isin(["FED"]))
     # .order_by(_.Close_Year)
     .mutate(total = _.Amount.cumsum(order_by=_.Close_Year, group_by=_.Manager_Type))
     .mutate(lag = _.total.lag(1))
     .mutate(delta = (100*(_.total - _.lag) / _.total).round(2)  )
     .filter(_.Close_Year >=2019)
     .select(_.Manager_Type, _.Close_Year, _.total, _.lag, _.delta)
    )
    
    public_delta = deltas.filter(_.Manager_Type.isin(["FED", "STAT", "LOC", "DIST"])).to_pandas().delta[0]
    private_delta = deltas.filter(_.Manager_Type.isin(["PVT", "NGO"])).to_pandas().delta[0]
    trib_delta = deltas.filter(_.Manager_Type=="TRIB").to_pandas().delta[0]

    #total_dollars = round( summary.agg(total = _.Amount.sum()).to_pandas().values[0][0] )

    return public_delta, private_delta, trib_delta

public_delta, private_delta, trib_delta = calc_delta(df)
# -


with st.container():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label=f"Public", value=f"${public_dollars:,}", delta = f"{public_delta:}%")
    col2.metric(label=f"Private", value=f"${private_dollars:,}", delta = f"{private_delta:}%")
    col3.metric(label=f"Tribal", value=f"${tribal_dollars:,}", delta = f"{trib_delta:}%")
    col4.metric(label=f"Total", value=f"${total_dollars:,}")    

selected = style_options[style_choice]
column = selected["property"]
colors = dict(selected["stops"])


# +
@st.cache_data
def get_area_totals(_df, column):
    return _df.group_by(_[column]).agg(area = _.Shape_Area.sum() / (100*100)).to_pandas()
area_totals = get_area_totals(df,column)

@st.cache_data
def bar(area_totals, column):
    plt = alt.Chart(area_totals).mark_bar().encode(
            x=column,
            y=alt.Y("area").scale(type="log"),
            color=alt.Color(column).scale(domain =  list(colors.keys()), range = list(colors.values()))
        ).properties(height=350)
    return plt
#bar


# +

@st.cache_data
def calc_timeseries(_df, column):
    timeseries = (
        _df
        .filter(~_.Close_Year.isnull())
        .filter(_.Close_Year > 0)
        .group_by([_.Close_Year, _[column]])
        .agg(Amount = _.Amount.sum())
        .mutate(Close_Year = _.Close_Year.cast("int"),
                Amount = _.Amount.cumsum(group_by=_[column], order_by=_.Close_Year))
        
        .to_pandas()
    )
    return timeseries
timeseries = calc_timeseries(df, column)

@st.cache_data
def chart_time(timeseries, column):
    # use the colors 
    plt = alt.Chart(timeseries).mark_line().encode(
        x='Close_Year:O',
        y = alt.Y('Amount:Q'),
        color=alt.Color(column).scale(domain =  list(colors.keys()), range = list(colors.values()))
    ).properties(height=350)
    return plt


# +
st.divider()

with st.container():
    plt1, plt2 = st.columns(2)
    
    with plt1:
        "Total Area protected (hectares):"
        st.altair_chart(bar(area_totals, column))
    with plt2:
        "Annual investment ($) in protected area"
        st.altair_chart(chart_time(timeseries, column))


# +

import leafmap.deckgl as deckgl
from shapely import wkb
import geopandas as gpd

@st.cache_data
def leaf_map(gdf):
    m = deckgl.Map(center=[35, -100], zoom=4)
    m.add_gdf(gdf)
    return m.to_streamlit()

@st.cache_data
def crs():
    conn = ibis.duckdb.connect()
    crs = conn.read_geo("static/test.geojson").crs
    return crs
    
@st.cache_data
def query_database(response):
    z = con.execute(response).fetchall()
    return pd.DataFrame(z).head(250)

@st.cache_data
def get_geom(tbl):
    #tbl['geometry'] = tbl['geometry'].apply(wkb.loads)
    gdf = gpd.GeoDataFrame(tbl, geometry='geometry')
    gdf.to_crs({'init': 'epsg:4326'})
    
    return gdf

## Database connection, reading directly from remote parquet file
from sqlalchemy import create_engine
from langchain.sql_database import SQLDatabase
db_uri = "duckdb:///my.duckdb"
engine = create_engine(db_uri) #connect_args={'read_only': True})
con = engine.connect()
con.execute("install spatial; load spatial;")
con.execute(f"create or replace table protected as select *, st_geomfromwkb(geom) as geometry from read_parquet('{parquet}');").fetchall()
db = SQLDatabase(engine, view_support=True)

from langchain_openai import ChatOpenAI 
from langchain_community.llms import Ollama
models = {
    "chatgpt3.5": ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=st.secrets["OPENAI_API_KEY"]),
          "chatgpt-o4": ChatOpenAI(model="gpt-4o", temperature=0, api_key=st.secrets["OPENAI_API_KEY"]),
         }
other_models ={
          "duckdb-nsql": Ollama(model="duckdb-nsql", temperature=0),
          "sqlcoder": Ollama(model="mannix/defog-llama3-sqlcoder-8b", temperature=0),
          "mixtral":  Ollama(model="mixtral", temperature=0),
          "wizardlm2":  Ollama(model="wizardlm2", temperature=0),
          "sqlcoder": Ollama(model="sqlcoder", temperature=0),
          "zephyr": Ollama(model="zephyr", temperature=0),
          "llama3": Ollama(model="llama3", temperature=0),
         }

map_tool = {"leafmap": leaf_map,
         #   "deckgl": deck_map
           }


with st.sidebar:
    st.divider()
    choice = st.radio("Select an LLM:", models)
    llm = models[choice]
    map_choice = st.radio("Select mapping tool", map_tool)
    mapper = map_tool[map_choice]
    
## A SQL Chain
from langchain.chains import create_sql_query_chain
chain = create_sql_query_chain(llm, db)


st.divider()


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


with st.container():

    '''
    Ask a question! Some examples:

    - What is are most expensive protected sites?
    - Which states have the highest average cost per acre?
    - Which sites are owned, managed or sponsored by the Trust for Public Land? include all columns
    '''

    chatbox = st.container()
    with chatbox:           
        if prompt := st.chat_input(key="chain"):
            st.chat_message("user").write(prompt)
            with st.chat_message("assistant"):
                response = chain.invoke({"question": prompt + " No limit, use fuzzy matching when asked to match specific names."})
                st.write(response)
                tbl = query_database(response)
                #if 'geometry' in tbl:
                #    gdf = get_geom(tbl)
                #    mapper(gdf)
                #    n = len(gdf)
                #    st.write(f"matching features: {n}")
                st.dataframe(tbl)
                csv = convert_df(tbl)
                st.download_button(label="Download data as CSV",
                                   data=csv,
                                   file_name="results.csv",
                                   mime="text/csv")


# +
st.divider()

st.markdown('''

## Data Sources

PRIVATE DRAFT.  Developed at UC Berkeley. All data copyright to Trust for Public Land.  See <https://conservationalmanac.org/> for details.

''')
