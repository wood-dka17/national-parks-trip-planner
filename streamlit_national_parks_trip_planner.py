import streamlit as st
import pandas as pd
import math
import pydeck as pdk

st.set_page_config(page_title="National Parks Trip Planner", layout="wide")

# -----------------------------
# Data: All 63 National Parks
# -----------------------------
parks = [
    ("Acadia","ME",44.35,-68.21),
    ("American Samoa","AS",-14.26,-170.68),
    ("Arches","UT",38.68,-109.57),
    ("Badlands","SD",43.75,-102.50),
    ("Big Bend","TX",29.25,-103.25),
    ("Biscayne","FL",25.65,-80.08),
    ("Black Canyon of the Gunnison","CO",38.57,-107.72),
    ("Bryce Canyon","UT",37.59,-112.18),
    ("Canyonlands","UT",38.20,-109.93),
    ("Capitol Reef","UT",38.37,-111.26),
    ("Carlsbad Caverns","NM",32.17,-104.44),
    ("Channel Islands","CA",34.01,-119.42),
    ("Congaree","SC",33.79,-80.78),
    ("Crater Lake","OR",42.94,-122.10),
    ("Cuyahoga Valley","OH",41.28,-81.57),
    ("Death Valley","CA/NV",36.53,-116.93),
    ("Denali","AK",63.11,-151.00),
    ("Dry Tortugas","FL",24.63,-82.87),
    ("Everglades","FL",25.29,-80.90),
    ("Gates of the Arctic","AK",67.78,-153.30),
    ("Gateway Arch","MO",38.62,-90.19),
    ("Glacier","MT",48.80,-114.00),
    ("Glacier Bay","AK",58.50,-137.00),
    ("Grand Canyon","AZ",36.10,-112.11),
    ("Grand Teton","WY",43.79,-110.68),
    ("Great Basin","NV",38.98,-114.30),
    ("Great Sand Dunes","CO",37.73,-105.51),
    ("Great Smoky Mountains","TN/NC",35.68,-83.53),
    ("Guadalupe Mountains","TX",31.92,-104.87),
    ("Haleakalā","HI",20.72,-156.17),
    ("Hawaiʻi Volcanoes","HI",19.38,-155.20),
    ("Hot Springs","AR",34.52,-93.05),
    ("Indiana Dunes","IN",41.65,-87.06),
    ("Isle Royale","MI",48.10,-88.55),
    ("Joshua Tree","CA",33.87,-115.90),
    ("Katmai","AK",58.60,-154.70),
    ("Kenai Fjords","AK",59.92,-149.65),
    ("Kings Canyon","CA",36.80,-118.55),
    ("Kobuk Valley","AK",67.55,-159.28),
    ("Lake Clark","AK",60.97,-153.42),
    ("Lassen Volcanic","CA",40.49,-121.51),
    ("Mammoth Cave","KY",37.18,-86.10),
    ("Mesa Verde","CO",37.23,-108.46),
    ("Mount Rainier","WA",46.85,-121.75),
    ("New River Gorge","WV",38.07,-81.08),
    ("North Cascades","WA",48.77,-121.30),
    ("Olympic","WA",47.97,-123.50),
    ("Petrified Forest","AZ",35.07,-109.78),
    ("Pinnacles","CA",36.48,-121.16),
    ("Redwood","CA",41.30,-124.00),
    ("Rocky Mountain","CO",40.40,-105.58),
    ("Saguaro","AZ",32.25,-110.50),
    ("Sequoia","CA",36.48,-118.57),
    ("Shenandoah","VA",38.53,-78.35),
    ("Theodore Roosevelt","ND",46.97,-103.45),
    ("Virgin Islands","VI",18.34,-64.73),
    ("Voyageurs","MN",48.50,-92.88),
    ("White Sands","NM",32.78,-106.33),
    ("Wind Cave","SD",43.57,-103.48),
    ("Wrangell–St. Elias","AK",61.00,-142.00),
    ("Yellowstone","WY/MT/ID",44.60,-110.50),
    ("Yosemite","CA",37.83,-119.50),
    ("Zion","UT",37.30,-113.05),
]

df = pd.DataFrame(parks, columns=["Park","State","lat","lon"])

# -----------------------------
# Helper Functions
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def optimize_order(df, parks):
    if len(parks) <= 2:
        return parks

    remaining = parks.copy()
    ordered = [remaining.pop(0)]

    while remaining:
        last = df[df.Park == ordered[-1]].iloc[0]
        next_park = min(
            remaining,
            key=lambda p: haversine(
                last.lat, last.lon,
                df[df.Park == p].iloc[0].lat,
                df[df.Park == p].iloc[0].lon
            )
        )
        ordered.append(next_park)
        remaining.remove(next_park)

    return ordered

def get_route_coordinates(df, ordered_parks):
    return [[df[df.Park == p].iloc[0].lon, df[df.Park == p].iloc[0].lat] for p in ordered_parks]

# -----------------------------
# UI
# -----------------------------
st.title("🏞️ U.S. National Parks Trip Planner")

col1, col2 = st.columns([1, 2])

with col1:
    selected = st.multiselect("Choose parks:", df["Park"].tolist())
    optimize_route = st.toggle(
        "Optimize park order to minimize drive distance",
        help="Automatically group nearby parks together"
    )
    avg_speed = st.slider("Estimated driving speed (mph)", 45, 75, 60)

# Determine effective order (THIS is the key fix)
if optimize_route and len(selected) >= 2:
    ordered_parks = optimize_order(df, selected)
    st.caption("Park order optimized to reduce total distance")
else:
    ordered_parks = selected

with col2:
    layers = []

    # Park points
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_radius=60000,
            get_color=[0, 100, 200, 160],
            pickable=True,
        )
    )

    # Route line
    if len(ordered_parks) >= 2:
        route_coords = get_route_coordinates(df, ordered_parks)
        layers.append(
            pdk.Layer(
                "PathLayer",
                data=[{"path": route_coords}],
                get_path="path",
                get_width=5,
                get_color=[160, 32, 240],  # purple
                width_scale=20,
                width_min_pixels=3,
            )
        )

    view = pdk.ViewState(latitude=39.5, longitude=-98.35, zoom=3.5)
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view))

# -----------------------------
# Itinerary Table
# -----------------------------
if len(ordered_parks) >= 2:
    rows = []
    total_dist = 0

    for i in range(len(ordered_parks) - 1):
        p1 = df[df.Park == ordered_parks[i]].iloc[0]
        p2 = df[df.Park == ordered_parks[i + 1]].iloc[0]
        dist = haversine(p1.lat, p1.lon, p2.lat, p2.lon)
        hours = dist / avg_speed
        total_dist += dist

        rows.append({
            "From": ordered_parks[i],
            "To": ordered_parks[i + 1],
            "Distance (miles)": round(dist, 1),
            "Est. Drive Time (hrs)": round(hours, 1),
        })

    itinerary = pd.DataFrame(rows)
    st.subheader("Trip Distances")
    st.dataframe(itinerary, width="stretch")
    st.metric("Total Distance (miles)", round(total_dist, 1))
else:
    st.info("Select at least two parks to calculate distances.")
