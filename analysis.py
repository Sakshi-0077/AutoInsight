import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

COLUMN_MISSING_DROP_THRESHOLD = 0.50
ROW_MISSING_DROP_THRESHOLD = 0.50

MIN_UNIQUE_FOR_OUTLIER_CHECK = 10
CATEGORICAL_MAX_UNIQUE_FOR_CHART = 20
MIN_ROWS_FOR_RELIABLE_STATS = 30

def get_column_types(df):
    numerical = df.select_dtypes(include="number").columns.tolist()

    categorical = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    return numerical, categorical

def get_overview(df):
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "duplicates": int(df.duplicated().sum()),
        "missing_values": int(df.isnull().sum().sum()),
    }

def get_missing_values(df):
    result = pd.DataFrame({
        "Missing": df.isnull().sum(),
        "Percentage": (df.isnull().mean() * 100).round(2),
    })

    return result[result["Missing"] > 0]

def _looks_like_id_column(df, column):

    column_name = column.lower().strip()

    id_names = [
        "id",
        "user_id",
        "customer_id",
        "employee_id",
        "student_id",
        "product_id",
        "order_id",
        "transaction_id",
        "account_id",
        "record_id",
        "index",
        "code",
    ]

    # Exact ID column names
    if column_name in id_names:
        return True

    # Common ID suffixes
    if column_name.endswith("_id"):
        return True

    # Code columns
    if column_name.endswith("_code"):
        return True

    return False

def _looks_like_calendar_year_column(df, column):
    if "year" not in column.lower():
        return False

    if not pd.api.types.is_numeric_dtype(df[column]):
        return False

    values = df[column].dropna()

    if values.empty:
        return False

    plausible_year = values.between(1900, 2100)

    return plausible_year.mean() > 0.80

def get_outlier_eligible_columns(df):
    numerical, _ = get_column_types(df)

    eligible = []

    for column in numerical:

        if df[column].nunique(dropna=True) <= MIN_UNIQUE_FOR_OUTLIER_CHECK:
            continue

        if _looks_like_id_column(df, column):
            continue

        if _looks_like_calendar_year_column(df, column):
            continue

        eligible.append(column)

    return eligible

def get_outliers(df):

    eligible_columns = get_outlier_eligible_columns(df)

    result = {}

    for column in eligible_columns:

        data = df[column].dropna()

        if len(data) < 4:
            result[column] = 0
            continue

        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            result[column] = 0
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        result[column] = int(
            (
                (data < lower_bound)
                | (data > upper_bound)
            ).sum()
        )

    return result

def remove_outliers(df):

    df = df.copy()

    eligible_columns = get_outlier_eligible_columns(df)

    outlier_mask = pd.Series(
        False,
        index=df.index
    )

    for column in eligible_columns:

        data = df[column].dropna()

        if len(data) < 4:
            continue

        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        column_outliers = (
            (df[column] < lower_bound)
            | (df[column] > upper_bound)
        )

        column_outliers = column_outliers.fillna(False)

        outlier_mask |= column_outliers

    removed = int(outlier_mask.sum())

    df = df.loc[
        ~outlier_mask
    ].reset_index(drop=True)

    return df, removed

def standardize_text(df):
    df = df.copy()

    missing_tokens = [
        "",
        "nan",
        "NaN",
        "None",
        "none",
        "NULL",
        "null",
        "NA",
        "N/A",
        "n/a",
        "?",
    ]

    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

            df[column] = df[column].replace(
                missing_tokens,
                pd.NA
            )

    return df

def handle_missing_values(df):
    df = df.copy()

    # Drop columns having more than 50% missing values
    col_missing_pct = df.isnull().mean()

    columns_to_drop = (
        col_missing_pct[
            col_missing_pct > COLUMN_MISSING_DROP_THRESHOLD
        ]
        .index
        .tolist()
    )

    df = df.drop(
        columns=columns_to_drop
    )

    # Drop rows having more than 50% missing values
    rows_to_drop = []

    if len(df.columns) > 0:

        row_missing_pct = df.isnull().mean(axis=1)

        rows_to_drop = (
            row_missing_pct[
                row_missing_pct > ROW_MISSING_DROP_THRESHOLD
            ]
            .index
            .tolist()
        )

        df = df.drop(
            index=rows_to_drop
        )

    # Fill numerical columns with median
    numerical, categorical = get_column_types(df)

    for column in numerical:

        if df[column].isnull().any():

            median_value = df[column].median()

            if pd.notna(median_value):

                df[column] = df[column].fillna(
                    median_value
                )

    # Fill categorical columns with mode
    for column in categorical:

        if df[column].isnull().any():

            mode = df[column].mode()

            if not mode.empty:

                df[column] = df[column].fillna(
                    mode.iloc[0]
                )

            else:

                df[column] = df[column].fillna(
                    "Unknown"
                )

    # Final safety check
    # If any missing values somehow remain,
    # remove those rows rather than returning
    # an incorrectly labelled "clean" dataset.

    remaining_missing_rows = (
        df.isnull().any(axis=1)
    )

    final_rows_dropped = int(
        remaining_missing_rows.sum()
    )

    if final_rows_dropped > 0:

        df = df.loc[
            ~remaining_missing_rows
        ]

    missing_report = {
        "columns_dropped_missing": columns_to_drop,
        "rows_dropped_missing": (
            len(rows_to_drop)
            + final_rows_dropped
        ),
    }

    return df, missing_report

