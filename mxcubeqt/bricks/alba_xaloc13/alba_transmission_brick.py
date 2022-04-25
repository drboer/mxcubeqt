#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from mxcubeqt.bricks.transmission_brick import TransmissionBrick

from mxcubecore import HardwareRepository as HWR

__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "General"

class AlbaTransmissionBrick(TransmissionBrick):

    def __init__(self, *args):
        TransmissionBrick.__init__(self, *args)
        if HWR.beamline.transmission is not None:
            HWR.beamline.transmission.update_values()
    
