#!/usr/bin/env python

import json, time, os
from urllib.request import urlopen

CAB_LINK = "https://cab.brown.edu/asoc-api/?output=json&page=asoc.rjs&route=search&term=999999"
WAIT_SEC = 30
MAX_TIME = 10000

def load_page():
	page_html = urlopen(CAB_LINK).read()
	page_json = json.loads(page_html)
	return page_json

def find_course(course_code):
	global course
	page_json = load_page()
	total_courses = page_json["numCourses"]
	# Check all courses
	for i in range (total_courses):
		course = page_json["courses"][i]
		# Check for crn:
		if course_code[:3] in "CRN":
			section = crn_to_section(course, course_code[4:])
			if section is not None:
				course = section
				return True
		# Otherwise, check course code:
		elif course["code"] == course_code: return True
	return False

def crn_to_section(course, crn):
	for j in range(len(course["sections"])):
		section = course["sections"][j]
		if section["crn"] == crn: return section
	return None

def wait_for_open(course_code):
	for i in range(MAX_TIME):
		find_course(course_code)
		if course["warn"] is False:
			return "course_open"
		i += WAIT_SEC
		print(i)
		time.sleep(WAIT_SEC)
	return "time_exceeded"

# boilerplate
#if __name__ == '__main__':
#	main()