"""
Convenience functions for the construction of spatial weights based on
contiguity and distance criteria.
"""

__author__ = "Sergio J. Rey <srey@asu.edu> "

from .Contiguity import buildContiguity, Queen, Rook
from .Distance import knnW, Kernel, DistanceBand
from .util import get_ids, get_points_array_from_shapefile, min_threshold_distance
from ..io.FileIO import FileIO as ps_open
from .. import cg
from ..cg.voronoi import voronoi_frames
from .weights import WSP
import numpy as np

__all__ = ['queen_from_shapefile', 'rook_from_shapefile', 'knnW_from_array',
           'knnW_from_shapefile', 'threshold_binaryW_from_array',
           'threshold_binaryW_from_shapefile', 'threshold_continuousW_from_array',
           'threshold_continuousW_from_shapefile', 'kernelW', 'kernelW_from_shapefile',
           'adaptive_kernelW', 'adaptive_kernelW_from_shapefile',
           'min_threshold_dist_from_shapefile', 'build_lattice_shapefile', 'voronoiW']

def spw_from_gal(galfile):
    """
    Sparse scipy matrix for w from a gal file.

    Parameters
    ----------

    galfile  : string
               name of gal file including suffix

    Returns
    -------

    spw      : sparse_matrix
               scipy sparse matrix in CSR format

    ids      : array
               identifiers for rows/cols of spw

    Examples
    --------
    >>> import libpysal
    >>> spw = libpysal.weights.user.spw_from_gal(libpysal.examples.get_path("sids2.gal"))
    >>> spw.sparse.nnz
    462

    """

    return ps_open(galfile, 'r').read(sparse=True)

def min_threshold_dist_from_shapefile(shapefile, radius=None, p=2):
    """
    Kernel weights with adaptive bandwidths.

    Parameters
    ----------

    shapefile  : string
                 shapefile name with shp suffix.
    radius     : float
                 If supplied arc_distances will be calculated
                 based on the given radius. p will be ignored.
    p          : float
                 Minkowski p-norm distance metric parameter:
                 1<=p<=infinity
                 2: Euclidean distance
                 1: Manhattan distance

    Returns
    -------
    d          : float
                 Maximum nearest neighbor distance between the n
                 observations.

    Examples
    --------
    >>> import libpysal.api as ps
    >>> import libpysal
    >>> md = ps.min_threshold_dist_from_shapefile(libpysal.examples.get_path("columbus.shp"))
    >>> md
    0.6188641580768541
    >>> ps.min_threshold_dist_from_shapefile(libpysal.examples.get_path("stl_hom.shp"), libpysal.cg.sphere.RADIUS_EARTH_MILES)
    31.846942936393717

    Notes
    -----
    Supports polygon or point shapefiles. For polygon shapefiles, distance is
    based on polygon centroids. Distances are defined using coordinates in
    shapefile which are assumed to be projected and not geographical
    coordinates.

    """
    points = get_points_array_from_shapefile(shapefile)
    if radius is not None:
        kdt = cg.kdtree.Arc_KDTree(points, radius=radius)
        nn = kdt.query(kdt.data, k=2)
        nnd = nn[0].max(axis=0)[1]
        return nnd
    return min_threshold_distance(points, p)


def build_lattice_shapefile(nrows, ncols, outFileName):
    """
    Build a lattice shapefile with nrows rows and ncols cols.

    Parameters
    ----------

    nrows       : int
                  Number of rows
    ncols       : int
                  Number of cols
    outFileName : str
                  shapefile name with shp suffix

    Returns
    -------
    None

    """
    if not outFileName.endswith('.shp'):
        raise ValueError("outFileName must end with .shp")
    o = ps_open(outFileName, 'w')
    dbf_name = outFileName.split(".")[0] + ".dbf"
    d = ps_open(dbf_name, 'w')
    d.header = [ 'ID' ]
    d.field_spec = [ ('N', 8, 0) ]
    c = 0
    for i in range(nrows):
        for j in range(ncols):
            ll = i, j
            ul = i, j + 1
            ur = i + 1, j + 1
            lr = i + 1, j
            o.write(cg.Polygon([ll, ul, ur, lr, ll]))
            d.write([c])
            c += 1
    d.close()
    o.close()

def _test():
    import doctest
    # the following line could be used to define an alternative to the '<BLANKLINE>' flag
    #doctest.BLANKLINE_MARKER = 'something better than <BLANKLINE>'
    start_suppress = np.get_printoptions()['suppress']
    np.set_printoptions(suppress=True)
    doctest.testmod()
    np.set_printoptions(suppress=start_suppress)

if __name__ == '__main__':
    _test()


