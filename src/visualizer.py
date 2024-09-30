# team_matching/visualizer.py

import itertools
import logging
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns

from .data_loader import Student


def visualize_preference_graph(students: List[Student], output_path: Path) -> None:
    """
    Visualizes the student preference graph, highlighting mutual preferences and loops.

    Args:
        students (List[Student]): List of all students.
        output_path (Path): Path to save the generated graph image.
    """
    try:
        logging.info("Creating preference graph.")
        G = nx.DiGraph()

        # Add nodes
        for student in students:
            G.add_node(student.email, name=student.name)

        # Create a mapping from email to student for quick lookup
        email_to_student = {student.email: student for student in students}

        # Add edges for preferred partners
        for student in students:
            preferred_email = student.preferred_partner_email.strip()
            if preferred_email and preferred_email in email_to_student:
                G.add_edge(student.email, preferred_email)
                logging.debug(f"Added edge from {student.email} to {preferred_email}")

        # Detect mutual preferences (bidirectional edges)
        mutual_preferences = [(u, v) for u, v in G.edges() if G.has_edge(v, u)]
        logging.debug(f"Detected {len(mutual_preferences)} mutual preferences.")

        # Detect preference loops (cycles)
        loops = list(nx.simple_cycles(G))
        logging.debug(f"Detected {len(loops)} preference loops.")

        # Visualization
        pos = nx.spring_layout(G)  # You can choose a layout that suits you

        plt.figure(figsize=(12, 8))

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')

        # Draw all edges
        nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrows=True, arrowstyle='->', alpha=0.5)

        # Highlight mutual preferences
        if mutual_preferences:
            nx.draw_networkx_edges(
                G, pos, edgelist=mutual_preferences, edge_color='green',
                arrows=True, arrowstyle='->', width=2, label='Mutual Preferences'
            )

        # Highlight loops
        for loop in loops:
            loop_edges = list(zip(loop, loop[1:] + [loop[0]]))
            nx.draw_networkx_edges(
                G, pos, edgelist=loop_edges, edge_color='red',
                arrows=True, arrowstyle='->', width=2, label='Preference Loops'
            )

        # Draw labels
        labels = {student.email: student.name for student in students}
        nx.draw_networkx_labels(G, pos, labels, font_size=10)

        plt.title('Student Preference Graph')
        plt.axis('off')
        plt.legend(scatterpoints=1)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logging.info(f"Preference graph saved to {output_path}")

    except Exception as e:
        logging.error(f"Failed to visualize preference graph: {e}", exc_info=True)
        raise


def visualize_group_meeting_preferences(groups: List[List[Student]], output_path: Path) -> None:
    """
    Visualizes group assignments with respect to meeting preferences.

    Args:
        groups (List[List[Student]]): List of groups, each containing a list of students.
        output_path (Path): Path to save the generated visualization.
    """
    try:
        logging.info("Creating group meeting preferences visualization.")
        plt.figure(figsize=(10, max(6, len(groups) * 1.5)))

        group_labels = []
        meeting_prefs = []
        for idx, group in enumerate(groups, start=1):
            group_num = f'Group {idx}'
            group_labels.extend([group_num] * len(group))
            meeting_prefs.extend([student.meeting_preference for student in group])

        data = {'Group': group_labels, 'Meeting Preference': meeting_prefs}
        df = pd.DataFrame(data)
        preference_order = ['In Person', 'Remote', 'No Preference']

        sns.countplot(
            y='Group',
            hue='Meeting Preference',
            data=df,
            palette='pastel',
            order=[f'Group {i}' for i in range(1, len(groups) + 1)],
            hue_order=preference_order
        )
        plt.title('Group Meeting Preferences')
        plt.xlabel('Number of Students')
        plt.ylabel('Group')
        plt.legend(title='Meeting Preference', loc='lower right')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logging.info(f"Group meeting preferences visualization saved to {output_path}")

    except Exception as e:
        logging.error(f"Failed to visualize group meeting preferences: {e}", exc_info=True)
        raise


