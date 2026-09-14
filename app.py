import streamlit as st
import pandas as pd

from analysis import (
    get_overview,
    get_column_types,
    get_missing_values,
    get_outliers,
    get_chartable_columns,
    clean_data,
    create_histogram,
    create_boxplot,
    create_bar_chart,
    create_heatmap,
    create_scatter_plot,
)

from insights import (
    generate_insights,
    build_insights_text,
)

st.set_page_config(
    page_title="AutoInsight",
    layout="wide",
)

st.title("AutoInsight")
st.write(
    "Automated Data Cleaning, Visualization "
    "and Fact-Based Insights"
)

uploaded_file = st.file_uploader(
    "Upload a CSV dataset",
    type=["csv"],
)

if uploaded_file is None:
    st.info("Upload a CSV file to begin.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Unable to read the CSV file: {e}")
    st.stop()

if df.empty:
    st.error("The uploaded dataset is empty.")
    st.stop()

st.header("1. Dataset Overview")

overview = get_overview(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Rows", overview["rows"])

with col2:
    st.metric("Columns", overview["columns"])

with col3:
    st.metric("Duplicate Rows", overview["duplicates"])

with col4:
    st.metric("Missing Values", overview["missing_values"])

numerical, categorical = get_column_types(df)

with st.expander("View Column Types"):
    st.write("**Numerical columns:**")
    st.write(numerical)
    st.write("**Categorical columns:**")
    st.write(categorical)

missing_values = get_missing_values(df)

if not missing_values.empty:
    st.subheader("Missing Values")
    st.dataframe(missing_values)

st.header("2. Data Quality & Cleaning")

with st.spinner("Checking and cleaning dataset..."):
    cleaned_df, report = clean_data(df)

if cleaned_df is None:
    st.error(
        "The dataset could not be cleaned reliably."
    )

    for issue in report.get("issues", []):
        st.error(issue)

    for warning in report.get("warnings", []):
        st.warning(warning)

    st.stop()

st.success("Dataset cleaning completed.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Original Rows",
        report["original_rows"]
    )

with col2:
    st.metric(
        "Final Rows",
        report["final_rows"]
    )

with col3:
    st.metric(
        "Duplicates Removed",
        report["duplicates_removed"]
    )

with col4:
    st.metric(
        "Outlier Rows Removed",
        report["outliers_removed"]
    )

st.subheader("Cleaned Dataset")

st.dataframe(
    cleaned_df.head(20),
    use_container_width=True
)

remaining_missing = int(
    cleaned_df.isnull().sum().sum()
)

remaining_duplicates = int(
    cleaned_df.duplicated().sum()
)

if remaining_missing == 0:
    st.success("No missing values remain.")
else:
    st.error(
        f"{remaining_missing} missing values remain."
    )

if remaining_duplicates == 0:
    st.success("No duplicate rows remain.")
else:
    st.error(
        f"{remaining_duplicates} duplicate rows remain."
    )

csv_data = cleaned_df.to_csv(index=False)

st.download_button(
    label="Download Cleaned CSV",
    data=csv_data,
    file_name="cleaned_dataset.csv",
    mime="text/csv",
)

st.header("3. Visualizations")

(
    continuous_numeric,
    bar_chart_columns,
    calendar_year_numeric,
) = get_chartable_columns(cleaned_df)

visualization_options = ["Select Visualization"]

if continuous_numeric:
    visualization_options.append("Histogram")
    visualization_options.append("Boxplot")

if bar_chart_columns:
    visualization_options.append("Bar Chart")

if len(continuous_numeric) >= 2:
    visualization_options.append("Scatter Plot")
    visualization_options.append("Correlation Heatmap")

selected_visualization = st.selectbox(
    "Choose a visualization",
    visualization_options,
)

if selected_visualization == "Histogram":
    column = st.selectbox(
        "Select numerical column",
        continuous_numeric,
    )

    fig = create_histogram(
        cleaned_df,
        column,
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

elif selected_visualization == "Boxplot":
    column = st.selectbox(
        "Select numerical column",
        continuous_numeric,
    )

    fig = create_boxplot(
        cleaned_df,
        column,
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

elif selected_visualization == "Bar Chart":
    column = st.selectbox(
        "Select categorical column",
        bar_chart_columns,
    )

    fig = create_bar_chart(
        cleaned_df,
        column,
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

elif selected_visualization == "Scatter Plot":
    col1, col2 = st.columns(2)

    with col1:
        x_column = st.selectbox(
            "Select X-axis",
            continuous_numeric,
        )

    with col2:
        y_options = [
            column
            for column in continuous_numeric
            if column != x_column
        ]

        y_column = st.selectbox(
            "Select Y-axis",
            y_options,
        )

    fig = create_scatter_plot(
        cleaned_df,
        x_column,
        y_column,
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

elif selected_visualization == "Correlation Heatmap":
    fig = create_heatmap(cleaned_df)

    if fig is not None:
        st.pyplot(
            fig,
            use_container_width=True
        )
    else:
        st.warning(
            "At least two numerical columns "
            "are required."
        )

st.header("4. Insights")

final_outliers = get_outliers(cleaned_df)

insights = generate_insights(
    cleaned_df,
    report,
    outlier_counts=final_outliers,
)

st.write(insights)

st.download_button(
    label="Download Insights (TXT)",
    data=build_insights_text(insights),
    file_name="autoinsight_report.txt",
    mime="text/plain",
)