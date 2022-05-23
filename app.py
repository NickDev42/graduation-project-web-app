# import colorama
import jinja2
import plotly.utils
from flask import Flask, render_template, url_for, request
import folium
import pandas as pd
from folium.plugins import MeasureControl, MousePosition
import plotly.express as plt
import json
# import seaborn as sns
# import dash
# import matplotlib.pyplot as plt
# df_suburbs = pd.read_excel("C:\waterwatch_clean2.xlsx", sheet_name='Sheet1')
db_data = pd.read_csv("C:\\Users\Public\data.csv", delimiter=',')
db_data_json = pd.read_json("C:\\Users\Public\csvjson.json")
db_data_parse = json.load(open("C:\\Users\Public\csvjson.json"))
measure_control = MeasureControl()

# print(db_data_json.head().to_json())

server = Flask(__name__)

# def fn():
#     return
#     vis = plt.pie(db_data, values="Density", names="TreeType")
#
#     map = hello_world()
#     return render_template("index.html", map=map, visualisation=vis)
@server.route('/')
def fn():
    vis = dataVis()

    map = hello_world()
    return render_template("index.html", map=map, visualisation=vis)

@server.route('/healthservice')
def fn1():
    visHealth = dataVisHealth()
    mapHealth = treeHealth()
    return render_template("secondpage.html", map=mapHealth, visualisation=visHealth)

lorem = "Pythom"
map_osm = folium.Map(location=[35.000, 33.000], zoom_start=8)
map_health = folium.Map(location=[35.000, 33.000], zoom_start=8)

def hello_world():  # put application's code here
    db_data_locations = db_data_json[["Latitute", "Longitute"]]
    db_data_locations_list = db_data_locations.values.tolist()
    db_data_locations_list_size = len(db_data_locations_list)

    for point in range(0, db_data_locations_list_size):
        html = popup_html(point)

        popup1 = folium.Popup(folium.Html(html, script=True), max_width=500)
        if db_data_json["TreeType"][point] == "Carrop":
            # folium.Marker(db_data_locations_list[point]).add_to(map_osm)
            folium.Circle(location=db_data_locations_list[point], color="green", popup=popup1,
                          opacity=db_data_json["Density"][point], radius=db_data_json["Density"][point]*1000, fill_color="green").add_to(map_osm)
        elif db_data_json["TreeType"][point] == "Pine":
            # folium.Marker(db_data_locations_list[point]).add_to(map_osm)
            folium.Circle(location=db_data_locations_list[point], color="red", popup=popup1,
                          opacity=db_data_json["Density"][point], radius=db_data_json["Density"][point]*1000, fill_color="red").add_to(map_osm)
        else:
            # folium.Marker(db_data_locations_list[point]).add_to(map_osm)
            folium.Circle(location=db_data_locations_list[point], color="blue", popup=popup1,
                          opacity=db_data_json["Density"][point], radius=db_data_json["Density"][point]*1000, fill_color="blue").add_to(map_osm)

    map_osm.add_child(measure_control)
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
    # folium.Rectangle([(34.995, 33.005), (35.995, 33.075)], color="black", fill_color="black").add_to(map_osm)
    map_osm.save('templates/map.html')
    return map_osm._repr_html_()


def treeHealth():  # put application's code here
    db_data_locations = db_data_json[["Latitute", "Longitute"]]
    db_data_locations_list = db_data_locations.values.tolist()
    db_data_locations_list_size = len(db_data_locations_list)

    for point in range(0, db_data_locations_list_size):
        html = popup_html(point)

        popup1 = folium.Popup(folium.Html(html, script=True), max_width=500)
        if db_data_json["Health"][point] == "Healthy":
            # folium.Marker(db_data_locations_list[point]).add_to(map_osm)
            folium.Circle(location=db_data_locations_list[point], color="green", popup=popup1,
                          opacity=db_data_json["Density"][point], radius=20, fill_color="green").add_to(map_health)
        else:
            folium.Circle(location=db_data_locations_list[point], color="red", popup=popup1,
                          opacity=db_data_json["Density"][point], radius=20, fill_color="green").add_to(map_health)
    map_health.add_child(measure_control)
    # el = folium.MacroElement().add_to(map_health)
    # el._template = jinja2.Template("""
    #         {% macro script(this, kwargs) %}
    #             """ + map_health.get_name() + """.on('measurefinish', function(evt){
    #                 fetch("/measureFinish", {
    #                     method: "post",
    #                     headers: {
    #                         "Accept": "application/json",
    #                         "Content-Type": "application/json"
    #                     },
    #                     body: JSON.stringify({
    #                         oJS_In: evt
    #                     }, getCircularReplacer())
    #                 });
    #             });
    #
    #             const getCircularReplacer = () => {
    #               const seen = new WeakSet()
    #               return (key, value) => {
    #                 if (typeof value === "object" && value !== null) {
    #                   if (seen.has(value)) {
    #                     return
    #                   }
    #                   seen.add(value)
    #                 }
    #                 return value
    #               }
    #             }
    #         {% endmacro %}
    #     """)
    # folium.Rectangle([(34.995, 33.005), (35.995, 33.075)], color="black", fill_color="black").add_to(map_osm)
    map_health.save('templates/mapHealth.html')
    return map_health._repr_html_()

@server.route('/map')
def map():
    return render_template('map.html')

@server.route('/maphealth')
def mapHealth():
    return render_template('mapHealth.html')

@server.route('/vis')
def dataVis():
    dv = plt.pie(db_data, values="Density", names="TreeType")
    return dv._repr_html_()

@server.route('/visHealth')
def dataVisHealth():
    dh = plt.histogram(db_data_json, x="Health")
    return dh._repr_html_()


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
        dict_extrema['x_min'] = lng if lng < dict_extrema['x_min'] else dict_extrema['x_min']
        dict_extrema['y_min'] = lat if lat < dict_extrema['y_min'] else dict_extrema['y_min']

    for o_point in db_data_parse:
        dict_point = dict()
        dict_point['x'] = o_point['Longitute']
        dict_point['y'] = o_point['Latitute']
        if b_intersects_base(dict_extrema, dict_point):
            li_intersect_point.append(o_point)

    print(li_intersect_point)
     # print(len(li_intersect_point))

    return json.loads('{ "response": "success" }')

def popup_html(row):
    i = row
    latitute = db_data_json["Latitute"][i]
    longitute = db_data_json["Longitute"][i]
    treeType = db_data_json["TreeType"][i]
    density = db_data_json["Density"][i]
    health = db_data_json["Health"][i]
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
                    <td style="background-color: blue"><span style="color: white">Tree Type</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(treeType)+"""</span></td>
                </tr>
                <tr>
                    <td style="background-color: blue"><span style="color: white">Density</span></td>
                    <td style="background-color: white"><span style="color: blue">"""+str(density)+"""</span></td>
                </tr>
                <tr>
                    <td style="background-color: blue"><span style="color: white">Healthy</span></td>
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


def b_intersects_base(dict_extrema, dict_point):
    return ((dict_extrema['x_min'] < dict_point['x'] < dict_extrema['x_max']) and
            (dict_extrema['y_min'] < dict_point['y'] < dict_extrema['y_max']))


if __name__ == '__main__':
    server.run()
