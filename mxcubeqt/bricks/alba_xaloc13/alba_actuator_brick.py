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

import logging

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.base_components import BaseWidget

from mxcubecore import HardwareRepository as HWR

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__version__ = "3"
__category__ = "ALBA"


#
# These state list is as in ALBAEpsActuator.py
#
STATE_IN, STATE_OUT, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = (
    0,
    1,
    9,
    11,
    13,
    23,
)

STATES = {
    STATE_IN: colors.LIGHT_GRAY,
    STATE_OUT: colors.LIGHT_GREEN,
    STATE_MOVING: colors.LIGHT_YELLOW,
    STATE_FAULT: colors.LIGHT_RED,
    STATE_ALARM: colors.LIGHT_RED,
    STATE_UNKNOWN: colors.LIGHT_GRAY,
}


class AlbaActuatorBrick(BaseWidget):
    def __init__(self, *args):
        """
        Descript. :
        """
        BaseWidget.__init__(self, *args)
        self.logger = logging.getLogger("GUI Alba Actuator")
        self.logger.info("__init__()")

        # Hardware objects ----------------------------------------------------
        self.actuator_hwo = None
        self.state = None

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("in_cmd_name", "string", "")
        self.add_property("out_cmd_name", "string", "")

        # Graphic elements ----------------------------------------------------
        self.widget = qt_import.load_ui_file("alba_actuator.ui")

        qt_import.QHBoxLayout(self)

        self.layout().addWidget(self.widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.layout().setContentsMargins(0, 0, 0, 0)

        self.widget.cmdInButton.clicked.connect(self.do_cmd_in)
        self.widget.cmdOutButton.clicked.connect(self.do_cmd_out)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.MinimumExpanding
        )

        # Other ---------------------------------------------------------------
        self.setToolTip(
            "To control the photon shutter "
        )

        #self.widget.stateLabel.hide()

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.actuator_hwo is not None:
                self.disconnect(
                    self.actuator_hwo,
                    qt_import.SIGNAL("stateChanged"),
                    self.state_changed,
                )

            self.actuator_hwo = self.get_hardware_object(new_value)
            self.update()
            if self.actuator_hwo is not None:
                self.setEnabled(True)
                self.connect(
                    self.actuator_hwo,
                    qt_import.SIGNAL("stateChanged"),
                    self.state_changed,
                )
                self.actuator_hwo.force_emit_signals()
                logging.getLogger("HWR").info(
                    "User Name is: %s" % self.actuator_hwo.get_user_name()
                )
                self.widget.actuatorBox.setTitle(self.actuator_hwo.get_user_name())
            else:
                self.setEnabled(False)
        elif property_name == "in_cmd_name":
            self.widget.cmdInButton.setText(new_value)
        elif property_name == "out_cmd_name":
            self.widget.cmdOutButton.setText(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def update(self, state=None):
        if self.actuator_hwo is not None:
            if state == None:
                state = self.actuator_hwo.get_state()
                self.logger.info("State = %s" % state )
                status = self.actuator_hwo.get_status()
                self.logger.info("Status = %s" % status )
                self.widget.stateLabel.setText(status)
                colors.set_widget_color(self.widget.stateLabel, STATES[state])

                #self.widget.cmdInButton.setEnabled(True)
                #self.widget.cmdOutButton.setEnabled(True)
                #self.widget.cmdInButton.setChecked(True)
                #self.widget.cmdOutButton.setChecked(True)

                self.widget.cmdInButton.setEnabled(False)
                self.widget.cmdOutButton.setEnabled(False)
                self.widget.cmdInButton.setChecked(False)
                self.widget.cmdOutButton.setChecked(False)

                if state == STATE_IN:
                    self.widget.cmdOutButton.setEnabled(True)
                    self.widget.cmdInButton.setChecked(True)
                elif state == STATE_OUT:
                    self.widget.cmdInButton.setEnabled(True)
                    self.widget.cmdOutButton.setChecked(True)

                self.state = state

    def state_changed(self, state):
        if state != self.state:
            self.update()

    def do_cmd_in(self):
        if self.actuator_hwo.username == 'Photon Shutter': # for photon shuter, close calls do_cmd_out
            logging.getLogger("HWR").info("Sending supervisor to transfer phase")
            HWR.beamline.supervisor.set_phase("Transfer")
        if self.actuator_hwo is not None:
            self.actuator_hwo.cmd_in()

    def do_cmd_out(self):
        if self.actuator_hwo is not None:
            self.actuator_hwo.cmd_out()
