import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
import numpy as np
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/start<br/>'
        f'/api/v1.0/start_end<br/>'
    ) 

@app.route("/api/v1.0/precipitation")
def precipitation():
    precipitations = session.query(measurement.date,measurement.prcp).\
    filter(measurement.date.between('2016-08-23','2017-08-23')).\
    order_by(measurement.date).all()

    Dates = [p[0] for p in precipitations]
    Prcp = [p[1] for p in precipitations]

    Prcp_by_Date = pd.DataFrame({'date':Dates,'precipitation':Prcp})
    Prcp_by_Date.set_index('date',inplace=True)
    
    prcp_json = Prcp_by_Date.to_dict(orient='split')
    
    return jsonify({'status': 'ok', 'json_data': prcp_json})

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(station.station, station.name, station.latitude,station.longitude,station.elevation).statement
    station_df = pd.read_sql_query(stations, session.bind)
    station_df.set_index('station',inplace=True)
    station_jason = station_df.to_dict(orient='split')

    return jsonify({'status': 'ok', 'json_data': station_jason})

@app.route("/api/v1.0/tobs")
def tobs():
    tob = session.query(measurement.date,measurement.tobs).\
    filter(measurement.date.between('2016-08-23','2017-08-23')).\
    order_by(measurement.date).all()

    Dates = [t[0] for t in tob]
    Tobs = [t[1] for t in tob]

    Tob_by_Date = pd.DataFrame({'date':Dates,'tob':Tobs})
    Tob_by_Date.set_index('date',inplace=True)
    
    tobs_json = Tob_by_Date.to_dict(orient='split')
    
    return jsonify({'status': 'ok', 'json_data': tobs_json})

@app.route("/api/v1.0/start")
def start(start_date):
    start_date = input("Please enter a start date.")
    temp_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).all()
    temperatures_start = list(np.ravel(temp_data))

    return jsonify(temperatures_start)

@app.route('/api/v1.0/start_end')
def start_end(start,end):
    temp_data =calc_temps(start, end)
    
    temps = []
    for temp in results:
        temp_dict = {}
        temp_dict["TMIN"] = temp[0]
        temp_dict["TAVG"] = temp[1]
        temp_dict["TMAX"] = temp[2]
        temps.append(temp_dict)

    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
