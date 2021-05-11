#from flask.helpers import make_response
from flask import Flask, make_response, request, jsonify
from flask_mongoengine import MongoEngine
from bson.json_util import dumps
from collections import Counter
import datetime

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#db = "ProductivityDb"
#collection = db["Tracker"]


# initializing databse info
app.config["MONGODB_HOST"] = "mongodb+srv://test:test@cluster0.ylrrh.mongodb.net/ProductivityDb?retryWrites=true&w=majority"
#app.config["MONGODB_HOST"] = "mongodb://localhost:27017/ProductivityDb"
db = MongoEngine()
db.init_app(app)


# Time stamp class
class Tracker(db.Document):
    trk_id = db.SequenceField()
    time_mins = db.IntField()
    date_tracked = db.DateTimeField()
    category = db.StringField()
    location = db.StringField()


@app.route('/api/trackers', methods=['GET'])
def get_trackers():
    trackers = []
    for tracker in Tracker.objects:
        new_tracker_dict = tracker.to_mongo().to_dict()
        new_tracker_dict["date_tracked"] = tracker.date_tracked.isoformat()
        new_tracker_dict.pop("_id", None)
        trackers.append(new_tracker_dict)
    return make_response(dumps(trackers), 200)


@app.route('/api/trackers', methods=['POST'])
def add_trackers():
    # submit entry to collection
    # time '%Y-%m-%d %H:%M:%S.%f'
    content = request.json
    tracker = Tracker(time_mins=content['time_mins'],
                      date_tracked=content['date_tracked'], category=content['category'], location=content['location'])
    tracker.save()
    return make_response("", 201)


@app.route('/api/trackers/<trk_id>', methods=['GET', 'PUT', 'DELETE'])
def each_tracker(trk_id):

    # get entry from collection using stamp id
    if request.method == "GET":
        tracker_obj = Tracker.objects(
            trk_id=trk_id).first()
        if tracker_obj:
            new_tracker_dict = tracker_obj.to_mongo().to_dict()
            new_tracker_dict["date_tracked"] = tracker_obj.date_tracked.isoformat()
            new_tracker_dict.pop("_id", None)
            return make_response(dumps(new_tracker_dict), 200)
        else:
            return make_response("", 404)

    # update entry in collection using stamp id
    elif request.method == "PUT":
        content = request.json
        tracker_obj = Tracker.objects(
            trk_id=trk_id).first()
        tracker_obj.update(time_mins=content['time_mins'], date_tracked=content['date_tracked'],
                           category=content['category'], location=content['location'])
        return make_response("", 204)

    # Delete an entry in collection using stamp id
    elif request.method == "DELETE":
        tracker_obj = Tracker.objects(
            trk_id=trk_id).first()
        tracker_obj.delete()
        return make_response("", 204)


@app.route('/api/trackers/cat_freq', methods=['GET'])
def get_cat_freqs():
    trackers = []
    freq = {}
    categories = []
    for tracker in Tracker.objects:
        new_tracker_dict = tracker.to_mongo().to_dict()
        trackers.append(new_tracker_dict["category"])
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
    return make_response(dumps(categories), 200)


@app.route('/api/trackers/loc_freq', methods=['GET'])
def get_loc_freqs():
    trackers = []
    freq = {}
    locations = []
    for tracker in Tracker.objects:
        new_tracker_dict = tracker.to_mongo().to_dict()
        trackers.append(new_tracker_dict["location"])
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
    return make_response(dumps(locations), 200)


@app.route('/api/trackers/cat_freq_against_time', methods=['GET'])
def get_cat_freqs_time():
    trackers = []
    freq = {}
    categories = []
    count = 0
    for tracker in Tracker.objects:
        new_list = []
        new_tracker_dict = tracker.to_mongo().to_dict()
        new_list.append(new_tracker_dict["category"])
        new_list.append(new_tracker_dict["time_mins"])
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
    return make_response(dumps(categories), 200)


@app.route('/api/trackers/loc_freq_against_time', methods=['GET'])
def get_loc_freqs_time():
    trackers = []
    freq = {}
    locations = []
    count = 0
    for tracker in Tracker.objects:
        new_list = []
        new_tracker_dict = tracker.to_mongo().to_dict()
        new_list.append(new_tracker_dict["location"])
        new_list.append(new_tracker_dict["time_mins"])
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
    return make_response(dumps(locations), 200)


if __name__ == '__main__':
    app.run()
