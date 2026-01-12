import time
import matplotlib.pyplot as plt
import numpy as np

def plot_run_times(run_data: dict) -> None:
    """Plot the run times as a stacked bar chart."""
    # Extract data from run_data dictionary
    run_times = run_data['total']
    number_of_runs = len(run_times)
    
    # Plot the run times as stacked bar chart
    current_time = time.strftime("%Y%m%d-%H%M%S")

    # Create stacked bar chart
    run_numbers = list(range(1, number_of_runs+1))

    # Convert lists to numpy arrays for easier stacking calculations
    forward_times = np.array(run_data['forward'])
    waiting_times = np.array(run_data['enemies_stacked'])
    spike_times = np.array(run_data['spike'])
    collecting_times = np.array(run_data['collecting'])
    backward_times = np.array(run_data['backward'])

    # Create the stacked bars
    fig, ax = plt.subplots(figsize=(12, 8))
    width = 0.8

    # Stack the bar
    ax.bar(run_numbers, forward_times, width, label='Running Forward', color='#1f77b4')
    ax.bar(run_numbers, waiting_times, width, bottom=forward_times, label='Waiting for Stacked Enemies', color="#b4670e")
    ax.bar(run_numbers, spike_times, width, bottom=forward_times + waiting_times, label='Spike Phase', color="#A10C2D")
    ax.bar(run_numbers, collecting_times, width, bottom=forward_times + waiting_times + spike_times, label='Collecting Phase', color="#4116a3")
    ax.bar(run_numbers, backward_times, width, bottom=forward_times + waiting_times + spike_times + collecting_times, label='Running Backward', color="#25af13")

    ax.set_xlabel('Run Number')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Time Breakdown for Each Run. Average Total Time: {:.2f} seconds'.format(np.mean(run_times)))
    ax.legend(loc="upper right")
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'gw_vaettir_bot/logs/run_times_stacked_{current_time}.png')
    plt.show()