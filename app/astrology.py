import swisseph as swe
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from functools import lru_cache

# Set path to ephemeris files
EPHE_PATH = os.path.join(os.path.dirname(__file__), "ephe")
swe.set_ephe_path(EPHE_PATH)
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Rashi Names
RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Nakshatra Names
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

# Panet Names
PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mars": swe.MARS,
    "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER,
    "venus": swe.VENUS,
    "saturn": swe.SATURN,
    "rahu": swe.MEAN_NODE,  # Rahu (North Node)
    "ketu": swe.MEAN_NODE   # Ketu (180° from Rahu)
}

# Tithi Names (1–30)
TITHIS = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Amavasya"
]

# Paksha Names
PAKSHA = ["Shukla", "Krishna"]

# Yoga Names (27)
YOGAS = [
    "Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma",
    "Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
    "Siddhi","Vyatipada","Variyan","Parigha","Shiva","Siddha","Sadhya","Shubha",
    "Shukla","Brahma","Indra","Vaidhriti"
]

# Karana Names (11 unique, repeat cycle)
KARANAS = [
    "Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti",
    "Shakuni","Chatushpada","Naga","Kimstughna"
]

@lru_cache(maxsize=50000)
def calc_body(jd, body):
    return swe.calc_ut(jd, body)[0][0]

@lru_cache(maxsize=50000)
def ayanamsa(jd):
    return swe.get_ayanamsa_ut(jd)


def binary_search_transition(jd_left, jd_right, value_fn, boundary, direction="start", tol=1e-6):
    """
    Finds JD where value_fn(jd) crosses boundary.
    tol ~ 1e-6 JD ≈ 0.086 seconds
    """

    left_val = value_fn(jd_left)

    while abs(jd_right - jd_left) > tol:
        mid = (jd_left + jd_right) / 2
        val = value_fn(mid)

        if boundary in (0, 360):
            # wrap-around detection (359 → 0)
            crossed = val < left_val
        else:
            crossed = val >= boundary

        if direction == "start":
            if not crossed:
                jd_left = mid
                left_val = val
            else:
                jd_right = mid
        else:  # end
            if crossed:
                jd_right = mid
            else:
                jd_left = mid
                left_val = val

    return jd_right


def get_moon_sidereal_longitude(jd):
    """
    Returns Moon sidereal longitude for a given Julian Day.
    """
    moon_lon = calc_body(jd, swe.MOON)
    ayan = ayanamsa(jd)
    return (moon_lon - ayan) % 360


def jd_to_local_datetime(jd, tz_offset):
    """Convert Julian Day to local datetime string"""
    if jd is None:
        return None

    # Convert JD → UTC datetime
    utc_dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(days=(jd - 2440587.5))

    # Convert UTC → local timezone
    local_dt = utc_dt + timedelta(hours=tz_offset)

    return local_dt.strftime("%Y-%m-%d %H:%M:%S")


