from flask import Flask
from obspy import read
from preprocessing import Seismic
import json


app = Flask(__name__)


dixondale = "G:/3D Seismic Volumes-SEGY/Seismic Data 3DX/Dixondale/DixondalePSTM_8-14-19_filtered_export3.sgy"


stream = read(dixondale, format="SEGY")
stream.normalize()


seismicData = Seismic(stream)


@app.route("/")
def index():
    return json.dumps(seismicData.seismic_array.tolist())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)