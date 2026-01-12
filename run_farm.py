"""
Vaettir Farm Entry Point
========================

This is the main entry point for the Guild Wars Vaettir farming bot.
Simply run this file to start the farming process.

The actual farming logic is contained in the `farm` directory.
"""

# Import the main function from the farm module
from gw_vaettir_bot import start_farm

def main():
    """Main entry point for the Vaettir farm."""
    print("=== Guild Wars Vaettir Farm ===")

    try:
        # Start the farming process
        start_farm(5)  # You can adjust the number of runs here
        print("\nFarming process completed.")
    except KeyboardInterrupt:
        print("\n\nFarm stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main()