from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="WBCYA Church on the Run", layout="wide")

MILES_PER_KILOMETRE = 0.621371
GOAL_MILES = 388
DATA_DIR = Path(__file__).parent

st.sidebar.title("WBCYA Run Club: Church on the Run")
# st.sidebar.header("Fundraising Link:")
st.sidebar.markdown("[JustGiving Page](https://www.justgiving.com/page/windsor-run-club)")

st.title("WBCYA Church on the Run Fundraiser")
st.markdown("Last updated: 14/11/12 18:00")

st.divider()

daily_distances = pd.read_csv(DATA_DIR / "Church On The Run - DailyTotals.csv")
participant_distances = pd.read_csv(DATA_DIR / "Church On The Run - ParticipantTotals.csv")
activity_log = pd.read_csv(DATA_DIR / "Church On The Run - ActivityLog.csv")

total_miles = participant_distances["DISTANCE"].sum() * MILES_PER_KILOMETRE
goal_percentage = total_miles / GOAL_MILES * 100

distance_column, goal_column = st.columns(2)
distance_column.metric(
    "Total distance completed",
    f"{total_miles:,.2f} miles",
    f"of {GOAL_MILES:,} miles",
)
goal_column.metric("% of goal completed", f"{goal_percentage:.0f}%")
st.progress(min(goal_percentage / 100, 1.0))

st.subheader("Distance Per Day")
daily_distances["DATE"] = pd.to_datetime(
    daily_distances["DATE"], format="%d/%m/%y"
)
last_reported_activity_date = daily_distances.loc[
    daily_distances["DIST (km)"] > 0, "DATE"
].max()
first_reported_date = daily_distances["DATE"].min()
days_elapsed = (last_reported_activity_date - first_reported_date).days + 1
average_distance_per_day = (
    daily_distances.loc[
        daily_distances["DATE"] <= last_reported_activity_date, "DIST (km)"
    ].sum()
    / days_elapsed
    * MILES_PER_KILOMETRE
)
daily_chart = daily_distances.loc[daily_distances["DIST (km)"] > 0].copy()
daily_chart["Date"] = daily_chart["DATE"]
daily_chart = daily_chart.sort_values("Date")
daily_chart["Date"] = daily_chart["Date"].dt.strftime("%d %b")
daily_chart["Distance (miles)"] = daily_chart["DIST (km)"] * MILES_PER_KILOMETRE
st.bar_chart(daily_chart, x="Date", y="Distance (miles)")
with st.container(border=True):
    st.metric("Average distance per day", f"{average_distance_per_day:.2f} miles")

participant_table = participant_distances[["PARTICIPANT", "DISTANCE"]].copy()
participant_table["DISTANCE"] *= MILES_PER_KILOMETRE
participant_table = (
    participant_table.rename(
        columns={
            "PARTICIPANT": "Participant",
            "DISTANCE": "Total distance (miles)",
        }
    )
    .sort_values("Total distance (miles)", ascending=False)
    .reset_index(drop=True)
)


def longest_activity(activity_type):
    activities = activity_log.loc[activity_log["ACTIVITY"] == activity_type]
    longest_distance_km = activities["DIST (km)"].max()
    participants = activities.loc[
        activities["DIST (km)"] == longest_distance_km, "PARTICIPANT"
    ].drop_duplicates()
    return (
        longest_distance_km,
        longest_distance_km * MILES_PER_KILOMETRE,
        ", ".join(participants),
    )


longest_run_km, longest_run_miles, longest_run_participants = longest_activity("RUN")
longest_walk_km, longest_walk_miles, longest_walk_participants = longest_activity("WALK")
activity_counts = activity_log["PARTICIPANT"].value_counts()
max_activities = activity_counts.max()
most_active_participants = ", ".join(
    activity_counts[activity_counts == max_activities].index
)
activity_type_totals = activity_log.groupby("ACTIVITY").agg(
    activities=("PARTICIPANT", "size"),
    distance_km=("DIST (km)", "sum"),
)
run_count = int(activity_type_totals.loc["RUN", "activities"])
run_miles = activity_type_totals.loc["RUN", "distance_km"] * MILES_PER_KILOMETRE
walk_count = int(activity_type_totals.loc["WALK", "activities"])
walk_miles = activity_type_totals.loc["WALK", "distance_km"] * MILES_PER_KILOMETRE
activity_log["DATE"] = pd.to_datetime(activity_log["DATE"], format="%d/%m/%y")
daily_activity_totals = activity_log.groupby("DATE").agg(
    activities=("PARTICIPANT", "size"),
    distance_km=("DIST (km)", "sum"),
)
busiest_activity_count = daily_activity_totals["activities"].max()
busiest_days = daily_activity_totals.loc[
    daily_activity_totals["activities"] == busiest_activity_count
]
busiest_day_dates = ", ".join(date.strftime("%d %b") for date in busiest_days.index)
busiest_day_summary = " / ".join(
    f"{int(day['activities'])} activities · "
    f"{day['distance_km'] * MILES_PER_KILOMETRE:.2f} mi"
    for _, day in busiest_days.iterrows()
)

participant_column, highlights_column = st.columns(2, gap="small")
with participant_column:
    st.subheader("Distance Per Participant")
    st.dataframe(
        participant_table,
        hide_index=True,
        width="content",
        column_config={
            "Total distance (miles)": st.column_config.NumberColumn(format="%.2f mi")
        },
    )

with highlights_column:
    st.subheader("Activity Highlights")
    run_column, walk_column = st.columns(2)
    with run_column:
        with st.container(border=True):
            st.metric("Runs", f"{run_count}", f"{run_miles:.2f} mi total", delta_color="off")
    with walk_column:
        with st.container(border=True):
            st.metric("Walks", f"{walk_count}", f"{walk_miles:.2f} mi total", delta_color="off")

    longest_run_column, longest_walk_column = st.columns(2)
    with longest_run_column:
        with st.container(border=True):
            st.metric(
                "Longest run",
                f"{longest_run_miles:.2f} mi",
                f"{longest_run_km:.2f} km · {longest_run_participants}",
                delta_color="off",
            )
    with longest_walk_column:
        with st.container(border=True):
            st.metric(
                "Longest walk",
                f"{longest_walk_miles:.2f} mi",
                f"{longest_walk_km:.2f} km · {longest_walk_participants}",
                delta_color="off",
            )

    most_active_column, busiest_day_column = st.columns(2)
    with most_active_column:
        with st.container(border=True):
            st.metric(
                "Most activities",
                f"{max_activities} activities",
                most_active_participants,
                delta_color="off",
            )
    with busiest_day_column:
        with st.container(border=True):
            st.metric(
                "Busiest day",
                busiest_day_dates,
                busiest_day_summary,
                delta_color="off",
            )

st.caption("Distances are converted from kilometres to miles.")
