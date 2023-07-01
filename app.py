"""Creates a map application using Streamlit."""

# pylint: disable=import-error

import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import dotenv


def main() -> None:
    """The main function of the app."""

    if os.path.exists(".env"):
        dotenv.load_dotenv(".env")
        token = os.environ["MAPBOX_TOKEN"]
    else:
        token = None

    # Connect to the SQLite database
    engine = create_engine("sqlite:///processed.db")
    # Query the database and load data into a Pandas DataFrame
    query = "SELECT * FROM presampled_points"

    data = pd.read_sql_query(query, engine)

    data["tUNITS"] = data["tUNITS"].astype(float)
    data["vacant"] = data["vacant"].astype(bool)
    data["zipcode_str"] = data["zipcode_str"].astype(str)
    data["x"] = data["x"].astype(float)
    data["y"] = data["y"].astype(float)

    data["lat"] = data["y"]
    data["lon"] = data["x"]

    # Sidebar filters
    st.sidebar.header("Filters")
    st.sidebar.header("Filters")
    selected_units = st.sidebar.slider(
        "tUNITS",
        min_value=min(data["tUNITS"]),
        max_value=max(data["tUNITS"]),
        value=(min(data["tUNITS"]), max(data["tUNITS"])),
    )
    selected_building_types = st.sidebar.multiselect(
        "Building Type",
        data["building_type"].unique(),
        default=data["building_type"].unique(),
    )
    selected_zipcode = st.sidebar.text_input("Zipcode", "")
    selected_vacant = st.sidebar.selectbox("Vacant", ["All", "Vacant", "Not Vacant"])

    # Apply filters to the DataFrame
    filtered = data[
        (data["tUNITS"] >= selected_units[0])
        & (data["tUNITS"] <= selected_units[1])
        & (data["building_type"].isin(selected_building_types))
        & (data["zipcode_str"].str.contains(selected_zipcode))
        & (
            (selected_vacant == "All")
            | (data["vacant"] == (selected_vacant == "Vacant"))
        )
    ]

    # Display the filtered DataFrame
    st.dataframe(filtered)

    # Create and display the map
    st.header("Building Map")
    st.write(f"Number of buildings: {len(filtered)}")

    if len(filtered) > 1000:
        st.warning("Too many buildings to display. Showing 1000 random buildings.")
        filtered = filtered.sample(1000)

    fig = px.scatter_mapbox(filtered, lat="y", lon="x", color="building_type", zoom=9)
    if token:
        fig.update_layout(mapbox_style="basic", mapbox_accesstoken=token)
    else:
        fig.update_layout(mapbox_style="open-street-map")

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=False)


if __name__ == "__main__":
    main()
