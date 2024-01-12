import pandas as pd


def get_indx(lst, element):
    '''
    Pega todos os indices que um dado elemento aparece numa lista.
    '''
    return [index for index, value in enumerate(lst) if value == element]

def read_QE_band(file_name):
    '''
    Converte o arquivo .gnu que sai do quantum espresso e
    transforma num Dataframe onde cada coluna é uma banda.
    
    Args: 
    file_name: string com o caminho do arquivo txt copiado
    do QE e modificado*
    
    Returns:
    Dataframe pandas com as bandas em colunas separadas (e0, e1, e2...)
    
    *Obs: Precisa primeiro copiar o .gnu para um .txt, dar shift + tab
    para "encostar na parede", substituir "  " por " " e colocar "k E" na
    primeira coluna.
    '''
    
    banda = pd.read_csv(file_name, sep = ' ')
    indices = list(set(banda['k']))
    indices.sort()
    bandas = {}
    bandas['k'] = indices
    ncol = list(banda['k']).count(indices[0])
    for i in range(ncol):
        bandas['e'+str(i)] = []
    for i in indices:
        pos = get_indx(banda['k'], i)
        lista_energias = [banda['E'][p] for p in pos]
        for n in range(ncol):
            bandas['e'+str(n)].append(lista_energias[n])
    bandas = pd.DataFrame(bandas)
    return pd.DataFrame(bandas)