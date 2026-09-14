import pandas as pd
import numpy as np

from analysis import get_column_types


# =========================
# SETTINGS
# =========================

MIN_GROUP_SIZE = 5

CORRELATION_THRESHOLD = 0.50

STRONG_CORRELATION_THRESHOLD = 0.80

CATEGORY_DOMINANCE_THRESHOLD = 0.60

TREND_CHANGE_THRESHOLD = 0.15


# =========================
# NUMBER FORMATTING
# =========================

def format_number(value):

    if pd.isna(value):
        return "not available"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f} million"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f} thousand"

    if float(value).is_integer():
        return f"{int(value):,}"

    return f"{value:,.2f}"


def format_percent(value):

    return f"{value * 100:.1f}%"


# =========================
# BASIC DATA FACTS
# =========================

def get_basic_facts(df):

    numerical, categorical = get_column_types(df)

    facts = []

    facts.append(
        f"The dataset contains {len(df):,} records "
        f"and {len(df.columns):,} columns."
    )

    if numerical:

        facts.append(
            f"The numerical columns are: "
            f"{', '.join(numerical)}."
        )

    if categorical:

        facts.append(
            f"The categorical columns are: "
            f"{', '.join(categorical)}."
        )

    return facts


# =========================
# NUMERICAL FACTS
# =========================

def get_numerical_facts(df):

    numerical, _ = get_column_types(df)

    facts = []

    for column in numerical:

        data = df[column].dropna()

        if len(data) < MIN_GROUP_SIZE:
            continue

        mean = data.mean()

        median = data.median()

        minimum = data.min()

        maximum = data.max()

        facts.append(
            f"For {column}, the typical value "
            f"(median) is {format_number(median)}. "
            f"The average is {format_number(mean)}, "
            f"and values range from "
            f"{format_number(minimum)} to "
            f"{format_number(maximum)}."
        )

    return facts


# =========================
# CATEGORY FACTS
# =========================

def get_category_facts(df):

    _, categorical = get_column_types(df)

    facts = []

    for column in categorical:

        data = df[column].dropna()

        if len(data) < MIN_GROUP_SIZE:
            continue

        counts = data.value_counts()

        if counts.empty:
            continue

        top_category = counts.index[0]

        top_count = counts.iloc[0]

        percentage = (
            top_count / len(data)
        )

        facts.append(
            f"In {column}, the most common group "
            f"is '{top_category}', which contains "
            f"{format_percent(percentage)} "
            f"of the records."
        )

    return facts


# =========================
# GROUP COMPARISONS
# =========================

def get_group_facts(df):

    numerical, categorical = get_column_types(df)

    facts = []

    for category_column in categorical:

        unique_values = (
            df[category_column]
            .dropna()
            .unique()
        )

        if len(unique_values) < 2:
            continue

        if len(unique_values) > 15:
            continue

        for numerical_column in numerical:

            temp = df[
                [
                    category_column,
                    numerical_column
                ]
            ].dropna()

            if temp.empty:
                continue

            grouped = (
                temp
                .groupby(category_column)[
                    numerical_column
                ]
                .agg(
                    ["mean", "count"]
                )
            )

            grouped = grouped[
                grouped["count"]
                >= MIN_GROUP_SIZE
            ]

            if len(grouped) < 2:
                continue

            highest = grouped["mean"].idxmax()

            lowest = grouped["mean"].idxmin()

            highest_value = grouped.loc[
                highest,
                "mean"
            ]

            lowest_value = grouped.loc[
                lowest,
                "mean"
            ]

            if lowest_value == 0:
                continue

            difference = (
                abs(
                    highest_value
                    - lowest_value
                )
                / abs(lowest_value)
            )

            if difference >= TREND_CHANGE_THRESHOLD:

                facts.append(
                    f"When comparing {numerical_column} "
                    f"across {category_column}, the highest "
                    f"average is for '{highest}' "
                    f"({format_number(highest_value)}), "
                    f"while the lowest is for '{lowest}' "
                    f"({format_number(lowest_value)}). "
                    f"The difference between them is about "
                    f"{format_percent(difference)}."
                )

    return facts


# =========================
# CORRELATION FACTS
# =========================

def get_correlation_facts(df):

    numerical, _ = get_column_types(df)

    facts = []

    if len(numerical) < 2:
        return facts

    correlation = df[numerical].corr()

    checked = set()

    for column_a in numerical:

        for column_b in numerical:

            if column_a == column_b:
                continue

            pair = tuple(
                sorted(
                    [
                        column_a,
                        column_b
                    ]
                )
            )

            if pair in checked:
                continue

            checked.add(pair)

            value = correlation.loc[
                column_a,
                column_b
            ]

            if pd.isna(value):
                continue

            if abs(value) < CORRELATION_THRESHOLD:
                continue

            if abs(value) >= STRONG_CORRELATION_THRESHOLD:

                strength = "strong"

            else:

                strength = "moderate"

            if value > 0:

                direction = (
                    "when one goes up, the other "
                    "also tends to go up"
                )

            else:

                direction = (
                    "when one goes up, the other "
                    "tends to go down"
                )

            facts.append(
                f"{column_a} and {column_b} have a "
                f"{strength} relationship. Their "
                f"correlation is {value:.2f}, meaning "
                f"{direction}."
            )

    return facts


