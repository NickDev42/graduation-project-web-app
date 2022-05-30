# import colorama
import jinja2
import plotly.utils
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, DateTimeField, DateField, BooleanField, TextAreaField, SelectField)
from flask import Flask, render_template, url_for, request, session, redirect
from wtforms.validators import DataRequired
import folium
import pandas as pd
from folium.plugins import MeasureControl, MousePosition
import plotly.express as plt
import json
import os
# import seaborn as sns
# import dash
# import matplotlib.pyplot as plt
# df_suburbs = pd.read_excel("C:\waterwatch_clean2.xlsx", sheet_name='Sheet1')
db_data = pd.read_csv("C:\\Users\Public\data.csv", delimiter=',')
db_data_json = pd.read_json("C:\\Users\Public\csvjson.json")
db_data_parse = json.load(open("C:\\Users\Public\jsondata.json"))
db_data_json_new = pd.read_json("C:\\Users\Public\jsondata.json")
measure_control = MeasureControl()


# print(db_data_json.head().to_json())

server = Flask(__name__)
server.config['SECRET_KEY'] = 'mysecretkey'

class AfforestationForm(FlaskForm):
    location = StringField("choose the location", validators=[DataRequired()])

    startDate = DateField()
    endDate = DateField()
    submit = SubmitField('Submit')

@server.route('/afforestationform', methods=['GET', 'POST'])
def form():
    map = treeTypeMap()
    form = AfforestationForm()
    if form.validate_on_submit():
        session['location'] = form.location.data
        session['startDate'] = form.startDate.data
        session['endDate'] = form.endDate.data
        return redirect(url_for('thankyou'))
    return render_template('applicationform.html', form=form)

@server.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')



@server.route('/')
def fn():
    vis = dataVis()

    map = treeTypeMap()
    return render_template("index.html", map=map, visualisation=vis)

@server.route('/healthservice')
def fn1():
    visHealth = dataVisHealth()
    mapHealth = treeHealth()
    return render_template("treeHealth.html", map=mapHealth, visualisation=visHealth)

@server.route('/soiltypeservice')
def fn2():
    visSoil = dataVisSoil()
    mapSoil = soilType()
    return render_template("soilType.html", map=mapSoil, visualisation=visSoil)


@server.route('/vegetationSpecific')
def specData():
    specVis = specificDV()
    map = treeTypeMap()
    return render_template("specificData.html", map=map, visualisation=specVis)

@server.route('/healthSpecific')
def specDataHealthTrees():
    specVis = specificDVhealth()
    map = treeHealth()
    return render_template("specificDatahealth.html", map=map, visualisation=specVis)

@server.route('/soilSpecific')
def specDataSoilType():
    specVis = specificDVsoil()
    map = soilType()
    return render_template("specificDataSoil.html", map=map, visualisation=specVis)

lorem = "Pythom"
map_osm = folium.Map(location=[35.000, 33.000], zoom_start=8)
map_health = folium.Map(location=[35.000, 33.000], zoom_start=8)
map_soil = folium.Map(location=[35.000, 33.000], zoom_start=8)
map_osm.add_child(MeasureControl())
map_health.add_child(measure_control)
map_soil.add_child(MeasureControl())
el = folium.MacroElement().add_to(map_osm)
el._template = jinja2.Template("""
        {% macro script(this, kwargs) %}
            """+map_osm.get_name()+""".on('measurefinish', function(evt){
                fetch("/measureFinish", {
                    method: "post",
                    headers: {
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        oJS_In: evt
                    }, getCircularReplacer())
                });
            });

            const getCircularReplacer = () => {
              const seen = new WeakSet()
              return (key, value) => {
                if (typeof value === "object" && value !== null) {
                  if (seen.has(value)) {
                    return
                  }
                  seen.add(value)
                }
                return value
              }
            }
        {% endmacro %}
    """)

