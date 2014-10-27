
import subprocess

from seisflows.tools import unix
from seisflows.tools.configtools import loadclass, ConfigObj, ParameterObj

OBJ = ConfigObj('SeisflowsObjects')
PAR = ParameterObj('SeisflowsParameters')
PATH = ParameterObj('SeisflowsPaths')


class specfem3d_legacy(loadclass('solver','specfem3d')):

    def check(self):
        """ Checks parameters, paths, and dependencies
        """
        super(specfem3d_legacy,self).check()

        if 'system' not in OBJ:
            raise Excpetion

        global system
        import system


    def mpirun(self,script,outfile='/dev/null'):
        """ Wrapper for mpirun
        """
        unix.cd('bin')

        with open(outfile) as f:
            subprocess.call(
                  system.mpiargs()
                  + unix.basename(script),
                  shell=True,
                  stdout=f)
        unix.cd('..')
