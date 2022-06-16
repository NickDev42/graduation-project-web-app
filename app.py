# import colorama
import sqlite3

import jinja2
import plotly.utils
from flask_wtf import FlaskForm
from numpy import unicode
from wtforms import (StringField, SubmitField, DateTimeField, DateField, BooleanField, TextAreaField, SelectField)
from flask import Flask, render_template, url_for, request, session, redirect, flash
from wtforms.validators import DataRequired
import folium
import pandas as pd
from folium.plugins import MeasureControl, MousePosition
import plotly.express as plt
import json
from datetime import datetime, date
import time
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user, login_manager

import os
# import seaborn as sns
# import dash
# import matplotlib.pyplot as plt
# df_suburbs = pd.read_excel("C:\waterwatch_clean2.xlsx", sheet_name='Sheet1')
# db_data = pd.read_csv("C:\\Users\Public\data.csv", delimiter=',')
# db_data_json = pd.read_json("C:\\Users\Public\csvjson.json")
db_data_parse = json.load(open("jsondatafile.json"))
db_data_json_new = pd.read_json("jsondatafile.json")
measure_control = MeasureControl()

basedir = os.path.abspath(os.path.dirname(__file__))
# print(db_data_json.head().to_json())

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
# app.config['SQLALCHEMY_DATABASE_URI'] = ' postgres://rkxtjqdykwwckc:d520ddc63215694388218b32a734557d2906fcc69b09c12471dcd212a62712d3@ec2-52-71-23-11.compute-1.amazonaws.com:5432/dddnbklebrv3sh'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)


