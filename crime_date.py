"""
Parker Jackson
Nov 2024
Class that uses info pulled from PDF online to provide different case info.
"""
class CrimeDate:
    def __init__(self, date):
        self.date = date
        self.incidents = []  # List to hold all incidents for this date

    def add_incident(self, incident):
        """Add an incident to this date's list of incidents."""
        self.incidents.append(incident)

    def __repr__(self):
        incident_details = "\n\n".join(repr(incident) for incident in self.incidents)
        return f"\n{self.date}\n" \
               f"Total Incidents: {len(self.incidents)}\n" \
               f"{incident_details}"

class Incident:
    def __init__(self, crime_date, location, disposition, reported_time, nature_of_crime, case_number=None):
        self.location = location
        self.disposition = disposition
        self.reported_time = reported_time
        self.nature_of_crime = nature_of_crime
        self.case_number = case_number
        crime_date.add_incident(self)  # Add this incident to the specified CrimeDate

    def __repr__(self):
        return f"Crime Report:\n" \
               f"  Location: {self.location}\n" \
               f"  Reported Time: {self.reported_time}\n" \
               f"  Nature of Crime: {self.nature_of_crime}\n" \
