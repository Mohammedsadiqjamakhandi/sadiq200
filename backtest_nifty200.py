import os
import pandas as pd
from your_strategy import check_signal  # <- implement your signal logic here

folder = "data/"
for file in os.listdir(folder):
    if file.endswith(".csv"):
        path = os.path.join(folder, file)
        df = pd.read_csv(path)
        symbol = file.replace(".csv", "")
        
        result = check_signal(df, symbol)
        if result:
            print(f"{symbol}: {result}")
