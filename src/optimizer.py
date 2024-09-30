# team_matching/optimizer.py

from ortools.sat.python import cp_model
from typing import List, Dict
from .data_loader import Student
import math



# Weights for objective components
WEIGHT_GROUP_SIZE = 10000000
WEIGHT_SKILL_DIFF = 10
WEIGHT_PREFERENCE = 1000


def assign_groups(
    students: List[Student],
    group_size_min: int = 3,
    group_size_max: int = 4,
) -> List[List[Student]]:
    """
    Assign students to groups while satisfying various constraints and optimizing objectives.

    Args:
        students (List[Student]): List of Student objects.
        group_size_min (int): Minimum group size.
        group_size_max (int): Maximum group size.

    Returns:
        List[List[Student]]: A list of groups, each group is a list of Student objects.
    """
    num_students = len(students)

    # Calculate the maximum number of groups needed
    max_groups = math.ceil(num_students / group_size_min)

    # Calculate the minimum number of groups that cannot be of size 4
    num_full_groups = num_students // 4
    remaining_students = num_students % 4

    if remaining_students == 0:
        min_non_4_groups = 0
    elif remaining_students >= group_size_min:
        min_non_4_groups = 1  # One group with size equal to remaining_students
    else:
        # Adjust groups to have sizes of 3 and 4 to accommodate all students
        min_non_4_groups = group_size_min - remaining_students

    model = cp_model.CpModel()

    # -------------------------------
    # Variables
    # -------------------------------

    # Group assignment variables: assigned_group[i] = g means student i is assigned to group g
    assigned_group = {
        i: model.NewIntVar(0, max_groups - 1, f'assigned_group_{i}')
        for i in range(num_students)
    }

    # Boolean variables indicating if student i is in group g
    is_in_group = {
        (i, g): model.NewBoolVar(f'is_in_group_{i}_{g}')
        for i in range(num_students)
        for g in range(max_groups)
    }

    # Link is_in_group variables with assigned_group variables
    for i in range(num_students):
        for g in range(max_groups):
            model.Add(assigned_group[i] == g).OnlyEnforceIf(is_in_group[i, g])
            model.Add(assigned_group[i] != g).OnlyEnforceIf(is_in_group[i, g].Not())

    # Identify missing students (those with empty GitHub usernames)
    missing_student_indices = [
        i for i, student in enumerate(students) if not student.github_username.strip()
    ]

    # Variables for counting missing students in each group
    missing_students_in_group = {
        g: model.NewIntVar(0, len(missing_student_indices), f'missing_students_in_group_{g}')
        for g in range(max_groups)
    }

    # Variables indicating group sizes
    group_sizes = {
        g: model.NewIntVar(0, group_size_max, f'group_size_{g}')
        for g in range(max_groups)
    }

    # Variables indicating if a group is used
    group_is_used = {
        g: model.NewBoolVar(f'group_is_used_{g}')
        for g in range(max_groups)
    }

    # Boolean variables indicating if group size is 4 or not 4
    group_size_is_4 = {
        g: model.NewBoolVar(f'group_size_is_4_{g}')
        for g in range(max_groups)
    }
    group_size_is_not_4 = {
        g: model.NewBoolVar(f'group_size_is_not_4_{g}')
        for g in range(max_groups)
    }

    # -------------------------------
    # Constraints
    # -------------------------------

    # Group size constraints
    add_group_size_constraints(
        model, num_students, max_groups, group_size_min, group_size_max,
        group_sizes, group_is_used, group_size_is_4, group_size_is_not_4, is_in_group,
        min_non_4_groups
    )

    # Preferred Partner Constraints
    add_preferred_partner_constraints(model, students, assigned_group)

    # Missing Students Constraint: No more than 1 missing student per group
    add_missing_students_constraints(
        model, max_groups, missing_student_indices, missing_students_in_group, is_in_group
    )

    # Conflict Penalties
    conflict_penalties = []
    total_conflict_penalty = model.NewIntVar(0, num_students * 1000, 'total_conflict_penalty')

    # Available Times Penalties (High Weight)
    add_available_times_penalties(
        model, students, num_students, max_groups, conflict_penalties, is_in_group
    )

    # Meeting Preference Penalties
    add_meeting_preference_penalties(
        model, students, num_students, max_groups, conflict_penalties, is_in_group
    )

    # Section Penalties
    add_section_penalties(
        model, students, num_students, max_groups, conflict_penalties, is_in_group
    )

    # Calculate total conflict penalty
    calculate_total_conflict_penalty(model, conflict_penalties, total_conflict_penalty)

    # Skill Balancing and Minimum Skill Constraint
    skill_diff = add_skill_constraints(
        model, students, num_students, max_groups, group_sizes, group_is_used, is_in_group
    )

    # Preference Satisfaction Score
    preference_score = calculate_preference_score(
        model, students, assigned_group
    )

    # Total number of groups of size 4
    total_groups_of_4 = model.NewIntVar(0, max_groups, 'total_groups_of_4')
    model.Add(total_groups_of_4 == sum(group_size_is_4[g] for g in range(max_groups)))

    # -------------------------------
    # Objective Function
    # -------------------------------

    # Weights for objective components
    WEIGHT_GROUP_SIZE = 100_000_000
    WEIGHT_SKILL_DIFF = 10
    WEIGHT_PREFERENCE = 3_000

    model.Maximize(
        total_groups_of_4 * WEIGHT_GROUP_SIZE
        + preference_score * WEIGHT_PREFERENCE
        - total_conflict_penalty
        - skill_diff * WEIGHT_SKILL_DIFF
    )

    # -------------------------------
    # Solve the model
    # -------------------------------

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 6
    solver.parameters.max_time_in_seconds = 60 * 15 * 4 * 8 # 60 * 15 * 4 * 8  # 8 hours
    solver.parameters.log_search_progress = True
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        groups = [[] for _ in range(max_groups)]
        for i in range(num_students):
            g = solver.Value(assigned_group[i])
            students[i].assigned_group = g + 1  # Group numbers start from 1
            groups[g].append(students[i])
        # Remove empty groups
        groups = [group for group in groups if len(group) > 0]
        # Renumber groups to be consecutive
        renumber_groups(students)
        return groups
    else:
        print("No solution found.")
        return []


