from __future__ import division, print_function, absolute_import

from subprocess import call, PIPE, Popen
import sys
import re

from numpy.testing import dec, assert_
from numpy.compat import asbytes

from scipy.linalg import _flapack as flapack

# XXX: this is copied from numpy trunk. Can be removed when we will depend on
# numpy 1.3


class FindDependenciesLdd:
    def __init__(self):
        self.cmd = ['ldd']

        try:
            st = call(self.cmd, stdout=PIPE, stderr=PIPE)
        except OSError:
            raise RuntimeError("command %s cannot be run" % self.cmd)

    def get_dependencies(self, file):
        p = Popen(self.cmd + [file], stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if not (p.returncode == 0):
            raise RuntimeError("Failed to check dependencies for %s" % file)

        return stdout

    def grep_dependencies(self, file, deps):
        stdout = self.get_dependencies(file)

        rdeps = dict([(asbytes(dep), re.compile(asbytes(dep))) for dep in deps])
        founds = []
        for l in stdout.splitlines():
            for k, v in rdeps.items():
                if v.search(l):
                    founds.append(k)

        return founds


class TestF77Mismatch(object):
    @dec.skipif(not(sys.platform[:5] == 'linux'),
                "Skipping fortran compiler mismatch on non Linux platform")
    def test_lapack(self):
        f = FindDependenciesLdd()
        deps = f.grep_dependencies(flapack.__file__,
                                   ['libg2c', 'libgfortran'])
        assert_(not (len(deps) > 1),
"""Both g77 and gfortran runtimes linked in scipy.linalg.flapack ! This is
likely to cause random crashes and wrong results. See numpy INSTALL.rst.txt for
more information.""")
