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
                return next(csv_reader, cls.default_data())
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return cls.default_data()

    @classmethod
    def write_data(cls, data):
        try:
            with open(Config.CSV_FILE_PATH, mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=cls.CSV_FIELDS)
                writer.writeheader()
                writer.writerow(data)
        except Exception as e:
            print(f"Error writing to CSV file: {e}")

    @staticmethod
    def default_data():
        return {
            "green_flags": 0,
            "red_flags": 0,
            "attendance": 0,
            "showDateTime": False,
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
        "showDateTime",  # New field
        "country"  # New field
    ]

    @classmethod
    def read_data(cls):
        try:
            with open(Config.CSV_BEER_FILE_PATH, "r") as file:
                csv_reader = csv.DictReader(file)
                data = next(csv_reader, cls.default_data())
                
                # Ensure proper types
                data['beers_total_available'] = int(data.get('beers_total_available', 1000))
                data['beers_consumed'] = int(data.get('beers_consumed', 0))
                data['showDateTime'] = data.get('showDateTime', 'false').lower() == 'true'
                return data
        except Exception as e:
            print(f"Error reading beer data: {e}")
            return cls.default_data()

    @classmethod
    def write_data(cls, data):
        filtered = {k: data.get(k, 0) for k in cls.CSV_FIELDS}
        try:
            with open(Config.CSV_BEER_FILE_PATH, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=cls.CSV_FIELDS)
                writer.writeheader()
                writer.writerow(filtered)
        except Exception as e:
            print(f"Error writing beer data: {e}")

    @staticmethod
    def default_data():
        return {
            "location": "Unknown",
            "beers_total_available": 1000,
            "beers_consumed": 0,
            "background_color": "0,0,0",
            "text_color": "255,255,255",
            "showDateTime": False,
            "country": "Philippines"
        }