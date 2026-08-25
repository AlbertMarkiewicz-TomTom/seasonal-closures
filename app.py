import json
from datetime import datetime
import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

st.set_page_config(page_title="Seasonal Closures Explorer", layout="wide")

MONTH_MAP = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

DISPLAY_MONTHS = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
DISPLAY_ORDER = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]

# Unified dashboard colors #659314"
OPEN_COLOR = "#659314"
CLOSED_COLOR = "#ff8c00"
OTHER_COLOR = "#ffd700"

STATUS_COLORS = {
    "open": OPEN_COLOR,
    "closed": CLOSED_COLOR,
    "conditional": OTHER_COLOR,
    "other": OTHER_COLOR,
}

MAP_STATUS_COLORS = {
    "open": OPEN_COLOR,
    "closed": CLOSED_COLOR,
    "conditional": OTHER_COLOR,
    "other": OTHER_COLOR,
}

st.sidebar.title("Data Source")
uploaded = st.sidebar.file_uploader("Load JSON file", type=["json"])

if uploaded is None:
    st.info("Upload a JSON file to start.")
   
with st.expander(
    "Instructions for Creating Seasonal Road Closure JSON Files",
    expanded=False,
):
    st.markdown("""
    Purpose

Use the prompt below to create a downloadable JSON file containing roads that are regularly closed during winter or another recurring season.

The resulting file must be compatible with the road closure application and must follow the required schema exactly.

Ready-to-use prompt

Replace [COUNTRY] with the required country name.

Search the internet thoroughly for roads in [COUNTRY] that are regularly closed during winter or another recurring season.
 
Focus on confirmed recurring seasonal closures, including:
 
- mountain roads and mountain passes;
- scenic roads;
- roads in national and provincial parks;
- remote regional roads;
- roads closed because of snow, avalanche risk, wildlife protection, winter maintenance limitations, or seasonal border operations;
- private or toll roads only if they are open to public motor traffic during the operating season.
 
Use current and reliable sources. Prioritize:
 
1. official national road authorities;
2. official regional or provincial road authorities;
3. national park authorities;
4. local government websites;
5. official tourism organizations;
6. reliable traffic information services.
 
Do not include:
 
- roads closed only because of temporary construction;
- roads affected only by short-term weather events;
- permanently closed roads;
- hiking trails;
- cycling-only routes;
- roads that are open throughout the year but may occasionally close during storms;
- unverified locations;
- duplicate sections of the same road, unless the sections have different seasonal closure schedules.
 
Create a downloadable JSON file using exactly the following structure:
 
{
"records": [
{
"name": "Location or road section name",
"road": "Official road number or road name",
"coordinates": "latitude, longitude",
"status": "open",
"estimated_closing_time": "October",
"estimated_opening_time": "May"
}
]
}
 
Follow these data rules exactly:
 
1. The root object must contain one field named "records".
2. "records" must be an array.
3. Every record must contain exactly these six fields:
- "name"
- "road"
- "coordinates"
- "status"
- "estimated_closing_time"
- "estimated_opening_time"
4. Do not add fields such as "note", "source", "country", "region", "id", or "description".
5. All field names and values must be written in English, except official place names and official road names.
6. Coordinates must use the format:
"latitude, longitude"
7. Use decimal degrees with a period as the decimal separator.
8. Use the coordinates of a representative point on the seasonally closed road section, mountain pass, or closure gate.
9. Do not invent coordinates. Verify them using reliable maps or official geographic information.
10. If coordinates cannot be verified reliably, use:
"coordinates": null
11. The "status" field must represent the expected or confirmed status on the date when the file is created.
12. Use only:
"status": "open"
or:
"status": "closed"
13. Do not automatically set every road to "closed" merely because it is seasonally closed in winter.
14. If the file is created during the normal summer operating season, roads should normally have "status": "open", unless a current reliable source confirms that a road remains closed.
15. If the file is created during the normal winter closure season, use "status": "closed" when the seasonal schedule or current traffic information confirms the closure.
16. Check the current date before assigning the status.
17. The "estimated_closing_time" field means the month in which the road normally closes. It does not mean the entire period during which the road remains closed.
18. The "estimated_opening_time" field means the month in which the road normally reopens.
19. Time fields may contain only English month names.
20. If the exact month is uncertain, a maximum of two consecutive months may be used, for example:
"October–November"
"May–June"
21. Use an en dash between two months.
22. Do not use terms such as:
- early May
- mid-May
- late May
- spring
- summer
- winter
- weather dependent
- variable
- unknown
23. Valid examples include:
"estimated_closing_time": "October"
"estimated_closing_time": "October–November"
"estimated_opening_time": "May"
"estimated_opening_time": "May–June"
24. Do not represent the full closure period as:
"estimated_closing_time": "October–May"
25. Before creating the file, verify every record against at least one reliable source.
26. Use at least two independent sources for uncertain dates, road numbers, coordinates, or seasonal status whenever possible.
27. Prefer official information if sources conflict.
28. Remove records that cannot be verified with sufficient confidence.
29. Avoid duplicate records based on the combination of "name" and "road".
30. Use the official road number that applies to the seasonally closed section. Do not use an outdated road number if a current one can be verified.
 
Before returning the file, perform the following validation:
 
- validate the JSON syntax;
- confirm that the file contains a root object with a "records" array;
- confirm that every record has exactly the six required fields;
- confirm that every status is either "open" or "closed";
- confirm that every time value contains only one English month or two English months separated by an en dash;
- confirm that no value contains "early", "mid", "late", "spring", "summer", "winter", "variable", or a full closure period;
- confirm that coordinates are valid decimal coordinates or null;
- confirm that there are no duplicate records;
- confirm that the status is appropriate for the current date;
- confirm that the file is not empty.
 
Save the completed file as:
 
[COUNTRY]_seasonal_closures.json
 
Provide the completed JSON as a directly downloadable file. Do not return only a JSON code block.
 
After creating the file, briefly report:
 
- the total number of records;
- the number of records marked "open";
- the number of records marked "closed";
- the main official sources used;
- any records for which coordinates or dates are approximate.

Expected JSON format
{
"records": [
{
"name": "Example Mountain Road",
"road": "Road F123",
"coordinates": "64.123456, -18.123456",
"status": "open",
"estimated_closing_time": "October–November",
"estimated_opening_time": "May–June"
}
]
}
    """)
    
    st.stop()

