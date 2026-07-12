import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def create_radar_chart():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    greedy_path = os.path.join(base_dir, 'output', 'greedy_26', 'summary.csv')
    ga_path = os.path.join(base_dir, 'output', 'ga_26', 'summary.csv')
    output_path = os.path.join(base_dir, 'output', 'comparison_26', 'comparison_deviation_radar.png')

    # Load data
    df_greedy = pd.read_csv(greedy_path)
    df_ga = pd.read_csv(ga_path)

    categories = df_greedy['Profile'].tolist()
    N = len(categories)

    # Values for deviation
    greedy_dev = df_greedy['Avg Deviation'].tolist()
    ga_dev = df_ga['Avg Deviation'].tolist()

    # Append first value to close the circular graph
    greedy_dev += greedy_dev[:1]
    ga_dev += ga_dev[:1]
    categories_plot = categories + [categories[0]]

    # What will be the angle of each axis in the plot? (divide the plot / number of variable)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # Initialise the spider plot
    fig = plt.figure(figsize=(16, 16), dpi=150)
    ax = plt.subplot(111, polar=True)

    # If you want the first axis to be on top:
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], categories, size=10, y=0.08)

    # Wrap long labels
    import textwrap
    wrapped_labels = [textwrap.fill(cat, 30) for cat in categories]
    ax.set_xticklabels(wrapped_labels, fontsize=10)

    # Adjust label alignment based on angle
    for label, angle in zip(ax.get_xticklabels(), angles[:-1]):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')

    # Increase the distance of the labels from the plot
    ax.tick_params(axis='x', pad=30)

    # Draw ylabels
    ax.set_rlabel_position(0)
    
    # max value for deviation is around 60%, so let's set limits
    max_val = max(max(greedy_dev), max(ga_dev))
    limit = int(np.ceil(max_val / 10.0)) * 10
    
    plt.yticks(np.arange(10, limit+1, 10), [str(i) for i in range(10, limit+1, 10)], color="grey", size=10)
    plt.ylim(0, limit)

    # Plot Greedy
    ax.plot(angles, greedy_dev, linewidth=2.5, linestyle='solid', label="Greedy", color="#FFC300")
    ax.fill(angles, greedy_dev, "#FFC300", alpha=0.1)

    # Plot GA
    ax.plot(angles, ga_dev, linewidth=2.5, linestyle='solid', label="Genetic Algorithm", color="#800080")
    ax.fill(angles, ga_dev, "#800080", alpha=0.1)

    # Title and Legend
    plt.title('Average Deviation Radar Profile Comparison\n(Lower is Better)', size=20, y=1.1, pad=30)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1), fontsize=14)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.5)
    print(f"Deviation Radar chart saved to: {output_path}")

if __name__ == '__main__':
    create_radar_chart()
