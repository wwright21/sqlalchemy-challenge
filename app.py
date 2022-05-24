# this is for the SQLAlchemy homework

import sqlalchemy
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the 2 tables in hawaii.sqlite
Station = Base.classes.station
Measurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_end_date")

# precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation values for a date"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # This is a copy / paste from the jupyter notebook
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.date(2017, 8, 23)
    year_ago = last_date - dt.timedelta(weeks=52)

    # Query the data
    results = session.query(Measurement.date, Measurement.prcp).\
                  filter(Measurement.date >= year_ago).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    precipitation = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precip"] = prcp
        precipitation.append(precip_dict)

    return jsonify(precipitation)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results2 = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results2))

    return jsonify(all_stations)

# temperature observations route
@app.route("/api/v1.0/tobs")
def temp_obs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations"""
    # Define a few variables that will take the data from the last year
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.date(2017, 8, 23)
    year_ago = last_date - dt.timedelta(weeks=52)
    # Query the dates and temperature observations of the most active station for the previous year of data
    results3 = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == 'USC00519281').all()

    session.close()

    # Convert list of tuples into normal list
    temps = list(np.ravel(results3))

    return jsonify(temps)

# temperature observations - start date only
@app.route("/api/v1.0/start_date<start>")
def temp_start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations starting from a particular date"""


    # Query the dates and temperature observations 
    results_min = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date > start_date).all()

    results_max = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date > start_date).all()

    results_avg = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date > start_date).all()

    session.close()

    # Convert list of tuples into normal list
    min_temps = list(np.ravel(results_min))
    max_temps = list(np.ravel(results_max))
    avg_temps = list(np.ravel(results_avg))

    return jsonify(min_temps, max_temps, avg_temps)



# BOILERPLATE
if __name__ == "__main__":
    app.run(debug=True)