data = json.load(uploaded)
country = "Seasonal Closures Dashboard"

if isinstance(data, dict):
    country = data.get("country", country)
    records = data.get("records", [])
elif isinstance(data, list):
    records = data
else:
    st.error("Unsupported JSON structure")
    st.stop()

df = pd.DataFrame(records)

if df.empty:
    st.warning("The uploaded JSON file does not contain any records.")
    st.stop()

if "coordinates" in df.columns:
    coords = df["coordinates"].astype(str).str.split(",", expand=True)
    if len(coords.columns) >= 2:
        df["lat"] = pd.to_numeric(coords[0].str.strip(), errors="coerce")
        df["lon"] = pd.to_numeric(coords[1].str.strip(), errors="coerce")
else:
    df["lat"] = pd.NA
    df["lon"] = pd.NA

search_text = st.sidebar.text_input("Search road/location")

if "status" in df.columns:
    statuses = sorted(df["status"].dropna().unique())
    selected = st.sidebar.multiselect("Status", statuses, default=statuses)
    filtered = df[df["status"].isin(selected)].copy()
else:
    filtered = df.copy()

if search_text:
    name_col = filtered["name"].astype(str) if "name" in filtered.columns else ""
    road_col = filtered["road"].astype(str) if "road" in filtered.columns else ""
    filtered = filtered[
        name_col.str.contains(search_text, case=False, na=False)
        | road_col.str.contains(search_text, case=False, na=False)
    ]

st.title(country)

c1, c2, c3 = st.columns(3)
c1.metric("Locations", len(filtered))

if "status" in filtered.columns:
    c2.metric("Closed", len(filtered[filtered["status"] == "closed"]))
    c3.metric("Open", len(filtered[filtered["status"] == "open"]))


def months(text):
    if not isinstance(text, str):
        return []

    found = [v for k, v in MONTH_MAP.items() if k in text.lower()]

    if len(found) == 1:
        return found

    if len(found) >= 2:
        a, b = found[0], found[-1]
        if a <= b:
            return list(range(a, b + 1))
        return list(range(a, 13)) + list(range(1, b + 1))

    return []


def closed_period(close_txt, open_txt):
    close_m = months(close_txt)
    open_m = months(open_txt)
    transition = set(close_m + open_m)

    if not close_m or not open_m:
        return set(), transition

    start = close_m[-1]
    end = open_m[0]
    closed = set()
    m = (start % 12) + 1

    while m != end:
        closed.add(m)
        m = (m % 12) + 1

    return closed, transition


CURRENT_MONTH = datetime.now().month


def current_status(row):
    closed, transition = closed_period(
        row.get("estimated_closing_time", ""),
        row.get("estimated_opening_time", ""),
    )

    if CURRENT_MONTH in transition:
        return "conditional"
    if CURRENT_MONTH in closed:
        return "closed"
    return "open"


filtered["current_status"] = filtered.apply(current_status, axis=1)

map_tab, timeline_tab, overview_tab, stats_tab = st.tabs(
    ["🗺 Map & Records", "❄️ Winter Timeline", "📅 Monthly Overview", "📊 Statistics"]
)

