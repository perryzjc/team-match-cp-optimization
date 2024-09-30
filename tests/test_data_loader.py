# tests/test_data_loader.py

import pytest
from src.data_loader import load_students_from_csv, Student
from io import StringIO


def test_load_students_from_csv():
    csv_data = StringIO("""
"Timestamp","Email Address","What is your name?","What is your student ID?","What is your github.com username?","Would you like to be partnered with a specific person in CS169A?","If you have someone in mind, write their full name below. Otherwise, you can leave this question blank.","If you have someone in mind, write their full berkeley email address below. Otherwise, you can leave this question blank.","How strong are your Ruby skills?","How strong are your HTML/CSS skills?","How strong are your JavaScript skills?","Do you generally prefer to meet in-person, or remote?","What times are generally available to meet?","What section have you been attending / planning to attend?","Anything else we should know?"
"2024-09-26 09:00:00","student1@mockuniversity.edu","Alex Green","111111111","alexg123","Yes","Taylor White","taylorw@mockuniversity.edu","3","4","2","In Person","Weekdays, Evenings","3PM Tuesday","I'm open to any partner but prefer someone with strong JavaScript skills."
"2024-09-26 09:05:00","student2@mockuniversity.edu","Taylor White","222222222","taylorw456","Yes","Alex Green","alexg123@mockuniversity.edu","4","3","5","Remote","Weekdays, Mornings","11AM Tuesday","I am flexible with times but prefer early morning meetings."
"2024-09-26 09:10:00","student3@mockuniversity.edu","Jordan Lee","333333333","jordanlee789","No","N/A","N/A","2","5","4","No Preference","Weekends, Evenings","1PM Tuesday","I prefer to work with someone with strong HTML/CSS skills."
"2024-09-26 09:15:00","student4@mockuniversity.edu","Morgan Black","444444444","morganb101","Yes","Jordan Lee","jordanlee789@mockuniversity.edu","5","2","3","In Person","Weekdays, Mid-day","2PM Wednesday","I can meet in person but prefer to have at least one remote meeting per week."
""")

    students = load_students_from_csv(csv_data)
    assert len(students) == 4
    assert students[0].name == 'Alex Green'
    assert students[1].preferred_partner_email == 'alexg123@mockuniversity.edu'
