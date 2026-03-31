from flask import Flask, jsonify, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import sqlite3
import os
from datetime import datetime, date, timedelta
from icalendar import Calendar

app = Flask(__name__)
DB = "cleaning.db"

PROPERTIES = [
    {"id": 1,  "name": "Hapsal Holiday Homes",                  "address": "Nõmme Villa Puhkemaja", "door": "4821/11", "booking_ical": "https://ical.booking.com/v1/export/t/cdc2e17f-1990-4c8d-a4c2-c0a9510df914.ics", "airbnb_ical": ""},
    {"id": 2,  "name": "Hapsal Forest Cabin",                    "address": "Nõmme Villa Metsamaja", "door": "4321",    "booking_ical": "https://ical.booking.com/v1/export?t=7f4c3a33-b891-4a2a-95d6-6b3ddb1b7616", "airbnb_ical": ""},
    {"id": 3,  "name": "Hapsal Spa Villa 1",                     "address": "Nõmme Villa 1",         "door": "1111",    "booking_ical": "https://ical.booking.com/v1/export?t=0242fe5a-3f69-4b8a-ad9d-805902e07049", "airbnb_ical": ""},
    {"id": 4,  "name": "Hapsal Spa Villa 2",                     "address": "Nõmme Villa 2",         "door": "2222",    "booking_ical": "https://ical.booking.com/v1/export?t=cc3380df-112e-48e8-9a9c-a601f7a90ce2", "airbnb_ical": ""},
    {"id": 5,  "name": "Hapsal Spa Villa 3",                     "address": "Nõmme Villa 3",         "door": "3333",    "booking_ical": "https://ical.booking.com/v1/export?t=c8491ffc-5e88-4fc9-94d0-b4328bb4bc5c", "airbnb_ical": ""},
    {"id": 6,  "name": "Kesklinna majutus",                      "address": "Lihula mnt 9-38",       "door": "9038",    "booking_ical": "https://ical.booking.com/v1/export?t=c0291b5a-39ce-4c15-929b-92cab07bbda0", "airbnb_ical": ""},
    {"id": 7,  "name": "Holyday apartment",                      "address": "Mulla 10-30",           "door": "1030",    "booking_ical": "https://ical.booking.com/v1/export/t/aa144406-5849-4071-8542-ced587bae6b0.ics", "airbnb_ical": ""},
    {"id": 8,  "name": "Promenaadi apartment",                   "address": "Kooli 7a-4",            "door": "7474",    "booking_ical": "https://ical.booking.com/v1/export/t/ef2b4e0b-f87b-469d-8204-f7be61c73249.ics", "airbnb_ical": ""},
    {"id": 9,  "name": "Haapsalu aparterment",                   "address": "Niine 18-7",            "door": "1807",    "booking_ical": "https://ical.booking.com/v1/export?t=c7c29932-d4a6-4192-ba5f-72d334014b7b", "airbnb_ical": ""},
    {"id": 10, "name": "Liidia korter 1",                        "address": "Lihula mnt 8",          "door": "118",     "booking_ical": "https://ical.booking.com/v1/export/t/ed7a4537-2039-450f-b53a-4bf6ba88fbf0.ics", "airbnb_ical": ""},
    {"id": 11, "name": "Liidia korter 2",                        "address": "Lihula mnt 8",          "door": "228",     "booking_ical": "https://ical.booking.com/v1/export/t/f304477c-38df-4df0-8d06-d616ee2b6fcd.ics", "airbnb_ical": ""},
    {"id": 12, "name": "Liidia korter 3",                        "address": "Lihula mnt 8",          "door": "338",     "booking_ical": "https://ical.booking.com/v1/export/t/f4c8c6d6-71c9-4637-9ce1-c87e9af1c55a.ics", "airbnb_ical": ""},
    {"id": 13, "name": "Liidia korter 4",                        "address": "Lihula mnt 8",          "door": "448",     "booking_ical": "https://ical.booking.com/v1/export/t/c60ac14a-7587-4688-9e78-b2a7dde18527.ics", "airbnb_ical": ""},
    {"id": 14, "name": "Trendy apartment in Haapsalu center",    "address": "Mulla 10-34",           "door": "1992",    "booking_ical": "https://ical.booking.com/v1/export/t/15f24799-4196-4ad9-928e-4b96dcc0ade7.ics", "airbnb_ical": "https://www.airbnb.com.ee/calendar/ical/1151576915081726318.ics?t=d0edcd2b1a604c679f7ebcb921a221c1"},
    {"id": 15, "name": "Hubane väikemaja Haapsalus",             "address": "Kajaka 12",             "door": "120",     "booking_ical": "https://ical.booking.com/v1/export?t=e9db1ec7-9fd3-49b4-bd6b-91ebb01350ba", "airbnb_ical": "https://www.airbnb.com.ee/calendar/ical/1004172354912663420.ics?t=cc9ae59fa6d242fdb870b1d5ccf965f7"},
    {"id": 16, "name": "K&A apartament",                         "address": "Põllu 1-18",            "door": "2812",    "booking_ical": "https://ical.booking.com/v1/export?t=79f3e8ac-0ac8-4005-a8d4-eb1bbdf23d4c", "airbnb_ical": ""},
    {"id": 17, "name": "Stylish seaside apartment",              "address": "Suur-Liiva 15-10",      "door": "312",     "booking_ical": "https://ical.booking.com/v1/export?t=abf8401e-070e-41d1-9ba5-063d687f62ed", "airbnb_ical": "https://www.airbnb.com.ee/calendar/ical/1420788285740968197.ics?t=f6b465a499de42de9c2e236f1cc4424f"},
    {"id": 18, "name": "Kodurahu apartement",                    "address": "Suur-Liiva 15-22",      "door": "",        "booking_ical": "https://ical.booking.com/v1/export?t=65be58e8-fba9-4516-ae1b-bb5e6a3ed65e", "airbnb_ical": ""},
    {"id": 19, "name": "Top View Apartment Haapsalu",            "address": "Uus Sadama 29/2-11",    "door": "",        "booking_ical": "https://ical.booking.com/v1/export?t=48d015cb-6441-48b1-9b3f-7000f9360934", "airbnb_ical": "https://www.airbnb.com.ee/calendar/ical/1562960035746343171.ics?t=040c8758055c41fe85257931bd0065ea"},
    {"id": 20, "name": "Haapsalu home by the sea",               "address": "Väike-Mere 7-4",        "door": "",        "booking_ical": "https://ical.booking.com/v1/export/t/e9deaca5-c59f-4dd0-937c-48b091c56833.ics", "airbnb_ical": "https://www.airbnb.com.ee/calendar/ical/43034838.ics?t=7dcf5a69243d4b79bc68a5e8818f0f45"},
    {"id": 21, "name": "Marienholm Seaside Studio",              "address": "Uus Sadama 29/2-10",    "door": "",        "booking_ical": "https://ical.booking.com/v1/export/t/8d1094a9-479f-4551-8619-1bb7acec6ad9.ics", "airbnb_ical": "https://www.airbnb.com.ee/calendar/ical/1645661646988748563.ics?t=6e5850a43e6241c8b4c7b3d7291de1b8"},
    {"id": 22, "name": "Wiigi Luxury Seaview Apartment",         "address": "Uus-Sadama tn 27/1-2",  "door": "",        "booking_ical": "https://ical.booking.com/v1/export/t/b569d649-0713-4790-b41e-97f8abf93093.ics", "airbnb_ical": ""},
    {"id": 23, "name": "Christian apartment stay in Haapsalu",   "address": "Niine 32-23",           "door": "",        "booking_ical": "https://ical.booking.com/v1/export?t=9203d6eb-54ba-451b-8988-2ea94057d1c3", "airbnb_ical": "https://www.airbnb.com.ee/calendar/ical/1479741152194956043.ics?t=b20f6da580724995b08999f2c4688894"},
]