def visualize_skill_balance(groups: List[List[Student]], output_path: Path) -> None:
    """
    Visualizes the skill balance across groups.

    Args:
        groups (List[List[Student]]): List of groups, each containing a list of students.
        output_path (Path): Path to save the generated bar chart.
    """
    try:
        logging.info("Creating skill balance visualization.")
        group_nums = []
        total_skills = []
        for idx, group in enumerate(groups, start=1):
            group_num = idx
            group_nums.append(group_num)
            total_skill = sum(student.total_skill_score() for student in group)
            total_skills.append(total_skill)
            logging.debug(f"Group {group_num}: Total Skill Score = {total_skill}")

        avg_skill = sum(total_skills) / len(total_skills) if total_skills else 0
        logging.debug(f"Average Skill Score across groups: {avg_skill}")

        plt.figure(figsize=(10, 6))
        plt.bar(group_nums, total_skills, color='skyblue')
        plt.axhline(y=avg_skill, color='red', linestyle='--', label='Average Skill')
        plt.xlabel('Group Number')
        plt.ylabel('Total Skill Score')
        plt.title('Skill Balance Across Groups')
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logging.info(f"Skill balance visualization saved to {output_path}")

    except Exception as e:
        logging.error(f"Failed to visualize skill balance: {e}", exc_info=True)
        raise


def visualize_availability(groups: List[List[Student]], output_path_prefix: Path) -> None:
    """
    Visualizes the availability overlap within each group.

    Args:
        groups (List[List[Student]]): List of groups, each containing a list of students.
        output_path_prefix (Path): Prefix path for saving availability visualizations.
    """
    try:
        logging.info("Creating availability visualizations for each group.")
        for idx, group in enumerate(groups, start=1):
            group_num = idx
            logging.debug(f"Processing availability for Group {group_num}")
            # Collect all possible times
            all_times = set(itertools.chain.from_iterable(student.available_times for student in group))
            all_times = sorted(all_times)
            logging.debug(f"All available times for Group {group_num}: {all_times}")

            # Create a DataFrame for availability
            data = []
            student_names = []
            for student in group:
                availability = [1 if time in student.available_times else 0 for time in all_times]
                data.append(availability)
                student_names.append(student.name)
                logging.debug(f"{student.name} availability: {availability}")
            df = pd.DataFrame(data, columns=all_times, index=student_names)

            # Plot heatmap
            plt.figure(figsize=(12, max(4, len(group) * 0.5 + 2)))
            sns.heatmap(df, annot=True, cmap='Greens', cbar=False, linewidths=0.5, fmt='d')
            plt.title(f'Group {group_num} Availability')
            plt.ylabel('Student')
            plt.xlabel('Available Times')
            plt.tight_layout()

            output_file = output_path_prefix.parent / f"{output_path_prefix.stem}_group_{group_num}.png"
            plt.savefig(output_file)
            plt.close()
            logging.info(f"Availability heatmap for Group {group_num} saved to {output_file}")

    except Exception as e:
        logging.error(f"Failed to visualize availability: {e}", exc_info=True)
        raise


def generate_group_summary(
    students: List[Student],
    groups: List[List[Student]],
    output_path: Path
) -> None:
    """
    Generates a CSV file summarizing key metrics for each group.

    Args:
        students (List[Student]): List of all students.
        groups (List[List[Student]]): List of groups, each containing a list of students.
        output_path (Path): Path to save the generated summary CSV.
    """
    try:
        logging.info("Generating group summary CSV.")
        summary_data = []
        email_to_student = {student.email: student for student in students}

        for idx, group in enumerate(groups, start=1):
            group_num = idx
            num_students = len(group)
            total_skill = sum(student.total_skill_score() for student in group)
            avg_skill = total_skill / num_students if num_students else 0
            meeting_prefs = [student.meeting_preference for student in group]
            num_in_person = meeting_prefs.count('In Person')
            num_remote = meeting_prefs.count('Remote')
            num_no_pref = meeting_prefs.count('No Preference')

            # Calculate preferred partners satisfied within the group
            prefs_satisfied = 0
            for student in group:
                preferred_email = student.preferred_partner_email.strip()
                if preferred_email and preferred_email in email_to_student:
                    preferred_student = email_to_student[preferred_email]
                    if preferred_student in group:
                        prefs_satisfied += 1
                        logging.debug(
                            f"Student {student.email} has preferred partner {preferred_email} in Group {group_num}"
                        )

            # Calculate availability overlap score
            times_sets = [set(student.available_times) for student in group]
            availability_overlap = set.intersection(*times_sets) if times_sets else set()
            availability_score = len(availability_overlap)
            logging.debug(
                f"Group {group_num}: Availability Overlap Score = {availability_score}"
            )

            summary_data.append({
                'Group Number': group_num,
                'Number of Students': num_students,
                'Total Skill Score': total_skill,
                'Average Skill Score': avg_skill,
                'In Person': num_in_person,
                'Remote': num_remote,
                'No Preference': num_no_pref,
                'Preferred Partners Satisfied': prefs_satisfied,
                'Availability Overlap Score': availability_score
            })

        df_summary = pd.DataFrame(summary_data)
        df_summary.to_csv(output_path, index=False)
        logging.info(f"Group summary CSV saved to {output_path}")

    except Exception as e:
        logging.error(f"Failed to generate group summary: {e}", exc_info=True)
        raise


