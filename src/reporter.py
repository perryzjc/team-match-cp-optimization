# cs169a_team_match/team_matching/reporter.py

from typing import List
from pathlib import Path
import logging
import pandas as pd

from .data_loader import Student, detect_preference_loops


def generate_report(
        students: List[Student],
        groups: List[List[Student]],
        output_path: Path
) -> None:
    """
    Generates a statistical report of the group assignments and saves it to a file.

    Args:
        students (List[Student]): List of all students.
        groups (List[List[Student]]): List of groups, each containing a list of students.
        output_path (Path): Path to the output report file.
    """
    try:
        logging.info("Generating statistical report.")
        total_students = len(students)
        total_groups = len(groups)
        groups_of_3 = sum(1 for group in groups if len(group) == 3)
        groups_of_4 = sum(1 for group in groups if len(group) == 4)
        unassigned_students = [s for s in students if s.assigned_group is None]

        # Detect preference loops
        students_in_loops = detect_preference_loops(students)
        loop_report = _report_preference_loops(students_in_loops)

        # Compile report content
        report_content = [
            f"Total students processed: {total_students}",
            f"Number of groups formed: {total_groups}",
            f"Groups with 3 students: {groups_of_3}",
            f"Groups with 4 students: {groups_of_4}",
            f"Students in preference loops: {len(students_in_loops)}",
            loop_report,
            "Unassigned students:"
        ]

        for student in unassigned_students:
            report_content.append(f"- {student.name} ({student.email})")

        # Write report to file
        with output_path.open('w', encoding='utf-8') as report_file:
            report_file.write('\n'.join(report_content))

        logging.info(f"Report successfully written to {output_path}")

    except Exception as e:
        logging.error(f"Failed to generate report: {e}", exc_info=True)
        raise


def _report_preference_loops(loops: List[List[Student]]) -> str:
    """
    Generates a string report of the detected preference loops.

    Args:
        loops (List[List[Student]]): List of preference loops, each loop is a list of students.

    Returns:
        str: Formatted string detailing the preference loops.
    """
    if not loops:
        logging.debug("No preference loops detected.")
        return "No preference loops detected.\n"

    logging.debug(f"Detected {len(loops)} preference loop(s).")
    loop_reports = [f"No preference loops detected.\n"]
    loop_reports = []

    loop_reports.append(
        f"Detected {len(loops)} preference loop(s) involving {len({student for loop in loops for student in loop})} students:")
    for idx, loop in enumerate(loops, start=1):
        student_names = [student.name for student in loop]
        loop_str = " -> ".join(student_names) + f" -> {student_names[0]}"
        loop_reports.append(f"Loop {idx}: {loop_str}")
        logging.debug(f"Loop {idx}: {loop_str}")

    loop_reports.append("")  # Add an empty line for separation
    return '\n'.join(loop_reports)


def report_missing_students(
        missing_students_df: pd.DataFrame,
        output_path: Path = None
) -> None:
    """
    Reports missing students by logging their information and optionally writing to a CSV file.

    Args:
        missing_students_df (pd.DataFrame): DataFrame containing missing students' information.
        output_path (Path, optional): Path to save the missing students CSV. Defaults to None.
    """
    try:
        num_missing_students = len(missing_students_df)
        if num_missing_students == 0:
            logging.info("No missing students found.")
            return

        logging.warning(f"Number of missing students: {num_missing_students}")
        logging.warning("Missing students:")

        for _, student in missing_students_df.iterrows():
            logging.warning(f"- {student['Student Name']} ({student['Email']})")

        if output_path:
            missing_students_df.to_csv(output_path, index=False)
            logging.info(f"Missing students written to {output_path}")

    except Exception as e:
        logging.error(f"Failed to report missing students: {e}", exc_info=True)
        raise


def generate_output_csv(students, output_csv):
    import pandas as pd

    data = []
    for student in students:
        student_data = {
            'Group Number': student.assigned_group,
            'Email Address': student.email,
            'What is your name?': student.name,
            'What is your student ID?': student.student_id,
            'What is your github.com username?': student.github_username,
            # Add other fields as needed
        }
        data.append(student_data)
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