def remove_duplicates(df):

    before = len(df)

    df = (
        df
        .drop_duplicates()
        .reset_index(drop=True)
    )

    removed = before - len(df)

    return df, removed

def remove_constant_columns(df):

    constant_columns = [
        column
        for column in df.columns
        if df[column].nunique(dropna=False) <= 1
    ]

    df = df.drop(
        columns=constant_columns
    )

    return df, constant_columns

def check_dataset_sufficiency(df):

    issues = []
    warnings = []

    if len(df) == 0:
        issues.append(
            "Dataset contains no rows."
        )

    if len(df.columns) == 0:
        issues.append(
            "Dataset contains no usable columns."
        )

    if len(df) > 0 and len(df) < MIN_ROWS_FOR_RELIABLE_STATS:

        warnings.append(
            f"Only {len(df)} rows remain. "
            f"Statistical analysis may be less reliable "
            f"with fewer than {MIN_ROWS_FOR_RELIABLE_STATS} rows."
        )

    if len(df.columns) == 1:

        warnings.append(
            "Dataset contains only one column. "
            "Relationship-based analysis will be limited."
        )

    numerical, categorical = get_column_types(df)

    if not numerical and not categorical:

        issues.append(
            "No supported data columns were found."
        )

    if df.isnull().sum().sum() > 0:

        issues.append(
            "Missing values remain after cleaning."
        )

    if df.duplicated().sum() > 0:

        issues.append(
            "Duplicate rows remain after cleaning."
        )

    return issues, warnings

def clean_data(df):

    original_rows = len(df)

    original_missing = int(
        df.isnull().sum().sum()
    )

    original_duplicates = int(
        df.duplicated().sum()
    )

    # 1. Standardize missing values
    df = standardize_text(df)

    # 2. Remove duplicate rows
    df, duplicates_removed = remove_duplicates(df)

    # 3. Handle missing values
    df, missing_report = handle_missing_values(df)

    # 4. Remove outliers
    df, outliers_removed = remove_outliers(df)

    # 5. Remove constant columns
    df, constant_columns_removed = (
        remove_constant_columns(df)
    )

    # 6. Final checks
    issues = []

    if len(df.columns) == 0:

        issues.append(
            "No usable columns remain after cleaning."
        )

    if len(df) == 0:

        issues.append(
            "No rows remain after cleaning."
        )

    # Missing values MUST be zero
    remaining_missing = int(
        df.isnull().sum().sum()
    )

    if remaining_missing > 0:

        issues.append(
            "Missing values remain after cleaning."
        )

    # Duplicate rows MUST be zero
    remaining_duplicates = int(
        df.duplicated().sum()
    )

    if remaining_duplicates > 0:

        issues.append(
            "Duplicate rows remain after cleaning."
        )

    # If fundamental cleaning failed
    if len(df.columns) == 0 or len(df) == 0:

        return None, {
            "status": "failed",
            "issues": issues,
        }

    report = {

        "status": "success",

        "original_rows": original_rows,

        "final_rows": len(df),

        "rows_removed": (
            original_rows - len(df)
        ),

        "original_missing_values": (
            original_missing
        ),

        "duplicates_found": (
            original_duplicates
        ),

        "duplicates_removed": (
            duplicates_removed
        ),

        "columns_dropped_missing": (
            missing_report[
                "columns_dropped_missing"
            ]
        ),

        "rows_dropped_missing": (
            missing_report[
                "rows_dropped_missing"
            ]
        ),

        "outliers_removed": (
            outliers_removed
        ),

        "constant_columns_removed": (
            constant_columns_removed
        ),

        "remaining_missing_values": (
            remaining_missing
        ),

        "remaining_duplicates": (
            remaining_duplicates
        ),

        "warnings": [],
    }

    # Small dataset = warning, NOT failure
    if len(df) < MIN_ROWS_FOR_RELIABLE_STATS:

        report["warnings"].append(
            f"Only {len(df)} rows remain. "
            f"Statistical analysis may be less reliable."
        )

    return df, report

def create_histogram(df, column):

    fig, ax = plt.subplots()

    ax.hist(
        df[column].dropna(),
        bins=20
    )

    ax.set_title(
        f"Distribution of {column}"
    )

    ax.set_xlabel(column)

    ax.set_ylabel("Frequency")

    fig.tight_layout()

    return fig

