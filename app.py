import flask
from flask import request, render_template, abort, Response
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Spectral5
from bokeh.transform import factor_cmap
import pickle
import numpy as np
import pandas as pd
from bokeh.client import pull_session
from bokeh.embed import server_session

with open("data/topics_recommender.pkl", "rb") as f:
    ski_rec = pickle.load(f)

# Initialize the app
app = flask.Flask(__name__)

# Homepage


@app.route("/", methods=['GET', 'POST'])
def render():
    return flask.render_template('form.html')


@app.route("/results", methods=['POST'])
def recommend():

    print(request.form)

    filters = ['staff', 'terrain', 'waittime', 'liftspeed',
               'powder', 'groom', 'family', 'beginner', 'food', 'crowded']

    current_filter = []

    # geo
    geo = str(request.form['geography'])
    geo = geo.strip()

    if geo in ski_rec['State'].unique():
        temp = ski_rec[ski_rec['State'] == geo]

    # Beginner
    if int(request.form['ability_level']) == 0:
        current_filter = ['beginner']
    else:
        pass

    # Snow_conditions
    if int(request.form['snow_conditions']) == 1:
        current_filter.append('powder')
    else:
        current_filter.append('groom')

    # liftspeed
    if "feat_1" in request.form:
        current_filter.append('liftspeed')
    else:
        pass

    # food
    if "feat_2" in request.form:
        current_filter.append('food')
    else:
        pass

    # waittime
    if "feat_3" in request.form:
        current_filter.append('waittime')
    else:
        pass

    # staff
    if "feat_4" in request.form:
        current_filter.append('staff')
    else:
        pass

    # terrain
    if "feat_5" in request.form:
        current_filter.append('terrain')
    else:
        pass

    # crowded
    if "feat_6" in request.form:
        current_filter.append('crowded')
    else:
        pass

    # family
    if "feat_7" in request.form:
        current_filter.append('family')
    else:
        pass

    columns = ['Ski Area']+current_filter

    temp = temp[columns]
    temp['total_score'] = temp[current_filter].sum(axis=1)

    g = temp.groupby('Ski Area').agg(['mean'])
    g.columns = g.columns.droplevel(1)
    resorts_out = g.sort_values(by='total_score', ascending=False).head().index.map(str)
    rec = [res for res in resorts_out]

    rec_df = g.sort_values('total_score', ascending=False).head(5)
    rec_df[rec_df.select_dtypes(include=['number']).columns] *= 100

    rec_df = rec_df.reset_index()
    rec_df_long = pd.melt(rec_df, id_vars='Ski Area', value_vars=current_filter)

    group = rec_df_long.groupby(by=['Ski Area', 'variable'])

    index_cmap = factor_cmap('Ski Area_variable', palette=Spectral5,
                             factors=sorted(rec_df_long['Ski Area'].unique()), end=1)

    p = figure(width=800, height=300, title="Mean Score by SKi Area and Factors",
               x_range=group, toolbar_location=None, tooltips=[("Score", "@value_mean")])

    p.vbar(x='Ski Area_variable', top='value_mean', width=1, source=group,
           line_color="white", fill_color=index_cmap)

    p.y_range.start = 0
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.xaxis.axis_label = "Factors on each Ski Area"
    p.xaxis.major_label_orientation = 1.2
    p.outline_line_color = None

    script, div = components(p)

    kwargs = {'script': script, 'div': div}

    return flask.render_template('rec1.html',
                                 recommendation=rec, **kwargs)


# Run the app
app.run(debug=True, port=33507)