# Code Login Form: https://github.com/sathyainfotech/Login-Registration-SQLite.git
con=sqlite3.connect("mydb.db")
con.execute("CREATE TABLE if not exists login(id INTEGER PRIMARY KEY, email TEXT, password TEXT, organisation TEXT)")
con.execute("CREATE TABLE if not exists afforestation(id INTEGER PRIMARY KEY, coordinates BLOB, startDate DATE not null, endDate DATE not null, organisation TEXT not null)")
con.close()
@app.route('/loginform')
def loginform():
    return render_template("loginform.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        con = sqlite3.connect("mydb.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from login where email=? and password = ?", (email, password))
        data = cur.fetchone()

        if data:
            session["email"] = data["email"]
            session["password"] = data["password"]
            return redirect("user")
        else:
            flash("Email and Password incorrect", "danger")
    return redirect(url_for("loginform"))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        try:
            organisation = request.form['organisation']
            email = request.form['email']
            password = request.form['password']
            con = sqlite3.connect("mydb.db")
            cur = con.cursor()
            cur.execute("INSERT INTO login(organisation, email, password) values(?, ?, ?)", (organisation, email, password))
            con.commit()
            flash("Registration completed", "success")
        except:
            flash("Registration unsuccessful", "danger")
        finally:
            return redirect(url_for("user"))
            con.close()
    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    filepath = "specific.json"
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        pass
    return redirect(url_for("login"))

@app.route('/user', methods=["GET", "POST"])
def user():
    return render_template("user.html")


class AfforestationForm(FlaskForm):
    # location = json.loads(open("bounds.json"))
    coordinates = StringField()
    startDate = DateField()
    endDate = DateField()
    organisation = StringField()
    submit = SubmitField('Submit')


class JoinForm(FlaskForm):
    afforestation = StringField()
    name = StringField()
    email = StringField()
    submit = SubmitField('Submit')



# here was afforestation form
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')



@app.route('/')
def fn():
    vis = dataVis()

    map = treeTypeMap()
    return render_template("index.html", map=map, visualisation=vis)

@app.route('/healthservice')
def fn1():
    visHealth = dataVisHealth()
    # mapHealth = treeHealth()
    map = treeTypeMap()
    return render_template("contextInfo.html", map=map, visualisation=visHealth)

@app.route('/soiltypeservice')
def fn2():
    visSoil = dataVisSoil()
    # mapSoil = soilType()
    map = treeTypeMap()
    return render_template("soilType.html", map=map, visualisation=visSoil)

@app.route('/statusafforestation')
def fn3():
    map = treeTypeMap()
    return render_template("statusAfforestation.html", map=map)

@app.route('/statusSpecific')
def fn4():
    map = treeTypeMap()
    return render_template("statusSpecific.html", map=map)

@app.route('/contextSpecific')
def fn5():
    map = treeTypeMap()
    return render_template("contextSpecific.html", map=map)

@app.route('/vegetationSpecific')
def specData():
    specVis = specificDV()
    map = treeTypeMap()
    return render_template("specificData.html", map=map, visualisation=specVis)

@app.route('/healthSpecific')
def specDataHealthTrees():
    specVis = specificDVhealth()
    # map = treeHealth()
    map = treeTypeMap()
    return render_template("specificDatahealth.html", map=map, visualisation=specVis)

@app.route('/soilSpecific')
def specDataSoilType():
    specVis = specificDVsoil()
    # map = soilType()
    map = treeTypeMap()
    return render_template("specificDataSoil.html", map=map, visualisation=specVis)

lorem = "Pythom"
map_osm = folium.Map(location=[35.000, 33.000], zoom_start=8)
# map_osm = Map(mapobj=folium.Map(location=[35.000, 33.000], zoom_start=8), measure_control=MeasureControl(), data_source=db_data_json_new)
map_health = folium.Map(location=[35.000, 33.000], zoom_start=8)
map_soil = folium.Map(location=[35.000, 33.000], zoom_start=8)
map_osm.add_child(MeasureControl())
map_health.add_child(measure_control)
map_soil.add_child(MeasureControl())
el = folium.MacroElement().add_to(map_osm)
el._template = jinja2.Template("""
        {% macro script(this, kwargs) %}
            var map_osm = """+map_osm.get_name()+""";
            """+map_osm.get_name()+""".on('measurefinish', function(evt){
                fetch("/measureFinish", {
                    method: "post",
                    headers: {
                        "Accept": "app/json",
                        "Content-Type": "app/json"
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



@app.route('/news')
def afforestation_news():
    con = sqlite3.connect("mydb.db")
    cur = con.cursor()
    cur.execute("SELECT id, startDate, endDate, organisation from afforestation")
    details = cur.fetchall()

    print(details)
    return render_template("news.html", details=details)


polygons_list = list()
pts_in_list = list()



def treeTypeMap():  # put app's code here
    db_data_locations = db_data_json_new[["Latitude", "Longitude"]]
    db_data_locations_list = db_data_locations.values.tolist()
    db_data_locations_list_size = len(db_data_locations_list)
    global afforestation_filename

    con = sqlite3.connect("mydb.db")
    cur = con.cursor()
    cur.execute("SELECT startDate, coordinates, points, endDate, id FROM afforestation")
    polygons = cur.fetchall()
    print(type(polygons))

    for polygon in polygons:
        html = popup_html(polygon[0], polygon[1], polygon[3], polygon[4])
        popup1 = folium.Popup(folium.Html(html, script=True), max_width=500)

        # html = popup_html(polygon)
        if len(polygon) < 2:
            continue
        act_polygon = json.loads(polygon[1])
        pts_in_list = json.loads(polygon[2])  # get the points from the area in polygon
        print(pts_in_list)

        print(type(pts_in_list))
        polydata(f"polygon{polygons.index(polygon)}", pts_in_list) #attach data from pts list to specific polygon json file -- done

        afforestation_filename = "jsons/polygon{0}.json".format(str(polygons.index(polygon)))
        print(afforestation_filename)
        # with open(f"polygon{polygons.index(polygon)}", "w") as outfile_pts:
        #     json.dump(pts_in_list, outfile_pts)
        print(polygons.index(polygon))
        print(type(act_polygon))
        print(act_polygon)
        # act_polygon = polygon[1]
        locations=list()
        print(act_polygon)
        print(type(act_polygon))
        # folium.Polygon(locations = polygon)
        for locs in act_polygon:
            locations.append((locs['lat'], locs['lng']))
            # popup1 = folium.Popup(folium.Html(html, script=True), max_width=500)
        if datetime.strptime(polygon[0], '%Y-%m-%d') > datetime.combine(date.today(), datetime.min.time()):
            poly = folium.Polygon(locations=locations, popup=popup1, color="red", weight=2, fill_color="red", fill_opacity=0.1)
            poly.add_to(map_osm)
            polygons_list.append(poly)
        else:
            poly = folium.Polygon(locations=locations, popup=popup1, color="green", weight=2, fill_color="green", fill_opacity=0.1)
            poly.add_to(map_osm)
            polygons_list.append(poly)

    filepath = "templates/map.html"
    if os.path.exists(filepath):
        os.remove(filepath)
        map_osm.save('templates/map.html')

    return map_osm._repr_html_()


@app.route('/visstatus')
def visualise_polygon():
    print("shshshshsh")
    print(afforestation_filename)
    obj = pd.read_json(afforestation_filename)
    print("shshshshsh")
    dv = plt.pie(obj, names="TreeType")
    return dv._repr_html_()


@app.route('/visstatushealth')
def visualise_polygon_health():
    obj = pd.read_json(afforestation_filename)
    dv = plt.histogram(obj, x="Burnt")
    return dv._repr_html_()


@app.route('/visstatussoil')
def visualise_polygon_soil():
    obj = pd.read_json(afforestation_filename)
    dv = plt.pie(data_frame=obj.groupby(['SoilTexture']).mean().reset_index(), values="SoilDepth", names="SoilTexture")
    return dv._repr_html_()


@app.route('/visstatuselevation')
def visualise_polygon_elevation():
    obj = pd.read_json(afforestation_filename)
    dv = plt.histogram(data_frame=obj.groupby(['Elevationlvl']).mean().reset_index(), x="Elevationlvl", y="Heightlvl")
    dv.update_layout(showlegend=False)
    return dv._repr_html_()


@app.route('/visstatusweather')
def visualise_polygon_weather():
    obj = pd.read_json(afforestation_filename)
    dv = plt.pie(data_frame=obj.groupby(['Rain']).mean().reset_index(), values="AvgRain", names="Rain")
    return dv._repr_html_()


@app.route('/visstatusslope')
def visualise_polygon_slope():
    obj = pd.read_json(afforestation_filename)
    dv = plt.histogram(data_frame=obj.groupby(['Aspect']).mean().reset_index(), x="Aspect", y="Slope")
    return dv._repr_html_()


@app.route('/globalsoil')
def visualise_soil():
    dv = plt.pie(db_data_json_new, values="SoilDepth", names="SoilTexture")
    return dv._repr_html_()


@app.route('/globalelevation')
def visualise_elevation():
    dv = plt.histogram(db_data_json_new, x="Elevationlvl", y="Heightlvl")
    return dv._repr_html_()


@app.route('/globalweather')
def visualise_weather():
    dv = plt.pie(db_data_json_new, values="AvgRain", names="Rain")
    return dv._repr_html_()


@app.route('/globalslope')
def visualise_slope():
    dv = plt.histogram(db_data_json_new, x="Aspect", y="Slope")
    return dv._repr_html_()


def polydata(filename, file_src):
    with open(f"jsons/{filename}.json", "w") as outfile_pts:
            print(pts_in_list)
            json.dump(file_src, outfile_pts)


# def treeHealth():  # put app's code here
#     db_data_locations = db_data_json_new[["Latitude", "Longitude"]]
#     db_data_locations_list = db_data_locations.values.tolist()
#     db_data_locations_list_size = len(db_data_locations_list)
#
#     for point in range(0, db_data_locations_list_size):
#         html = popup_html(point)
#
#         popup1 = folium.Popup(folium.Html(html, script=True), max_width=500)
#         if db_data_json_new["Burnt"][point] == "No":
#             # folium.Marker(db_data_locations_list[point]).add_to(map_osm)
#             folium.Circle(location=db_data_locations_list[point], color="green", popup=popup1,
#                           opacity=db_data_json_new["Density"][point], radius=20, fill_color="green").add_to(map_health)
#         else:
#             folium.Circle(location=db_data_locations_list[point], color="red", popup=popup1,
#                           opacity=db_data_json_new["Density"][point], radius=20, fill_color="green").add_to(map_health)
#     # map_health.add_child(measure_control)
#     map_health.save('templates/mapHealth.html')
#     return map_health._repr_html_()




@app.route('/map')
def map():
    return render_template('map.html')


@app.route('/maphealth')
def mapHealth():
    return render_template('mapHealth.html')

trees_json_file = pd.read_json("treesplanted.json")
@app.route('/treesplanted')
def trees_planted():
    dv = plt.line(trees_json_file, x="Year", y="TreesPlanted", markers=True)
    return dv._repr_html_()

@app.route('/vis')
def dataVis():
    dv = plt.pie(db_data_json_new, names="TreeType")
    return dv._repr_html_()


@app.route('/visHealth')
def dataVisHealth():
    dh = plt.histogram(db_data_json_new, x="Burnt")
    return dh._repr_html_()


@app.route('/visSoil')
def dataVisSoil():
    dv = plt.pie(db_data_json_new, values="SoilDepth", names="SoilTexture")

    return dv._repr_html_()


dict_extrema = dict()
data_list = list()
li_intersect_point = list()


@app.route('/measureFinish', methods = ['POST'])
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

    with open("specific.json", "w") as outfile:
        json.dump(li_intersect_point, outfile)
    print(li_intersect_point)
    print(len(li_intersect_point))
    print("********************")

    data_list.clear()
    data_list.append(data['points'])
    print(data_list)
    return json.loads('{ "response": "success" }')


@app.route('/afforestationform', methods=['GET', 'POST'])
def form():
    map = treeTypeMap()
    form = AfforestationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # print(coordinates)
                startDate = request.form['startDate']
                endDate = request.form['endDate']
                organisation = request.form['organisation']

                ar_points = json.loads("""[]""")

                for point in data_list[0]:
                    o_point = json.loads("""{}""")
                    o_point["lat"] = point["lat"]
                    o_point["lng"] = point["lng"]
                    ar_points.append(o_point)

                # startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
                # endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
                conn = sqlite3.connect("mydb.db")
                cur = conn.cursor()
                cur.execute("INSERT INTO afforestation(coordinates, startDate, endDate, organisation, points) VALUES(?,?,?,?,?)",
                            (json.dumps(ar_points), startDate, endDate, organisation, json.dumps(li_intersect_point)))
                conn.commit()
            except Exception as e:
                # time.sleep(5)
                # return redirect(url_for("form"))
                print(e)
            finally:
                return redirect(url_for('fn'))
                conn.close()

    return render_template('applicationform.html', form=form)


@app.route('/joinform', methods=['GET', 'POST'])
def join_form():
    map = treeTypeMap()
    form = JoinForm()
    session["afforestation"] = get_afforestations()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # print(coordinates)

                afforestation = request.form['afforestation']
                name = request.form['name']
                email = request.form['email']

                # startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
                # endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
                conn = sqlite3.connect("mydb.db")
                cur = conn.cursor()
                cur.execute("CREATE TABLE if not exists volunteer(afforestation INTEGER PRIMARY KEY, name TEXT, email TEXT)")
                cur.execute("INSERT INTO volunteer(afforestation, name, email) VALUES(?,?,?)",
                            (afforestation, name, email))
                conn.commit()
            except Exception as e:
                # time.sleep(5)
                # return redirect(url_for("form"))
                print(e)
            finally:
                return redirect(url_for('fn'))
                conn.close()

    return render_template('joinform.html', form=form, afforestation_list = session["afforestation"])


def get_afforestations():
    con = sqlite3.connect("mydb.db")
    cur = con.cursor()
    cur.execute("select id, organisation from afforestation WHERE startDate >= CURRENT_DATE ")
    data = cur.fetchall()
    # data = [(val[0], val[1]) for val in data]
    con.close()
    return data


@app.route('/dvs')
def specificDV():

        # for index in range(0, len(li_intersect_point)):
        #     json.dump(li_intersect_point[index], outfile)

    specific_data = pd.read_json("specific.json")
    new_data_visualisation = plt.pie(specific_data, values="Density", names="Vegetation") # error is somewhere here
    return new_data_visualisation._repr_html_()

@app.route('/dvshealth')
def specificDVhealth():

        # for index in range(0, len(li_intersect_point)):
        #     json.dump(li_intersect_point[index], outfile)

    specific_data_health = pd.read_json("specific.json")
    # new_data_visualisation = plt.pie(specific_data, values="Density", names="Vegetation") # error is somewhere here
    new_data_visualisation = plt.histogram(specific_data_health, x="Burnt")
    return new_data_visualisation._repr_html_()

@app.route('/dvssoil')
def specificDVsoil():

    specific_data_soil = pd.read_json("specific.json")
    new_data_visualisation = plt.pie(specific_data_soil, values="SoilDepth", names="SoilTexture")
    return new_data_visualisation._repr_html_()

def popup_html(startDate, coordinates, endDate, id):
    # i = row
    # latitute = db_data_json_new["Latitude"][i]
    # longitute = db_data_json_new["Longitude"][i]
    # treeType = db_data_json_new["Vegetation"][i]
    # density = db_data_json_new["Density"][i]
    # health = db_data_json_new["Burnt"][i]

    html = """
        <!DOCTYPE html>
        <html>
        <center>
        <body>
        <table style="height: 150px; width: 500px;">
            <tbody>
                <tr>
                    <td style="background-color: blue"><span style="color: white">StartDate</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(startDate)+"""</span></td>
                </tr>
                <tr>
                    <td style="background-color: blue"><span style="color: white">EndDate</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(endDate)+"""</span></td>
                </tr>
                <tr>
                    <td style="background-color: blue"><span style="color: white">Coordinates</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(coordinates)+"""</span></td>
                </tr>
                <tr>
                    <td style="background-color: blue"><span style="color: white">ID</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(id)+"""</span></td>
                </tr>
                <tr>
                    <a href="/statusSpecific" target="_top"><button>See Status</button></a>
                    <a href="/contextSpecific" target="_top"><button>See Contextual Information</button></a>
                </tr>
            </tbody>
        </table>
        </center>
        </html>
    """
    return html



def b_intersects_base_x(dict_extrema, dict_point):
    return (dict_extrema['x_min'] < dict_point['x'] < dict_extrema['x_max'])
            # and
            # (dict_extrema['y_min'] < dict_point['y'] < dict_extrema['y_max']))

def b_intersects_base_y(db_extrema, dict_point):
    return (dict_extrema['y_min'] < dict_point['y'] < dict_extrema['y_max'])


if __name__ == '__main__':
    app.run()
