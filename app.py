import streamlit as st
import uuid
import urllib.parse
from datetime import date, timedelta
from mysql.connector import Error
from database import get_connection
from api import get_destination_names, get_destination_details, search_flights, search_trains, search_buses
from pdf_generator import generate_booking_pdf

st.set_page_config(page_title="Travel Booking & Trip Management", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
#MainMenu, footer, [data-testid="stToolbar"] {visibility:hidden;}
header[data-testid="stHeader"] {background: transparent!important; box-shadow: none!important; height: 0px!important;}
.block-container {max-width:1450px; padding-top:0.8rem!important; padding-bottom:1rem;}
.stApp {background: radial-gradient(circle at 15% 15%, #bfdbfe 0%, transparent 35%), radial-gradient(circle at 85% 15%, #fbcfe8 0%, transparent 35%), linear-gradient(135deg,#f8fafc,#eef2ff); background-attachment: fixed;}
.page-title { font-size:36px; font-weight:900; background:linear-gradient(90deg,#1d4ed8,#7c3aed,#db2777); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0px; }
.login-title { text-align:center;font-size:42px;font-weight:900; background:linear-gradient(90deg,#2563eb,#7c3aed,#db2777); -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.login-subtitle {text-align:center;color:#64748b;font-size:17px;margin-bottom:20px;}
.hero { background:linear-gradient(135deg,#1e3a8a,#4f46e5,#7c3aed,#db2777); border-radius:24px;padding:28px;color:white;margin:10px 0; }
.hero h1 {color:white!important;}.hero p {color:#e0e7ff!important;}
div[data-testid="stVerticalBlockBorderWrapper"] { background:rgba(255,255,255,0.95); border-radius:18px; border:1px solid #e2e8f0; box-shadow:0 8px 25px rgba(15,23,42,0.08); }
.stImage img {width:100%;height:210px;object-fit:cover;border-radius:12px;}
.stButton > button { background:linear-gradient(90deg,#2563eb,#7c3aed);color:white;border:none; border-radius:12px;font-weight:700;min-height:40px; }
.stDownloadButton > button { background:linear-gradient(90deg,#2563eb,#7c3aed)!important; color:white!important; width:100%; border-radius:10px; border:none; font-weight:700; }
section[data-testid="stSidebar"] {background:linear-gradient(180deg,#0f172a,#172554,#312e81);}
section[data-testid="stSidebar"] * {color:white;}
div[data-testid="stMetric"]{background:white; padding:10px; border-radius:12px; border:1px solid #e2e8f0}
div[data-testid="stMetric"] label, div[data-testid="stMetric"] div{color:#0f172a!important}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "customer_id" not in st.session_state: st.session_state.customer_id = None
if "customer_name" not in st.session_state: st.session_state.customer_name = None

def execute_query(query, params=(), fetch=False, dictionary=False):
    conn = None; cursor = None
    try:
        conn = get_connection(); cursor = conn.cursor(dictionary=dictionary)
        cursor.execute(query, params)
        if fetch: return cursor.fetchall()
        conn.commit(); return cursor.lastrowid
    except Error as e:
        if conn: conn.rollback()
        st.error(f"Database error: {e}"); return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def fetch_one(query, params=(), dictionary=True):
    rows = execute_query(query, params, fetch=True, dictionary=dictionary)
    return rows[0] if rows else None
def money(value): return f"₹{float(value or 0):,.2f}"
def page_title(title, subtitle=""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle: st.caption(subtitle)

if not st.session_state.logged_in:
    st.markdown('<div class="login-title">✈️ Travel Booking & Trip Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Explore the world • Book your dream • Create memories</div>', unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.5, 1])
    with center:
        auth_mode = st.radio("Account", ["Login", "Register"], horizontal=True)
        if auth_mode == "Login":
            st.subheader("Welcome Back 👋")
            email = st.text_input("Email"); password = st.text_input("Password", type="password")
            if st.button("🔐 Login", use_container_width=True):
                if not email.strip() or not password: st.warning("Enter your email and password.")
                else:
                    user = fetch_one("SELECT customer_id, full_name FROM customers WHERE email=%s AND password=%s", (email.strip(), password))
                    if user:
                        st.session_state.logged_in = True; st.session_state.customer_id = user["customer_id"]; st.session_state.customer_name = user["full_name"]; st.rerun()
                    else: st.error("Invalid email or password.")
        else:
            st.subheader("Create Your Account 📝")
            full_name = st.text_input("Full Name"); email = st.text_input("Email"); phone = st.text_input("Phone"); address = st.text_area("Address")
            password = st.text_input("Password", type="password"); confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("📝 Create Account", use_container_width=True):
                if not full_name.strip() or not email.strip() or not password: st.warning("Fill in all required fields.")
                elif password!= confirm_password: st.error("Passwords do not match.")
                else:
                    existing = fetch_one("SELECT customer_id FROM customers WHERE email=%s", (email.strip(),))
                    if existing: st.error("Email already registered.")
                    else:
                        result = execute_query("INSERT INTO customers (full_name,email,phone,address,password) VALUES (%s,%s,%s,%s,%s)", (full_name.strip(), email.strip(), phone.strip(), address.strip(), password))
                        if result is not None: st.success("Account created! Please select Login.")
    st.stop()

st.sidebar.markdown("## ✈️ Travel Booking")
st.sidebar.success(f"Welcome, {st.session_state.customer_name}!")
menu = st.sidebar.radio("EXPLORE", ["🏠 Dashboard","🌴 Destinations","🎒 Tour Packages","🏨 Hotels","✈️ Transport Search","🗺️ Maps","🎫 Book Package","💳 Payment","📋 Itinerary","❌ Cancellation","⭐ Reviews","🧳 Trip History","🎫 My Bookings",])
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False; st.session_state.customer_id = None; st.session_state.customer_name = None; st.rerun()

if menu == "🏠 Dashboard":
    page_title("✈️ Explore the World", "Your complete travel companion")
    st.markdown('<div class="hero"><h1>Discover. Book. Travel. 🌎</h1><p>Explore destinations, tour packages, hotels and transport. Manage your travel in one application.</p></div>', unsafe_allow_html=True)
    dc = fetch_one("SELECT COUNT(*) AS total FROM destinations") or {"total": 0}; pc = fetch_one("SELECT COUNT(*) AS total FROM tour_packages") or {"total": 0}; hc = fetch_one("SELECT COUNT(*) AS total FROM hotels") or {"total": 0}; bc = fetch_one("SELECT COUNT(*) AS total FROM bookings WHERE customer_id=%s", (st.session_state.customer_id,)) or {"total": 0}
    c1, c2, c3, c4 = st.columns(4); c1.metric("🌴 Destinations", dc["total"]); c2.metric("🎒 Packages", pc["total"]); c3.metric("🏨 Hotels", hc["total"]); c4.metric("🎫 My Bookings", bc["total"])
    st.markdown("### 🌟 Popular Destinations")
    destinations = execute_query("SELECT * FROM destinations ORDER BY destination_id LIMIT 4", fetch=True, dictionary=True) or []
    cols = st.columns(4)
    for i, row in enumerate(destinations):
        with cols[i]:
            with st.container(border=True):
                if row.get("image_url"): st.image(row["image_url"], use_container_width=True)
                st.markdown(f"### 📍 {row['destination_name']}")
                st.caption(row.get("country") or ""); st.write((row.get("description") or "")[:100])

elif menu == "🌴 Destinations":
    page_title("🌴 Destinations", "Discover places around the world")
    search = st.text_input("🔎 Search destination")
    data = execute_query("SELECT * FROM destinations WHERE destination_name LIKE %s OR country LIKE %s ORDER BY destination_name", (f"%{search}%", f"%{search}%"), fetch=True, dictionary=True) or []
    if data:
        cols = st.columns(3)
        for i, row in enumerate(data):
            with cols[i % 3]:
                with st.container(border=True):
                    if row.get("image_url"): st.image(row["image_url"], use_container_width=True)
                    st.markdown(f"### 📍 {row['destination_name']}"); st.caption(f"🌎 {row.get('country') or ''}"); st.write((row.get("description") or "")[:90])

elif menu == "🎒 Tour Packages":
    page_title("🎒 Tour Packages", "Find your next adventure")
    api_names = get_destination_names(); selected_destination = st.selectbox("Explore destination details", api_names)
    details = get_destination_details(selected_destination)
    if details:
        st.markdown(f"## 🌴 {selected_destination}"); st.write(f"**Country:** {details.get('country', 'N/A')}"); st.write(details.get("description", "No description available."))
        price_val = details.get("price") or details.get("estimated_price")
        if price_val is not None: st.metric("Estimated trip price", money(price_val))
    st.divider(); st.markdown("### 🎒 Available Packages")
    search = st.text_input("Search package name")
    packages = execute_query("SELECT tp.*, d.destination_name, d.country FROM tour_packages tp JOIN destinations d ON tp.destination_id = d.destination_id WHERE tp.package_name LIKE %s OR d.destination_name LIKE %s ORDER BY tp.package_id", (f"%{search}%", f"%{search}%"), fetch=True, dictionary=True) or []
    if packages:
        cols = st.columns(2)
        for i, package in enumerate(packages):
            with cols[i % 2]:
                with st.container(border=True):
                    if package.get("image_url"): st.image(package["image_url"], use_container_width=True)
                    st.subheader(package["package_name"]); st.caption(f"{package['destination_name']}, {package['country']}"); st.markdown(f"### {money(package.get('price'))}")

elif menu == "🏨 Hotels":
    page_title("🏨 Hotels", "Find your comfortable stay")
    destinations = execute_query("SELECT destination_id, destination_name FROM destinations ORDER BY destination_name", fetch=True, dictionary=True) or []
    destination_names = ["All Destinations"] + [d["destination_name"] for d in destinations]
    selected_destination = st.selectbox("Choose destination", destination_names)
    search = st.text_input("Search hotel")
    query = "SELECT h.*, d.destination_name FROM hotels h JOIN destinations d ON h.destination_id = d.destination_id WHERE h.hotel_name LIKE %s"; params = [f"%{search}%"]
    if selected_destination!= "All Destinations": query += " AND d.destination_name = %s"; params.append(selected_destination)
    query += " ORDER BY h.rating DESC"
    hotels = execute_query(query, tuple(params), fetch=True, dictionary=True) or []
    if hotels:
        cols = st.columns(3)
        for i, hotel in enumerate(hotels):
            with cols[i % 3]:
                with st.container(border=True):
                    if hotel.get("image_url"): st.image(hotel["image_url"], use_container_width=True)
                    st.subheader(hotel["hotel_name"]); st.caption(hotel["destination_name"]); st.markdown(f"**{money(hotel.get('price_per_night'))} / night**")

elif menu == "✈️ Transport Search":
    page_title("✈️ Transport Search", "Search available travel options")
    tab1, tab2 = st.tabs(["Database Transport", "Travel API Demo"])
    with tab1:
        c1, c2 = st.columns(2)
        with c1: source = st.text_input("From", key="db_source")
        with c2: destination = st.text_input("To", key="db_destination")
        transport_type = st.selectbox("Transport type", ["All", "Flight", "Train", "Bus"], key="db_transport_type")
        query = "SELECT * FROM transport WHERE 1=1"; params = []
        if source: query += " AND source_location LIKE %s"; params.append(f"%{source}%")
        if destination: query += " AND destination_location LIKE %s"; params.append(f"%{destination}%")
        if transport_type!= "All": query += " AND transport_type = %s"; params.append(transport_type)
        query += " ORDER BY departure_time"
        results = execute_query(query, tuple(params), fetch=True, dictionary=True) or []
        for item in results:
            with st.container(border=True):
                st.subheader(f"{item['transport_type']} — {item['provider_name']}"); st.write(f"{item['source_location']} → {item['destination_location']}"); st.markdown(f"### {money(item.get('price'))}")
    with tab2:
        st.markdown("#### ✈️ Travel API Demo - Live Demo Search")
        st.caption("Demo transport search - works without any API key")
        c1, c2, c3 = st.columns(3)
        with c1: api_source = st.text_input("From City", "Hyderabad", key="api_source")
        with c2: api_dest = st.text_input("To City", "Goa", key="api_dest")
        with c3: api_date = st.date_input("Travel Date", key="api_date")
        api_type = st.selectbox("Transport Type", ["All", "Flight", "Train", "Bus"], key="api_type")
        if st.button("🔍 Search Travel API", use_container_width=True):
            if not api_source or not api_dest:
                st.warning("Please enter source and destination")
            elif api_source.lower() == api_dest.lower():
                st.warning("Source and destination cannot be same")
            else:
                all_results = []
                if api_type in ["All", "Flight"]: all_results.extend(search_flights(api_source, api_dest, api_date))
                if api_type in ["All", "Train"]: all_results.extend(search_trains(api_source, api_dest, api_date))
                if api_type in ["All", "Bus"]: all_results.extend(search_buses(api_source, api_dest, api_date))
                if all_results:
                    st.success(f"Found {len(all_results)} options from {api_source} to {api_dest}")
                    for item in all_results:
                        with st.container(border=True):
                            t = item['transport_type']; icon = "✈️" if t=="Flight" else "🚆" if t=="Train" else "🚌"
                            st.markdown(f"### {icon} {t} - {item['operator']}")
                            col1, col2, col3 = st.columns(3)
                            with col1: st.write(f"**{item['source']} → {item['destination']}**")
                            with col2: st.write(f"🕐 {item['departure']} - {item['arrival']} ({item['duration']})")
                            with col3: st.markdown(f"**{money(item['price'])}**")
                            st.caption(f"Date: {item['travel_date']}")
                else: st.info("No results found")

elif menu == "🗺️ Maps":
    page_title("🗺️ Travel Maps", "Explore your destination - Goa, Manali, Dubai & more")
    locations = execute_query("SELECT destination_id, destination_name, country, description, image_url, latitude, longitude FROM destinations WHERE latitude IS NOT NULL AND longitude IS NOT NULL ORDER BY destination_name", fetch=True, dictionary=True) or []
    if locations:
        place_names = ["🌍 All Places (World View)"] + [f"📍 {loc['destination_name']} - {loc['country']}" for loc in locations]
        selected_place = st.selectbox("Select place to view map", place_names)
        if selected_place == "🌍 All Places (World View)":
            st.markdown("### 🌍 All Destinations World Map")
            map_data = [{"latitude": float(row["latitude"]), "longitude": float(row["longitude"])} for row in locations]
            st.map(map_data, zoom=1)
        else:
            idx = place_names.index(selected_place) - 1; loc = locations[idx]
            lat = float(loc["latitude"]); lon = float(loc["longitude"])
            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.markdown(f"### 📍 {loc['destination_name']} Map - {loc['country']}")
                st.map([{"latitude": lat, "longitude": lon}], zoom=8)
                gmap_url = f"https://www.google.com/maps?q={lat},{lon}&z=12"
                st.link_button(f"🗺️ Open {loc['destination_name']} in Google Maps", gmap_url, use_container_width=True)
            with c2:
                with st.container(border=True):
                    if loc.get("image_url"): st.image(loc["image_url"], use_container_width=True)
                    st.subheader(loc["destination_name"]); st.caption(f"🌎 {loc['country']}"); st.write(loc.get("description") or "")

elif menu == "🎫 Book Package":
    page_title("🎫 Book Your Trip", "Create a travel booking")
    packages = execute_query("SELECT tp.package_id, tp.package_name, tp.destination_id, tp.duration_days, tp.price, d.destination_name FROM tour_packages tp JOIN destinations d ON tp.destination_id = d.destination_id ORDER BY tp.package_id", fetch=True, dictionary=True) or []
    hotels = execute_query("SELECT hotel_id, hotel_name, destination_id, price_per_night FROM hotels ORDER BY hotel_name", fetch=True, dictionary=True) or []
    transports = execute_query("SELECT transport_id, transport_type, provider_name, source_location, destination_location, price, destination_id FROM transport ORDER BY transport_id", fetch=True, dictionary=True) or []
    if packages and hotels and transports:
        package_labels = [f"{p['package_name']} — {p['destination_name']}" for p in packages]
        selected_package_label = st.selectbox("Select package", package_labels); selected_package = packages[package_labels.index(selected_package_label)]
        matching_hotels = [h for h in hotels if h["destination_id"] == selected_package["destination_id"]]
        if matching_hotels:
            hotel_labels = [h["hotel_name"] for h in matching_hotels]; selected_hotel_label = st.selectbox("Select hotel", hotel_labels); selected_hotel = matching_hotels[hotel_labels.index(selected_hotel_label)]
            matching_transports = [t for t in transports if t["destination_id"] == selected_package["destination_id"]]
            if matching_transports:
                transport_labels = [f"{t['transport_type']} — {t['provider_name']}" for t in matching_transports]
                selected_transport_label = st.selectbox("Select transport", transport_labels); selected_transport = matching_transports[transport_labels.index(selected_transport_label)]
                c1, c2 = st.columns(2)
                with c1: travel_date = st.date_input("Travel date", min_value=date.today(), value=date.today() + timedelta(days=1))
                with c2: people = st.number_input("Number of people", min_value=1, max_value=20, value=1)
                nights = max(1, int(selected_package["duration_days"]) - 1)
                total_amount = (float(selected_package["price"]) + float(selected_hotel["price_per_night"])*nights + float(selected_transport["price"]))*people
                st.metric("Total", money(total_amount))
                if st.button("🎫 Confirm Booking", use_container_width=True):
                    booking_id = execute_query("INSERT INTO bookings (customer_id, package_id, hotel_id, transport_id, travel_date, number_of_people, total_amount, booking_status) VALUES (%s,%s,%s,%s,%s,%s,%s,'Pending')", (st.session_state.customer_id, selected_package["package_id"], selected_hotel["hotel_id"], selected_transport["transport_id"], travel_date, people, total_amount))
                    if booking_id: st.success(f"Booking created! ID: {booking_id}")

elif menu == "💳 Payment":
    page_title("💳 Payment", "Demo payment management")
    bookings = execute_query("SELECT b.booking_id, b.total_amount, tp.package_name FROM bookings b LEFT JOIN tour_packages tp ON b.package_id=tp.package_id WHERE b.customer_id = %s AND b.booking_status!= 'Cancelled' ORDER BY b.booking_id DESC", (st.session_state.customer_id,), fetch=True, dictionary=True) or []
    if bookings:
        labels = [f"Booking #{b['booking_id']} — {b.get('package_name')} — {money(b['total_amount'])}" for b in bookings]
        selected_label = st.selectbox("Select booking", labels); selected = bookings[labels.index(selected_label)]
        st.metric("Amount payable", money(selected["total_amount"]))
        method = st.selectbox("Payment method", ["UPI", "Card", "Net Banking", "Cash"])
        if method == "UPI":
            qr_data = f"TravelBooking|Booking={selected['booking_id']}|Amount={selected['total_amount']}"
            qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=" + urllib.parse.quote(qr_data)
            st.image(qr_url, width=220)
        if st.button("✅ Confirm Demo Payment"):
            transaction_id = "TXN" + uuid.uuid4().hex[:10].upper()
            payment_id = execute_query("INSERT INTO payments (booking_id, payment_method, transaction_id, amount, payment_status) VALUES (%s,%s,%s,%s,'Success')", (selected["booking_id"], method, transaction_id, selected["total_amount"]))
            if payment_id is not None:
                execute_query("UPDATE bookings SET booking_status = 'Confirmed' WHERE booking_id = %s", (selected["booking_id"],)); st.success(f"Payment recorded: {transaction_id}")

elif menu == "📋 Itinerary":
    page_title("📋 Itinerary", "Plan activities")
    bookings = execute_query("SELECT b.booking_id, b.travel_date, tp.package_name, d.destination_name FROM bookings b JOIN tour_packages tp ON b.package_id = tp.package_id JOIN destinations d ON tp.destination_id = d.destination_id WHERE b.customer_id = %s AND b.booking_status = 'Confirmed' ORDER BY b.booking_id DESC", (st.session_state.customer_id,), fetch=True, dictionary=True) or []
    if bookings:
        labels = [f"#{b['booking_id']} — {b['package_name']}" for b in bookings]; selected_label = st.selectbox("Select booking", labels); selected = bookings[labels.index(selected_label)]
        with st.form("itinerary_form"):
            day_number = st.number_input("Day number", 1, 30, 1); activity_title = st.text_input("Activity title"); activity_description = st.text_area("Activity description"); location = st.text_input("Location", value=selected["destination_name"])
            submitted = st.form_submit_button("➕ Add Activity")
            if submitted and activity_title.strip():
                execute_query("INSERT INTO itinerary (booking_id, day_number, activity_date, activity_title, activity_description, location) VALUES (%s,%s,%s,%s,%s,%s)", (selected["booking_id"], day_number, selected["travel_date"], activity_title.strip(), activity_description.strip(), location.strip()))
                st.success("Added")

elif menu == "❌ Cancellation":
    page_title("❌ Cancel Booking", "Manage bookings")
    bookings = execute_query("SELECT booking_id, total_amount, booking_status FROM bookings WHERE customer_id = %s AND booking_status!= 'Cancelled' ORDER BY booking_id DESC", (st.session_state.customer_id,), fetch=True, dictionary=True) or []
    if bookings:
        labels = [f"Booking #{b['booking_id']} — {b['booking_status']}" for b in bookings]; selected_label = st.selectbox("Select booking", labels); selected = bookings[labels.index(selected_label)]
        reason = st.text_area("Reason")
        if st.button("❌ Confirm Cancellation"):
            execute_query("INSERT INTO cancellations (booking_id, reason, refund_amount, cancellation_status) VALUES (%s,%s,%s,'Requested')", (selected["booking_id"], reason or "No reason", selected["total_amount"]))
            execute_query("UPDATE bookings SET booking_status = 'Cancelled' WHERE booking_id = %s", (selected["booking_id"],)); st.success("Cancellation recorded.")

elif menu == "⭐ Reviews":
    page_title("⭐ Reviews", "Share experience")
    destinations = execute_query("SELECT destination_id, destination_name FROM destinations ORDER BY destination_name", fetch=True, dictionary=True) or []
    if destinations:
        selected_label = st.selectbox("Destination", [d["destination_name"] for d in destinations])
        selected_destination = destinations[[d["destination_name"] for d in destinations].index(selected_label)]
        rating = st.slider("Rating", 1, 5, 5)
        review_text = st.text_area("Write review", placeholder="Amazing experience! Super trip...")
        if st.button("⭐ Submit Review", use_container_width=True):
            if not review_text.strip():
                st.warning("Please write something!")
            else:
                execute_query("INSERT INTO reviews (customer_id, destination_id, rating, review_text) VALUES (%s,%s,%s,%s)", (st.session_state.customer_id, selected_destination["destination_id"], rating, review_text.strip()))
                st.success(f"Review saved for {selected_label}!")
                st.balloons()
                st.rerun()
    st.divider()
    st.markdown("### 💬 Recent Reviews - What travelers say")
    reviews = execute_query("SELECT r.*, c.full_name, d.destination_name FROM reviews r JOIN customers c ON r.customer_id = c.customer_id LEFT JOIN destinations d ON r.destination_id = d.destination_id ORDER BY r.review_id DESC LIMIT 20", fetch=True, dictionary=True) or []
    if reviews:
        for review in reviews:
            with st.container(border=True):
                stars = "⭐" * int(review.get('rating') or 0)
                st.markdown(f"#### 📍 {review.get('destination_name')} — {stars} {review.get('rating')}/5")
                st.caption(f"By **{review.get('full_name')}**")
                st.write(f"_{review.get('review_text') or ''}_")
    else:
        st.info("No reviews yet. Be the first to review! 👆")

elif menu == "🧳 Trip History":
    page_title("🧳 Trip History", "Review your travel records")
    bookings_history = execute_query("SELECT b.*, tp.package_name, tp.image_url, d.destination_name, d.image_url as dest_image, d.country FROM bookings b LEFT JOIN tour_packages tp ON b.package_id = tp.package_id LEFT JOIN destinations d ON tp.destination_id = d.destination_id WHERE b.customer_id = %s AND b.booking_status='Confirmed' ORDER BY b.travel_date DESC", (st.session_state.customer_id,), fetch=True, dictionary=True) or []
    for item in bookings_history:
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                img = item.get('image_url') or item.get('dest_image')
                if img: st.image(img, use_container_width=True)
            with c2:
                st.subheader(f"📍 {item.get('destination_name')} - {item.get('package_name')}")
                st.write(f"Travel Date: {item.get('travel_date')} | People: {item.get('number_of_people')}")
                st.success(f"Status: {item.get('booking_status')} | Total: {money(item.get('total_amount'))}")

elif menu == "🎫 My Bookings":
    page_title("🎫 My Bookings", "View bookings with images")
    bookings = execute_query("SELECT b.*, tp.package_name, tp.duration_days, tp.image_url as package_image, d.destination_name, d.image_url as dest_image, h.hotel_name, t.transport_type, t.provider_name, t.source_location, t.destination_location FROM bookings b LEFT JOIN tour_packages tp ON b.package_id = tp.package_id LEFT JOIN destinations d ON tp.destination_id = d.destination_id LEFT JOIN hotels h ON b.hotel_id = h.hotel_id LEFT JOIN transport t ON b.transport_id = t.transport_id WHERE b.customer_id = %s ORDER BY b.booking_id DESC", (st.session_state.customer_id,), fetch=True, dictionary=True) or []
    if bookings:
        for booking in bookings:
            with st.container(border=True):
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    img_url = booking.get('package_image') or booking.get('dest_image')
                    if img_url: st.image(img_url, use_container_width=True)
                with col_info:
                    st.subheader(f"Booking #{booking['booking_id']} — {booking.get('package_name')}")
                    t_type = (booking.get('transport_type') or '').lower()
                    t_icon = "✈️" if 'flight' in t_type else "🚂" if 'train' in t_type else "🚌" if 'bus' in t_type else "🚗"
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"📍 {booking.get('destination_name')}")
                        st.write(f"🗓️ {booking.get('travel_date')}")
                        st.write(f"👥 {booking.get('number_of_people')} People")
                    with c2:
                        st.write(f"🏨 {booking.get('hotel_name') or 'N/A'}")
                        st.write(f"{t_icon} {booking.get('transport_type') or 'N/A'} - {booking.get('provider_name') or ''}")
                        st.write(f"Status: **{booking.get('booking_status')}**")
                    st.markdown(f"### Total: {money(booking.get('total_amount'))}")
                    pdf_details = {"Booking ID": booking["booking_id"], "Customer": st.session_state.customer_name, "Package": booking.get("package_name") or "N/A", "Destination": booking.get("destination_name") or "N/A", "Hotel": booking.get("hotel_name") or "N/A", "Transport": f"{booking.get('transport_type')} - {booking.get('provider_name')}", "Travel Date": str(booking.get("travel_date") or "N/A"), "People": booking.get("number_of_people") or 1, "Total Amount": money(booking.get("total_amount")), "Status": booking.get("booking_status") or "N/A"}
                    try:
                        pdf_bytes = generate_booking_pdf(pdf_details)
                        st.download_button("📄 Download Booking PDF", data=pdf_bytes, file_name=f"booking_{booking['booking_id']}.pdf", mime="application/pdf", key=f"download_pdf_{booking['booking_id']}", use_container_width=True)
                    except Exception as e: st.error(f"PDF error: {e}")
    else: st.info("You have not made any bookings yet.")

st.caption("✈️ Travel Booking & Trip Management System | Python • Streamlit • MySQL") 
