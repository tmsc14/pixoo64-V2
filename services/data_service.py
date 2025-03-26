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
    CSV_FIELDS = ["beers_week", "beers_month", "beers_total", "background_color", "text_color"]
    @classmethod
    def read_data(cls):
        try:
            with open(Config.CSV_BEER_FILE_PATH, "r") as file:
                return next(csv.DictReader(file), cls.default_data())
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
            "beers_week": 0,
            "beers_month": 0,
            "beers_total": 0,
            "background_color": "0,0,0",
            "text_color": "255,255,255",
        }