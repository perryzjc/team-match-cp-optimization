#!/usr/bin/env python3
"""
Entry point for running the team matching process.
"""

import argparse
import logging
from pathlib import Path
import sys

import pandas as pd

from src.data_loader import (
    load_students_from_csv,
    load_roster_from_csv,
    identify_missing_students,
    add_missing_students
)
from src.optimizer import assign_groups
from src.reporter import generate_report, report_missing_students, generate_output_csv
from src.visualizer import (
    visualize_preference_graph,
    visualize_group_meeting_preferences,
    visualize_skill_balance,
    visualize_group_sizes,
    visualize_groups_network,
    visualize_availability_heatmap,
    visualize_availability
)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configures the logging settings.
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run the team matching process."
    )
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Path to the input CSV file containing student data."
    )
    parser.add_argument(
        "roster_csv",
        type=Path,
        help="Path to the roster CSV file."
    )
    parser.add_argument(
        "output_path",
        type=Path,
        help="Base directory path where all outputs (output CSV, reports, and graphs) will be saved."
    )
    parser.add_argument(
        "--include-missing",
        action="store_true",
        help="Include missing students in the optimization process."
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)."
    )
    return parser.parse_args()


def create_directories(output_path: Path) -> (Path, Path, Path):
    """
    Creates necessary directories for saving output CSV, reports, and graphs.
    """
    output_csv_path = output_path / 'output.csv'
    reports_folder = output_path / 'reports'
    graphs_folder = output_path / 'graphs'
    availability_folder = graphs_folder / 'availability'

    for folder in [reports_folder, graphs_folder, availability_folder]:
        folder.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Created directory: {folder}")

    return output_csv_path, reports_folder, graphs_folder, availability_folder


def main(
    input_csv: Path,
    roster_csv: Path,
    output_path: Path,
    include_missing_students: bool
) -> None:
    """
    Main function to orchestrate the team matching process.
    """
    try:
        logging.info("Creating directories for outputs.")
        output_csv_path, reports_path, graphs_path, availability_folder = create_directories(output_path)

        preference_graph_path = graphs_path / 'preference_graph.png'

        logging.info("Loading students from input CSV.")
        students = load_students_from_csv(input_csv)

        logging.info("Loading roster from roster CSV.")
        roster_df = load_roster_from_csv(roster_csv)

        logging.info("Identifying missing students.")
        missing_students_df = identify_missing_students(roster_df, students)

        if not missing_students_df.empty:
            logging.info("Reporting missing students.")
            report_missing_students(missing_students_df, reports_path / 'missing_students_report.txt')
        else:
            logging.info("No missing students found.")

        if include_missing_students:
            logging.info("Adding missing students to the student list.")
            add_missing_students(students, missing_students_df)

        logging.info("Assigning groups.")
        groups = assign_groups(students)

        logging.info("Generating output CSV.")
        generate_output_csv(students, output_csv_path)

        logging.info("Generating report.")
        generate_report(students, groups, reports_path / 'team_report.txt')

        logging.info("Generating group summary.")
        group_summary_path = reports_path / 'group_summary.csv'
        generate_group_summary(groups, group_summary_path)

        logging.info("Generating visualizations.")
        visualize_preference_graph(students, preference_graph_path)
        visualize_group_meeting_preferences(groups, graphs_path / 'group_meeting_preferences.png')
        visualize_skill_balance(groups, graphs_path / 'skill_balance.png')
        visualize_group_sizes(groups, graphs_path / 'group_size_distribution.png')
        visualize_groups_network(groups, graphs_path / 'group_network.png')

        logging.info("Generating availability visualizations.")
        visualize_availability_heatmap(students, availability_folder / 'availability_heatmap.png')
        visualize_availability(groups, availability_folder / 'availability_groups')

        logging.info("Team matching process completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)


def generate_group_summary(groups, output_path: Path) -> None:
    """
    Generates a summary of groups and saves it to a CSV file.
    """
    data = []
    for i, group in enumerate(groups):
        group_data = {
            'Group Number': i + 1,
            'Members': ', '.join([student.name for student in group]),
            # Add other summary fields as needed
        }
        data.append(group_data)
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    logging.debug(f"Group summary saved to {output_path}")


if __name__ == '__main__':
    args = parse_arguments()
    setup_logging(args.log_level)
    main(
        input_csv=args.input_csv,
        roster_csv=args.roster_csv,
        output_path=args.output_path,
        include_missing_students=args.include_missing
    )
