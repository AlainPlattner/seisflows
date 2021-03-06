
from os.path import abspath, join
from shutil import copyfile

import numpy as np


def loadbypar(path, parameters, iproc, prefix='', suffix=''):
    """ Reads SPECFEM database files for given processor rank, callable by a
        single mpi process
    """
    keys = []
    vals = []
    for key in sorted(parameters):
        val = loadbin(path, iproc, prefix+key+suffix)
        keys += [key]
        vals += [val]
    return keys, vals


def loadbyproc(path, parameter, nproc):
    """ Reads SPECFEM database files for given material parameter
    """
    vals = []
    for iproc in range(nproc):
        vals += [loadbin(path, iproc, parameter)]
    return vals


def loadbin(path, proc, par):
    """ Reads a single SPECFEM database file
    """
    filename = 'proc%06d_%s.bin' % (proc, par)
    return read_fortran(join(path, filename))


def savebin(v, path, proc, par):
    """ Writes a single SPECFEM database file
    """
    filename = 'proc%06d_%s.bin' % (proc, par)
    write_fortran(v, join(path, filename))


def copybin(src, dst, proc, par):
    """ Copies SPECFEM database file
    """
    filename = 'proc%06d_%s.bin' % (proc, par)
    copyfile(join(src, filename), join(dst, filename))


def splitvec(v,  nproc, ngll, idim):
    parts = []
    for iproc in range(nproc):
        imin = nproc*ngll*idim + ngll*iproc 
        imax = nproc*ngll*idim + ngll*(iproc+1)
        parts += [v[imin:imax]]
    return parts


def splitvec(v,  nproc, ngll, idim):
    parts = []
    for iproc in range(nproc):
        imin = sum(ngll)*idim + sum(ngll[:iproc])
        imax = sum(ngll)*idim + sum(ngll[:iproc+1])
        parts += [v[imin:imax]]
    return parts


def read_fortran(filename):
    """ Reads Fortran style binary data and returns a numpy array.
    """
    with open(filename, 'rb') as file:
        # read size of record
        file.seek(0)
        n = np.fromfile(file, dtype='int32', count=1)[0]

        # read contents of record
        file.seek(4)
        v = np.fromfile(file, dtype='float32')

    return v[:-1]


def write_fortran(v, filename):
    """ Writes Fortran style binary data. Data are written as single precision
        floating point numbers.
    """
    n = np.array([4*len(v)], dtype='int32')
    v = np.array(v, dtype='float32')

    with open(filename, 'wb') as file:
        n.tofile(file)
        v.tofile(file)
        n.tofile(file)


def Model(keys):
    return dict((key, []) for key in keys)


class Minmax(object):
    def __init__(self, keys):
        self.keys = keys
        self.minvals = dict((key, +np.Inf) for key in keys)
        self.maxvals = dict((key, -np.Inf) for key in keys)

    def items(self):
        return ((key, self.minvals[key], self.maxvals[key]) for key in self.keys)

    def update(self, keys, vals):
        for key,val in zip(keys, vals):
            minval = val.min()
            maxval = val.max()
            minval_all = self.minvals[key]
            maxval_all = self.maxvals[key]
            if minval < minval_all: self.minvals.update({key: minval})
            if maxval > maxval_all: self.maxvals.update({key: maxval})

    def write(self, path, logpath):
        if not logpath:
            return
        filename = join(logpath, 'output.minmax')
        with open(filename, 'a') as f:
            f.write(abspath(path)+'\n')
            for key,minval,maxval in self.items():
                f.write('%-15s %10.3e %10.3e\n' % (key, minval, maxval))
            f.write('\n')


