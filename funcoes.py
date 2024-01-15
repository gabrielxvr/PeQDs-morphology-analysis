import pandas as pd
from io import StringIO

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


def read_crystal_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    start_index = lines.index(' CARTESIAN COORDINATES - PRIMITIVE CELL\n') + 4
    for i in range(start_index, len(lines)):
        if lines[i].split()[0].isdigit():
            last_line = i
    data_df = {'atom_number': [],
        'atom_species': [],
        'X(ANGSTROM)': [],
        'Y(ANGSTROM)': [],
        'Z(ANGSTROM)': []}
    data_df = pd.DataFrame(data_df)
    for line in lines[start_index : last_line+1]:
        line_list = []
        for k in range(len(line.split())):
            if k != 2:
                line_list.append(float(line.split()[k]))
            if k == 2:
                line_list.append(line.split()[k])
        line_list = line_list[1:]
        data_df.loc[len(data_df)] = line_list
        
    return data_df

def read_crystal_file_lat(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    start_index = lines.index('     THE SELECTED PLANE IS IN THE X-Y PLANE\n') + 4  
    B1 = lines[start_index].split()[1:]
    B2 = lines[start_index+1].split()[1:]
    B3 = lines[start_index+2].split()[1:]
    return [B1,B2,B3]


def sort_atoms(df_atoms):
    """Sort the atoms by atomic numbers
    
    Output:
        A sorted dataframe
    """
    
    df_sorted = df_atoms.sort_values('atom_number', ascending=False).reset_index(drop=True)
    
    return df_sorted

def zero_xyz(df_atoms):
    """Add the min value to Z
    
    Output:
        A normalized dataframe
    """
    
    df_atoms['Z(ANGSTROM)'] = df_atoms['Z(ANGSTROM)'] - df_atoms['Z(ANGSTROM)'].min()
    
    return df_atoms


def print_POSCAR(df_atoms, lat):
    for k in lat:
        print('   '+ '    '.join([format(float(b), '.15f')[:15] for b in k]))
    species = sorted(set(df_atoms['atom_species']), key=list(df_atoms['atom_species']).index)
    print(' '.join(species))
    quant = []
    for s in species:
        quant.append(list(df_atoms['atom_species']).count(s))
    for i in range(len(quant)):
        quant[i] = str(quant[i])
    print(' '.join(quant))
    print('direct')

    for i in range(len(df_atoms['Z(ANGSTROM)'])):
        pos = [df_atoms['X(ANGSTROM)'][i],df_atoms['Y(ANGSTROM)'][i],df_atoms['Z(ANGSTROM)'][i]]
        for j in range(len(pos)):
            pos[j] = format(pos[j], '.15f')
            pos[j] = pos[j][:15]
        line = '   ' + '   '.join(map(str, pos)) + ' ' + df_atoms['atom_species'][i]
        print(line)
        
def convert_crystal_data(file_name):
    df_atoms = read_crystal_file(file_name)
    df_atoms = sort_atoms(df_atoms)
    df_atoms = zero_xyz(df_atoms)
    lat = read_crystal_file_lat(file_name)
    print_POSCAR(df_atoms,lat)
    return df_atoms