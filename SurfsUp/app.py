# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta
import json



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
Session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        f"Welcome to the Climate API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )

# Route to get precipitation data for the last 12 months
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Get the most recent date in the dataset
    latest_date = Session.query(func.max(Measurement.date)).scalar()
    year_ago = datetime.strptime(latest_date, '%Y-%m-%d') - timedelta(days=365)
    
    # Query to retrieve precipitation data for the last 12 months
    results = Session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.date <= latest_date).\
        all()

    # Convert results to a dictionary (date as key and prcp as value)
    precip_dict = {date: prcp for date, prcp in results}
    
    return jsonify(precip_dict)

# Route to get list of stations
@app.route('/api/v1.0/stations')
def stations():
    # Query to get all station IDs
    results = Session.query(Station.station).all()
    
    # Convert results to a list of stations
    stations_list = [station[0] for station in results]
    
    return jsonify(stations_list)

# Route to get temperature observations for the most active station in the last year
@app.route('/api/v1.0/tobs')
def tobs():
    # Get the most active station (based on the previous query)
    most_active_station = Session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()
    
    most_active_station_id = most_active_station[0]
    
    # Calculate the date one year ago from the latest date
    latest_date = Session.query(func.max(Measurement.date)).scalar()
    year_ago = datetime.strptime(latest_date, '%Y-%m-%d') - timedelta(days=365)
    
    # Query the temperature data for the most active station in the last 12 months
    results = Session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= year_ago).\
        all()
    
    # Convert the results to a list of temperature observations
    tobs_list = [{'date': date, 'temperature': tobs} for date, tobs in results]
    
    return jsonify(tobs_list)

# Route to get min, avg, and max temperatures for a given start date
@app.route('/api/v1.0/<start>')
def start_temp_stats(start):
    # Query the min, avg, and max temperatures for all dates >= start
    results = Session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()
    
    # Convert the results to a dictionary
    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temp_stats)

# Route to get min, avg, and max temperatures for a given start and end date
@app.route('/api/v1.0/<start>/<end>')
def start_end_temp_stats(start, end):
    # Query the min, avg, and max temperatures for the dates >= start and <= end
    results = Session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert the results to a dictionary
    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temp_stats)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)