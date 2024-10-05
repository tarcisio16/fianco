import numpy as np

# Definire il tipo di dati per l'array strutturato
dtype = [('colonna1', np.uint64), ('colonna2', np.uint16)]

# Creare un array strutturato con 2^16 voci
n_entries = 2**32
data = np.zeros(n_entries, dtype=dtype)

# Dimensione dell'array in byte
data_size = data.nbytes

# Dimensione dei dati calcolata
calculated_size = n_entries * (8 + 2)  # 8 byte per uint64 + 2 byte per uint16

# Calcolare l'overhead
overhead = data_size - calculated_size

# Stampa dei risultati
print("Array:")
print(data)
print(f"\nNumero di voci: {n_entries}")
print(f"Data size: {data_size} bytes")
print(f"Calculated size: {calculated_size} bytes")
print(f"Overhead: {overhead} bytes")