# -------------------------------
# Helper Functions
# -------------------------------

def add_group_size_constraints(
    model: cp_model.CpModel,
    num_students: int,
    max_groups: int,
    group_size_min: int,
    group_size_max: int,
    group_sizes: Dict[int, cp_model.IntVar],
    group_is_used: Dict[int, cp_model.BoolVarT],
    group_size_is_4: Dict[int, cp_model.BoolVarT],
    group_size_is_not_4: Dict[int, cp_model.BoolVarT],
    is_in_group: Dict[tuple, cp_model.BoolVarT],
    min_non_4_groups: int,
):
    """
    Add constraints related to group sizes.
    """
    for g in range(max_groups):
        # Define group size
        model.Add(
            group_sizes[g] == sum(is_in_group[i, g] for i in range(num_students))
        )

        # A group is used if its size is at least the minimum group size
        model.Add(group_sizes[g] >= group_size_min).OnlyEnforceIf(group_is_used[g])
        model.Add(group_sizes[g] < group_size_min).OnlyEnforceIf(group_is_used[g].Not())

        # Enforce group size limits when the group is used
        model.Add(group_sizes[g] <= group_size_max).OnlyEnforceIf(group_is_used[g])

        # Ensure that if a group is not used, its size is zero
        model.Add(group_sizes[g] == 0).OnlyEnforceIf(group_is_used[g].Not())

        # Boolean variables for group size being 4 or not 4
        model.Add(group_sizes[g] == 4).OnlyEnforceIf(group_size_is_4[g])
        model.Add(group_sizes[g] != 4).OnlyEnforceIf(group_size_is_4[g].Not())

        model.Add(group_sizes[g] != 4).OnlyEnforceIf(group_size_is_not_4[g])
        model.Add(group_sizes[g] == 4).OnlyEnforceIf(group_size_is_not_4[g].Not())

    # # Limit the total number of groups not of size 4
    # total_groups_not_of_4 = model.NewIntVar(0, max_groups, 'total_groups_not_of_4')
    # model.Add(
    #     total_groups_not_of_4 == sum(group_size_is_not_4[g] for g in range(max_groups))
    # )
    # model.Add(total_groups_not_of_4 <= min_non_4_groups)


def add_preferred_partner_constraints(
    model: cp_model.CpModel,
    students: List[Student],
    assigned_group: Dict[int, cp_model.IntVar],
):
    """
    Add constraints to ensure preferred partners are assigned to the same group.
    """
    email_to_index = {
        student.email.strip(): idx for idx, student in enumerate(students)
    }

    for i, student in enumerate(students):
        preferred_email = student.preferred_partner_email.strip()
        if preferred_email and preferred_email in email_to_index:
            j = email_to_index[preferred_email]
            # Both students i and j should be in the same group
            model.Add(assigned_group[i] == assigned_group[j])