# =========================
# TREND FACTS
# =========================

def get_time_column(df):

    for column in df.columns:

        if "year" in column.lower():

            if pd.api.types.is_numeric_dtype(
                df[column]
            ):

                values = df[column].dropna()

                if not values.empty:

                    valid = values.between(
                        1900,
                        2100
                    )

                    if valid.mean() >= 0.80:

                        return column

    for column in df.columns:

        if "date" in column.lower():

            parsed = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            if parsed.notna().mean() >= 0.80:

                return column

    return None


def get_trend_facts(df):

    numerical, _ = get_column_types(df)

    time_column = get_time_column(df)

    facts = []

    if time_column is None:
        return facts

    if "year" in time_column.lower():

        time_values = df[time_column]

    else:

        time_values = pd.to_datetime(
            df[time_column],
            errors="coerce"
        ).dt.year

    for column in numerical:

        if column == time_column:
            continue

        temp = pd.DataFrame({
            "time": time_values,
            "value": df[column]
        }).dropna()

        if temp.empty:
            continue

        grouped = (
            temp
            .groupby("time")["value"]
            .mean()
            .sort_index()
        )

        if len(grouped) < 2:
            continue

        first_value = grouped.iloc[0]

        last_value = grouped.iloc[-1]

        first_year = grouped.index[0]

        last_year = grouped.index[-1]

        if first_value == 0:
            continue

        change = (
            last_value
            - first_value
        ) / abs(first_value)

        if abs(change) < TREND_CHANGE_THRESHOLD:
            continue

        if change > 0:

            facts.append(
                f"The average {column} increased from "
                f"{format_number(first_value)} in "
                f"{int(first_year)} to "
                f"{format_number(last_value)} in "
                f"{int(last_year)}, an increase of "
                f"{format_percent(change)}."
            )

        else:

            facts.append(
                f"The average {column} decreased from "
                f"{format_number(first_value)} in "
                f"{int(first_year)} to "
                f"{format_number(last_value)} in "
                f"{int(last_year)}, a decrease of "
                f"{format_percent(abs(change))}."
            )

    return facts


# =========================
# VARIABILITY
# =========================

def get_variability_facts(df):

    numerical, _ = get_column_types(df)

    facts = []

    for column in numerical:

        data = df[column].dropna()

        if len(data) < MIN_GROUP_SIZE:
            continue

        mean = data.mean()

        std = data.std()

        if mean == 0:
            continue

        ratio = abs(std / mean)

        if ratio >= 1:

            facts.append(
                f"{column} varies considerably across "
                f"the dataset. The standard deviation is "
                f"about {format_percent(ratio)} of the average."
            )

    return facts


# =========================
# BUILD FACTS
# =========================

def collect_data_facts(
    df,
    report=None
):

    facts = []

    facts += get_basic_facts(df)

    facts += get_numerical_facts(df)

    facts += get_category_facts(df)

    facts += get_group_facts(df)

    facts += get_correlation_facts(df)

    facts += get_trend_facts(df)

    facts += get_variability_facts(df)

    # Remove duplicate facts

    unique_facts = []

    seen = set()

    for fact in facts:

        if fact not in seen:

            unique_facts.append(fact)

            seen.add(fact)

    return unique_facts


# =========================
# PLAIN ENGLISH STORY
# =========================

def create_story(facts):

    if not facts:

        return (
            "I could not find any strong patterns in "
            "this dataset that were clear enough to "
            "report confidently."
        )

    story_parts = []

    # Opening

    story_parts.append(
        facts[0]
    )

    # General picture

    if len(facts) > 1:

        story_parts.append(
            "Looking at the data more closely, "
            + facts[1]
        )

    # Main findings

    if len(facts) > 2:

        story_parts.append(
            "One of the main things that stands out is "
            + facts[2]
        )

    # Additional findings

    if len(facts) > 3:

        additional = facts[3:8]

        for fact in additional:

            story_parts.append(
                "Another useful point is "
                + fact
            )

    # Ending

    story_parts.append(
        "Overall, these are the main patterns visible "
        "in the data. These observations describe "
        "what is present in the dataset; they do not "
        "by themselves prove that one factor causes another."
    )

    return "\n\n".join(
        story_parts
    )


# =========================
# MAIN FUNCTION
# =========================

def generate_insights(
    df,
    report=None,
    outlier_counts=None
):

    facts = collect_data_facts(
        df,
        report
    )

    return create_story(
        facts
    )


# =========================
# TXT REPORT
# =========================

def build_insights_text(
    insights
):

    return (
        "AutoInsight - Data Story\n"
        "========================\n\n"
        + insights
    )