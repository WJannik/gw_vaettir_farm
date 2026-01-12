# Import the main function from the farm module
from gw_vaettir_bot import start_farm

def main():
    try:
        # Start the farming process
        start_farm(5)  # You can adjust the number of runs here
        print("\nFarming process completed.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main()