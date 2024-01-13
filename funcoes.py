import pandas as pd

def read_QE_band(file_name):
    '''
    Converte o arquivo .gnu que sai do quantum espresso e
    transforma num Dataframe onde cada coluna é uma banda.
    
    Args: 
    file_name: string com o caminho do arquivo .gnu gerado pelo QE
    Returns:
    Dataframe pandas com as bandas em colunas separadas (e0, e1, e2...) 
    '''
    data = []
    with open(file_name, 'r') as input_file:
        for line in input_file:
            parts = line.strip().split()
            if len(parts) == 2:
                k, E = parts
                data.append([float(k), float(E)])

    columns = ['k', 'E']
    banda = pd.DataFrame(data, columns=columns)    
    indices = list(set(banda['k']))
    indices.sort()
    bandas = {}
    bandas['k'] = indices
    ncol = list(banda['k']).count(indices[0])
    for i in range(ncol):
        bandas['e'+str(i)] = []
    for i in indices:
        pos = [index for index, value in enumerate(banda['k']) if value == i]
        lista_energias = [banda['E'][p] for p in pos]
        for n in range(ncol):
            bandas['e'+str(n)].append(lista_energias[n])
    bandas = pd.DataFrame(bandas)
    return pd.DataFrame(bandas)