def add_missing_students_constraints(
    model: cp_model.CpModel,
    max_groups: int,
    missing_student_indices: List[int],
    missing_students_in_group: Dict[int, cp_model.IntVar],
    is_in_group: Dict[tuple, cp_model.BoolVarT],
):
    """
    Add constraints to limit the number of missing students per group.
    """
    for g in range(max_groups):
        model.Add(
            missing_students_in_group[g] == sum(
                is_in_group[i, g] for i in missing_student_indices
            )
        )
        # Constraint: No more than 1 missing student per group
        model.Add(missing_students_in_group[g] <= 1)


def add_available_times_penalties(
    model: cp_model.CpModel,
    students: List[Student],
    num_students: int,
    max_groups: int,
    conflict_penalties: List[tuple],
    is_in_group: Dict[tuple, cp_model.BoolVarT],
):
    """
    Add penalties for grouping students with no overlapping available times.
    """
    WEIGHT_AVAILABILITY_CONFLICT = 1300  # High weight to discourage conflicts

    for i in range(num_students):
        for j in range(i + 1, num_students):
            overlap = students[i].available_times & students[j].available_times
            # Skip pairs where availability is unknown (empty)
            if not students[i].available_times or not students[j].available_times:
                continue  # Do not penalize pairs where availability is unknown
            if not overlap:
                for g in range(max_groups):
                    both_in_group = model.NewBoolVar(f'avail_conflict_{i}_{j}_{g}')
                    model.AddBoolAnd([is_in_group[i, g], is_in_group[j, g]]).OnlyEnforceIf(
                        both_in_group
                    )
                    model.AddBoolOr(
                        [is_in_group[i, g].Not(), is_in_group[j, g].Not()]
                    ).OnlyEnforceIf(both_in_group.Not())
                    conflict_penalties.append((both_in_group, WEIGHT_AVAILABILITY_CONFLICT))


def add_meeting_preference_penalties(
    model: cp_model.CpModel,
    students: List[Student],
    num_students: int,
    max_groups: int,
    conflict_penalties: List[tuple],
    is_in_group: Dict[tuple, cp_model.BoolVarT],
):
    """
    Add penalties for grouping students with conflicting meeting preferences.
    """
    WEIGHT_MEETING_PREFERENCE_CONFLICT = 1_000

    for i in range(num_students):
        for j in range(i + 1, num_students):
            if (
                students[i].meeting_preference != 'No Preference'
                and students[j].meeting_preference != 'No Preference'
                and students[i].meeting_preference != students[j].meeting_preference
            ):
                for g in range(max_groups):
                    both_in_group = model.NewBoolVar(f'meeting_conflict_{i}_{j}_{g}')
                    model.AddBoolAnd([is_in_group[i, g], is_in_group[j, g]]).OnlyEnforceIf(
                        both_in_group
                    )
                    model.AddBoolOr(
                        [is_in_group[i, g].Not(), is_in_group[j, g].Not()]
                    ).OnlyEnforceIf(both_in_group.Not())
                    conflict_penalties.append((both_in_group, WEIGHT_MEETING_PREFERENCE_CONFLICT))


def add_section_penalties(
    model: cp_model.CpModel,
    students: List[Student],
    num_students: int,
    max_groups: int,
    conflict_penalties: List[tuple],
    is_in_group: Dict[tuple, cp_model.BoolVarT],
):
    """
    Add penalties for grouping students from different sections.
    """
    WEIGHT_SECTION_CONFLICT = 50

    for i in range(num_students):
        for j in range(i + 1, num_students):
            if (
                students[i].section.strip()
                and students[j].section.strip()
                and students[i].section.strip() != students[j].section.strip()
            ):
                for g in range(max_groups):
                    both_in_group = model.NewBoolVar(f'section_conflict_{i}_{j}_{g}')
                    model.AddBoolAnd([is_in_group[i, g], is_in_group[j, g]]).OnlyEnforceIf(
                        both_in_group
                    )
                    model.AddBoolOr(
                        [is_in_group[i, g].Not(), is_in_group[j, g].Not()]
                    ).OnlyEnforceIf(both_in_group.Not())
                    conflict_penalties.append((both_in_group, WEIGHT_SECTION_CONFLICT))


