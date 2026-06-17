import os

path = os.path.abspath(r"D. Model/Genetic Algorithm/ga_dicky.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Locate standard imports start
imports_start = "import pandas as pd"
if imports_start in content:
    content = content.replace(imports_start, "from __future__ import annotations\nimport pandas as pd", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully added from __future__ import annotations!")
else:
    print("Target import pandas as pd not found!")
