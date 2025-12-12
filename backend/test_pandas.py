import pandas as pd
import sys

print("Testing Pandas...")
try:
    df = pd.DataFrame({'a': [1, 2, 3]})
    print("Pandas works!")
    print(df)
except Exception as e:
    print(f"Pandas Error: {e}")
    sys.exit(1)
