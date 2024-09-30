# CS169A Team Match Script

Apply optimization techniques to enhance the team matching experience for the CS169A course.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Inputs](#inputs)
  - [Roster CSV](#roster-csv)
  - [Input CSV](#input-csv)
- [Outputs](#outputs)
  - [Output CSV](#output-csv)
  - [Report](#report)
  - [Visualizations](#visualizations)
- [Requirements](#requirements)
- [Directory Structure](#directory-structure)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview

The **CS169A Team Match Script** leverages optimization algorithms to facilitate effective team assignments for the CS169A course. By analyzing student preferences and roster information, the script ensures balanced and harmonious team formations, enhancing the overall learning experience.

## Features

- **Data Loading:** Imports student and roster data from CSV files.
- **Missing Student Identification:** Detects and reports students missing from the roster.
- **Group Assignment:** Utilizes optimization techniques to assign students to teams.
- **Reporting:** Generates comprehensive reports detailing group statistics and unassigned students.
- **Visualizations:** Produces various visual representations of team dynamics and preferences.
- **Customization:** Allows inclusion of missing students in the optimization process via command-line flags.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/cs169a_team_match.git
   cd cs169a_team_match
   ```

2. **Create a Virtual Environment:**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Unix or MacOS
   .venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To execute the team matching script, use the following command structure:
This command looks messy, it might be cleaned up in the future (;; too much hw to do rn)
```bash
python script.py \
    <input_csv> \
    <roster_csv> \
    <output_path> \
    --include-missing
```

### Example Command

```bash
python script.py data/input/input.csv data/roster/roster_2024-09-27.csv data/output --include-missing
```

### Command Breakdown

1. **Python Interpreter:**
   - `python`: Invokes the Python interpreter. Ensure you're using Python 3.6 or higher.

2. **Script Path:**
   - `script.py`: Path to the main application script.

3. **Positional Arguments:**
   - `data/input/input.csv`: Path to the input CSV file containing student responses from the Google Form survey.
   - `data/roster/roster_2024-09-27.csv`: Path to the roster CSV file obtained from Bcourses.
   - `data/output/output.csv`: Path where the output files will be saved.
4. **Optional Flags:**
   - `--include-missing`: Includes missing students in the optimization process. Omit this flag if you do not wish to include missing students.

## Inputs

### Roster CSV

- **Source:** Obtain the roster CSV file from Bcourses.
- **Purpose:** Contains the list of enrolled students along with their contact information.

### Input CSV

- **Source:** Generated from the Google Sheet linked to your Google Form survey.
- **Purpose:** Captures student responses regarding their preferences, skills, and availability.
- **Accessing the CSV:**
  1. Open the Google Form responses in Google Sheets.
  2. Navigate to `File` > `Download` > `Comma-separated values (.csv)` to obtain the `input.csv` file.

## Outputs

### Output CSV
Check [SPEC.md#](SPEC.MD) for the output csv format.

### Report
- **Description:** A comprehensive textual report detailing various statistics about the group assignments.

### Visualizations

1. **Preference Graph (`preference_graph.png`):**
   - **Purpose:** Visualizes student preferences, highlighting mutual preferences and preference loops.
   - **Usage:** Helps in identifying patterns and potential conflicts in student preferences.

2. **Group Meeting Preferences (`group_meeting_preferences.png`):**
   - **Purpose:** Shows the distribution of meeting preferences (e.g., In Person, Remote, No Preference) across different groups.
   - **Usage:** Ensures that group compositions consider varying meeting preferences for optimal collaboration.

3. **Skill Balance (`skill_balance.png`):**
   - **Purpose:** Displays the total and average skill scores across groups.
   - **Usage:** Assists in verifying that groups are balanced in terms of skills.

4. **Group Size Distribution (`group_size_distribution.png`):**
   - **Purpose:** Illustrates the distribution of group sizes.
   - **Usage:** Ensures that groups adhere to desired size constraints.

5. **Group Network (`group_network.png`):**
   - **Purpose:** Represents groups as clusters in a network graph.
   - **Usage:** Visualizes interconnections and collaborations within and across groups.

6. **Availability Visualizations:**
   - **Availability Heatmap (`availability_heatmap.png`):**
     - **Purpose:** Shows overlapping availability among all students.
     - **Usage:** Facilitates scheduling by identifying common available times.
   - **Group-specific Availability (`availability_groups_group_<number>.png`):**
     - **Purpose:** Displays availability overlaps within each group.
     - **Usage:** Ensures that group members have compatible schedules.

## Requirements

- **Python Version:** Python 3.6 or higher
- **Dependencies:** Listed in `requirements.txt`

### Installing Dependencies

After setting up your virtual environment, install the required packages using:

```bash
pip install -r requirements.txt
```

## License
This project is licensed under the [MIT License](LICENSE).
