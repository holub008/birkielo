import pandas as pd
from db import get_connection

def _get_existing_event_occurrences(cursor):
    cursor.execute("""
        SELECT
            e.name,
            eo.date
        FROM event e
        JOIN event_occurrence eo
            ON eo.event_id = e.id
    """)

    results = cursor.fetchall()

    return pd.DataFrame(results, columns=['event_name', 'date'])


class EventOccurrenceArbiter:

    def __init__(self):
        with get_connection() as con:
            with con.cursor() as cursor:
                existing_events = _get_existing_event_occurrences(cursor)
                existing_events['year'] = [d.year for d in existing_events.date]
                self._existing_events = existing_events


        self._keyword_to_event_name_enumeration = {
            "birkebeiner": "American Birkebeiner",
            "birkie": "American Birkebeiner",
            "city of lakes": "City of Lakes Loppet",
            "blue hills": "Blue Hills Ascent",
            "pre-loppet": "Pre-Loppet",
            "preloppet": "Pre-Loppet",
            "great bear chase": "Great Bear Chase",
            "lakeland loppet": "Lakeland Loppet",
            "seeley": "Seeley Hills Classic",
            "squirrel hill": "Squirrel Hill Ski Race",
            "double pole derby": "Double Pole Derby",
            "sisu": "SISU Ski Fest",
            "us cross country ski championship": "US Cross Country Ski Championship",
            "ashwabay": "Mt. Ashwabay Summit Ski Race",
            "big island and back": " Big Island and Back",
            "vasa": "Vasaloppet USA",
            "book across": "Book Across the Bay",
            "pepsi": "Pepsi Challenge",
            "nordic spirit": "Nordic Spirit",
            "boulder lake": "Boulder Lake Ski Race",
            "marine": "Marine O'Brien",
            "noque": "Noquemanon Ski Marathon",
            "rennet": "Ski Rennet",
            "mn pursuit": "MN Pursuit Champs",
            "north end": "North End Classic",
            "pre-birkie": "Pre-Birkie",
            "prebirkie": "Pre-Birkie",
            "wolf track": "Wolf Track Rendezvous",
            "badger state": "Badger State Games",
            "turtle river": "Turtle River Pursuit"}

    def enumerate_event_name(self, candidate_event_name):
        candidate_event_name_lower = candidate_event_name.lower()
        for keyword, event_name in self._keyword_to_event_name_enumeration.items():
            if keyword in candidate_event_name_lower:
                return event_name

        return None

    def should_keep(self, candidate_event_name, candidate_event_date):
        candidate_event_year = candidate_event_date.year

        enumerated_candidate_event_name = self.enumerate_event_name(candidate_event_name)

        if not enumerated_candidate_event_name:
            return True

        for index, existing_event in self._existing_events.iterrows():
            if existing_event.event_name == enumerated_candidate_event_name and \
                            existing_event.year == candidate_event_year:
                return False

        return True

