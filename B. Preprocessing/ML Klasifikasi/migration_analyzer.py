"""
MIGRATION ANALYZER - Compare old ML predictions with new rule-based predictions.

This script:
1. Loads the current dataset with ML-based consumption_labels
2. Generates new predictions using rule-based classifier
3. Compares old vs new
4. Generates detailed migration report
5. Identifies which food_groups have the most changes
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Import the rule-based classifier
sys.path.insert(0, str(Path(__file__).parent))
from rule_based_classifier import RuleBasedFoodClassifier


def analyze_migration():
    """Run complete migration analysis"""
    
    print("\n" + "="*80)
    print("MIGRATION ANALYSIS: ML-based vs Rule-based Consumption Label Classification")
    print("="*80)
    
    # Load current dataset
    print("\n[1/5] Loading current dataset...")
    data = pd.read_csv(
        Path(__file__).parent.parent.parent / 'A. Data/Data Processed/05_final_dataset.csv'
    )
    print(f"✓ Loaded {len(data)} items from 05_final_dataset.csv")
    print(f"  Columns: {list(data.columns[:10])}...")
    
    # Generate new predictions
    print("\n[2/5] Generating rule-based predictions...")
    classifier = RuleBasedFoodClassifier()
    new_predictions = classifier.predict_batch(data)
    print(f"✓ Generated {len(new_predictions)} predictions")
    
    # Add new columns to data
    data['new_consumption_label'] = new_predictions['label'].values
    data['new_confidence'] = new_predictions['confidence'].values
    
    # Compare
    print("\n[3/5] Comparing old vs new predictions...")
    data['label_changed'] = data['consumption_label'] != data['new_consumption_label']
    num_changed = data['label_changed'].sum()
    num_unchanged = (~data['label_changed']).sum()
    
    print(f"✓ Analysis complete")
    print(f"  Items unchanged: {num_unchanged:,} ({num_unchanged/len(data)*100:.1f}%)")
    print(f"  Items changed:   {num_changed:,} ({num_changed/len(data)*100:.1f}%)")
    
    # Generate migration report
    print("\n[4/5] Generating detailed migration report...")
    report_lines = []
    
    report_lines.append("\n" + "="*80)
    report_lines.append("MIGRATION REPORT: DETAILED COMPARISON")
    report_lines.append("="*80)
    
    report_lines.append(f"\nTotal items in dataset: {len(data):,}")
    report_lines.append(f"Items with label changes: {num_changed:,} ({num_changed/len(data)*100:.1f}%)")
    report_lines.append(f"Items unchanged: {num_unchanged:,} ({num_unchanged/len(data)*100:.1f}%)")
    
    # Summary of label changes
    report_lines.append("\n" + "-"*80)
    report_lines.append("LABEL DISTRIBUTION COMPARISON")
    report_lines.append("-"*80)
    
    labels = ['Main Course', 'Side Dish', 'Drink', 'Snack']
    report_lines.append(f"\n{'Label':<15} | {'Old (ML)':<10} | {'New (Rule)':<10} | {'Change':<10}")
    report_lines.append("-" * 60)
    
    for label in labels:
        old_count = (data['consumption_label'] == label).sum()
        new_count = (data['new_consumption_label'] == label).sum()
        change = new_count - old_count
        sign = "+" if change > 0 else ""
        report_lines.append(
            f"{label:<15} | {old_count:<10} | {new_count:<10} | {sign}{change:<9}"
        )
    
    # Confidence distribution
    report_lines.append("\n" + "-"*80)
    report_lines.append("CONFIDENCE DISTRIBUTION (New Rules)")
    report_lines.append("-"*80)
    
    conf_dist = data['new_confidence'].value_counts()
    for conf_level in ['high', 'medium', 'low']:
        count = conf_dist.get(conf_level, 0)
        report_lines.append(f"  {conf_level:<10}: {count:>5} items ({count/len(data)*100:>5.1f}%)")
    
    # Analyze which food_groups have most changes
    report_lines.append("\n" + "-"*80)
    report_lines.append("FOOD_GROUPS WITH MOST LABEL CHANGES (Top 10)")
    report_lines.append("-"*80)
    
    changes_by_group = data[data['label_changed']].groupby('food_group').size().sort_values(ascending=False)
    
    report_lines.append(f"\n{'Food Group':<40} | {'Changes':<10} | {'% of Total':<10}")
    report_lines.append("-" * 65)
    
    for food_group, count in changes_by_group.head(10).items():
        pct = (count / num_changed * 100)
        report_lines.append(f"{food_group:<40} | {count:<10} | {pct:>6.1f}%")
    
    # Analyze specific label transition patterns
    report_lines.append("\n" + "-"*80)
    report_lines.append("LABEL TRANSITION PATTERNS (Old -> New)")
    report_lines.append("-"*80)
    
    changed_data = data[data['label_changed']]
    if len(changed_data) > 0:
        transitions = changed_data.groupby(['consumption_label', 'new_consumption_label']).size()
        
        report_lines.append("\n{:<20} -> {:<20} : Count")
        report_lines.append("-" * 55)
        
        for idx, count in transitions.items():
            old_label, new_label = idx  # type: ignore
            report_lines.append(f"{old_label:<20} -> {new_label:<20} : {count:>5}")
    
    # Top ambiguous food_groups
    report_lines.append("\n" + "-"*80)
    report_lines.append("DETAILED CHANGES BY AMBIGUOUS FOOD_GROUP")
    report_lines.append("-"*80)
    
    ambiguous_groups = [
        'Fruits and Fruit Juices',
        'Dairy and Egg Products',
        'Baked Products',
        'Soups, Sauces, and Gravies',
        'Legumes and Legume Products'
    ]
    
    for group in ambiguous_groups:
        group_data = data[data['food_group'] == group]
        group_changes = group_data[group_data['label_changed']]
        
        if len(group_changes) > 0:
            report_lines.append(f"\n{group} ({len(group_data)} items, {len(group_changes)} changed)")
            report_lines.append("  " + "-"*60)
            
            # Show transition patterns for this group
            transitions = group_changes.groupby(['consumption_label', 'new_consumption_label']).size()
            for idx, count in transitions.items():
                old_label, new_label = idx  # type: ignore
                report_lines.append(f"    {old_label:15} -> {new_label:15} : {count:>3} items")
            
            # Show sample items
            report_lines.append("  Sample changes:")
            for idx, (_, row) in enumerate(group_changes.head(3).iterrows()):
                food_name = row['food_name'][:50]
                old_label = row['consumption_label']
                new_label = row['new_consumption_label']
                conf = row['new_confidence']
                report_lines.append(
                    f"    • {food_name:<50} {old_label:15} -> {new_label:15} ({conf})"
                )
    
    # Confidence level analysis
    report_lines.append("\n" + "-"*80)
    report_lines.append("CONFIDENCE LEVELS BY CHANGE STATUS")
    report_lines.append("-"*80)
    
    for status, data_subset in [("Unchanged", data[~data['label_changed']]), 
                                  ("Changed", data[data['label_changed']])]:
        report_lines.append(f"\n{status}:")
        conf_dist = data_subset['new_confidence'].value_counts()
        for conf_level in ['high', 'medium', 'low']:
            count = conf_dist.get(conf_level, 0)
            pct = (count / len(data_subset) * 100) if len(data_subset) > 0 else 0
            report_lines.append(f"  {conf_level:<10}: {count:>5} items ({pct:>5.1f}%)")
    
    report_lines.append("\n" + "="*80)
    report_lines.append("ANALYSIS COMPLETE")
    report_lines.append("="*80)
    
    # Print and return report
    report_text = "\n".join(report_lines)
    print("\n[5/5] Report generation complete")
    
    return data, report_text


def main():
    """Main entry point"""
    try:
        data, report = analyze_migration()
        
        # Print report to console
        print(report)
        
        # Save detailed CSV for inspection
        output_csv = Path(__file__).parent / 'migration_comparison.csv'
        
        # Select relevant columns for output
        output_data = data[[
            'fdc_id', 'food_name', 'food_group',
            'consumption_label', 'new_consumption_label', 'new_confidence',
            'label_changed'
        ]]
        
        output_data.to_csv(output_csv, index=False)
        print(f"\n✓ Detailed comparison saved: {output_csv}")
        
        # Also save just the changed items
        changed_csv = Path(__file__).parent / 'migration_changes_only.csv'
        output_data[output_data['label_changed']].to_csv(changed_csv, index=False)
        print(f"✓ Changed items only saved: {changed_csv}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