def get_nakshatra_details(jd, tz_offset=5.5):
    """
    Returns nakshatra name, pada, start_time, end_time
    """

    nak_deg = 360 / 27

    # Current moon longitude
    current_lon = get_moon_sidereal_longitude(jd)
    nak_index = int(current_lon // nak_deg)
    nak_name = NAKSHATRAS[nak_index]

    # Pada (1–4)
    pada = int((current_lon % nak_deg) // (nak_deg / 4)) + 1

    start_boundary = nak_index * nak_deg
    end_boundary = start_boundary + nak_deg
    value_fn = get_moon_sidereal_longitude

    # ---- Start time ----
    start_jd = binary_search_transition(jd - 1, jd, value_fn, start_boundary, direction="start")

    # ---- End time ----
    end_jd = binary_search_transition(jd, jd + 1, value_fn, end_boundary, direction="end")

    return {
        "nakshatra": nak_name,
        "pada": pada,
        "start_time": jd_to_local_datetime(start_jd, tz_offset),
        "end_time": jd_to_local_datetime(end_jd, tz_offset)
    }

def get_lagna_sidereal_longitude(jd, lat, lon):
    """
    Returns sidereal longitude of Lagna (Ascendant)
    """
    houses = swe.houses(jd, lat, lon)[0]
    tropical_asc = houses[0]  # Ascendant
    ayan = ayanamsa(jd)
    return (tropical_asc - ayan) % 360


def get_lagna_details(jd, lat, lon, tz_offset=5.5):
    """
    Returns Lagna name, start_time, end_time
    """
    try:
        lagna_lon = get_lagna_sidereal_longitude(jd, lat, lon)
        lagna_index = int(lagna_lon // 30)
        lagna_name = RASHIS[lagna_index]

        def lagna_fn(jd):
            return get_lagna_sidereal_longitude(jd, lat, lon)

        start_boundary = lagna_index * 30
        end_boundary = start_boundary + 30

        # ---- Start time ----
        start_jd = binary_search_transition(jd - 1, jd, lagna_fn, start_boundary, direction="start")

        # ---- End time ----
        end_jd = binary_search_transition(jd, jd + 1, lagna_fn, end_boundary, direction="end")

        return {
            "rashi": lagna_name,
            "start_time": jd_to_local_datetime(start_jd, tz_offset),
            "end_time": jd_to_local_datetime(end_jd, tz_offset)
        }
    except Exception as e:
        raise ValueError(f"Error calculating Lagna: {str(e)}")

def get_tithi_details(jd, tz_offset=5.5):
    """
    Returns tithi number, name, paksha, start_time, end_time
    """
    try:
        def moon_sun_diff(jd):
            sun_lon = calc_body(jd, swe.SUN)
            moon_lon = calc_body(jd, swe.MOON)
            return (moon_lon - sun_lon) % 360

        diff = moon_sun_diff(jd)
        tithi_index = int(diff // 12)
        tithi_num = tithi_index + 1
        tithi_name = TITHIS[tithi_index]
        paksha = "Shukla" if tithi_num <= 15 else "Krishna"

        start_boundary = tithi_index * 12
        end_boundary = start_boundary + 12
        value_fn = moon_sun_diff
        print("start_boundary :",start_boundary,"end_boundary :",end_boundary)

        # ---- Start time ----
        print(jd - 1, jd, value_fn, start_boundary,"start")
        start_jd = binary_search_transition(jd - 1, jd, value_fn, start_boundary, direction="start")

        # ---- End time ----
        end_jd = binary_search_transition(jd, jd + 1, value_fn, end_boundary, direction="end")


        return {
            "number": tithi_num,
            "name": tithi_name,
            "paksha": paksha,
            "start_time": jd_to_local_datetime(start_jd, tz_offset),
            "end_time": jd_to_local_datetime(end_jd, tz_offset)
        }

    except Exception as e:
        raise ValueError(f"Error calculating Tithi: {str(e)}")

def get_yoga_details(jd, tz_offset=5.5):
    """
    Returns yoga number, name, start_time, end_time
    """
    try:
        yoga_deg = 360 / 27

        def yoga_angle(jd):
            sun = calc_body(jd, swe.SUN)
            moon = calc_body(jd, swe.MOON)
            ayan = ayanamsa(jd)
            sun_sid = (sun - ayan) % 360
            moon_sid = (moon - ayan) % 360
            return (sun_sid + moon_sid) % 360

        angle = yoga_angle(jd)
        yoga_index = int(angle // yoga_deg)
        yoga_name = YOGAS[yoga_index]

        start_boundary = yoga_index * yoga_deg
        end_boundary = start_boundary + yoga_deg
        value_fn = yoga_angle

        # ---- Start time ----
        start_jd = binary_search_transition(jd - 1, jd, value_fn, start_boundary, direction="start")

        # ---- End time ----
        end_jd = binary_search_transition(jd, jd + 1, value_fn, end_boundary, direction="end")
        return {
            "number": yoga_index + 1,
            "name": yoga_name,
            "start_time": jd_to_local_datetime(start_jd, tz_offset),
            "end_time": jd_to_local_datetime(end_jd, tz_offset)
        }
    except Exception as e:
        raise ValueError(f"Error calculating Yoga: {str(e)}")

def get_karana_details(jd, tz_offset=5.5):
    """
    Returns karana name, start_time, end_time
    """
    try:
        def diff(jd):
            sun = calc_body(jd, swe.SUN)
            moon = calc_body(jd, swe.MOON)
            return (moon - sun) % 360

        karana_index = int(diff(jd) // 6)

        repeating = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]
        if karana_index == 0:
            name = "Kimstughna"
        elif 1 <= karana_index <= 56:
            name = repeating[(karana_index - 1) % 7]
        else:
            fixed = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]
            name = fixed[karana_index - 57]

        start_boundary = karana_index * 6
        end_boundary = start_boundary + 6
        value_fn = diff

        # ---- Start time ----
        print(jd - 1, jd, value_fn, start_boundary,"start")
        start_jd = binary_search_transition(jd - 1, jd, value_fn, start_boundary, direction="start")

        # ---- End time ----
        end_jd = binary_search_transition(jd, jd + 1, value_fn, end_boundary, direction="end")

        return {
            "name": name,
            "start_time": jd_to_local_datetime(start_jd, tz_offset),
            "end_time": jd_to_local_datetime(end_jd, tz_offset)
        }
    except Exception as e:
        raise ValueError(f"Error calculating Karana: {str(e)}")

def get_var(jd,tz_offset=5.5):
    try:
        local_jd = jd + tz_offset/24
        weekday = swe.day_of_week(local_jd)
        VARAS = ["Somavara", "Mangalavara", "Budhavara",
                "Guruvara", "Shukravara", "Shanivara","Ravivara"]
        return VARAS[weekday]
    except Exception as e:
        raise ValueError(f"Error calculating Var: {str(e)}")

def get_masa(jd):
    try:
        sun_lon = calc_body(jd, swe.SUN)
        ayan = ayanamsa(jd)
        sidereal_sun = (sun_lon - ayan) % 360
        masa_num = int(sidereal_sun // 30)

        MASA = [
            "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
            "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"
        ]
        return MASA[masa_num]
    except Exception as e:
        raise ValueError(f"Error calculating Masa: {str(e)}")
 
def get_sunrise_sunset(year, month, day, lat, lon, tz_offset=5.5):
    try:
        # swe.rise_trans: 1 = rise, 2 = set
        jd_start = swe.julday(year, month, day, 0)
        geopos = [lon, lat, 0]  # longitude, latitude, altitude
        sunrise_jd= swe.rise_trans(jd_start, swe.SUN, 1, geopos)[1][0]
        sunset_jd  = swe.rise_trans(jd_start, swe.SUN, 2, geopos)[1][0]

        # Convert JD to local time (default IST: UTC+5:30)
        sunrise_local = jd_to_local_datetime(sunrise_jd, tz_offset)
        sunset_local = jd_to_local_datetime(sunset_jd, tz_offset)

        return sunrise_jd,sunrise_local, sunset_local
    except Exception as e:
        raise ValueError(f"Error calculating sunrise_sunset: {str(e)}")
    
def get_moonrise_moonset(sunrise_jd, lat, lon, tz_offset=5.5):
    """
    Panchang-based Moonrise & Moonset
    Window: sunrise → next sunrise
    """

    geopos = [lon, lat, 0]
    next_sunrise_jd = sunrise_jd + 1

    moonrise_jd = None
    moonset_jd = None

    # --- Moonrise ---
    try:
        # 1️⃣ Try within Panchang day
        rise = swe.rise_trans(
            sunrise_jd,
            swe.MOON,
            swe.CALC_RISE,
            geopos
        )[1][0]

        if sunrise_jd <= rise < next_sunrise_jd:
            moonrise_jd = rise
        else:
            # 2️⃣ Fallback: previous moonrise
            prev_rise = swe.rise_trans(
                sunrise_jd - 1,
                swe.MOON,
                swe.CALC_RISE,
                geopos
            )[1][0]

            if prev_rise < sunrise_jd:
                moonrise_jd = prev_rise

    except:
        pass

    # --- Moonset ---
    try:
        set_ = swe.rise_trans(
            sunrise_jd,
            swe.MOON,
            swe.CALC_SET,
            geopos
        )[1][0]

        if sunrise_jd <= set_ < next_sunrise_jd:
            moonset_jd = set_
    except:
        pass

    return {
        "moonrise": jd_to_local_datetime(moonrise_jd, tz_offset) if moonrise_jd else None,
        "moonset": jd_to_local_datetime(moonset_jd, tz_offset) if moonset_jd else None
    }


def get_planet_positions(year, month, day, hour, lat, lon):
    try:
        sunrise_jd,sunrise, sunset = get_sunrise_sunset(year, month, day, lat, lon)

        jd = swe.julday(year, month, day, hour)
        result = {}

        # Lagna
        lagna_details = get_lagna_details(sunrise_jd, lat, lon)
        result["lagna"] = lagna_details

        # Moon Nakshatra
        moon_details = get_nakshatra_details(sunrise_jd)
        result["moon"] = moon_details
        print("8",moon_details)

        # --- Panchang details ---
        tithi_details = get_tithi_details(sunrise_jd)
        result["tithi"] = tithi_details
        yoga_details = get_yoga_details(sunrise_jd)
        result["yoga"] = yoga_details
        karna_details  = get_karana_details(sunrise_jd)
        result["karna"] = karna_details
        masa = get_masa(sunrise_jd)
        vara = get_var(sunrise_jd)

        moon_time = get_moonrise_moonset(sunrise_jd,lat,lon)
        result["moon_time"] = moon_time
        
        

        return {
                    "lagna": result["lagna"],
                    "moon": result["moon"],
                    "tithi": result["tithi"],
                    "masa": masa,
                    "var": vara,
                    "yoga": result["yoga"],
                    "karana": result["karna"],
                    "sunrise": sunrise,
                    "sunset": sunset,
                    "moonset": result["moon_time"]["moonset"],
                    "moonrise":  result["moon_time"]["moonrise"] 
                    }
    except Exception as e:
        raise ValueError(f"Error calculating Panchang: {str(e)}")

def get_today_nakshatra_end_datetime(lat: float, lon: float, timezone_str: str):
    """
    Returns today's nakshatra end time as timezone-aware datetime
    """

    tz = ZoneInfo(timezone_str)

    # Current UTC
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)

    # Convert to local timezone
    local_now = now_utc.astimezone(tz)

    year = local_now.year
    month = local_now.month
    day = local_now.day

    # Calculate sunrise JD for this location
    sunrise_jd, _, _ = get_sunrise_sunset(year, month, day, lat, lon, tz_offset=0)

    # Calculate tz offset dynamically (in hours)
    tz_offset_hours = local_now.utcoffset().total_seconds() / 3600

    # Get nakshatra details
    nak_details = get_nakshatra_details(sunrise_jd, tz_offset=tz_offset_hours)

    # Convert end_time string → datetime
    end_time_str = nak_details["end_time"]

    if end_time_str is None:
        return None

    end_dt_naive = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

    # Attach timezone
    end_dt = end_dt_naive.replace(tzinfo=tz)

    return end_dt