el1 = folium.MacroElement().add_to(map_health)
el1._template = jinja2.Template("""
        {% macro script(this, kwargs) %}
            """+map_health.get_name()+""".on('measurefinish', function(evt){
                fetch("/measureFinish", {
                    method: "post",
                    headers: {
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        oJS_In: evt
                    }, getCircularReplacer())
                });
            });

            const getCircularReplacer = () => {
              const seen = new WeakSet()
              return (key, value) => {
                if (typeof value === "object" && value !== null) {
                  if (seen.has(value)) {
                    return
                  }
                  seen.add(value)
                }
                return value
              }
            }
        {% endmacro %}
    """)
el2 = folium.MacroElement().add_to(map_soil)
el2._template = jinja2.Template("""
        {% macro script(this, kwargs) %}
            """+map_soil.get_name()+""".on('measurefinish', function(evt){
                fetch("/measureFinish", {
                    method: "post",
                    headers: {
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        oJS_In: evt
                    }, getCircularReplacer())
                });
            });

            const getCircularReplacer = () => {
              const seen = new WeakSet()
              return (key, value) => {
                if (typeof value === "object" && value !== null) {
                  if (seen.has(value)) {
                    return
                  }
                  seen.add(value)
                }
                return value
              }
            }
        {% endmacro %}
    """)


def treeTypeMap():  # put application's code here
    db_data_locations = db_data_json_new[["Latitude", "Longitude"]]
    db_data_locations_list = db_data_locations.values.tolist()
    db_data_locations_list_size = len(db_data_locations_list)

    for point in range(0, db_data_locations_list_size):
        html = popup_html(point)

        popup1 = folium.Popup(folium.Html(html, script=True), max_width=500)
        if db_data_json_new["Vegetation"][point] == "No":
            # folium.Marker(db_data_locations_list[point]).add_to(map_osm)
            folium.Circle(location=db_data_locations_list[point], color="red", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=db_data_json_new["Density"][point]*1000,  fill_color="red").add_to(map_osm)
        elif db_data_json_new["Vegetation"][point] == "Low":
            # folium.Marker(db_data_locations_list[point]).add_to(map_osm)
            folium.Circle(location=db_data_locations_list[point], color="orange", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=db_data_json_new["Density"][point]*1000, fill_color="orange").add_to(map_osm)
        elif db_data_json_new["Vegetation"][point] == "Medium":
            # folium.Marker(db_data_locations_list[point]).add_to(map_osm)
            folium.Circle(location=db_data_locations_list[point], color="yellow", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=db_data_json_new["Density"][point]*1000, fill_color="yellow").add_to(map_osm)
        elif db_data_json_new["Vegetation"][point] == "High":
            folium.Circle(location = db_data_locations_list[point], color="green", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=db_data_json_new["Density"][point]*1000, fill_color="green").add_to(map_osm)
        else:
            folium.Circle(location=db_data_locations_list[point], color="black", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=db_data_json_new["Density"][point] * 1000,
                          fill_color="black").add_to(map_osm)


    map_osm.save('templates/map.html')
    return map_osm._repr_html_()


def treeHealth():  # put application's code here
    db_data_locations = db_data_json_new[["Latitude", "Longitude"]]
    db_data_locations_list = db_data_locations.values.tolist()
    db_data_locations_list_size = len(db_data_locations_list)

    for point in range(0, db_data_locations_list_size):
        html = popup_html(point)

        popup1 = folium.Popup(folium.Html(html, script=True), max_width=500)
        if db_data_json_new["Burnt"][point] == "No":
            # folium.Marker(db_data_locations_list[point]).add_to(map_osm)
            folium.Circle(location=db_data_locations_list[point], color="green", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="green").add_to(map_health)
        else:
            folium.Circle(location=db_data_locations_list[point], color="red", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="green").add_to(map_health)
    # map_health.add_child(measure_control)
    map_health.save('templates/mapHealth.html')
    return map_health._repr_html_()

