import sys
import signal
from dataProcessor import WeatherDataProcessor

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print('\nShutdown signal received, exiting gracefully...')
    sys.exit(0)

def main():
    """Main entry point with error handling"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    processor = None
    try:
        print("Starting Weather Data Processing Pipeline...")
        processor = WeatherDataProcessor()
        processor.start_processing()
        
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1
    finally:
        if processor:
            processor.shutdown()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)