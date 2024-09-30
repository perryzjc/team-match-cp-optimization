# Specification Document for Student Group Assignment Optimizer

## Table of Contents

1. [Introduction](#introduction)
2. [Objectives](#objectives)
3. [Inputs and Outputs](#inputs-and-outputs)
   - [Input Data](#input-data)
   - [Output Data](#output-data)
4. [Functional Requirements](#functional-requirements)
   - [Group Assignment Constraints](#group-assignment-constraints)
     - [Group Size Constraints](#group-size-constraints)
     - [Skill Balance Constraints](#skill-balance-constraints)
     - [Preferred Partner Constraints](#preferred-partner-constraints)
     - [Meeting Preference Constraints](#meeting-preference-constraints)
     - [Availability Constraints](#availability-constraints)
     - [Section Constraints](#section-constraints)
     - [Missing Students Constraints](#missing-students-constraints)
   - [Optimization Objectives](#optimization-objectives)
     - [Maximize Groups of Size 4](#maximize-groups-of-size-4)
     - [Minimize Conflict Penalties](#minimize-conflict-penalties)
     - [Balance Skill Levels](#balance-skill-levels)
     - [Maximize Preference Satisfaction](#maximize-preference-satisfaction)
   - [Loop Detection and Handling](#loop-detection-and-handling)
   - [Missing Students Identification and Inclusion](#missing-students-identification-and-inclusion)
5. [Non-Functional Requirements](#non-functional-requirements)
   - [Performance](#performance)
   - [Modularity and Maintainability](#modularity-and-maintainability)
   - [Data Privacy](#data-privacy)
6. [Assumptions and Considerations](#assumptions-and-considerations)
7. [Appendices](#appendices)
   - [Appendix A: Sample Input and Output Formats](#appendix-b-sample-input-and-output-formats)

---

## Introduction

This document specifies the requirements for a student group assignment optimizer designed to form balanced and compatible groups based on various criteria. The optimizer considers students' preferences, skills, availability, and other factors to assign them to groups that satisfy specified constraints and optimization objectives.

---

## Objectives

- **Efficient Group Formation**: Automatically assign students to groups that meet defined constraints and optimize certain objectives.
- **Fairness and Balance**: Ensure that groups are balanced in terms of skill levels and other attributes.
- **Preference Satisfaction**: Accommodate students' preferences for partners, meeting modes, and availability where possible.
- **Modularity**: Design the system with modular code for maintainability and extensibility.
- **Reporting and Visualization**: Provide reports and visualizations to evaluate the effectiveness of the group assignments.

---

## Inputs and Outputs

### Input Data

The optimizer requires two CSV files:

1. **Student Input CSV**: Contains data collected from students via a form. This includes their personal information, preferences, skills, availability, and constraints.

2. **Course Roster CSV**: Contains the complete list of students enrolled in the course. This is used to identify students who did not submit the input form.

#### Expected Fields in Student Input CSV

- **Student ID**
- **Name**
- **Email**
- **GitHub Username**
- **Preferred Partner Email**
- **Skills**:
  - **Ruby Skill** (1-5)
  - **HTML/CSS Skill** (1-5)
  - **JavaScript Skill** (1-5)
- **Meeting Preference** (In Person, Remote, No Preference)
- **Available Times** (Set of time slots)
- **Section Attended**
- **Additional Constraints**

#### Expected Fields in Course Roster CSV

- **Student ID**
- **Name**
- **Email**

### Output Data

The optimizer produces the following outputs:

- **Group Assignments CSV**: Lists students with their assigned group numbers and relevant information.
- **Reports**: Summarizes the group assignments, including statistics and any issues encountered.
- **Visualizations**: Graphs and charts that help evaluate the effectiveness of the optimization.

---

## Functional Requirements

### Group Assignment Constraints

The optimizer must assign students to groups while satisfying the following constraints:

#### Group Size Constraints

- **Preferred Group Size**: Groups should have **exactly 4 students** whenever possible.
- **Minimum Group Size**: Groups must have at least **3 students**.
- **Maximum Group Size**: Groups cannot have more than **4 students**.
- **Exceptions**:
  - The number of groups not of size 4 is minimized based on the total number of students.
  - The optimizer calculates the minimum number of groups that cannot be of size 4 and adjusts group sizes accordingly.

#### Skill Balance Constraints

- **Minimum Total Skill**: The total skill score of each group must be at least **`group_size * 5`**.
  - Each student's skill score is the sum of their individual skill levels in Ruby, HTML/CSS, and JavaScript.
- **Skill Distribution**: Minimize the maximum difference in total skill scores between groups to ensure balanced skill levels.

#### Preferred Partner Constraints

- **Mutual Preference**: If a student specifies a preferred partner, they must be assigned to the same group as that partner.
- **Non-Mutual Preference**: The optimizer treats all preferred partner requests equally, regardless of mutuality.
- **Loop Preferences**: For preference loops involving multiple students, the optimizer attempts to assign all involved students to the same group if feasible.

#### Meeting Preference Constraints

- **Conflict Minimization**: Penalize grouping students with conflicting meeting preferences (In Person vs. Remote).
- **No Preference**: Students who select "No Preference" are compatible with any meeting preference.

#### Availability Constraints

- **Overlap Encouragement**: The optimizer encourages grouping students with overlapping available times.
- **Conflict Penalty**: Grouping students with no overlapping available times incurs a high penalty.
- **Unknown Availability**: If a student's availability is unknown (missing), conflicts are not penalized.

#### Section Constraints

- **Section Consistency**: Penalize grouping students who attend different sections.
- **Optional Constraint**: This constraint has a lower priority compared to others.

#### Missing Students Constraints

- **Identification**: Students who did not submit the input form are identified using the course roster CSV.
- **Default Values**: Missing students are assigned default skill scores of **2** in all areas and "No Preference" for meeting mode.
- **Inclusion Option**: A boolean flag allows control over whether missing students are included in the optimization.
- **Group Limit**: No more than **1 missing student** can be assigned to the same group.

### Optimization Objectives

The optimizer aims to find an assignment of students to groups that satisfies the above constraints while optimizing the following objectives:

#### Maximize Groups of Size 4

- **Priority**: Maximizing the number of groups with exactly 4 students is given the highest priority.

#### Minimize Conflict Penalties

- **Conflict Types**:
  - Availability Conflicts
  - Meeting Preference Conflicts
  - Section Conflicts
- **Penalty Weights**:
  - **Availability Conflict**: > **Meeting Preference Conflict** > **Section Conflict**
- **Total Conflict Penalty**: The sum of weighted penalties, which the optimizer seeks to minimize.

#### Balance Skill Levels

- **Skill Difference Minimization**: Minimize the difference between the groups with the highest and lowest total skill scores.

#### Maximize Preference Satisfaction

- **Preferred Partners**: Maximize the number of preferred partner requests that are satisfied.
- **Preference Score**: The total number of satisfied preferred partner requests.

### Loop Detection and Handling

- **Preference Loops**: Detect loops in preferred partner requests involving multiple students.
- **Assignment**: Attempt to assign all students involved in a loop to the same group if feasible.
- **Reporting**: Generate reports detailing detected loops for transparency and potential manual adjustments.

### Missing Students Identification and Inclusion

- **Comparison with Roster**: Compare the student input CSV with the course roster to identify missing students.
- **Reporting**: Provide reports listing missing students and their count.
- **Optional Inclusion**:
  - Controlled via a boolean flag (`--include-missing`).
  - When included, missing students are assigned default values and considered in the optimization.
- **Default Assignments**:
  - **Skills**: Assigned a score of **2** in each skill area.
  - **Meeting Preference**: Set to "No Preference".
  - **Available Times**: Left empty.
  - **Constraints**: Left empty.

---

## Non-Functional Requirements

### Performance

- **Solver Efficiency**: The optimizer should find feasible solutions within a reasonable time frame (e.g., under 10 minutes).
- **Scalability**: Capable of handling large classes (e.g., 100+ students) without significant performance degradation.

### Modularity and Maintainability

- **Code Organization**: Use modular code with functions and classes organized in appropriate modules.
- **Readability**: Code should be well-documented with clear variable names and comments.
- **Extensibility**: Easy to modify or extend the optimizer to accommodate new constraints or objectives.

### Data Privacy

- **Sensitive Information**: Ensure that any reports or outputs shared externally do not contain sensitive student information.
- **Anonymization**: When necessary, anonymize data in visualizations and reports.

---

## Assumptions and Considerations

- **Data Integrity**:
  - Input data from CSV files is assumed to be correctly formatted and free of errors.
  - Skill scores are integers ranging from **1** to **5**.

- **Availability Data**:
  - Available times are represented as sets of time slots (e.g., days of the week).

- **Feasibility**:
  - It is assumed that the constraints are not mutually exclusive and that a feasible solution exists.
  - If no solution is found, the optimizer provides meaningful feedback.

- **Constraints Priority**:
  - **Hard Constraints**: Group size limits, preferred partner assignments, missing students per group.
  - **Soft Constraints**: Meeting preferences, availability overlaps, section consistency.

- **Conflict Penalties**:
  - Weights assigned to different conflicts reflect their relative importance but can be adjusted based on specific needs.

- **Solver Configuration**:
  - The optimizer uses the Google OR-Tools CP-SAT solver.
  - Solver parameters (e.g., time limits, logging) can be configured as needed.

---

## Appendices

### Appendix A: Sample Input and Output Formats

#### Sample Student Input CSV (`input.csv`)
Check [#data/input/input_sanitized.csv](data/input/input_sanitized.csv) for a sample student input file.

#### Sample Course Roster CSV (`course_roster.csv`)
Check [#data/input/course_roster_sanitized.csv](data/input/course_roster_sanitized.csv) for a sample course roster file.

#### Sample Output CSV (`group_assignments.csv`)
Check [#data/output/output.csv](data/output/output.csv) for a sample output file.