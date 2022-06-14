import folium
import jinja2
import pandas as pd
from folium.plugins import MeasureControl, MousePosition


class Map(folium.Map):
    def __init__(self, mapobj, data_source, measure_control):
        super().__init__()
        self.map = mapobj
        self.measure_control = measure_control
        self.map.add_child(measure_control)
        self.data_source = data_source
        self.element = folium.MacroElement().add_to(self.map)
        self.element._template = jinja2.Template("""
        {% macro script(this, kwargs) %}
            """+self.map.get_name()+""".on('measurefinish', function(evt){
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
