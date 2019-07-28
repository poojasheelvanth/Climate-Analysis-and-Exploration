import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from dateutil.relativedelta import relativedelta
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
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a Dictionary using date as the key and prcp as the value.
    #Return the JSON representation of your dictionary.
    session = Session(engine)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date > year_ago).all()
    
    all_measurements = []
    for date, prcp in precipitation_data:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_measurements.append(precipitation_dict)
    

    return jsonify(all_measurements)


@app.route("/api/v1.0/stations")
def stations():
    
    # Query all Stations
    session = Session(engine)
    results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of all_stations.
    all_stations = []
    for stations in results:
        stations_dict = {}
        stations_dict["Station"] = stations.station
        stations_dict["Station Name"] = stations.name
        stations_dict["Latitude"] = stations.latitude
        stations_dict["Longitude"] = stations.longitude
        stations_dict["Elevation"] = stations.elevation
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #query for the dates and temperature observations from a year from the last data point.
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    session = Session(engine)
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date > year_ago).group_by(Measurement.date).order_by(Measurement.date).all()

    
    results = session.query(Measurement.date,Measurement.tobs).all()
    
    all_measurements = []
    
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_measurements.append(tobs_dict)
    

    return jsonify(all_measurements)   

@app.route("/api/v1.0/<start_date>")
def start_stats(start_date):
    #Return a json list of the minimum temperature, the average temperature, and the
    #max temperature for a given start date
    # Query all the stations and for the given date. 
    minimum = session.query(Measurement.tobs, func.min(Measurement.tobs)).filter(Measurement.date >= start_date)
    maximum = session.query(Measurement.tobs, func.max(Measurement.tobs)).filter(Measurement.date >= start_date)
    average = session.query(Measurement.tobs, func.avg(Measurement.tobs)).filter(Measurement.date >= start_date)

    start_temp = {"Tmin": minimum[0][0], "Tmax": maximum[0][0], "Tavg": average[0][0]}
    
    
    return jsonify(start_temp)
    

@app.route("/api/v1.0/<start_date>&<end_date>")
def start(start_date, end_date):
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."
    minimum = session.query(Measurement.tobs, func.min(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date))
    maximum = session.query(Measurement.tobs, func.max(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date))
    average = session.query(Measurement.tobs, func.avg(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date))

    start_end_temps = {"Tmin": minimum[0][0], "Tmax": maximum[0][0], "Tavg": average[0][0]}
    
    return jsonify(start_end_temps)

if __name__ == '__main__':
    app.run(debug=True)
