# -*- coding: utf8 -*-
from __future__ import division
"""
LogGabor

See http://pythonhosted.org/LogGabor

"""
__author__ = "(c) Laurent Perrinet INT - CNRS"
import numpy as np

from SLIP import Image

class LogGabor(Image):
    """
    Defines a LogGabor framework by defining a ``loggabor`` function which return the envelope of a log-Gabor filter.

    Its envelope is equivalent to a log-normal probability distribution on the frequency axis, and von-mises on the radial axis.


    """
    def __init__(self, pe):
        Image.__init__(self, pe)
        self.init_logging(name='LogGabor')

    ## LOW LEVEL OPERATIONS
    def band(self, sf_0, B_sf):
        # selecting a donut (the ring around a prefered frequency)
        if sf_0 == 0.: return 1.
        # see http://en.wikipedia.org/wiki/Log-normal_distribution
        env = 1./self.f*np.exp(-.5*(np.log(self.f/sf_0)**2)/B_sf**2)
        return env

    def orientation(self, theta, B_theta):
        """
    Returns the orientation envelope:
    We use a von-Mises distribution on the orientation:
    - mean orientation is ``theta`` (in radians),
    - ``B_theta`` is the bandwidth (in radians). It is equal to the standard deviation of the Gaussian
    envelope which approximate the distribution for low bandwidths. The Half-Width at Half Height is
    given by approximately np.sqrt(2*B_theta_**2*np.log(2)).

        # selecting one direction,  theta is the mean direction, B_theta the spread
        # we use a von-mises distribution on the orientation
        # see http://en.wikipedia.org/wiki/Von_Mises_distribution
        """
        if B_theta is np.inf: # for large bandwidth, returns a strictly flat envelope
            enveloppe_orientation = 1.
        else: # non pathological case
            cos_angle = np.cos(self.f_theta-theta)
            enveloppe_orientation = np.exp(cos_angle/B_theta**2)
#        As shown in:
#        http://www.csse.uwa.edu.au/~pk/research/matlabfns/PhaseCongruency/Docs/convexpl.html
#        this single bump allows (without the symmetric) to code both symmetric and anti-symmetric parts
        return enveloppe_orientation

    ## MID LEVEL OPERATIONS
    def loggabor(self, u, v, sf_0, B_sf, theta, B_theta, preprocess=True):
        """

        Note that the convention for coordinates follows that of matrices: the origin is at the top left of the image, and coordinates are first the rows (vertical axis, going down) then the columns (horizontal axis, going right).

        """

        env = self.band(sf_0, B_sf) * \
              self.orientation(theta, B_theta) * \
              self.trans(u*1., v*1.)
        if preprocess : env *= self.f_mask
        # normalizing energy:
        env /= np.sqrt((np.abs(env)**2).mean())
        # in the case a a single bump (see ``orientation``), we should compensate the fact that the distribution gets complex:
        env *= np.sqrt(2.)
        return env

    def show_loggabor(self, u, v, sf_0, B_sf, theta, B_theta, title='', phase=0.):
        FT_lg = self.loggabor(u, v, sf_0, B_sf, theta, B_theta)
        fig, a1, a2 = self.show_FT(FT_lg * np.exp(-1j*phase))
        return fig, a1, a2

def _test():
    import doctest
    doctest.testmod()
#####################################
#
if __name__ == '__main__':
    _test()

    #### Main
    """
    Some examples of use for the class

    """
    lg = LogGabor('default_param.py')
    from SLIP import imread
    image = imread('database/lena512.png')[:,:,0]
    lg.set_size(image)
