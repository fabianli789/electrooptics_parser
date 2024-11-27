from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

import numpy as np
from nomad.config import config
from nomad.datamodel.data import Schema
from nomad.metainfo import Quantity, SchemaPackage, Section, MSection, SubSection
from runschema.run import Run
from runschema.calculation import Calculation

configuration = config.get_plugin_entry_point(
    'electrooptics_parser.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()


class ElectroopticsOutput(MSection):
    m_def = Section(validate=False)
    theta = Quantity(type=np.float64, shape=[2, '*'], description="""Each repeating subsection corresponds to a different theta-file, each theta-file represents a different
                                                                    trajectory. 1st row time, 2nd row is theta, which is the dot product between the electric field and 
                                                                    the alignment of the polymer chain.""")

class ElectroopticsFix(MSection):
    m_def = Section(validate=False)
    value = Quantity(type=str, shape=['*'])

class ElectroopticsSystem(MSection):
    m_def = Section(validate=False)
    atoms = Quantity(type=np.float64, description='no. of atoms in the system')
    bonds = Quantity(type=np.float64, description='no. of bonds in the system')
    angles = Quantity(type=np.float64, description='no. of angles in the system')
    dihedrals = Quantity(type=np.float64, description='no. of dihedrals in the system')
    impropers = Quantity(type=np.float64, description='no. of impropers in the system')
    atom_types = Quantity(type=np.float64, description='no. of atom types in the system')
    bond_types = Quantity(type=np.float64, description='no. of bond types in the system')
    angle_types = Quantity(type=np.float64, description='no. angle types in the system')
    dihedral_types = Quantity(type=np.float64, description='no. of dihedral types in the system')
    improper_types = Quantity(type=np.float64, description='no. of improper types in the system')
    atoms_values = Quantity(type=np.float64, shape=[7, '*'], description="""1st column is an index. 2nd column is the ID of molecule. 
                                                                         3rd column is type of atom. 4th column is partial
                                                                         charge in units of elementary charge e. Other columns are positions in Angstrom.""")
    bonds_values = Quantity(type=np.float64, shape=[4, '*'], description="""1st column is index. 2nd column is type of bond. 3rd column is atom ID that are connected by this bond. 
                                                                         4th column is atom ID but for the second atom.""")
    angles_values = Quantity(type=np.float64, shape=[5, '*'], description="""1st column is an index. 2nd column is the type. Other columns are angles.
                                                                          """)
    dihedrals_values = Quantity(type=np.float64, shape=['*', 6], description="""1st column is index, 2nd column is type. Other 4 columns are dihedrals formed by these 4 atoms.
                                                                             """)
    impropers_values = Quantity(type=np.float64, shape=['*', 6], description="""1st column is an index, 2nd column is type. Other 4 columns are Impropers formed by these 4 atoms.
                                                                             """)
    xlo = Quantity(type=np.float64, description='lower value of sample in x-direction, in Angstrom.')
    xhi = Quantity(type=np.float64, description='higher value of sample in x-direction, in Angstrom.')
    ylo = Quantity(type=np.float64, description='lower value of sample in y-direction, in Angstrom.')
    yhi = Quantity(type=np.float64, description='higher value of sample in y-direction, in Angstrom.')
    zlo = Quantity(type=np.float64, description='lower value of sample in z-direction, in Angstrom.')
    zhi = Quantity(type=np.float64, description='higher value of sample in z-direction, in Angstrom.')
class ElectroopticsInput(MSection):
    m_def = Section(validate=False)
    e_field = Quantity(type=np.float64, description='electric field in V/Ang')
    dimension = Quantity(type=int, description='dimension of the system.')
    boundary = Quantity(type=str, shape=['*'], description='periodicity of the system.')
    units = Quantity(type=str)
    atom_style = Quantity(type=str)
    neighbor = Quantity(type=str, shape=['*'])
    newton = Quantity(type=str)
    pair_style = Quantity(type=str, shape=['*'])
    pair_modify = Quantity(type=str, shape=['*'])
    kspace_style = Quantity(type=str, shape=['*'])
    bond_style = Quantity(type=str)
    angle_style = Quantity(type=str)
    dihedral_style = Quantity(type=str)
    improper_style = Quantity(type=str)
    compute = Quantity(type=str, shape=['*'])
    thermo_modify = Quantity(type=str, shape=['*'])
    thermo = Quantity(type=np.float64)
    minimize = Quantity(type=np.float64, shape=['*'])
    velocity = Quantity(type=str, shape=['*'])
    group = Quantity(type=str, shape=['*'], description='Which atoms by atom ID have been fixed by their positions.')
    dump = Quantity(type=str, shape=['*'])
    dump_modify = Quantity(type=str, shape=['*'])
    
    fix = SubSection(sub_section=ElectroopticsFix.m_def, repeats=True)
class ElectroopticsCalculation(Calculation):
    
    m_def = Section(validate=False, extends_base_section=False)    
    
    
    electrooptics_input = SubSection(sub_section=ElectroopticsInput.m_def, repeats=False)
    electrooptics_system = SubSection(sub_section=ElectroopticsSystem.m_def, repeats=False)
    electrooptics_output = SubSection(sub_section=ElectroopticsOutput.m_def, repeats=True)

m_package.__init_metainfo__()