def visualize_group_sizes(groups: List[List[Student]], output_path: Path) -> None:
    """
    Visualizes the distribution of group sizes.

    Args:
        groups (List[List[Student]]): List of groups, each containing a list of students.
        output_path (Path): Path to save the generated bar chart.
    """
    try:
        logging.info("Creating group size distribution visualization.")
        sizes = [len(group) for group in groups]
        size_counts = pd.Series(sizes).value_counts().sort_index()

        plt.figure(figsize=(6, 4))
        size_counts.plot(kind='bar', color='lightblue')
        plt.xlabel('Group Size')
        plt.ylabel('Number of Groups')
        plt.title('Group Size Distribution')
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logging.info(f"Group size distribution visualization saved to {output_path}")

    except Exception as e:
        logging.error(f"Failed to visualize group sizes: {e}", exc_info=True)
        raise


def visualize_groups_network(groups: List[List[Student]], output_path: Path) -> None:
    """
    Visualizes groups as clusters in a network graph.

    Args:
        groups (List[List[Student]]): List of groups, each containing a list of students.
        output_path (Path): Path to save the generated network graph image.
    """
    try:
        logging.info("Creating groups network visualization.")
        G = nx.Graph()
        group_colors = {}
        color_map = []

        # Assign a unique color to each group
        cmap = plt.get_cmap('tab20')
        for idx, group in enumerate(groups):
            group_num = idx + 1
            color = cmap(idx % 20)
            for student in group:
                G.add_node(student.email, name=student.name, group=group_num)
                group_colors[student.email] = color
                logging.debug(f"Assigned color to {student.email} in Group {group_num}")

        # Add edges between students in the same group
        for group in groups:
            for student1, student2 in itertools.combinations(group, 2):
                G.add_edge(student1.email, student2.email)
                logging.debug(f"Added edge between {student1.email} and {student2.email}")

        # Get positions
        pos = nx.spring_layout(G, seed=42)  # Fixed seed for reproducibility

        # Draw nodes with group-specific colors
        node_colors = [group_colors[node] for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_size=300, node_color=node_colors, alpha=0.8)

        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.5)

        # Draw labels
        labels = {node: G.nodes[node]['name'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        plt.title('Group Network Visualization')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logging.info(f"Groups network visualization saved to {output_path}")

    except Exception as e:
        logging.error(f"Failed to visualize groups network: {e}", exc_info=True)
        raise


def visualize_availability_heatmap(students: List[Student], output_path: Path) -> None:
    """
    Visualizes availability overlaps among all students.

    Args:
        students (List[Student]): List of all students.
        output_path (Path): Path to save the generated heatmap image.
    """
    try:
        logging.info("Creating availability overlap heatmap.")
        num_students = len(students)
        overlap_matrix = np.zeros((num_students, num_students), dtype=int)
        student_names = [student.name for student in students]

        for i in range(num_students):
            for j in range(num_students):
                if i <= j:  # Compute only upper triangle and mirror it
                    overlap = len(set(students[i].available_times) & set(students[j].available_times))
                    overlap_matrix[i, j] = overlap
                    overlap_matrix[j, i] = overlap
                    logging.debug(
                        f"Overlap between {students[i].name} and {students[j].name}: {overlap}"
                    )

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            overlap_matrix,
            xticklabels=student_names,
            yticklabels=student_names,
            cmap='Blues',
            annot=True,
            fmt='d'
        )
        plt.title('Availability Overlap Heatmap')
        plt.xlabel('Student')
        plt.ylabel('Student')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logging.info(f"Availability overlap heatmap saved to {output_path}")

    except Exception as e:
        logging.error(f"Failed to visualize availability heatmap: {e}", exc_info=True)
        raise
