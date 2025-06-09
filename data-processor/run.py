from dataProcessor import WeatherDataProcessor

if __name__ == "__main__":
    print("Starting Weather Data Processing Pipeline...")
    processor = WeatherDataProcessor()
    processor.start_processing()