def soilType():
    db_data_locations = db_data_json_new[["Latitude", "Longitude"]]
    db_data_locations_list = db_data_locations.values.tolist()
    db_data_locations_list_size = len(db_data_locations_list)

    for point in range(0, db_data_locations_list_size):
        html = popup_html(point)
        popup1 = folium.Popup(folium.Html(html, script=True), max_width=500)
        if db_data_json_new["SoilTexture"][point] == "Sand":
            folium.Circle(location=db_data_locations_list[point], color="#c2b280", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="c2b280").add_to(map_soil)
        elif db_data_json_new["SoilTexture"][point] == "Clay":
            folium.Circle(location=db_data_locations_list[point], color="#cc7357", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="#cc7357").add_to(map_soil)
        elif db_data_json_new["SoilTexture"][point] == "Loamy sand":
            folium.Circle(location=db_data_locations_list[point], color="#68604c", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="#68604c").add_to(map_soil)
        elif db_data_json_new["SoilTexture"][point] == "Sandy loam":
            folium.Circle(location=db_data_locations_list[point], color="#7e7763", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="#7e7763").add_to(map_soil)
        elif db_data_json_new["SoilTexture"][point] == "Loam":
            folium.Circle(location=db_data_locations_list[point], color="#655f4f", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="#655f4f").add_to(map_soil)
        elif db_data_json_new["SoilTexture"][point] == "Rock":
            folium.Circle(location=db_data_locations_list[point], color="#2e2822", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="#2e2822").add_to(map_soil)
        elif db_data_json_new["SoilTexture"][point] == "Gravelly sand":
            folium.Circle(location=db_data_locations_list[point], color="#e4c9b0", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="#e4c9b0").add_to(map_soil)
        elif db_data_json_new["SoilTexture"][point] == "Gravel":
            folium.Circle(location=db_data_locations_list[point], color="#909ba3", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="#909ba3").add_to(map_soil)
        elif db_data_json_new["SoilTexture"][point] == "Clay loam":
            folium.Circle(location=db_data_locations_list[point], color="#716957", popup=popup1,
                          opacity=db_data_json_new["Density"][point], radius=20, fill_color="#716957").add_to(map_soil)
    map_soil.save('templates/mapSoil.html')
    return map_soil._repr_html_()


@server.route('/map')
def map():
    return render_template('map.html')

@server.route('/maphealth')
def mapHealth():
    return render_template('mapHealth.html')

@server.route('/mapsoil')
def mapSoil():
    return render_template('mapSoil.html')

@server.route('/vis')
def dataVis():
    dv = plt.pie(db_data_json_new, values="Density", names="Vegetation")
    return dv._repr_html_()

@server.route('/visHealth')
def dataVisHealth():
    dh = plt.histogram(db_data_json_new, x="Burnt")
    return dh._repr_html_()

@server.route('/visSoil')
def dataVisSoil():
    dv = plt.pie(db_data_json_new, values="SoilDepth", names="SoilTexture")
    return dv._repr_html_()

dict_extrema = dict()
li_intersect_point = list()
@server.route('/measureFinish', methods = ['POST'] )
def measureFinish():
    data = request.data
    data = json.loads(data)
    data = data['oJS_In']
    dict_extrema['x_max'] = 0
    dict_extrema['y_max'] = 0
    dict_extrema['x_min'] = 0
    dict_extrema['y_min'] = 0
    pts_list = data['points']

    if len(pts_list) == 0:
        return json.loads('{ "response": "no_points" }')

    for point in pts_list:
        lat, lng = (point['lat'], point['lng'])
        dict_extrema['x_max'] = lng if lng > dict_extrema['x_max'] else dict_extrema['x_max']
        dict_extrema['y_max'] = lat if lat > dict_extrema['y_max'] else dict_extrema['y_max']
        # dict_extrema['x_min'] = lng if lng < dict_extrema['x_min'] else dict_extrema['x_min']
        # dict_extrema['y_min'] = lat if lat < dict_extrema['y_min'] else dict_extrema['y_min']

        if dict_extrema['x_min'] == 0:
            dict_extrema['x_min'] = lng
        else:
            dict_extrema['x_min'] = lng if lng < dict_extrema['x_min'] else dict_extrema['x_min']

        if dict_extrema['y_min'] == 0:
            dict_extrema['y_min'] = lat
        else:
            dict_extrema['y_min'] = lat if lat < dict_extrema['y_min'] else dict_extrema['y_min']

    for o_point in db_data_parse:
        dict_point = dict()
        dict_point['x'] = o_point['Longitude']
        dict_point['y'] = o_point['Latitude']
        if b_intersects_base_x(dict_extrema, dict_point) and b_intersects_base_y(dict_extrema, dict_point):
            li_intersect_point.append(o_point)

    # for obj in li_intersect_point:
    #     with open("specific.json", "w") as outfile:
    #         outfile.write(obj)
    # specific_data = pd.read_json("specific.json")
    # new_data_visualisation = plt.pie(specific_data, values="Density", names="TreeType")

    print(li_intersect_point)
    print(len(li_intersect_point))
    return json.loads('{ "response": "success" }')