with map_tab:
    mdf = filtered.dropna(subset=["lat", "lon"])

    st.markdown(
        f"""
        <div style="
            background-color:#ffffff;
            color:#111111;
            padding:10px 12px;
            border-radius:6px;
            border:1px solid #dddddd;
            margin-bottom:10px;
            max-width:320px;
            box-shadow:0 1px 3px rgba(0,0,0,0.12);
            font-size:14px;
            line-height:1.45;
        ">
            <div style="font-weight:700;color:#111111;margin-bottom:4px;">Map legend</div>
            <div style="color:#111111;"><span style="color:{OPEN_COLOR};font-size:50px;line-height:30px;">●</span> Open road</div>
            <div style="color:#111111;"><span style="color:{CLOSED_COLOR};font-size:50px;line-height:50px;">●</span> Closed road</div>
            <div style="color:#111111;"><span style="color:{OTHER_COLOR};font-size:50px;line-height:50px;">●</span> Other status</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not mdf.empty:
        m = folium.Map(location=[mdf.lat.mean(), mdf.lon.mean()], zoom_start=5)

        for _, r in mdf.iterrows():
            status = str(r.get("current_status", "")).lower()
            color = MAP_STATUS_COLORS.get(status, "#999999")

            popup = (
                f"<b>{r.get('name', '')}</b><br>"
                f"Road: {r.get('road', '')}<br>"
                f"Status: {status}<br>"
                f"Coordinates: {r['lat']:.6f}, {r['lon']:.6f}"
            )

            folium.CircleMarker(
                location=[r["lat"], r["lon"]],
                radius=8,
                color="black",
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.75,
                popup=popup,
            ).add_to(m)

        st_folium(m, width="100%", height=650)
    else:
        st.warning("No valid coordinates available for the selected records.")

    st.data_editor(filtered, use_container_width=True, disabled=True, hide_index=True)

with timeline_tab:
    st.markdown("### Color legend")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="background:#OPEN_COLOR;padding:9px;text-align:center;border-radius:5px;border:1px solid #OPEN_COLOR;">
                <b>OPEN</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="background:CLOSED_COLOR;padding:9px;text-align:center;border-radius:5px;color:white;border:1px solid CLOSED_COLOR;">
                <b>CLOSED</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div style="
                background:
                    repeating-linear-gradient(
                        -45deg,
                        CLOSED_COLOR,
                        CLOSED_COLOR 6px,
                        OPEN_COLOR 6px,
                        OPEN_COLOR 10px
                    );
                padding:9px;
                text-align:center;
                border-radius:5px;
                border:1px solid OPEN_COLOR;
                color:white;
                font-weight:bold;
            ">
                TRANSITIONAL PERIOD
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(18, max(8, len(filtered) * 0.6)))

    for row_idx, (_, row) in enumerate(filtered.iterrows()):
        closed, transition = closed_period(
            row.get("estimated_closing_time", ""),
            row.get("estimated_opening_time", ""),
        )

        for pos, month in enumerate(DISPLAY_ORDER):
            if month in transition:
                ax.add_patch(
                    Rectangle(
                        (pos, row_idx - 0.4),
                        1,
                        0.8,
                        facecolor=CLOSED_COLOR,
                        edgecolor=OPEN_COLOR,
                        hatch="//////",
                    )
                )
            elif month in closed:
                ax.add_patch(
                    Rectangle(
                        (pos, row_idx - 0.4),
                        1,
                        0.8,
                        facecolor=CLOSED_COLOR,
                        edgecolor=CLOSED_COLOR,
                    )
                )
            else:
                ax.add_patch(
                    Rectangle(
                        (pos, row_idx - 0.4),
                        1,
                        0.8,
                        facecolor=OPEN_COLOR,
                        edgecolor=OPEN_COLOR,
                    )
                )

    labels = [f"{r.get('name', '')} ({r.get('road', '')})" for _, r in filtered.iterrows()]

    ax.set_xlim(0, 12)
    ax.set_ylim(-1, len(labels))
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xticks(range(12))
    ax.set_xticklabels(DISPLAY_MONTHS)
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    ax.set_title("Winter closure timeline")


    st.pyplot(fig, use_container_width=True)

with overview_tab:
    selected_month = st.selectbox("Select month", list(MONTH_MAP.keys()))
    month_num = MONTH_MAP[selected_month]

    def is_closed_for_month(row, month_num):
        closed, transition = closed_period(
            row.get("estimated_closing_time", ""),
            row.get("estimated_opening_time", ""),
        )
        return month_num in closed or month_num in transition

    roads_closed = filtered[
        filtered.apply(
            lambda r: is_closed_for_month(r, month_num),
            axis=1,
        )
    ]

    st.metric("Roads closed", len(roads_closed))
    st.dataframe(roads_closed, use_container_width=True)

with stats_tab:
    ranking = filtered.copy()
    ranking["months_closed"] = ranking.apply(
        lambda r: len(
            closed_period(
                r.get("estimated_closing_time", ""),
                r.get("estimated_opening_time", ""),
            )[0]
        ),
        axis=1,
    )
    ranking = ranking.sort_values("months_closed", ascending=False)

    st.subheader("Longest Seasonal Closures")

    available_cols = [col for col in ["name", "road", "months_closed"] if col in ranking.columns]
    st.dataframe(ranking[available_cols], use_container_width=True)

    monthly = []
    for month in range(1, 13):
        monthly.append(
            filtered.apply(
                lambda r: month
                in closed_period(
                    r.get("estimated_closing_time", ""),
                    r.get("estimated_opening_time", ""),
                )[0],
                axis=1,
            ).sum()
        )

    fig2, ax2 = plt.subplots()
    ax2.bar(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], monthly)
    ax2.set_title("Closed roads by month")
    ax2.set_ylabel("Number of closed roads")
    st.pyplot(fig2, use_container_width=True)
