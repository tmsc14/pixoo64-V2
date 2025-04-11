import csv
from config import Config

class DataService:
    CSV_FIELDS = [
        "green_flags", "red_flags", "attendance", "showDateTime",
        "country", "background_color", "text_color", "line_color"
    ]

    @classmethod
    def read_data(cls):
        try:
            with open(Config.CSV_FILE_PATH, mode="r") as file:
                csv_reader = csv.DictReader(file)
                data = next(csv_reader, cls.default_data())
                data['showDateTime'] = data.get('showDateTime', 'false').lower() == 'true'
                return data
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return cls.default_data()

    @classmethod
    def write_data(cls, data):
        try:
            # Coerce all values to strings for CSV compatibility
            cleaned_data = {
                field: str(data.get(field, cls.default_data().get(field)))
                for field in cls.CSV_FIELDS
            }
            with open(Config.CSV_FILE_PATH, mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=cls.CSV_FIELDS)
                writer.writeheader()
                writer.writerow(cleaned_data)
        except Exception as e:
            print(f"Error writing to CSV file: {e}")

    @staticmethod
    def default_data():
        return {
            "green_flags": "0",
            "red_flags": "0",
            "attendance": "0",
            "showDateTime": "false",
            "country": "Australia",
            "background_color": "0,0,0",
            "text_color": "255,255,255",
            "line_color": "255,255,255",
        }

class BeerDataService:
    CSV_FIELDS = [
        "location", 
        "beers_total_available", 
        "beers_consumed", 
        "background_color", 
        "text_color", 
        "showDateTime",
        "country"
    ]

    @classmethod
    def read_data(cls):
        try:
            with open(Config.CSV_BEER_FILE_PATH, "r") as file:
                csv_reader = csv.DictReader(file)
                data = next(csv_reader, cls.default_data())
                data['beers_total_available'] = int(data.get('beers_total_available', 1000))
                data['beers_consumed'] = int(data.get('beers_consumed', 0))
                data['showDateTime'] = data.get('showDateTime', 'false').lower() == 'true'
                return data
        except Exception as e:
            print(f"Error reading beer data: {e}")
            return cls.default_data()

    @classmethod
    def write_data(cls, data):
        try:
            cleaned_data = {
                field: str(data.get(field, cls.default_data().get(field)))
                for field in cls.CSV_FIELDS
            }
            with open(Config.CSV_BEER_FILE_PATH, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=cls.CSV_FIELDS)
                writer.writeheader()
                writer.writerow(cleaned_data)
        except Exception as e:
            print(f"Error writing beer data: {e}")

    @staticmethod
    def default_data():
        return {
            "location": "Unknown",
            "beers_total_available": "1000",
            "beers_consumed": "0",
            "background_color": "0,0,0",
            "text_color": "255,255,255",
            "showDateTime": "false",
            "country": "Philippines"
        }
