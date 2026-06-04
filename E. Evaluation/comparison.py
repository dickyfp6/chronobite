import sys
import os
import pandas as pd
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
greedy_csv = os.path.join(current_dir, 'output', 'greedy', 'summary.csv')
ga_csv = os.path.join(current_dir, 'output', 'ga', 'summary.csv')
output_dir = os.path.join(current_dir, 'output', 'comparison')

def plot_radar_chart(df, title, filename):
    try:
        categories = list(df['Profile'])
        N = len(categories)
        
        # What will be the angle of each axis in the plot
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        # Initialise the spider plot
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        # If you want the first axis to be on top:
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Draw one axe per variable + add labels labels yet
        plt.xticks(angles[:-1], categories)
        
        # Draw ylabels
        ax.set_rlabel_position(0)
        plt.yticks([20, 40, 60, 80, 100], ["20","40","60","80","100"], color="grey", size=7)
        plt.ylim(0, 100)
        
        # ------- PART 2: Add plots
        
        # Plot Greedy
        values = df['CS Rate_Greedy'].values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, linestyle='solid', label="Greedy", color='teal')
        ax.fill(angles, values, 'teal', alpha=0.1)
        
        # Plot GA
        values = df['CS Rate_GA'].values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, linestyle='solid', label="Genetic Algorithm", color='coral')
        ax.fill(angles, values, 'coral', alpha=0.1)
        
        plt.title(title, size=15, y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, filename), dpi=300)
        plt.close()
    except Exception as e:
        print(f"Could not generate radar chart: {e}")

def main():
    print("==========================================")
    print(" COMPARING GREEDY VS GENETIC ALGORITHM ")
    print("==========================================")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(greedy_csv):
        print(f"[ERROR] Could not find Greedy summary at {greedy_csv}")
        return
        
    if not os.path.exists(ga_csv):
        print(f"[ERROR] Could not find GA summary at {ga_csv}")
        return
        
    df_greedy = pd.read_csv(greedy_csv)
    df_ga = pd.read_csv(ga_csv)
    
    # Merge on Profile
    merged = pd.merge(
        df_greedy, 
        df_ga, 
        on='Profile', 
        suffixes=('_Greedy', '_GA')
    )
    
    # Plot Side-by-Side CS Rate
    plt.figure(figsize=(12, 6))
    x = np.arange(len(merged['Profile']))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, merged['CS Rate_Greedy'], width, label='Greedy', color='teal')
    rects2 = ax.bar(x + width/2, merged['CS Rate_GA'], width, label='Genetic Algorithm', color='coral')
    
    ax.set_ylabel('Constraint Satisfaction Rate (%)')
    ax.set_title('Constraint Satisfaction: Greedy vs Genetic Algorithm')
    ax.set_xticks(x)
    ax.set_xticklabels(merged['Profile'], rotation=15, ha='right')
    ax.legend()
    ax.set_ylim(0, 110)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_cs_rate.png'), dpi=300)
    plt.close()
    
    # Plot Side-by-Side Avg Deviation (Lower is better)
    plt.figure(figsize=(12, 6))
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, merged['Avg Deviation_Greedy'], width, label='Greedy', color='teal')
    rects2 = ax.bar(x + width/2, merged['Avg Deviation_GA'], width, label='Genetic Algorithm', color='coral')
    
    ax.set_ylabel('Average Deviation from Target (%)')
    ax.set_title('Average Deviation: Greedy vs Genetic Algorithm (Lower is Better)')
    ax.set_xticks(x)
    ax.set_xticklabels(merged['Profile'], rotation=15, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_deviation.png'), dpi=300)
    plt.close()
    
    # Plot radar chart
    plot_radar_chart(merged, 'Constraint Satisfaction Radar Profile Comparison', 'comparison_radar.png')

    print("\nFINAL COMPARISON SUMMARY:")
    print("==========================================================================================")
    print(f"{'Profile':<50} | {'CS Rate (Greedy)':<18} | {'CS Rate (GA)':<15}")
    print("-" * 90)
    for idx, row in merged.iterrows():
        print(f"{row['Profile']:<50} | {row['CS Rate_Greedy']:<17.1f}% | {row['CS Rate_GA']:<14.1f}%")
    print("==========================================================================================")
    
    print("\n==========================================================================================")
    print(f"{'Profile':<50} | {'Avg Dev (Greedy)':<18} | {'Avg Dev (GA)':<15}")
    print("-" * 90)
    for idx, row in merged.iterrows():
        print(f"{row['Profile']:<50} | {row['Avg Deviation_Greedy']:<17.1f}% | {row['Avg Deviation_GA']:<14.1f}%")
    print("==========================================================================================")
    print(f"\nAll comparison charts saved to: {output_dir}")

if __name__ == "__main__":
    main()
