# AutoInsight

## Automated Data Cleaning, Visualization & Insight Generation

AutoInsight is a Streamlit-based data analysis application that automates the initial stages of Exploratory Data Analysis (EDA).

It takes a raw CSV dataset, analyzes its quality, performs automated data cleaning, generates visualizations, and extracts meaningful insights in simple English.

## Live Demo

[Open AutoInsight](https://autoinsight-gbjfsbbse5mzyakqieb3gw.streamlit.app/)

## Features

- Upload CSV datasets
- Automatically analyze dataset structure
- Detect missing values
- Handle missing values
- Remove duplicate records
- Standardize text data
- Detect and remove statistical outliers
- Remove constant columns
- Validate the cleaned dataset
- Generate interactive visualizations
- Generate automated data insights
- Present insights in plain English
- Download the cleaned dataset
- Download the generated insights report

## Visualizations

AutoInsight supports multiple visualization types:

- Histogram
- Boxplot
- Bar Chart
- Scatter Plot
- Correlation Heatmap

The available visualization options are based on the structure and column types of the uploaded dataset.

## Data Cleaning

AutoInsight follows a structured data-cleaning pipeline:

```text
Raw Dataset
     ↓
Data Inspection
     ↓
Text Standardization
     ↓
Duplicate Removal
     ↓
Missing Value Handling
     ↓
Outlier Detection
     ↓
Constant Column Removal
     ↓
Final Data Quality Check
     ↓
Clean Dataset
