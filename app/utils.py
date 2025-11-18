import ibis
from ibis import _
from variables import *
import altair as alt
import re
from leafmap.foliumap import PMTilesMapLibreTooltip
from branca.element import Template
import pandas as pd
import datetime

def get_counties(state_selection):
    if state_selection != 'All':
        counties = tpl_table.filter(_.state == state_selection).select('county').distinct().order_by('county').execute()
        counties = ['All'] + counties['county'].tolist()
    else: 
        counties = None
    return counties
     
def filter_data(table, state_choice, county_choice, year_range):

    min_year, max_year = year_range
    gdf = (table.filter(_.year>=(min_year))
           .filter(_.year<=(max_year))
          )
    if state_choice != "All":
        gdf = gdf.filter(_.state == state_choice)
        if (county_choice != "All") and (county_choice):
            gdf = gdf.filter(_.county == county_choice)
    return gdf

def group_data(table, style_choice):
    metric_col = style_choice_columns[style_choice]
    gdf = table.group_by(_.year).agg(total_amount = _[metric_col].sum())
    return gdf
    

def get_bounds(state_choice, county_choice, m):
    if state_choice != "All":
        gdf = county_bounds.filter(_.state == state_choice)

        if (county_choice != "All") and (county_choice):
            gdf = gdf.filter(_.county == county_choice)
        bounds = list(gdf.execute().total_bounds)   
    else:
        # if selecting all states, use these bounds
        bounds = [-167.80517179043034, 19.015233153742425, -66.97618043381198, 70.03327935821838]
    return bounds


def get_bar(df, style_choice, group_col, metric_col, paint, x_lab, y_lab, title):
    if isinstance(paint, dict):
        domain = [stop[0] for stop in paint['stops']]
        range_ = [stop[1] for stop in paint['stops']]
    
    chart = (alt.Chart(df)
                .mark_bar(stroke="black", strokeWidth=0.1)
                .encode(
                    x=alt.X(f"{group_col}:N", axis=alt.Axis(title=x_lab)),
                    y=alt.Y(f"{metric_col}:Q", axis=alt.Axis(title=y_lab)),
                    tooltip=[alt.Tooltip(group_col, type="nominal"), alt.Tooltip(metric_col, type="quantitative")],
                    )
             .properties(title=f"{title}")
            )
    st.altair_chart(chart, use_container_width = True)
    return 

def tpl_style_default(paint,pmtiles):
    source_layer_name = re.sub(r'\W+', '', os.path.splitext(os.path.basename(pmtiles))[0]) #stripping hyphens to get layer name 
    style =  {
    "version": 8,
    "sources": {
        "tpl": {
            "type": "vector",
            "url": "pmtiles://" + pmtiles,
            "attribution": "TPL"
        },
    },
    "layers": [{
            "id": "tpl",
            "source": "tpl",
            "source-layer": source_layer_name,
            "type": "fill",
            "paint": {
                "fill-color": paint,
                "fill-opacity": 1
            }
        }]
    }
    return style

def tpl_style(ids, paint, pmtiles):
    source_layer_name = re.sub(r'\W+', '', os.path.splitext(os.path.basename(pmtiles))[0]) #stripping hyphens to get layer name 
    style =  {
    "version": 8,
    "sources": {
        "tpl": {
            "type": "vector",
            "url": "pmtiles://" + pmtiles,
            "attribution": "TPL"
        },
    },
    "layers": [{
            "id": "tpl",
            "source": "tpl",
            "source-layer": source_layer_name,
            "type": "fill",
            # 'filter': ["match", ["get", 'fid'], ids, True, False],
            'filter': ['in', ['get', 'fid'], ["literal", ids]],
            "paint": {
                "fill-color": paint,
                "fill-opacity": 1
            }
        }]
    }
    return style



    
def extract_columns(sql_query):
    # Find all substrings inside double quotes
    columns = list(dict.fromkeys(re.findall(r'"(.*?)"', sql_query)))
    return columns
    
def get_colorbar(gdf, paint):
    """
    Extracts color hex codes and value range (vmin, vmax) from paint
    to make a color bar. Used for mapping continuous data. 
    """
    # numbers = [x for x in paint if isinstance(x, (int, float))]
    vmin = gdf.amount.min().execute()
    vmax = gdf.amount.max().execute()
    # min(numbers), max(numbers),
    colors = [x for x in paint if isinstance(x, str) and x.startswith('#')]
    orientation = 'vertical'
    position = 'bottom-right'
    label = "Acquisition Cost"
    height = 3
    width = .2
    return colors, vmin, vmax, orientation, position, label, height, width
    

def get_legend(paint, leafmap_backend, df = None, column = None):
    """
    Generates a legend dictionary with color mapping and formatting adjustments.
    """
    if 'stops' in paint:
        legend = {cat: color for cat, color in paint['stops']}
    else:
        legend = {}
    if df is not None:
        if ~df.empty:
            categories = df[column].to_list() #if we filter out categories, don't show them on the legend 
            legend = {cat: color for cat, color in legend.items() if str(cat) in categories}
    position, fontsize, bg_color = 'bottomright', 15, 'white'
    controls={'navigation': 'bottom-left', 
              'fullscreen':'bottom-left'}
    shape_type = 'circle'

    if leafmap_backend == 'maplibregl':
        position = 'bottom-right'
    return legend, position, bg_color, fontsize, shape_type, controls 