def calculate_total_conflict_penalty(
    model: cp_model.CpModel,
    conflict_penalties: List[tuple],
    total_conflict_penalty: cp_model.IntVar,
):
    """
    Calculate the total conflict penalty from individual penalties.
    """
    weighted_penalties = []
    for penalty_var, weight in conflict_penalties:
        weighted_penalty = model.NewIntVar(
            0, weight, f'weighted_penalty_{penalty_var.Name()}'
        )
        model.Add(weighted_penalty == weight).OnlyEnforceIf(penalty_var)
        model.Add(weighted_penalty == 0).OnlyEnforceIf(penalty_var.Not())
        weighted_penalties.append(weighted_penalty)

    if weighted_penalties:
        model.Add(total_conflict_penalty == sum(weighted_penalties))
    else:
        model.Add(total_conflict_penalty == 0)


def add_skill_constraints(
    model: cp_model.CpModel,
    students: List[Student],
    num_students: int,
    max_groups: int,
    group_sizes: Dict[int, cp_model.IntVar],
    group_is_used: Dict[int, cp_model.BoolVarT],
    is_in_group: Dict[tuple, cp_model.BoolVarT],
) -> cp_model.IntVar:
    """
    Add skill balancing constraints and return the skill difference variable.
    """
    total_skills = {
        g: model.NewIntVar(0, num_students * 15, f'total_skills_{g}')
        for g in range(max_groups)
    }

    for g in range(max_groups):
        model.Add(
            total_skills[g] == sum(
                (
                    students[i].ruby_skill
                    + students[i].html_css_skill
                    + students[i].js_skill
                ) * is_in_group[i, g]
                for i in range(num_students)
            )
        )

        # Minimum total skill constraint: total_skills[g] >= group_sizes[g] * 5
        min_total_skill = model.NewIntVar(0, num_students * 5, f'min_total_skill_{g}')
        model.AddMultiplicationEquality(min_total_skill, [group_sizes[g], 5])
        model.Add(total_skills[g] >= min_total_skill).OnlyEnforceIf(group_is_used[g])

    # Minimize the maximum difference in total skills between groups
    max_skill = model.NewIntVar(0, num_students * 15, 'max_skill')
    min_skill = model.NewIntVar(0, num_students * 15, 'min_skill')
    model.AddMaxEquality(max_skill, [total_skills[g] for g in range(max_groups)])
    model.AddMinEquality(min_skill, [total_skills[g] for g in range(max_groups)])
    skill_diff = model.NewIntVar(0, num_students * 15, 'skill_diff')
    model.Add(skill_diff == max_skill - min_skill)

    return skill_diff


def calculate_preference_score(
    model: cp_model.CpModel,
    students: List[Student],
    assigned_group: Dict[int, cp_model.IntVar],
) -> cp_model.IntVar:
    """
    Calculate the preference satisfaction score.
    """
    email_to_index = {
        student.email.strip(): idx for idx, student in enumerate(students)
    }
    preference_terms = []

    for i, student in enumerate(students):
        preferred_email = student.preferred_partner_email.strip()
        if preferred_email and preferred_email in email_to_index:
            j = email_to_index[preferred_email]
            is_same_group = model.NewBoolVar(f'is_same_group_{i}_{j}')
            model.Add(assigned_group[i] == assigned_group[j]).OnlyEnforceIf(is_same_group)
            model.Add(assigned_group[i] != assigned_group[j]).OnlyEnforceIf(
                is_same_group.Not()
            )
            preference_terms.append(is_same_group)

    preference_score = model.NewIntVar(0, len(preference_terms), 'preference_score')
    if preference_terms:
        model.Add(preference_score == sum(preference_terms))
    else:
        model.Add(preference_score == 0)

    return preference_score


def renumber_groups(students: List[Student]) -> None:
    """
    Renumber the groups to ensure consecutive numbering starting from 1.

    Args:
        students (List[Student]): List of Student objects with assigned_group attributes.
    """
    # Extract unique group numbers and sort them
    unique_groups = sorted(set(student.assigned_group for student in students))

    # Create a mapping from old group numbers to new consecutive numbers
    group_mapping = {old: new for new, old in enumerate(unique_groups, start=1)}

    # Update each student's assigned_group based on the mapping
    for student in students:
        student.assigned_group = group_mapping[student.assigned_group]
