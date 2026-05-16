#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

# Read improved function with UTF-8 encoding
with open('improved_portion_sizing.py', 'r', encoding='utf-8') as f:
    improved_content = f.read()

# Change function name from _v2 to original
improved_content = improved_content.replace('def calculate_portion_sizes_dynamic_v2(', 'def calculate_portion_sizes_dynamic(')

# Read ga_v1.py with UTF-8
with open('ga_v1.py', 'r', encoding='utf-8') as f:
    ga_content = f.read()

# Find the section comment for step 7
start_marker = '# 7. CALCULATE PORTION SIZES - Hitung gram dinamis'
start_idx = ga_content.find(start_marker)

if start_idx > 0:
    # Find the function definition
    func_start_idx = ga_content.find('def calculate_portion_sizes_dynamic(', start_idx)
    
    if func_start_idx > 0:
        # Find the end of function (start of next def)
        next_func_idx = ga_content.find('\ndef display_portion_summary_dynamic(', func_start_idx)
        
        if next_func_idx > 0:
            # Get the header comment section
            header_start = ga_content.rfind('\n#', 0, start_idx) + 1
            header_section = ga_content[header_start:start_idx + len(start_marker) + len('\n')]
            
            # Build replacement
            new_content = (
                ga_content[:header_start] + 
                header_section + 
                improved_content + 
                '\n\n' + 
                ga_content[next_func_idx:]
            )
            
            # Write back with UTF-8
            with open('ga_v1.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print('[OK] Function replaced successfully')
            print(f'Replaced from position {func_start_idx} to {next_func_idx}')
        else:
            print('[ERROR] Could not find display_portion_summary_dynamic')
    else:
        print('[ERROR] Could not find calculate_portion_sizes_dynamic function definition')
else:
    print('[ERROR] Could not find step 7 marker')
