import argparse
from gw_vaettir_bot import start_farm

def main(number_of_runs: int=5) -> None:
    try:
        # Start the farming process
        start_farm(number_of_runs)  # You can adjust the number of runs here
        print("\nFarming process completed.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Guild Wars Vaettir Farming Bot')
    parser.add_argument('runs', type=int, nargs='?', default=5, 
                       help='Number of farming runs to execute (default: 5)')
    
    args = parser.parse_args()
    main(args.runs) 