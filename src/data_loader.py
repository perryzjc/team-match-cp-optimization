import pandas as pd
from typing import List
import networkx as nx


class Student:
    """
    A class to represent a student and their attributes.
    """

    def __init__(self, student_id, name, email, github_username, preferred_partner_email,
                 ruby_skill, html_css_skill, js_skill, meeting_preference, available_times,
                 section, constraints):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.github_username = github_username
        self.preferred_partner_email: str = preferred_partner_email if preferred_partner_email else ""
        self.ruby_skill = ruby_skill
        self.html_css_skill = html_css_skill
        self.js_skill = js_skill
        self.meeting_preference = meeting_preference
        self.available_times = available_times
        self.section = section
        self.constraints = constraints
        self.assigned_group = None

    def total_skill_score(self):
        return self.ruby_skill + self.html_css_skill + self.js_skill


def load_students_from_csv(file_path: str) -> List[Student]:
    """
    Loads student data from a CSV file and returns a list of Student objects.
    """
    df = pd.read_csv(file_path)
    students = []
    for _, row in df.iterrows():
        student = Student(
            student_id=row['What is your student ID?'],
            name=row['What is your name?'],
            email=row['Email Address'],
            github_username=row['What is your github.com username?'],
            preferred_partner_email=str(row.get(
                'If you have someone in mind, write their full berkeley email address below. Otherwise, you can leave this question blank.',
                '')),
            ruby_skill=int(row['How strong are your Ruby skills?']),
            html_css_skill=int(row['How strong are your HTML/CSS skills?']),
            js_skill=int(row['How strong are your JavaScript skills?']),
            meeting_preference=row['Do you generally prefer to meet in-person, or remote?'],
            available_times=set(map(str.strip, str(row['What times are generally available to meet?']).split(','))),
            section=str(row['What section have you been attending / planning to attend?']),
            constraints=row['Anything else we should know?']
        )
        students.append(student)
    return students


def detect_preference_loops(students: List[Student]) -> List[List[Student]]:
    """
    Detects preference loops among students.

    Returns:
        A list of lists, where each sublist represents a loop of students.
    """
    email_to_student = {student.email: student for student in students}
    G = nx.DiGraph()
    for student in students:
        G.add_node(student.email)
        if student.preferred_partner_email:
            preferred_email = student.preferred_partner_email.strip()
            if preferred_email in email_to_student:
                G.add_edge(student.email, preferred_email)

    cycles = list(nx.simple_cycles(G))
    loops = []
    for cycle in cycles:
        loop_students = [email_to_student[email] for email in cycle]
        loops.append(loop_students)
    return loops


def load_roster_from_csv(roster_csv):
    """
    Loads the roster CSV into a DataFrame.
    """
    roster_df = pd.read_csv(roster_csv)
    return roster_df


def identify_missing_students(roster_df, students):
    """
    Identifies students who are in the roster but not in the input CSV.

    Returns a DataFrame of missing students.
    """
    roster_emails = roster_df['Email'].str.strip().tolist()
    input_emails = [student.email.strip() for student in students]
    missing_emails = set(roster_emails) - set(input_emails)
    missing_students_df = roster_df[roster_df['Email'].str.strip().isin(missing_emails)]
    return missing_students_df


def add_missing_students(students, missing_students_df):
    """
    Adds missing students to the students list with default values.
    """
    for index, row in missing_students_df.iterrows():
        student = Student(
            student_id=str(row['Student SIS ID']),
            name=row['Student Name'],
            email=row['Email'],
            github_username=row.get('GitHub Username', ''),
            preferred_partner_email='',
            ruby_skill=2,
            html_css_skill=2,
            js_skill=2,
            meeting_preference='No Preference',
            available_times=set(),
            section=row.get('Section', ''),
            constraints=''
        )
        students.append(student)

