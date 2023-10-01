
import pandas as pd
from unidecode import unidecode
import numpy as np 
import matplotlib.pyplot as plt

#a)

#Captacoes/Funding = Depósito Total (a)
# Load the Excel file into a DataFrame
file_path = r"C:\Users\Pichau\OneDrive\Documentos\merged_passivos.xlsx"
df = pd.read_excel(file_path)

# Convert the 'Data' column to datetime format
df['Data'] = pd.to_datetime(df['Data'])

# Clean non-numeric values from 'Depósito Total (a)' column
df['Depósito Total (a)'] = pd.to_numeric(df['Depósito Total (a)'], errors='coerce')

df['Depósito Total (a)'] = df['Depósito Total (a)'] * -1

df['Instituição'] = df['Instituição'].apply(lambda x: unidecode(x) if isinstance(x, str) else x)

# Drop rows with NaN values in 'Depósito Total (a)' column
df.dropna(subset=['Depósito Total (a)'], inplace=True)

# Continue with the rest of the code
grouped = df.groupby(['Data', 'Instituição'])['Depósito Total (a)'].sum().reset_index()


#Funing Expenses/DRE

# Load the Excel file into a DataFrame
file_path = r"C:\Users\Pichau\OneDrive\Documentos\merged_DRE.xlsx"
df2 = pd.read_excel(file_path)

# Convert the 'Data' column to datetime format
df2['Data'] = pd.to_datetime(df2['Data'])

# Clean non-numeric values from 'Depósito Total (a)' column
df2['Despesas de Captação (b1)'] = pd.to_numeric(df2['Despesas de Captação (b1)'], errors='coerce')

df2['Instituição'] = df2['Instituição'].apply(lambda x: unidecode(x) if isinstance(x, str) else x)

# Drop rows with NaN values in 'Depósito Total (a)' column
df2.dropna(subset=['Despesas de Captação (b1)'], inplace=True)

# Continue with the rest of the code
grouped2 = df2.groupby(['Data', 'Instituição'])['Despesas de Captação (b1)'].sum().reset_index()

df_resultado = pd.merge(grouped, grouped2, on=['Data', 'Instituição'])


# Ordene o DataFrame pelo nome da Instituição e pela Data
df_resultado.sort_values(by=['Instituição', 'Data'], inplace=True)

# Agrupe os dados por Instituição
grupo_instituicao = df_resultado.groupby('Instituição')

# Crie uma nova coluna "Funding Expenses" com a diferença entre as "Despesas de Captação (b1)" do período t-1 até t
df_resultado['Funding Expenses'] = grupo_instituicao['Despesas de Captação (b1)'].diff()


# Ordene o DataFrame pelo nome da Instituição e pela Data
df_resultado.sort_values(by=['Instituição', 'Data'], inplace=True)


# Crie uma nova coluna "Total Funding t-1" que armazena as "Depósito Total (a)" do período anterior (t-1)
df_resultado['Total Funding t-1'] = grupo_instituicao['Depósito Total (a)'].shift(1)


# Ordene o DataFrame pelo nome da Instituição e pela Data
df_resultado.sort_values(by=['Instituição', 'Data'], inplace=True)

# Agrupe os dados por Instituição
grupo_instituicao = df_resultado.groupby('Instituição')


# Calcule a nova coluna "Funding Cost" conforme a fórmula especificada
df_resultado['Funding Cost'] = df_resultado['Despesas de Captação (b1)'] / ((df_resultado['Total Funding t-1'] + df_resultado['Depósito Total (a)']) / 2) * 100

# Reordene o DataFrame para a ordem original (se necessário)
df_resultado.sort_index(inplace=True)

#b)
# Verifique se há valores infinitos ou negativos infinitos na coluna "Funding Cost"
inf_mask = (df_resultado['Funding Cost'] == np.inf) | (df_resultado['Funding Cost'] == -np.inf)

# Crie um novo DataFrame excluindo as linhas com valores infinitos
df_resultado = df_resultado[~inf_mask]

# Agrupe os dados por período (Data) e calcule a soma de todas as Depósito Total (a) para cada período
sum_total_funding = df_resultado.groupby('Data')['Depósito Total (a)'].sum().reset_index()

# Renomeie a coluna resultante para refletir a soma das Depósito Total (a)
sum_total_funding.rename(columns={'Depósito Total (a)': 'Sum Funding'}, inplace=True)

# Crie a coluna "Weight" que é igual à multiplicação da coluna "Depósito Total (a)" pela coluna "Funding Cost"
df_resultado['Weight'] = df_resultado['Depósito Total (a)'] * df_resultado['Funding Cost']

# Agrupe os dados por período (Data) e calcule a soma de todos os pesos para cada período
sum_total_weight = df_resultado.groupby('Data')['Weight'].sum().reset_index()

# Renomeie a coluna resultante para refletir a soma dos pesos
sum_total_weight.rename(columns={'Weight': 'Sum Weight'}, inplace=True)

sum_t = pd.merge(sum_total_funding, sum_total_weight, on=['Data'])

sum_t['Avg_Funding_Cost'] = sum_t['Sum Weight'] / sum_t['Sum Funding']

plt.figure(figsize=(12,6))
plt.plot(sum_t['Data'], sum_t['Avg_Funding_Cost'], marker='o', linestyle='-')
plt.title('Time Series of Average Funding Cost')
plt.xlabel('Time')
plt.ylabel('Average Funding Cost')
plt.grid(True)

plt.tight_layout()
plt.show()