import ibis
from ibis import _
from variables import *
import altair as alt
import re

def get_counties(state_selection):
    if state_selection != 'All':
        counties = database.filter(_.state_name == state_selection).select('county').distinct().order_by('county').execute()
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
        # gdf = gdf.filter(_.state_name.isin(state_choice))
        gdf = gdf.filter(_.state_name == state_choice)

        if (county_choice != "All") and (county_choice):
            county_choice = re.sub(r"(?i)\s*(County)\b", "", county_choice)    
            gdf = gdf.filter(_.county == county_choice)
    return gdf

def group_data(table, style_choice):
    metric_col = style_choice_columns[style_choice]
    gdf = table.group_by(_.year).agg(total_amount = _[metric_col].sum())
    return gdf
    

def fit_bounds(state_choice, county_choice, m):
    if state_choice != "All":
        # gdf = county_bounds.filter(_.state_name.isin(state_choice))
        gdf = county_bounds.filter(_.state_name == state_choice)

        if (county_choice != "All") and (county_choice):
            gdf = gdf.filter(_.county == county_choice)
        bounds = list(gdf.execute().total_bounds)
        m.fit_bounds(bounds) # need to zoom to filtered area    
        return


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
                    # color=alt.Color(
                    #         f"{group_col}:N",
                    #         legend=alt.Legend(title=style_choice,symbolStrokeWidth=0.5),
                    #         scale=alt.Scale(domain=domain, range=range_)
                    #      ),
                    )
             .properties(title=f"{title}")
            )
    st.altair_chart(chart, use_container_width = True)
    return 

def tpl_style_default(paint):
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


def tpl_style(ids, paint):
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
            'filter': ['in', ['get', 'fid'], ["literal", ids]],
            "paint": {
                "fill-color": paint,
                "fill-opacity": 1
            }
        }]
    }
    return style

    
def get_legend(paint):
    """
    Generates a legend dictionary with color mapping and formatting adjustments.
    """
    legend = {cat: color for cat, color in paint['stops']}
    position, fontsize, bg_color = 'bottom-left', 15, 'white'
    bg_color = 'rgba(255, 255, 255, 0.6)'
    fontsize = 12
    return legend, position, bg_color, fontsize



@st.cache_data
def tpl_summary(_df):
    summary = _df.group_by(_.Manager_Type).agg(Amount = _.Amount.sum())
    public_dollars = round( summary.filter(_.Manager_Type.isin(["FED", "STAT", "LOC", "DIST"])).agg(total = _.Amount.sum()).to_pandas().values[0][0] )
    private_dollars = round( summary.filter(_.Manager_Type.isin(["PVT", "NGO"])).agg(total = _.Amount.sum()).to_pandas().values[0][0] )
    # tribal_dollars = summary.filter(_.Manager_Type.isin(["TRIB"])).agg(total = _.Amount.sum()).to_pandas().values[0][0] 
    # tribal_dollars = tribal_dollars if tribal_dollars else round(tribal_dollars)
    total_dollars = round( summary.agg(total = _.Amount.sum()).to_pandas().values[0][0] )
    return public_dollars, private_dollars, total_dollars

# @st.cache_data
def calc_delta(_df):
    deltas = (_df
     .group_by(_.Manager_Type, _.year)
     .agg(Amount = _.Amount.sum())
     .mutate(total = _.Amount.cumsum(order_by=_.year, group_by=_.Manager_Type))
     .mutate(lag = _.total.lag(1))
     .mutate(delta = (100*(_.total - _.lag) / _.total).round(2)  )
     # .filter(_.year >=2019)
     .select(_.Manager_Type, _.year, _.total, _.lag, _.delta)
    )
    public_delta = deltas.filter(_.Manager_Type.isin(["FED", "STAT", "LOC", "DIST"])).to_pandas()
    public_delta =  0 if public_delta.empty else public_delta.delta[-1]
    private_delta = deltas.filter(_.Manager_Type.isin(["PVT", "NGO"])).to_pandas()
    private_delta =  0 if private_delta.empty else private_delta.delta[-1]
    return public_delta, private_delta
    
# @st.cache_data
def get_area_totals(_df, column):
    return _df.group_by(_[column]).agg(area = _.Shape_Area.sum() / (100*100)).to_pandas()


# @st.cache_data
def bar(area_totals, column, paint):
    # domain = [stop[0] for stop in paint['stops']]
    # range_ = [stop[1] for stop in paint['stops']]
    plt = alt.Chart(area_totals).mark_bar().encode(
            x=column,
            y=alt.Y("area"),
            # color=alt.Color(column).scale(domain = domain, range = range_)
        ).properties(height=350)
    return plt
#bar

# +

# @st.cache_data
# def calc_timeseries(_df, column):
#     timeseries = (
#         _df
#         .filter(~_.year.isnull())
#         .filter(_.year > 0)
#         .group_by([_.year, _[column]])
#         .agg(Amount = _.Amount.sum())
#         .mutate(year = _.year.cast("int"),
#                 Amount = _.Amount.cumsum(group_by=_[column], order_by=_.year))
        
#         .to_pandas()
#     )
#     return timeseries


# @st.cache_data
def chart_time(timeseries, column, paint):
    domain = [stop[0] for stop in paint['stops']]
    range_ = [stop[1] for stop in paint['stops']]
    # use the colors 
    plt = alt.Chart(timeseries).mark_line().encode(
        x='year:O',
        y = alt.Y('Amount:Q'),
            color=alt.Color(column,scale= alt.Scale(domain=domain, range=range_))
    ).properties(height=350)
    return plt