CLEANERS = [
    {"id": 1, "name": "Lilia Rešetnikova", "phone": "+37258199090", "email": "lilia138@gmail.com"},
    {"id": 2, "name": "Gertu Taavet",      "phone": "+3725883252",  "email": "gertu@masterclean.ee"},
]

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cleaning_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prop_id INTEGER NOT NULL,
            prop_name TEXT NOT NULL,
            checkout_date TEXT NOT NULL,
            next_checkin TEXT,
            platform TEXT,
            status TEXT DEFAULT 'unassigned',
            cleaner_id INTEGER,
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(prop_id, checkout_date)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            synced_at TEXT DEFAULT (datetime('now')),
            tasks_found INTEGER
        )
    """)
    conn.commit()
    conn.close()

def parse_ical(url, prop_id, platform):
    """Fetch and parse iCal, return list of (checkout_date, next_checkin) tuples."""
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        cal = Calendar.from_ical(r.content)
        bookings = []
        for component in cal.walk():
            if component.name == "VEVENT":
                dtstart = component.get("DTSTART")
                dtend   = component.get("DTEND")
                if dtstart and dtend:
                    start = dtstart.dt
                    end   = dtend.dt
                    if hasattr(start, "date"): start = start.date()
                    if hasattr(end,   "date"): end   = end.date()
                    bookings.append((start, end))
        # Sort by start date
        bookings.sort(key=lambda x: x[0])
        # For each booking end (checkout), find next checkin
        results = []
        for i, (start, end) in enumerate(bookings):
            next_checkin = bookings[i+1][0] if i+1 < len(bookings) else None
            results.append({
                "checkout": end.isoformat(),
                "next_checkin": next_checkin.isoformat() if next_checkin else None,
                "platform": platform,
            })
        return results
    except Exception as e:
        print(f"iCal error {prop_id} {platform}: {e}")
        return []

def sync_calendars():
    """Read all iCal links and create cleaning tasks for upcoming checkouts."""
    print(f"[{datetime.now()}] Sünkroniseerimist alustan...")
    today = date.today()
    window_end = today + timedelta(days=14)
    conn = get_db()
    total = 0

    for prop in PROPERTIES:
        all_events = []
        if prop["booking_ical"]:
            all_events += parse_ical(prop["booking_ical"], prop["id"], "Booking.com")
        if prop["airbnb_ical"]:
            all_events += parse_ical(prop["airbnb_ical"], prop["id"], "Airbnb")

        for ev in all_events:
            checkout = date.fromisoformat(ev["checkout"])
            if today <= checkout <= window_end:
                try:
                    conn.execute("""
                        INSERT OR IGNORE INTO cleaning_tasks
                        (prop_id, prop_name, checkout_date, next_checkin, platform)
                        VALUES (?, ?, ?, ?, ?)
                    """, (prop["id"], prop["name"], ev["checkout"], ev["next_checkin"], ev["platform"]))
                    total += 1
                except Exception as e:
                    print(f"DB error: {e}")

    conn.execute("INSERT INTO sync_log (tasks_found) VALUES (?)", (total,))
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] Sünkroniseerimine lõpetatud. {total} ülesannet leitud.")

# ── API routes ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/tasks")
def get_tasks():
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM cleaning_tasks
        ORDER BY checkout_date ASC, next_checkin ASC
    """).fetchall()
    conn.close()
    prop_map = {p["id"]: p for p in PROPERTIES}
    tasks = []
    for r in rows:
        p = prop_map.get(r["prop_id"], {})
        tasks.append({
            "id": r["id"],
            "prop_id": r["prop_id"],
            "prop_name": r["prop_name"],
            "address": p.get("address", ""),
            "door": p.get("door", ""),
            "checkout_date": r["checkout_date"],
            "next_checkin": r["next_checkin"],
            "platform": r["platform"],
            "status": r["status"],
            "cleaner_id": r["cleaner_id"],
            "note": r["note"] or "",
        })
    return jsonify(tasks)

@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    data = request.json
    conn = get_db()
    fields = []
    values = []
    for key in ["status", "cleaner_id", "note"]:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if fields:
        values.append(task_id)
        conn.execute(f"UPDATE cleaning_tasks SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/sync", methods=["POST"])
def manual_sync():
    sync_calendars()
    conn = get_db()
    last = conn.execute("SELECT synced_at FROM sync_log ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return jsonify({"ok": True, "synced_at": last["synced_at"] if last else None})

@app.route("/api/last_sync")
def last_sync():
    conn = get_db()
    last = conn.execute("SELECT synced_at FROM sync_log ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return jsonify({"synced_at": last["synced_at"] if last else None})

@app.route("/api/cleaners")
def get_cleaners():
    return jsonify(CLEANERS)

@app.route("/api/properties")
def get_properties():
    return jsonify([{"id": p["id"], "name": p["name"], "address": p["address"], "door": p["door"]} for p in PROPERTIES])

# ── Scheduler ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    sync_calendars()  # sync once on startup
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_calendars, "interval", hours=1)
    scheduler.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
