1️⃣ Fundamental Principle (Very Important)

In Vedic astrology there are two categories of calculations:

🔹 A. Astronomical (Location-INDEPENDENT)

These depend only on celestial motion (Sun, Moon, planets).

🔹 B. Topocentric / Panchang (Location-DEPENDENT)

These depend on observer’s location on Earth.

#################################################################

2️⃣ Calculation in astrology.py

Let’s go one by one.
_________________________________________________________________
Note:
Swiss Ephemeris:

Always calculates true astronomical positions

Outputs tropical longitude

You must explicitly convert to sidereal

Ayanamsa (THE bridge) is used to calculate sidereal from tropical for vedic astrology
 _________________________________________________________________
 🌙 Sidereal Longitude of the Moon
1️⃣ What is “Longitude” in astrology?

When we say longitude in astrology, we mean:

📍 Position of a planet along the zodiac circle, measured from 0° Aries to 360°.

So:

0° Aries → starting point

30° per zodiac sign

Full circle = 360°

2️⃣ Two different zodiacs exist

This is CRITICAL.

🔹 A. Tropical Zodiac (Western astrology)

Fixed to seasons (Tropical zodiac ignores where the stars actually are.)

0° Aries = March equinox

Used by default in astronomy

🔹 B. Sidereal Zodiac (Vedic astrology)

Fixed to stars

0° Aries = actual star reference

Slowly shifts due to precession

📌 Vedic astrology always uses sidereal.

3️⃣ What is Ayanamsa?

Because Earth’s axis wobbles:

Tropical zodiac slowly drifts

Difference between tropical and sidereal = Ayanamsa

Today:

Ayanamsa ≈ 24°

4️⃣ Sidereal Longitude – Definition
✅ Sidereal Longitude of Moon =
Moon's tropical longitude − Ayanamsa
(mod 360)


Meaning:

Where the Moon actually is relative to fixed stars

5️⃣ Example (Simple)

Let’s say at some moment:

Moon tropical longitude = 210°

Ayanamsa = 24°

Then:

Sidereal Moon longitude = 210 − 24 = 186°


That means:

186° lies in Libra/Scorpio region

This is what Vedic astrology uses

_______________________________________________________
JD = Julian Day
It is just a continuous count of days.

Example:

jd + 1.0 → 24 hours later

jd - 1.0 → 24 hours earlier

 ________________________________________________________________

🌙 1. Nakshatra (Moon Star)
🔹 What is Nakshatra?

The Moon’s sidereal longitude is divided into 27 equal parts

Each part = 13°20′

The Nakshatra where Moon lies = Moon Nakshatra

🔹 What does Nakshatra depend on?

✅ ONLY Moon’s sidereal longitude
❌ NOT dependent on location

Location is asked to convert time, not to change Nakshatra.

🔹 Why time matters?

Because Moon is moving (~13° per day).

📌 Nakshatra depends on TIME, not PLACE

_____________________________________________________________________

☀️ 2. Sunrise & Sunset
🔹 What is Sunrise/Sunset?

Moment when Sun crosses horizon

🔹 What does it depend on?

✅ Latitude
✅ Longitude
❌ Not zodiac

📌 Purely location-based

__________________________________________________________

🌅 3. Vara (Day – Monday, Tuesday, etc.)
🔹 Definition (Vedic)

Vara starts at local sunrise, not midnight

🔹 Depends on?

✅ Location (sunrise time)

___________________________________________________________

🌙☀️ 4. Tithi
🔹 What is Tithi?

Angular difference between Moon & Sun

Each 12° = 1 Tithi

🔹 Depends on?

✅ Sun longitude
✅ Moon longitude
❌ Not location

BUT…

📌 Which Tithi is “today” depends on sunrise

So:

Tithi itself → global

Tithi of the day → location-based

Correct stat and end time for tithi :-

Calculate Sun & Moon longitude at sunrise_jd

Freeze Tithi name

Compute:

Start → when (Moon − Sun) crossed previous multiple of 12°

End → when it reaches next multiple

🧠 Same logic as Nakshatra boundary search
Only difference: relative longitude, not absolute.
when tithi is amvasya then need to take as value 360 end boundary will never occur

_____________________________________________________________

🌗 5. Karana

Half of a Tithi (6° Moon–Sun difference)

Same dependency as Tithi

start and end time :
Logic

Karana index = floor(tithi_fraction * 2)

Freeze Karana at sunrise

Boundary = 6° Moon–Sun separation

➡️ Automatically handled once Tithi is correct

_____________________________________________________________

☀️🌙 6. Yoga
🔹 What is Yoga?

Sum of Sun + Moon sidereal longitudes

Divided into 27 parts

🔹 Depends on?

❌ Not location
✅ Only celestial positions

But again:
📌 Yoga of the day is decided at sunrise

Panchang start and end time logic:

Compute Sun + Moon at sunrise_jd

Freeze Yoga

Find:

Start → sum crossed previous Yoga boundary

End → sum crosses next boundary

🧠 Same boundary-search logic as Nakshatra
Only value being tracked changes

___________________________________________________
MASA (Lunar Month)
What is Masa?

Masa is based on:

Sun’s zodiac sign

Amavasya timing


Masa does NOT change daily

No “start/end time” needed per API call

Correct handling

Determine current lunar month name

Determine Adhika / Nija if needed

Just return the name

✔️ No boundary search required here
___________________________________________________
♈ 7. Lagna (Ascendant)
What is Lagna?

Lagna = Sidereal Ascendant

Zodiac sign rising on eastern horizon

Depends on:

Exact time

Latitude

Longitude

Ayanamsa (Lahiri)

📌 Lagna does NOT depend on Moon or Sun
📌 Lagna changes when ascendant longitude crosses a 30° boundary

Panchang rule for Lagna timing

Fix Lagna name at sunrise

Compute:

Start time = when that Lagna began

End time = when next Lagna begins

End time may go into next civil date

_________________________________________
MOONRISE & MOONSET
What are they?

Times when Moon crosses horizon
Correct Logic

Use Swiss Ephemeris rise/set functions

These are pure astronomy, not Panchang

✔️ Compute directly
✔️ No sunrise anchoring
✔️ No boundary search

___________________________________________
edge case for boundary calculation in start time 
when start boundary is 0 or end boundary is 360
So in that finding longutitude on progressive jd will be finding by difference of two longitude %360 and this will always give zero 
so when end boundary is 360 then logic should be moving backward from 360 but we get value zero thus it will be never able to find end time 
same in case of start boundary is zero but it may happen the start time of any pachnag attribute is before the current day that is before 360 .So this also become one edge case which is handled in binar_search_optimistaion function
__________________________________________________