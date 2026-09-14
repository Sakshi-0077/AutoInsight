# AutoInsight

An end-to-end automated data analysis application that analyzes a user-provided CSV dataset, automatically identifies data-quality issues, cleans the dataset, generates relevant visualizations, and extracts meaningful insights in simple English.

The project combines a **Python-based data analysis backend** with an interactive **Streamlit interface**, making exploratory data analysis easier for both technical and non-technical users.

## Live Demo

**Streamlit App:**
[https://autoinsight-gbjfsbbse5mzyakqieb3gw.streamlit.app/](https://autoinsight-gbjfsbbse5mzyakqieb3gw.streamlit.app/)

## Features

* Upload CSV datasets directly through the web interface
* Automatic dataset analysis and profiling
* Numerical and categorical column identification
* Missing-value detection and handling
* Duplicate-row detection and removal
* Text standardization
* Statistical outlier detection and removal
* Constant-column detection and removal
* Final data-quality validation
* Interactive visualization selection
* Histogram generation
* Boxplot generation
* Bar chart generation
* Scatter plot generation
* Correlation heatmap generation
* Automated statistical insight extraction
* Plain-English data storytelling
* Download cleaned CSV directly from the application
* Download generated insights report

## How It Works

```text
                    ┌─────────────────────┐
                    │     Upload CSV      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Dataset Analysis    │
                    │                     │
                    │ • Rows / Columns    │
                    │ • Data Types        │
                    │ • Missing Values    │
                    │ • Duplicates        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Data Cleaning     │
                    │                     │
                    │ • Missing Values    │
                    │ • Duplicates        │
                    │ • Text Cleaning     │
                    │ • Outliers          │
                    │ • Constant Columns  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Quality Validation  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Visualization     │
                    │                     │
                    │ • Histogram         │
                    │ • Boxplot           │
                    │ • Bar Chart         │
                    │ • Scatter Plot      │
                    │ • Correlation Map   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Insight Generation  │
                    │                     │
                    │ • Patterns          │
                    │ • Relationships     │
                    │ • Trends            │
                    │ • Group Comparisons │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Download Results    │
                    └─────────────────────┘
```

## Data Cleaning

AutoInsight follows a structured data-cleaning pipeline.

### Missing Values

* Detect missing values automatically
* Remove columns with excessive missing data
* Remove rows with excessive missing data
* Numerical missing values → Median imputation
* Categorical missing values → Mode-based imputation
* Perform a final missing-value validation

### Duplicate Records

* Detect duplicate rows
* Remove duplicate records
* Report the number of duplicates removed

### Outlier Detection

Numerical outliers are detected using the **Interquartile Range (IQR)** method.

```text
IQR = Q3 - Q1

Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

### Text Standardization

Common representations of missing values and inconsistent text values are standardized before further analysis.

### Constant Columns

Columns containing only one unique value are removed because they do not provide useful variation for analysis.

## Data Quality Validation

After cleaning, AutoInsight validates the dataset before continuing with visualization and insight generation.

The application checks:

* Remaining missing values
* Remaining duplicate rows
* Empty datasets
* Unusable columns
* Dataset size

If the dataset becomes unusable after cleaning, the application reports the issue instead of continuing with unreliable analysis.

## Visualizations

### Histogram

Used to understand the distribution of numerical variables.

### Boxplot

Used to examine data spread and identify potential outliers.

### Bar Chart

Used to compare values across categorical groups.

### Scatter Plot

Used to examine relationships between two numerical variables.

### Correlation Heatmap

Used to identify relationships between numerical variables.

## Automated Insights

AutoInsight analyzes the cleaned dataset and extracts factual patterns such as:

* Dataset size and structure
* Typical numerical values
* Most common categories
* Differences between groups
* Relationships between numerical variables
* Trends over time
* Highly variable numerical columns

The results are presented in **plain English** so that users can understand the main findings without requiring advanced statistical knowledge.

The system focuses on observations supported by the data rather than unsupported assumptions or causal claims.

## Project Structure

```text
AutoInsight/
│
├── app.py
├── analysis.py
├── insights.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Main Components

**`app.py`**
Contains the Streamlit interface and complete application workflow.

**`analysis.py`**
Contains the core data-analysis, data-cleaning, outlier detection, validation, and visualization functions.

**`insights.py`**
Contains the logic for extracting factual patterns and generating easy-to-understand insights.

**`requirements.txt`**
Contains the Python dependencies required to run the application.

**`.gitignore`**
Prevents unnecessary files such as virtual environments and Python cache files from being uploaded to GitHub.

## Technology Stack

| Category             | Technology                  |
| -------------------- | --------------------------- |
| Programming Language | Python                      |
| Data Processing      | Pandas, NumPy               |
| Data Visualization   | Matplotlib, Seaborn         |
| Data Analysis        | Pandas, NumPy, Scikit-learn |
| Web Interface        | Streamlit                   |
| Spreadsheet Support  | OpenPyXL                    |
| Version Control      | Git & GitHub                |
| Deployment           | Streamlit Community Cloud   |

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Sakshi-0077/AutoInsight.git
cd AutoInsight
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser through the Streamlit local URL.

## Usage

1. Open the AutoInsight application.
2. Upload a CSV dataset.
3. Review the dataset overview.
4. Run the automated cleaning process.
5. Review the cleaning summary.
6. Check the dataset quality status.
7. Select a visualization type.
8. Select the required columns.
9. Generate the visualization.
10. Review the generated insights.
11. Download the cleaned dataset if required.
12. Download the insights report if required.

## Example Workflow

```text
CSV Dataset
     ↓
Dataset Overview
     ↓
Missing Values Detected
     ↓
Missing Values Handled
     ↓
Duplicate Rows Removed
     ↓
Outliers Detected
     ↓
Outliers Removed
     ↓
Dataset Validated
     ↓
Visualization Generated
     ↓
Data Insights Extracted
     ↓
Results Downloaded
```

## Use Cases

AutoInsight can be used for exploratory analysis of datasets related to:

* Sales
* Customers
* Products
* Finance
* Education
* Marketing
* Employees
* Business performance
* Surveys
* Operations
* General business datasets

It can be used as a first-pass analysis tool before performing deeper statistical analysis, machine learning, or domain-specific investigation.

## Deployment

The application is deployed using **Streamlit Community Cloud**.

**Live Application:**
[https://autoinsight-gbjfsbbse5mzyakqieb3gw.streamlit.app/](https://autoinsight-gbjfsbbse5mzyakqieb3gw.streamlit.app/)

**GitHub Repository:**
[https://github.com/Sakshi-0077/AutoInsight](https://github.com/Sakshi-0077/AutoInsight)

**Deployment Configuration:**

```text
Repository: Sakshi-0077/AutoInsight
Branch: main
Main File: app.py
```

## Future Improvements

* AI-powered natural-language data analysis
* LLM-based data storytelling using verified dataset facts
* Automatic visualization recommendations
* Advanced anomaly detection
* Additional statistical tests
* Support for Excel and additional file formats
* Interactive dashboards
* PDF and HTML report generation
* Automated business recommendations
* Advanced data-quality detection
* Automated exploratory data analysis reports
* Scalable cloud architecture

## Limitations

AutoInsight is designed primarily for exploratory data analysis and initial data preparation.

It does not replace:

* Domain expertise
* Advanced statistical analysis
* Formal hypothesis testing
* Business decision-making
* Specialized data-engineering pipelines
* Production-grade machine-learning workflows

The reliability of the results depends on the quality, size, and structure of the uploaded dataset.

## Project Goals

The main goals of AutoInsight are to:

1. Reduce repetitive manual data-analysis work.
2. Improve dataset quality before analysis.
3. Automate common data-cleaning tasks.
4. Simplify visualization generation.
5. Automatically identify useful patterns.
6. Present analytical findings in simple language.
7. Provide an end-to-end exploratory data-analysis workflow.

## Author

**Sakshi-0077**

GitHub: [https://github.com/Sakshi-0077](https://github.com/Sakshi-0077)

Project Repository: [https://github.com/Sakshi-0077/AutoInsight](https://github.com/Sakshi-0077/AutoInsight)

## License

This project is developed for educational, learning, and portfolio purposes.
