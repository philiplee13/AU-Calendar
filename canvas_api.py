import os
import requests
import json

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
        course_name.append(assignment["name"])
        assignment_due_date.append(assignment["due_at"])
        course_ids.append(assignment["course_id"])

    # pagination - use response.links to check "next" for url
    while response.links["current"]["url"] != response.links["last"]["url"]:
        response = requests.get(response.links["next"]["url"], headers = headers, params={"order_by" : "due_at"})
        next_group = response.json()
        for next_item in next_group:
            course_name.append(next_item["name"])
            assignment_due_date.append(next_item["due_at"])
            course_ids.append(next_item["course_id"])

# for loop all lists - and extract matching key values from course_ids
for name, due_date, course_id in zip(course_name,assignment_due_date,course_ids):
    for key, value in course_dict.items():
        if course_id == int(key):
            print(name, due_date, value)

print(final_dates)
# print(response.status_code)