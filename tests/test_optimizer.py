# tests/test_optimizer.py

from src.optimizer import assign_groups
from src.data_loader import Student

# tests/test_optimizer.py


def test_assign_groups_with_constraints():
    # Create mock students with various preferences and skills
    students = []
    student1 = Student('1', 'Alice', 'alice@berkeley.edu', 'alice', 'bob@berkeley.edu', 5, 5, 5, 'In Person', {'Weekdays'}, '', '')
    student2 = Student('2', 'Bob', 'bob@berkeley.edu', 'bob', 'alice@berkeley.edu', 5, 5, 5, 'In Person', {'Weekdays'}, '', '')
    student3 = Student('3', 'Charlie', 'charlie@berkeley.edu', 'charlie', '', 1, 1, 1, 'Remote', {'Weekends'}, '', '')
    student4 = Student('4', 'David', 'david@berkeley.edu', 'david', '', 1, 1, 1, 'Remote', {'Weekends'}, '', '')
    student5 = Student('5', 'Eve', 'eve@berkeley.edu', 'eve', '', 3, 3, 3, 'No Preference', {'Weekdays', 'Weekends'}, '', '')
    student6 = Student('6', 'Frank', 'frank@berkeley.edu', 'frank', '', 4, 4, 4, 'In Person', {'Weekdays'}, '', '')
    student7 = Student('7', 'Grace', 'grace@berkeley.edu', 'grace', '', 2, 2, 2, 'Remote', {'Weekdays', 'Weekends'}, '', '')
    students.extend([student1, student2, student3, student4, student5, student6, student7])

    groups = assign_groups(students)

    # Check that Alice and Bob are in the same group
    assert student1.assigned_group == student2.assigned_group

    # Check that students with conflicting meeting preferences are not grouped together unless one has 'No Preference'
    for group in groups:
        meeting_prefs = set(s.meeting_preference for s in group)
        if 'In Person' in meeting_prefs and 'Remote' in meeting_prefs:
            # Only acceptable if one has 'No Preference'
            for s in group:
                assert s.meeting_preference == 'No Preference'

    # Check group sizes
    for group in groups:
        assert 3 <= len(group) <= 4

    # Check skill balance
    total_skills = [sum(s.total_skill_score() for s in group) for group in groups]
    skill_diff = max(total_skills) - min(total_skills)
    assert skill_diff <= 25  # Adjust based on acceptable difference


def test_assign_groups_prioritize_group_size_4():
    # Create mock students
    students = []
    total_students = 15  # For example, 15 students
    for i in range(total_students):
        meeting_pref = 'No Preference'
        student = Student(
            student_id=str(i),
            name=f'Student{i}',
            email=f'student{i}@berkeley.edu',
            github_username=f'student{i}',
            preferred_partner_email='',
            ruby_skill=3,
            html_css_skill=3,
            js_skill=3,
            meeting_preference=meeting_pref,
            available_times={'Weekdays'},
            section='',
            constraints=''
        )
        students.append(student)

    groups = assign_groups(students)

    # Check that the number of groups of size 4 is maximized
    groups_of_4 = [group for group in groups if len(group) == 4]
    assert len(groups_of_4) == 15 // 4  # Should be as many groups of size 4 as possible

    # Print group assignments
    for idx, group in enumerate(groups):
        print(f"Group {idx + 1} (Size {len(group)}): {[student.name for student in group]}")


def test_assign_groups_with_availability_and_section_conflicts():
    # Create mock students
    students = []
    student1 = Student('1', 'Alice', 'alice@berkeley.edu', 'alice', 'bob@berkeley.edu', 5, 5, 5, 'In Person', {'Monday', 'Wednesday'}, 'Section A', '')
    student2 = Student('2', 'Bob', 'bob@berkeley.edu', 'bob', 'alice@berkeley.edu', 5, 5, 5, 'In Person', {'Monday', 'Wednesday'}, 'Section A', '')
    student3 = Student('3', 'Charlie', 'charlie@berkeley.edu', 'charlie', '', 1, 1, 1, 'Remote', {'Tuesday', 'Thursday'}, 'Section B', '')
    student4 = Student('4', 'David', 'david@berkeley.edu', 'david', '', 1, 1, 1, 'Remote', {'Tuesday', 'Thursday'}, 'Section B', '')
    student5 = Student('5', 'Eve', 'eve@berkeley.edu', 'eve', '', 3, 3, 3, 'No Preference', {'Monday', 'Tuesday', 'Wednesday', 'Thursday'}, 'Section C', '')
    students.extend([student1, student2, student3, student4, student5])

    groups = assign_groups(students)

    # Check that Alice and Bob are in the same group
    assert student1.assigned_group == student2.assigned_group

    # Check that students with no overlapping available times are not grouped together
    for group in groups:
        times_sets = [student.available_times for student in group]
        availability_overlap = set.intersection(*times_sets) if times_sets else set()
        assert availability_overlap, f"Group {group} has no overlapping available times."

    # Check group sizes
    for group in groups:
        assert 3 <= len(group) <= 4

    # Print group assignments
    for idx, group in enumerate(groups):
        print(f"Group {idx + 1}: {[student.name for student in group]}")


def test_group_minimum_total_skill():
    # Create mock students with varying skills
    students = [
        Student('1', 'Alice', 'alice@example.com', 'alice', '', 5, 5, 5, 'No Preference', set(), '', ''),
        Student('2', 'Bob', 'bob@example.com', 'bob', '', 4, 4, 4, 'No Preference', set(), '', ''),
        Student('3', 'Charlie', 'charlie@example.com', 'charlie', '', 3, 3, 3, 'No Preference', set(), '', ''),
        Student('4', 'David', 'david@example.com', 'david', '', 2, 2, 2, 'No Preference', set(), '', ''),
        Student('5', 'Eve', 'eve@example.com', 'eve', '', 1, 1, 1, 'No Preference', set(), '', ''),
    ]

    groups = assign_groups(students)

    # Check that the total skill score for each group is at least group_size * 4
    for group in groups:
        total_skill = sum(student.total_skill_score() for student in group)
        group_size = len(group)
        assert total_skill >= group_size * 4, f"Group total skill {total_skill} is less than {group_size * 4}"