@st.cache_data
def tpl_summary(_df):
    summary = _df.group_by(_.manager_type).agg(amount = _.amount.sum())
    public_dollars = round( summary.filter(_.manager_type.isin(["FED", "STAT", "LOC", "DIST"])).agg(total = _.amount.sum()).to_pandas().values[0][0] )
    private_dollars = round( summary.filter(_.manager_type.isin(["PVT", "NGO"])).agg(total = _.amount.sum()).to_pandas().values[0][0] )
    total_dollars = round( summary.agg(total = _.amount.sum()).to_pandas().values[0][0] )
    return public_dollars, private_dollars, total_dollars

# @st.cache_data
def calc_delta(_df):
    deltas = (_df
     .group_by(_.manager_type, _.year)
     .agg(amount = _.amount.sum())
     .mutate(total = _.amount.cumsum(order_by=_.year, group_by=_.manager_type))
     .mutate(lag = _.total.lag(1))
     .mutate(delta = (100*(_.total - _.lag) / _.total).round(2)  )
     # .filter(_.year >=2019)
     .select(_.manager_type, _.year, _.total, _.lag, _.delta)
    )
    public_delta = deltas.filter(_.manager_type.isin(["FED", "STAT", "LOC", "DIST"])).to_pandas()
    public_delta =  0 if public_delta.empty else public_delta.delta[-1]
    private_delta = deltas.filter(_.manager_type.isin(["PVT", "NGO"])).to_pandas()
    private_delta =  0 if private_delta.empty else private_delta.delta[-1]
    return public_delta, private_delta
    
# @st.cache_data
def get_area_totals(_df, column):
    return _df.group_by(_[column]).agg(area = _.Shape_Area.sum() / (100*100)).to_pandas()


# @st.cache_data
def bar(area_totals, column, paint):
    plt = alt.Chart(area_totals).mark_bar().encode(
            x=column,
            y=alt.Y("area"),
        ).properties(height=350)
    return plt

# @st.cache_data
def chart_time(timeseries, column, paint):
    domain = [stop[0] for stop in paint['stops']]
    range_ = [stop[1] for stop in paint['stops']]
    # use the colors 
    plt = alt.Chart(timeseries).mark_line().encode(
        x='year:O',
        y = alt.Y('amount:Q'),
            color=alt.Color(column,scale= alt.Scale(domain=domain, range=range_))
    ).properties(height=350)
    return plt
    
class CustomTooltip(PMTilesMapLibreTooltip):
    _template = Template("""
    {% macro script(this, kwargs) -%}
    var maplibre = {{ this._parent.get_name() }}.getMaplibreMap();
    const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

    maplibre.on('mousemove', function(e) {
        const features = maplibre.queryRenderedFeatures(e.point);
        const filtered = features.filter(f => f.properties && f.properties.fid);

        if (filtered.length) {
            const props = filtered[0].properties;
            const html = `
                <div><strong>fid:</strong> ${props.fid || 'N/A'}</div>
                <div><strong>Site:</strong> ${props.site || 'N/A'}</div>
                <div><strong>Sponsor:</strong> ${props.sponsor || 'N/A'}</div>
                <div><strong>Program:</strong> ${props.program || 'N/A'}</div>
                <div><strong>State:</strong> ${props.state || 'N/A'}</div>
                <div><strong>County:</strong> ${props.county || 'N/A'}</div>
                <div><strong>Year:</strong> ${props.year || 'N/A'}</div>
                <div><strong>Manager:</strong> ${props.manager || 'N/A'}</div>
                <div>
                    <strong>Amount:</strong> ${
                        props.amount
                            ? `$${parseFloat(props.amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                            : 'N/A'
                    }
                </div>
                <div>
                    <strong>Acres:</strong> ${
                        props.acres
                            ? parseFloat(props.acres).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                            : 'N/A'
                    }
                </div>
            `;
            popup.setLngLat(e.lngLat).setHTML(html).addTo(maplibre);
            if (popup._container) {
                popup._container.style.zIndex = 9999;
            }
        } else {
            popup.remove();
        }
    });
    {% endmacro %}
    """)
    
minio_key = os.getenv("MINIO_KEY")
if minio_key is None:
    minio_key = st.secrets["MINIO_KEY"]

minio_secret = os.getenv("MINIO_SECRET")
if minio_secret is None:
    minio_secret = st.secrets["MINIO_SECRET"]

def minio_logger(consent, query, sql_query, llm_explanation, llm_choice, filename="query_log.csv", bucket="shared-tpl",
                 key=minio_key, secret=minio_secret,
                 endpoint="minio.carlboettiger.info"):
    mc = minio.Minio(endpoint, key, secret)
    mc.fget_object(bucket, filename, filename)
    log = pd.read_csv(filename)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    if consent:
        df = pd.DataFrame({"timestamp": [timestamp], "user_query": [query], "llm_sql": [sql_query], "llm_explanation": [llm_explanation], "llm_choice":[llm_choice]})

    # if user opted out, do not store query
    else:  
        df = pd.DataFrame({"timestamp": [timestamp], "user_query": ['USER OPTED OUT'], "llm_sql": [''], "llm_explanation": [''], "llm_choice":['']})
    
    pd.concat([log,df]).to_csv(filename, index=False, header=True)
    mc.fput_object(bucket, filename, filename, content_type="text/csv")
