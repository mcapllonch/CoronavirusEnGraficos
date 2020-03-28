import pandas as pd
from collections import Counter


# Open Colombia's data
df = pd.read_csv('datos.csv')

# Count cases per province
counter = {k: v for k, v in sorted(Counter(df['Departamento']).items(), key=lambda item: item[1], reverse=True)}

# Create table to show
dc = {'Departamento': counter.keys(), 'Confirmados': counter.values()}
dfd = pd.DataFrame.from_dict(dc, orient='index').transpose()
dfd.to_html('departamentos.html', index=False)