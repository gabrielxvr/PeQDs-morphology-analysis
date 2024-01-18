import pandas as pd

def read_QE_band(file_name):
    '''
    Converts the .gnu file output from Quantum Espresso and 
    transforms it into a DataFrame where each column represents a band.

    Args:
        file_name: string containing the path to the .gnu file generated by QE
    Returns:
        Pandas DataFrame with bands in separate columns (e0, e1, e2...)
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


##############################################################################
# Functions to read Crystal output after cutting slabs for surface analysis. #
##############################################################################

def read_crystal_file(file_path):
    """ 
    Reads the out file and outpus a dataframe of atomic position
    """
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
    """
    Reads the out file and outpus list of new lattice vectors of the slab
    """
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
    """
    Takes a dataframe of atomic positions and a list of lattice vectors and
    prints it in the format of VASP POSCAR input file.
    """
    # ADD VACUUM:
    lat[2][2] = str(float(lat[2][2]) + max(df_atoms['Z(ANGSTROM)']) + 15)
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


def print_QE(df_atoms, lat):
    """
    Takes a dataframe of atomic positions and a list of lattice vectors and
    prints it in the format of Quantum Espresso input file.
    """
    # ADD VACUUM:
    lat[2][2] = str(float(lat[2][2]) + max(df_atoms['Z(ANGSTROM)']) + 15)
    print("CELL_PARAMETERS (alat=  1.889725989)")
    for k in lat:
        print('   '+ '   '.join([format(float(b), '.15f')[:15] for b in k]))
    print('ATOMIC_POSITIONS (crystal)')

    for i in range(len(df_atoms['Z(ANGSTROM)'])):
        pos = [df_atoms['X(ANGSTROM)'][i],df_atoms['Y(ANGSTROM)'][i],df_atoms['Z(ANGSTROM)'][i]]
        for j in range(len(pos)):
            pos[j] = format(pos[j], '.15f')
            pos[j] = pos[j][:15]
        line = df_atoms['atom_species'][i]+'   ' + '   '.join(map(str, pos))
        print(line)
        
def convert_crystal_data(file_name, QE = False):
    """
    Takes the file name, converts to sorted and translated dataframe, and
    prints it in either VASP or QE format.
    """
    df_atoms = read_crystal_file(file_name)
    df_atoms = sort_atoms(df_atoms)
    df_atoms = zero_xyz(df_atoms)
    lat = read_crystal_file_lat(file_name)
    if QE == False:
        print_POSCAR(df_atoms,lat)
    else:
        print_QE(df_atoms,lat)
    return df_atoms

##############################################################################
# Functions to read relax output and create scf inputs. #
##############################################################################

def read_relax(file_path_rr):
    """ 
    Reads the relax.out file and outpus a string of atomic position
    """
    file_name = 'relax.out'
    file_path_rr = file_path_rr + file_name
    with open(file_path_rr, 'r') as file:
        lines = file.readlines()
    start_index = lines.index('Begin final coordinates\n') + 2
    atomic_positions = ''.join(lines[start_index:start_index+16])
    return atomic_positions

def read_cell_parameters(file_path_rcp):
    """ 
    Reads the relax.in file and outpus a string of cell parameters
    """
    file_name = 'relax.in'
    file_path_rcp = file_path_rcp + file_name
    with open(file_path_rcp, 'r') as file:
        lines = file.readlines()
    start_index = lines.index('''CELL_PARAMETERS 'angstrom'\n''')
    cell_parameters = ''.join(lines[start_index:start_index+4])
    return cell_parameters
    


def save_scf(file_path_ss, atomic_positions, cell_parameters):
    content = """&CONTROL
    calculation   = 'scf',
    verbosity='high',
    restart_mode  = 'from_scratch',
    nstep         =  200
    pseudo_dir = './'
    prefix='out',
    tstress = .true.,
    tprnfor = .true.,
 /
&SYSTEM
    ibrav = 0,
    nat= 15,
    ntyp= 3,
    ecutwfc     = 30.0 ,
    ecutrho     = 300.0 ,
    nspin = 1 ,
    degauss = 0.01 ,
    occupations='smearing',
 /
&ELECTRONS
    electron_maxstep  = 500
    conv_thr          = 1.0e-6
    mixing_mode       = 'plain'
    mixing_beta       = 0.3
    diagonalization   = 'david'
 /
&IONS
    ion_dynamics      = 'bfgs'
    ion_positions     = 'default '
 /
 &cell
    cell_dynamics='bfgs',
    press=0.0,
    press_conv_thr=0.5,
/
ATOMIC_SPECIES
 Cs     132.905 Cs.upf
 Pb     207.200 Pb.upf
 Br     79.904  Br.upf
K_POINTS {automatic}
4 4 1 0 0 0
"""
    
    scf_text = content + cell_parameters + atomic_positions

    file_path_ss = file_path_ss + "scf.in"

    with open(file_path_ss, "w") as file:
        file.write(scf_text)

    print(f'The content has been saved to {file_path_ss}/scf.in.')