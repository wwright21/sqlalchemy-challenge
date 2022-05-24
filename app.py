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
        "<b>Welcome to the Climate Analysis API!</b><br/>"
        "<br/>"
        "<u>Available Routes:</u><br/>"
        "<br/>"
        "/api/v1.0/precipitation<br/>"
        "<i>This route returns the precipitation measurements for the last 12 months</i><br/>"
        "<br/>"
        "/api/v1.0/stations<br/>"
        "<i>This route lists all station IDs in the database</i><br/>"
        "<br/>"
        "/api/v1.0/tobs<br/>"
        "<i>This route returns the temperature observations for the last 12 months</i><br/>"
        "<br/>"
        "/api/v1.0/start_date:<br/>"
        "<i>This route returns the min, max, and average temperature observations given a start date.</i><br/>"
        "<i>Note: the date must be formatted like so: 2016-05-03 </i><br/>"
        "<br/>"
        "/api/v1.0/start_date/end_date:<br/>"
        "<i>This route returns the min, max, and average temperature observations between 2 dates in the dataset.</i><br/>"
        "<i>Note: the two dates must be formatted like so: 2016-05-03/2016-05-10 </i><br/>"
        )

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
@app.route("/api/v1.0/start_date:<start_date>")
def temp_start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations starting from a particular date"""
    results4 = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(func.strftime("%Y-%m-%d", Measurement.date) >= func.strftime("%Y-%m-%d", start_date)).all()

    session.close()

    temps = []
    for min, max, avg in results4:
        temp_dict = {}
        temp_dict['min'] = min
        temp_dict['max'] = max
        temp_dict['avg'] = avg
        temps.append(temp_dict)

    return jsonify(temps)


# temperature observations - start and end date
@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_between(start_date, end_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations between a start and end date"""
    results5 = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(func.strftime("%Y-%m-%d", Measurement.date) >= func.strftime("%Y-%m-%d", start_date))\
        .filter(func.strftime("%Y-%m-%d", Measurement.date) <= func.strftime("%Y-%m-%d", end_date)).all()

    session.close()

    temps2 = []
    for min, max, avg in results5:
        temp_dict = {}
        temp_dict['min'] = min
        temp_dict['max'] = max
        temp_dict['avg'] = avg
        temps2.append(temp_dict)

    return jsonify(temps2)


# BOILERPLATE
if __name__ == "__main__":
    app.run(debug=True)