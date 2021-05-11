import datetime
import random
import json

my_list = []
category = ["hanging out", "taking quiz", "studying",
            "doing assignments", "working on project"]
location = ["home", "library", "science building", "work", "park"]

date_today = "2021-01-01"
base = datetime.datetime.strptime(date_today, '%Y-%m-%d')
date_list = [base + datetime.timedelta(days=x) for x in range(100)]
date_list = [i.isoformat() for i in date_list]

for i in range(100):
    new_list = []
    new_list.append(random.randint(20, 200))
    new_list.append(date_list[i])
    new_list.append(random.choice(category))
    new_list.append(random.choice(location))
    my_list.append(new_list)

nosql_list = []

for i in range(len(my_list)):
    new_dict = {}
    new_dict["time_mins"] = my_list[i][0]
    new_dict["date_tracked"] = my_list[i][1]
    new_dict["category"] = my_list[i][2]
    new_dict["location"] = my_list[i][3]
    nosql_list.append(new_dict)

# for i in nosql_list:
#     print(i)
# print(nosql_list)
nosql_json = json.dumps(nosql_list)
with open('nosql.json', 'w') as out:
    json.dump(nosql_list, out)

sql_list = nosql_list
for i in sql_list:
    i["location_id"] = i.pop("location")
    location_index = location.index(i["location_id"]) + 1
    i["location_id"] = location_index

# for i in sql_list:
#     print(i)
# print(sql_list)
sql_json = json.dumps(sql_list)

print(nosql_json, "\n")
print(sql_json)

with open('sql.json', 'w') as out:
    json.dump(sql_list, out)
