# importing libraries
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_mongoengine import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import datetime

# Initialize flask app
app = Flask(__name__)
CORS(app)

# To locate database file
basedir = os.path.abspath(os.path.dirname(__file__))


# Database (name will be db.sqlite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')

# To prevent warnings from the console (not necessary)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db and marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Location Class
class Location(db.Model):
    loc_id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(75))
    entries = db.relationship('Tracker', backref='locale', lazy=True)

    def __init__(self, location_name):
        self.location_name = location_name

# Tracker Class


class Tracker(db.Model):
    trk_id = db.Column(db.Integer, primary_key=True)
    time_mins = db.Column(db.Integer)
    date_tracked = db.Column(db.DateTime)
    category = db.Column(db.String(75))
    location_id = db.Column(db.Integer, db.ForeignKey('location.loc_id'))

    def __init__(self, time_mins, date_tracked, category, location_id):
        self.time_mins = time_mins
        self.date_tracked = date_tracked
        self.category = category
        self.location_id = location_id

# Tracker Schema


class TrackerSchema(ma.Schema):
    class Meta:
        fields = ('loc_id', 'location_name')


class LocationSchema(ma.Schema):
    class Meta:
        fields = ('trk_id', 'time_mins', 'date_tracked',
                  'category', 'location_id')


# Initializing our schema
tracker_schema = TrackerSchema()
trackers_schema = TrackerSchema(many=True)  # commma after true
location_schema = LocationSchema()
location_schema = LocationSchema(many=True)

# Create a Tracker


@app.route('/api/trackers', methods=['POST'])
def add_tracker():
    locations = ["home", "library", "science building", "work", "park"]
    time_mins = request.json['time_mins']
    #date_tracked = request.json['date_tracked']
    date_tracked = datetime.datetime.strptime(
        request.json['date_tracked'], '%Y-%m-%dT%H:%M:%S.%f%z')
    category = request.json['category']
    if not isinstance(request.json['location'], int):
        location_id = locations.index(request.json['location']) + 1
    else:
        location_id = request.json['location_id']

    new_tracker = Tracker(time_mins, date_tracked, category, location_id)

    db.session.add(new_tracker)
    db.session.commit()

    return tracker_schema.jsonify(new_tracker)

# Get All Trackers


@app.route('/api/trackers', methods=['GET'])
def get_trackers():
    result = db.session.query(Tracker, Location).join(Location).all()
    all_trackers = []
    for tracker, location in result:
        new_dict = {}
        new_dict["trk_id"] = tracker.trk_id
        new_dict["time_mins"] = tracker.time_mins
        new_dict["date_tracked"] = tracker.date_tracked
        new_dict["category"] = tracker.category
        new_dict["location"] = location.location_name
        all_trackers.append(new_dict)
    return jsonify(all_trackers)

# Get Single Tracker


@app.route('/api/trackers/<trk_id>', methods=['GET'])
def get_tracker(trk_id):
    result = db.session.query(Tracker, Location).join(
        Location).filter(Tracker.trk_id == trk_id).all()
    all_trackers = []
    for tracker, location in result:
        new_dict = {}
        new_dict["trk_id"] = tracker.trk_id
        new_dict["time_mins"] = tracker.time_mins
        new_dict["date_tracked"] = tracker.date_tracked
        new_dict["category"] = tracker.category
        new_dict["location"] = location.location_name
        all_trackers.append(new_dict)
    return jsonify(all_trackers)

# Update a Tracker


@app.route('/api/trackers/<trk_id>', methods=['PUT'])
def update_tracker(trk_id):
    a_tracker = Tracker.query.get(trk_id)

    time_mins = request.json['time_mins']
    date_tracked = request.json['date_tracked']
    category = request.json['category']
    location_id = request.json['location_id']

    a_tracker.time_mins = time_mins
    a_tracker.date_tracked = date_tracked
    a_tracker.category = category
    a_tracker.location_id = location_id

    db.session.commit()

    return tracker_schema.jsonify(a_tracker)

# Delete Product


