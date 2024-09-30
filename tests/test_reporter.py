# tests/test_reporter.py

from src.reporter import generate_report
from src.data_loader import Student


def test_generate_report(tmpdir):
    student1 = Student('1', 'Alice', 'alice@berkeley.edu', 'alice', '', 3, 4, 5, 'In Person', {'Weekdays'}, '2PM Wednesday', '')
    student2 = Student('2', 'Bob', 'bob@berkeley.edu', 'bob', '', 4, 3, 5, 'In Person', {'Weekdays'}, '2PM Wednesday', '')
    student1.assigned_group = 1
    student2.assigned_group = 1
    students = [student1, student2]
    groups = [[student1, student2]]
    report_path = tmpdir.join("report.txt")
    generate_report(students, groups, report_path)
    with open(report_path, 'r') as f:
        report_content = f.read()
        assert "Total students processed: 2" in report_content
        assert "Number of groups formed: 1" in report_content