def create_boxplot(df, column):

    fig, ax = plt.subplots()

    ax.boxplot(
        df[column].dropna()
    )

    ax.set_title(
        f"Box Plot of {column}"
    )

    ax.set_ylabel(column)

    fig.tight_layout()

    return fig

def create_bar_chart(df, column):

    values = (
        df[column]
        .value_counts()
        .head(10)
    )

    fig, ax = plt.subplots()

    ax.bar(
        values.index.astype(str),
        values.values
    )

    ax.set_title(
        f"Top Values in {column}"
    )

    ax.set_xlabel(column)

    ax.set_ylabel("Count")

    ax.tick_params(
        axis="x",
        rotation=45
    )

    fig.tight_layout()

    return fig

def create_scatter_plot(df, x_column, y_column):

    fig, ax = plt.subplots()

    ax.scatter(
        df[x_column],
        df[y_column],
        alpha=0.7
    )

    ax.set_title(
        f"{x_column} vs {y_column}"
    )

    ax.set_xlabel(x_column)

    ax.set_ylabel(y_column)

    fig.tight_layout()

    return fig

def create_line_chart(df, x_column, y_column):

    data = df[
        [x_column, y_column]
    ].dropna()

    data = data.sort_values(
        by=x_column
    )

    fig, ax = plt.subplots()

    ax.plot(
        data[x_column],
        data[y_column]
    )

    ax.set_title(
        f"{y_column} over {x_column}"
    )

    ax.set_xlabel(x_column)

    ax.set_ylabel(y_column)

    fig.tight_layout()

    return fig

def create_heatmap(df):

    numerical, _ = get_column_types(df)

    if len(numerical) < 2:
        return None

    correlation = (
        df[numerical]
        .corr()
    )

    fig, ax = plt.subplots()

    sns.heatmap(
        correlation,
        annot=True,
        ax=ax,
        fmt=".2f"
    )

    ax.set_title(
        "Correlation Heatmap"
    )

    fig.tight_layout()

    return fig

def get_chartable_columns(df):

    numerical, categorical = get_column_types(df)

    continuous_numeric = []

    discrete_numeric = []

    calendar_year_numeric = []

    for column in numerical:

        # Ignore actual ID columns
        if _looks_like_id_column(df, column):
            continue

        # Detect year columns
        if _looks_like_calendar_year_column(
            df,
            column
        ):

            calendar_year_numeric.append(
                column
            )

        # Numerical columns with few unique values
        elif df[column].nunique(
            dropna=True
        ) <= MIN_UNIQUE_FOR_OUTLIER_CHECK:

            discrete_numeric.append(
                column
            )

        # Normal continuous numerical columns
        else:

            continuous_numeric.append(
                column
            )

    categorical_chartable = []

    for column in categorical:

        unique_count = df[column].nunique(
            dropna=True
        )

        if (
            unique_count > 1
            and unique_count <= CATEGORICAL_MAX_UNIQUE_FOR_CHART
        ):

            categorical_chartable.append(
                column
            )

    bar_chart_columns = (
        discrete_numeric
        + categorical_chartable
    )

    return (
        continuous_numeric,
        bar_chart_columns,
        calendar_year_numeric,
    )

def create_visualizations(df):

    (
        continuous_numeric,
        bar_chart_columns,
        calendar_year_numeric,
    ) = get_chartable_columns(df)

    visualizations = []

    for column in continuous_numeric:

        visualizations.append(
            (
                "histogram",
                column,
                create_histogram(
                    df,
                    column
                ),
            )
        )

        visualizations.append(
            (
                "boxplot",
                column,
                create_boxplot(
                    df,
                    column
                ),
            )
        )

    for column in calendar_year_numeric:

        visualizations.append(
            (
                "histogram",
                column,
                create_histogram(
                    df,
                    column
                ),
            )
        )

    for column in bar_chart_columns:

        visualizations.append(
            (
                "bar_chart",
                column,
                create_bar_chart(
                    df,
                    column
                ),
            )
        )

    if len(continuous_numeric) >= 2:

        max_scatter_columns = (
            continuous_numeric[:5]
        )

        for i in range(
            len(max_scatter_columns)
        ):

            for j in range(
                i + 1,
                len(max_scatter_columns)
            ):

                x = max_scatter_columns[i]

                y = max_scatter_columns[j]

                visualizations.append(
                    (
                        "scatter",
                        f"{x} vs {y}",
                        create_scatter_plot(
                            df,
                            x,
                            y
                        ),
                    )
                )

    if len(continuous_numeric) >= 2:

        heatmap = create_heatmap(df)

        if heatmap is not None:

            visualizations.append(
                (
                    "heatmap",
                    None,
                    heatmap
                )
            )

    return visualizations