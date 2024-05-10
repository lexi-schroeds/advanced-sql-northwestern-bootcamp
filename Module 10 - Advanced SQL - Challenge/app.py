#Leveraged Xpert Learning Assistant to finish this assignment

# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route('/api/v1.0/precipitation')
def get_precipitation_data():
    # Calculate the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    # Query precipitation data for the last year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary with date as key and precipitation as value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def get_stations_data():
    # Query all stations from the Station table
    stations = session.query(Station.station).all()

    # Convert the query result to a list of station names
    station_list = [station for station, in stations]

    return jsonify({'stations': station_list})

@app.route('/api/v1.0/tobs')
def get_tobs_data():
    most_active_station = 'USC00519281'
    most_recent_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    tobs_dict = {date: tobs for date, tobs in tobs_data}

    return jsonify(tobs_dict)

@app.route('/api/v1.0/start/<start_date>')
def get_temp_stats_from_start(start_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    min_temp, max_temp, avg_temp = temp_stats[0]

    return jsonify({'start_date': start_date.strftime('%Y-%m-%d'),
                    'min_temperature': min_temp,
                    'max_temperature': max_temp,
                    'avg_temperature': avg_temp})

@app.route('/api/v1.0/start/<start_date>/end/<end_date>')
def get_temp_stats_between_dates(start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    if temp_stats:
        min_temp, max_temp, avg_temp = temp_stats[0]
        return jsonify({'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'min_temperature': min_temp,
                        'max_temperature': max_temp,
                        'avg_temperature': avg_temp})
    else:
        return jsonify({'error': 'No temperature data found for the specified date range'})

if __name__ == '__main__':
    app.run(debug=True)
