import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo = False)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)


@app.route("/")
def home():
    """List all routes that are available"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value"""
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date

    most_recent_date_dt = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

    year_ago = most_recent_date_dt - dt.timedelta(days = 365)

    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()

    prcp_list = {date: prcp for date, prcp in prcp_data}

    session.close()
    return jsonify(prcp_list)


@app.route('/api/v1.0/stations')
def stations():

    session = Session(engine)

    """Return a JSON list of stations from the dataset."""

    stations_list = session.query(station.station).all()

    session.close()

    unravel_list = list(np.ravel(stations_list))
    return jsonify(unravel_list)


@app.route('/api/v1.0/tobs') 
def tobs():  
    station_id = 'USC00519281'

    session = Session(engine)

    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date

    most_recent_date_dt = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

    year_ago = most_recent_date_dt - dt.timedelta(days = 365)

    tobs_data = session.query(measurement.date, measurement.tobs)\
        .filter(measurement.date >= year_ago)\
        .filter(measurement.station == station_id).all()

    new_list =  {date: tobs for date, tobs in tobs_data}
    return jsonify(new_list)

@app.route('/api/v1.0/<start>') 
def start(start):
    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    session = Session(engine)

    year_query = session.query(func.min(measurement.tobs), \
                           func.max(measurement.tobs), \
                           func.avg(measurement.tobs)).\
                           filter(measurement.date >= start_date).all()
    
    session.close()
    unravel_list = list(np.ravel(year_query))
    return jsonify(unravel_list)


@app.route('/api/v1.0/<start>/<end>') 
def startend(start, end):
    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    session = Session(engine)

    year_query_2 = session.query(func.min(measurement.tobs), \
                           func.max(measurement.tobs), \
                           func.avg(measurement.tobs)). \
                           filter(measurement.date.between(start_date, end_date)).all()
    
    session.close()
    unravel_list = list(np.ravel(year_query_2))
    return jsonify(unravel_list)



if __name__ == "__main__":
    app.run(debug=True)