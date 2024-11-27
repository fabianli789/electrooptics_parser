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

import yaml
import os
import re
import datetime
import numpy as np
import filecmp
from pathlib import Path

from nomad.config import config
from nomad.datamodel.metainfo.workflow import Workflow
from nomad.parsing.parser import MatchingParser
from runschema.run import Run, Program
from runschema.calculation import Calculation

from electrooptics_parser.schema_packages.schema_package import ElectroopticsCalculation, ElectroopticsSystem, ElectroopticsInput, ElectroopticsFix, ElectroopticsOutput

configuration = config.get_plugin_entry_point(
    'electrooptics_parser.parsers:parser_entry_point'
)

def DetailedParser(filepath, archive):
    run = Run()
    archive.run.append(run)
    run.program = Program(name="Ka Chun Chan's Electrooptics Parser")
    
    calculation = ElectroopticsCalculation()
    run.calculation.append(calculation)

    electroopticsinput = ElectroopticsInput()
    calculation.electrooptics_input = electroopticsinput
    
    electroopticssystem = ElectroopticsSystem()
    calculation.electrooptics_system = electroopticssystem
    
    for root, dirs, files in sorted(os.walk(filepath.parent)):    
        natsort = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', s)]
        files = sorted(files, key = natsort)
        
        for file in files:    
            with open(root + '/' + file) as f:
                if 'in_electrooptics' in file:    
                    for i, line in enumerate(f):
                        parts = line.split()
                        if r'#' in line:
                            continue
                        if not line.strip():
                            continue
                        if re.search(r'\sT\s', line):
                            parts = line.split('equal ')
                            _temp = float(parts[1])
                            calculation.temperature = _temp
                        if re.search(r'variable\s*efield', line):
                            parts = line.split('equal ')
                            _e_field = float(parts[1])
                            electroopticsinput.e_field = _e_field
                        if 'dimension' in line:
                            parts = line.split()
                            _dimension = int(parts[1])
                            electroopticsinput.dimension = _dimension
                        if 'boundary' in line:
                            _boundary = [parts[b] for b in range(1, len(parts))]
                            electroopticsinput.boundary = _boundary
                        if 'units' in line:
                            _units = parts[1]
                            electroopticsinput.units = _units
                        if 'atom_style' in line:
                            _atom_style = parts[1]
                            electroopticsinput.atom_style = _atom_style
                        if 'neighbor' in line:
                            _neighbor = [parts[i] for i in range(1, len(parts))]
                            electroopticsinput.neighbor = _neighbor
                        if 'newton' in line:
                            _newton = parts[1]
                            electroopticsinput.newton = _newton
                        if 'pair_style' in line:
                            _pair_style = [parts[i] for i in range(1, len(parts))]
                            electroopticsinput.pair_style = _pair_style
                        if 'pair_modify' in line:
                            _pair_modify = [parts[i] for i in range(1, len(parts))]
                            electroopticsinput.pair_modify = _pair_modify
                        if 'kspace_style' in line:
                            _kspace_style = [parts[i] for i in range(1, len(parts))]
                            electroopticsinput.kspace_style = _kspace_style
                        if 'bond_style' in line:
                            _bond_style = parts[1]
                            electroopticsinput.bond_style = _bond_style
                        if 'angle_style' in line:
                            _angle_style = parts[1]
                            electroopticsinput.angle_style = _angle_style
                        if 'dihedral_style' in line:
                            _dihedral_style = parts[1]
                            electroopticsinput.dihedral_style = _dihedral_style
                        if 'improper_style' in line:
                            _improper_style = parts[1]
                            electroopticsinput.improper_style = _improper_style
                        if 'compute' in line:
                            _compute = [parts[i] for i in range(1, len(parts))]
                            electroopticsinput.compute = _compute
                        if 'thermo_modify' in line:
                            _thermo_modify = [parts[i] for i in range(1, len(parts))]
                            electroopticsinput.thermo_modify = _thermo_modify
                        if re.search(r'thermo\s*\d', line):
                            _thermo = float(parts[1])
                            electroopticsinput.thermo = _thermo
                        if 'minimize' in line:
                            _minimize = [float(parts[i]) for i in range(1, len(parts))]
                            electroopticsinput.minimize = _minimize
                        if 'velocity' in line:
                            _velocity = [parts[i] for i in range(1, len(parts))]
                            electroopticsinput.velocity = _velocity
                        if re.search(r'^fix\s', line):
                            electroopticsfix = ElectroopticsFix()
                            electroopticsinput.fix.append(electroopticsfix)
                            _fix = [parts[i] for i in range(1, len(parts))]
                            electroopticsfix.value = _fix
                        if re.search(r'group', line):
                            _group = [parts[i] for i in range(1, len(parts))]
                        if re.search(r'^\d', line):
                            _group.append(line)    
                        if re.search(r'dump\s', line):
                            _dump = [parts[i] for i in range(1, len(parts))]
                            electroopticsinput.dump = _dump
                        if 'dump_modify' in line:
                            _dump_modify = [parts[1] for i in range(1, len(parts))]
                            electroopticsinput.dump_modify = _dump_modify
                    electroopticsinput.group = _group
                if 'system_electrooptics' in file:
                    mode = 0
                    Atoms1 = [] # 1st column of Atoms-array
                    Atoms2 = [] # 2nd column of Atoms-array
                    Atoms3 = []
                    Atoms4 = []
                    Atoms5 = []
                    Atoms6 = []
                    Atoms7 = []
                    Bonds1 = [] # 1st column of Bonds-array
                    Bonds2 = []
                    Bonds3 = []
                    Bonds4 = []
                    Angles1 = []
                    Angles2 = []
                    Angles3 = []
                    Angles4 = []
                    Angles5 = []
                    Dihedrals1 = []
                    Dihedrals2 = []
                    Dihedrals3 = []
                    Dihedrals4 = []
                    Dihedrals5 = []
                    Dihedrals6 = []
                    Impropers1 = []
                    Impropers2 = []
                    Impropers3 = []
                    Impropers4 = []
                    Impropers5 = []
                    Impropers6 = []
                    for i, line in enumerate(f):
                        parts = line.split()
                        if 'lammps' in line.lower():
                            continue
                        if not line.strip():
                            continue
                        if 'atoms' in line:
                            _atoms = float(parts[0])
                            electroopticssystem.atoms = _atoms
                        if 'bonds' in line:
                            _bonds = float(parts[0])
                            electroopticssystem.bonds = _bonds
                        if 'angles' in line:
                            _angles = float(parts[0])
                            electroopticssystem.angles = _angles
                        if 'dihedrals' in line:
                            _dihedrals = float(parts[0])
                            electroopticssystem.dihedrals = _dihedrals
                        if 'impropers' in line:
                            _impropers = float(parts[0])
                            electroopticssystem.impropers = _impropers
                        if 'atom types' in line:
                            _atom_types = float(parts[0])
                            electroopticssystem.atom_types = _atom_types
                        if 'bond types' in line:
                            _bond_types = float(parts[0])
                            electroopticssystem.bond_types = _bond_types
                        if 'angle types' in line:
                            _angle_types = float(parts[0])
                            electroopticssystem.angle_types = _angle_types
                        if 'dihedral types' in line:
                            _dihedral_types = float(parts[0])
                            electroopticssystem.dihedral_types = _dihedral_types
                        if 'improper types' in line:
                            _improper_types = float(parts[0])
                            electroopticssystem.improper_types = _improper_types
                        if 'xlo' in line:
                            _xlo = float(parts[0])
                            _xhi = float(parts[1])
                            electroopticssystem.xlo = _xlo
                            electroopticssystem.xhi = _xhi
                        if 'ylo' in line:
                            _ylo = float(parts[0])
                            _yhi = float(parts[1])
                            electroopticssystem.ylo = _ylo
                            electroopticssystem.yhi = _yhi
                        if 'zlo' in line:
                            _zlo = float(parts[0])
                            _zhi = float(parts[1])
                            electroopticssystem.zlo = _zlo
                            electroopticssystem.zhi = _zhi
                        if re.search('Atoms', line):
                            mode = 1
                            continue
                        if mode == 1 and len(line.split(' ')) > 1:                
                            Atoms1.append(float(parts[0]))
                            Atoms2.append(float(parts[1]))
                            Atoms3.append(float(parts[2]))
                            Atoms4.append(float(parts[3]))
                            Atoms5.append(float(parts[4]))
                            Atoms6.append(float(parts[5]))
                            Atoms7.append(float(parts[6]))

                        if re.search(r'Bonds', line):
                            mode = 2
                            continue
                        if mode == 2 and len(line.split(' ')) > 1:
                            Bonds1.append(float(parts[0]))
                            Bonds2.append(float(parts[1]))
                            Bonds3.append(float(parts[2]))
                            Bonds4.append(float(parts[3]))
                        if re.search(r'Angles', line):
                            mode = 3
                            continue
                        if mode == 3 and len(line.split(' ')) > 1:
                            Angles1.append(float(parts[0]))
                            Angles2.append(float(parts[1]))
                            Angles3.append(float(parts[2]))
                            Angles4.append(float(parts[3]))
                            Angles5.append(float(parts[4]))
                        if re.search(r'Dihedrals', line):
                            mode = 4
                            continue
                        if mode == 4 and len(line.split(' ')) > 1:
                            Dihedrals1.append(float(parts[0]))
                            Dihedrals2.append(float(parts[1]))
                            Dihedrals3.append(float(parts[2]))
                            Dihedrals4.append(float(parts[3]))
                            Dihedrals5.append(float(parts[4]))
                            Dihedrals6.append(float(parts[5]))
                        if re.search(r'Impropers', line):
                            mode = 5
                            continue
                        if mode == 5 and len(line.split(' ')) > 1:
                            Impropers1.append(float(parts[0]))
                            Impropers2.append(float(parts[1]))
                            Impropers3.append(float(parts[2]))
                            Impropers4.append(float(parts[3]))
                            Impropers5.append(float(parts[4]))
                            Impropers6.append(float(parts[5]))

                    _atoms_values = np.zeros((int(_atoms), 7))        
                    _atoms_values[:,0] = Atoms1
                    _atoms_values[:,1] = Atoms2
                    _atoms_values[:,2] = Atoms3
                    _atoms_values[:,3] = Atoms4
                    _atoms_values[:,4] = Atoms5
                    _atoms_values[:,5] = Atoms6
                    _atoms_values[:,6] = Atoms7
                    electroopticssystem.atoms_values = _atoms_values

                    _bonds_values = np.zeros((int(_bonds), 4))
                    _bonds_values[:,0] = Bonds1
                    _bonds_values[:,1] = Bonds2
                    _bonds_values[:,2] = Bonds3
                    _bonds_values[:,3] = Bonds4
                    electroopticssystem.bonds_values = _bonds_values

                    _angles_values = np.zeros((int(_angles), 5))
                    _angles_values[:,0] = Angles1
                    _angles_values[:,1] = Angles2
                    _angles_values[:,2] = Angles3
                    _angles_values[:,3] = Angles4
                    _angles_values[:,4] = Angles5
                    electroopticssystem.angles_values = _angles_values

                    _dihedrals_values = np.zeros((int(_dihedrals), 6))
                    _dihedrals_values[:,0] = Dihedrals1
                    _dihedrals_values[:,1] = Dihedrals2
                    _dihedrals_values[:,2] = Dihedrals3
                    _dihedrals_values[:,3] = Dihedrals4
                    _dihedrals_values[:,4] = Dihedrals5
                    _dihedrals_values[:,5] = Dihedrals6
                    electroopticssystem.dihedrals_values = _dihedrals_values

                    _impropers_values = np.zeros((int(_impropers), 6))
                    _impropers_values[:,0] = Impropers1
                    _impropers_values[:,1] = Impropers2
                    _impropers_values[:,2] = Impropers3
                    _impropers_values[:,3] = Impropers4
                    _impropers_values[:,4] = Impropers5
                    _impropers_values[:,5] = Impropers6
                    electroopticssystem.impropers_values = _impropers_values
                if 'theta' in file:
                    column1 = []
                    column2 = []
                    electroopticsoutput = ElectroopticsOutput()
                    calculation.electrooptics_output.append(electroopticsoutput)
                    for i, line in enumerate(f):
                        parts = line.split()
                        if 'Time' in line:
                            continue
                        column1.append(float(parts[0]))
                        column2.append(float(parts[1]))
                        rows = i
                    _theta = np.zeros((rows, 2))
                    _theta[:,0] = column1
                    _theta[:,1] = column2
                    electroopticsoutput.theta = _theta
class NewParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        logger.info('NewParser.parse', parameter=configuration.parameter)

        archive.workflow2 = Workflow(name='test')
        
        mainfile = Path(mainfile)
        DetailedParser(mainfile, archive)