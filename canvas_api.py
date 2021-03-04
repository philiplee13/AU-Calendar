import os
import requests
import json
import datetime
from datetime import timedelta
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event

canvas_token = os.getenv('CANVAS_API')
headers = {'Authorization' : f'Bearer {canvas_token}'}

# all courses via GET
url = "https://auburn.instructure.com/api/v1/courses"
response = requests.get(url,headers = headers)
data = response.json()

# declare dictionaries / lists
course_dict = {}
course_name = []
assignment_due_date = []
course_ids = []
final_dates = []

# create dictionary of course IDs and course names
for course in data:
    course_dict.update({course["id"] : course["name"]})
print(course_dict)


# list out all assignments for each course via GET
for course_id in course_dict.keys():
    # print(name)
    # print('\n')
    # print(course_id)
    # print(course_id,name)
    url = f"https://auburn.instructure.com/api/v1/courses/{course_id}/assignments"
    response = requests.get(url,headers = headers, params={"order_by" : "due_at"})
    assignments = response.json()
    for assignment in assignments:
        # modify due_date (convert to datetime object, subtract 1 day, and reformat)
        assignment_date = datetime.datetime.strptime(assignment["due_at"],"%Y-%m-%dT%H:%M:%SZ")
        assignment_date = assignment_date.date() - datetime.timedelta(days=1)
        assignment_date = datetime.datetime.strftime(assignment_date,"%Y-%m-%d")
        # append to list
        term_start_date = "2021-03-03"
        if str(assignment_date) >= term_start_date:
            course_name.append(assignment["name"])
            assignment_due_date.append(assignment_date)
            course_ids.append(assignment["course_id"])

    # pagination - use response.links to check "next" for url
    while response.links["current"]["url"] != response.links["last"]["url"]:
        response = requests.get(response.links["next"]["url"], headers = headers, params={"order_by" : "due_at"})
        next_group = response.json()
        for next_item in next_group:
            # modify due_date (convert to datetime object, subtract 1 day, and reformat)
            next_assignment_date = datetime.datetime.strptime(next_item["due_at"],"%Y-%m-%dT%H:%M:%SZ")
            next_assignment_date = next_assignment_date.date() - datetime.timedelta(days=1)
            next_assignment_date = datetime.datetime.strftime(next_assignment_date,"%Y-%m-%d")

            # assignment due date needs to be later than term start date
            # append to list
            if str(next_assignment_date) >= term_start_date:
                course_name.append(next_item["name"])
                assignment_due_date.append(next_assignment_date)
                course_ids.append(next_item["course_id"])

# google calendar credentials
user_email = "philipyjlee95@gmail.com"
google_cred = os.getenv(GOOGLE_CALENDAR_CRED)
gc = GoogleCalendar(credentials_path = google_cred)
calendar = GoogleCalendar(user_email)
# for loop all lists - and extract matching key values from course_ids
for name, due_date, course_id in zip(course_name,assignment_due_date,course_ids):
    for key, value in course_dict.items():
        if course_id == int(key):
            # print(due_date.split("-")[0])
            # print(due_date.split("-")[1])
            # print(due_date.split("-")[2])
            final_name = name + " " + value
            start = datetime.datetime(int(due_date.split("-")[0]),int(due_date.split("-")[1]),int(due_date.split("-")[2]))
            event = Event(
                final_name,
                start = start,
                minutes_before_pop_reminder = 30
            )
            calendar.add_event(event)