@app.route('/api/trackers/<trk_id>', methods=['DELETE'])
def delete_product(trk_id):
    a_tracker = Tracker.query.get(trk_id)
    db.session.delete(a_tracker)
    db.session.commit()

    return tracker_schema.jsonify(a_tracker)


@app.route('/api/trackers/cat_freq', methods=['GET'])
def get_cat_freqs():
    result = db.session.query(Tracker, Location).join(Location).all()
    trackers = []
    freq = {}
    categories = []
    for tracker, location in result:
        new_dict = {}
        new_dict["trk_id"] = tracker.trk_id
        new_dict["time_mins"] = tracker.time_mins
        new_dict["date_tracked"] = tracker.date_tracked
        new_dict["category"] = tracker.category
        new_dict["location"] = location.location_name
        trackers.append(new_dict["category"])
    for i in trackers:
        if i in freq:
            freq[i] += 1
        else:
            freq[i] = 1
    for i in freq:
        cat = {}
        cat["category"] = i
        cat["count"] = freq[i]
        categories.append(cat)
    return jsonify(categories)


@app.route('/api/trackers/loc_freq', methods=['GET'])
def get_loc_freqs():
    result = db.session.query(Tracker, Location).join(Location).all()
    trackers = []
    freq = {}
    locations = []
    for tracker, location in result:
        new_dict = {}
        new_dict["trk_id"] = tracker.trk_id
        new_dict["time_mins"] = tracker.time_mins
        new_dict["date_tracked"] = tracker.date_tracked
        new_dict["category"] = tracker.category
        new_dict["location"] = location.location_name
        trackers.append(new_dict["location"])
    for i in trackers:
        if i in freq:
            freq[i] += 1
        else:
            freq[i] = 1
    for i in freq:
        loc = {}
        loc["location"] = i
        loc["count"] = freq[i]
        locations.append(loc)
    return jsonify(locations)


@app.route('/api/trackers/cat_freq_against_time', methods=['GET'])
def get_cat_freqs_time():
    result = db.session.query(Tracker, Location).join(Location).all()
    trackers = []
    freq = {}
    categories = []
    count = 0
    for tracker, location in result:
        new_dict = {}
        new_list = []
        new_dict["trk_id"] = tracker.trk_id
        new_dict["time_mins"] = tracker.time_mins
        new_dict["date_tracked"] = tracker.date_tracked
        new_dict["category"] = tracker.category
        new_dict["location"] = location.location_name
        new_list.append(new_dict["category"])
        new_list.append(new_dict["time_mins"])
        trackers.append(new_list)
    for i in trackers:
        if i[0] in freq:
            freq[trackers[count][0]] += trackers[count][1]
        else:
            freq[trackers[count][0]] = trackers[count][1]
        count += 1
    for i in freq:
        cat = {}
        cat["category"] = i
        cat["count_mins"] = freq[i]
        categories.append(cat)
    return jsonify(categories)


@app.route('/api/trackers/loc_freq_against_time', methods=['GET'])
def get_loc_freqs_time():
    result = db.session.query(Tracker, Location).join(Location).all()
    trackers = []
    freq = {}
    locations = []
    count = 0
    for tracker, location in result:
        new_dict = {}
        new_list = []
        new_dict["trk_id"] = tracker.trk_id
        new_dict["time_mins"] = tracker.time_mins
        new_dict["date_tracked"] = tracker.date_tracked
        new_dict["category"] = tracker.category
        new_dict["location"] = location.location_name
        new_list.append(new_dict["location"])
        new_list.append(new_dict["time_mins"])
        trackers.append(new_list)
    for i in trackers:
        if i[0] in freq:
            freq[trackers[count][0]] += trackers[count][1]
        else:
            freq[trackers[count][0]] = trackers[count][1]
        count += 1
    for i in freq:
        loc = {}
        loc["location"] = i
        loc["count_mins"] = freq[i]
        locations.append(loc)
    return jsonify(locations)


# Run Server
if __name__ == '__main__':
    app.run()