@server.route('/dvs')
def specificDV():
    with open("specific.json", "w") as outfile:
        json.dump(li_intersect_point, outfile)
        # for index in range(0, len(li_intersect_point)):
        #     json.dump(li_intersect_point[index], outfile)

    specific_data = pd.read_json("specific.json")
    new_data_visualisation = plt.pie(specific_data, values="Density", names="Vegetation") # error is somewhere here
    return new_data_visualisation._repr_html_()

@server.route('/dvshealth')
def specificDVhealth():
    with open("specific.json", "w") as outfile:
        json.dump(li_intersect_point, outfile)
        # for index in range(0, len(li_intersect_point)):
        #     json.dump(li_intersect_point[index], outfile)

    specific_data_health = pd.read_json("specific.json")
    # new_data_visualisation = plt.pie(specific_data, values="Density", names="Vegetation") # error is somewhere here
    new_data_visualisation = plt.histogram(specific_data_health, x="Burnt")
    return new_data_visualisation._repr_html_()

@server.route('/dvssoil')
def specificDVsoil():
    with open("specific.json", "w") as outfile:
        json.dump(li_intersect_point, outfile)
    specific_data_soil = pd.read_json("specific.json")
    new_data_visualisation = plt.pie(specific_data_soil, values="SoilDepth", names="SoilTexture")
    return new_data_visualisation._repr_html_()

def popup_html(row):
    i = row
    latitute = db_data_json_new["Latitude"][i]
    longitute = db_data_json_new["Longitude"][i]
    treeType = db_data_json_new["Vegetation"][i]
    density = db_data_json_new["Density"][i]
    health = db_data_json_new["Burnt"][i]
    html = """
        <!DOCTYPE html>
        <html>
        <center>
        <body>
        <table style="height: 126px; width: 305px;">
            <tbody>
                <tr>
                    <td style="background-color: blue"><span style="color: white">Latitude</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(latitute)+"""</span></td>
                </tr>
                <tr>
                    <td style="background-color: blue"><span style="color: white">Longitude</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(longitute)+"""</span></td>
                </tr>
                <tr>
                    <td style="background-color: blue"><span style="color: white">Vegetation</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(treeType)+"""</span></td>
                </tr>
                <tr>
                    <td style="background-color: blue"><span style="color: white">Density</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(density)+"""</span></td>
                </tr>
                <tr>
                    <td style="background-color: blue"><span style="color: white">Burnt</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(health)+"""</span></td>
                </tr>
            </tbody>
        </table>
        </center> 
        </html>
    """
    return html


def b_intersects_adv(tp_point):
    print("Not Implemented")


def b_intersects_base_x(dict_extrema, dict_point):
    return (dict_extrema['x_min'] < dict_point['x'] < dict_extrema['x_max'])
            # and
            # (dict_extrema['y_min'] < dict_point['y'] < dict_extrema['y_max']))

def b_intersects_base_y(db_extrema, dict_point):
    return (dict_extrema['y_min'] < dict_point['y'] < dict_extrema['y_max'])


if __name__ == '__main__':
    server.run()
