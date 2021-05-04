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

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import colors, icons, qt_import


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Motor"


class MotorPredefPosBrick(BaseWidget):

    STATE_COLORS = (
        colors.LIGHT_YELLOW,  # INITIALIZING
        colors.LIGHT_GREEN,  # ON
        colors.DARK_GRAY,  # OFF
        colors.LIGHT_GREEN,  # READY
        colors.LIGHT_YELLOW,  # BUSY
        colors.LIGHT_YELLOW,  # MOVING
        colors.LIGHT_GREEN,  # STANDBY
        colors.DARK_GRAY,  # DISABLED
        colors.DARK_GRAY,  # UNKNOWN
        colors.LIGHT_RED,  # ALARM
        colors.LIGHT_RED,  # FAULT
        colors.LIGHT_RED,  # INVALID
        colors.DARK_GRAY,  # OFFLINE
        colors.LIGHT_RED,  # LOWLIMIT
        colors.LIGHT_RED,  # HIGHLIMIT
        colors.DARK_GRAY,
    )  # NOTINITIALIZED

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.motor_hwobj = None

        # Internal values -----------------------------------------------------

        self.position_values = None
        self.position_names = None
        # Properties ----------------------------------------------------------
        self.add_property("label", "string", "")
        self.add_property("mnemonic", "string", "")
        self.add_property("icons", "string", "")
        self.add_property("showMoveButtons", "boolean", True)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("setEnabled", ())

        # Graphic elements ----------------------------------------------------
        _main_gbox = qt_import.QGroupBox(self)
        self.label = qt_import.QLabel("motor:", _main_gbox)
        self.positions_combo = qt_import.QComboBox(self)
        self.previous_position_button = qt_import.QPushButton(_main_gbox)
        self.next_position_button = qt_import.QPushButton(_main_gbox)

        # Layout --------------------------------------------------------------
        _main_gbox_hlayout = qt_import.QHBoxLayout(_main_gbox)
        _main_gbox_hlayout.addWidget(self.label)
        _main_gbox_hlayout.addWidget(self.positions_combo)
        _main_gbox_hlayout.addWidget(self.previous_position_button)
        _main_gbox_hlayout.addWidget(self.next_position_button)
        _main_gbox_hlayout.setSpacing(2)
        _main_gbox_hlayout.setContentsMargins(2, 2, 2, 2)

        _main_hlayout = qt_import.QHBoxLayout(self)
        _main_hlayout.addWidget(_main_gbox)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        # Size Policy ---------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.positions_combo.activated.connect(self.position_selected)
        self.previous_position_button.clicked.connect(self.select_previous_position)
        self.next_position_button.clicked.connect(self.select_next_position)

        # Other ---------------------------------------------------------------
        self.positions_combo.setFixedHeight(27)
        self.positions_combo.setToolTip("Moves the motor to a predefined position")
        self.previous_position_button.setIcon(icons.load_icon("Minus2"))
        self.previous_position_button.setFixedSize(27, 27)
        self.next_position_button.setIcon(icons.load_icon("Plus2"))
        self.next_position_button.setFixedSize(27, 27)

    def setToolTip(self, name=None, state=None):
        states = ("NOTREADY", "UNUSABLE", "READY", "MOVESTARTED", "MOVING", "ONLIMIT")
        if name is None:
            name = self["mnemonic"]
        if self.motor_hwobj is None:
            tip = "Status: unknown motor " + name
        else:
            if state is None:
                state = self.motor_hwobj.get_state()
            try:
                state_str = states[state]
            except IndexError:
                state_str = "UNKNOWN"
            tip = "State:" + state_str

        self.label.setToolTip(tip)

    def motor_state_changed(self, state):
        self.positions_combo.setEnabled(self.motor_hwobj.is_ready())
        if self.motor_hwobj.is_ready:
            colors.set_widget_color(
                    self.positions_combo,
                    colors.LIGHT_GREEN,
                    qt_import.QPalette.Button,
                    )
        else:
            colors.set_widget_color(
                    self.positions_combo,
                    colors.LIGHT_GRAY,
                    qt_import.QPalette.Button,
                    )
        self.predefined_position_changed(self.motor_hwobj.get_value(), offset=0)
        #self.setToolTip(state=state)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "label":
            if new_value == "" and self.motor_hwobj is not None:
                self.label.setText("<i>" + self.motor_hwobj.username + ":</i>")
            else:
                self.label.setText(new_value)
        elif property_name == "mnemonic":
            if self.motor_hwobj is not None:
                self.disconnect(
                    self.motor_hwobj, "stateChanged", self.motor_state_changed
                )
                self.disconnect(
                    self.motor_hwobj, "newPredefinedPositions", self.fill_positions
                )
                self.disconnect(
                    self.motor_hwobj,
                    "predefinedPositionChanged",
                    self.predefined_position_changed,
                )

            self.motor_hwobj = self.get_hardware_object(new_value)

            if self.motor_hwobj is not None:
                self.connect(
                    self.motor_hwobj, "newPredefinedPositions", self.fill_positions
                )
                self.connect(self.motor_hwobj, "stateChanged", self.motor_state_changed)
                self.connect(
                    self.motor_hwobj,
                    "predefinedPositionChanged",
                    self.predefined_position_changed,
                )
                self.fill_positions()
                if self.motor_hwobj.is_ready():
                    self.predefined_position_changed(
                        self.motor_hwobj.get_value(), 0
                    )
                if self["label"] == "":
                    lbl = self.motor_hwobj.user_name
                    self.label.setText("<i>" + lbl + ":</i>")
                colors.set_widget_color(
                    self.positions_combo,
                    MotorPredefPosBrick.STATE_COLORS[0],
                    qt_import.QPalette.Button,
                )
                self.motor_state_changed(self.motor_hwobj.get_state())
        elif property_name == "showMoveButtons":
            if new_value:
                self.previous_position_button.show()
                self.next_position_button.show()
            else:
                self.previous_position_button.hide()
                self.next_position_button.hide()
        elif property_name == "icons":
            icons_list = new_value.split()
            try:
                self.previous_position_button.setIcon(icons.load_icon(icons_list[0]))
                self.next_position_button.setIcon(icons.load_icon(icons_list[1]))
            except BaseException:
                pass
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def fill_positions(self, positions=None):
        self.positions_combo.clear()
        if self.motor_hwobj is not None:
            if positions is None:
                position_values = [e.value for e in self.motor_hwobj.VALUES]
                position_names = [e.name for e in self.motor_hwobj.VALUES]
        for p in position_values:
            if p != 'UNKNOWN':
                self.positions_combo.addItem(str(p))

        self.position_values = position_values
        self.position_names = position_names
        if self.motor_hwobj is not None:
            if self.motor_hwobj.is_ready():
                self.predefined_position_changed(
                    self.motor_hwobj.get_value(), 0
                )

    def position_selected(self, index):
        if index >= 0:
            self.motor_hwobj.set_value(self.motor_hwobj.VALUES[self.position_names[index]])
        self.positions_combo.setCurrentIndex(-1)
        self.next_position_button.setEnabled(index < (len(self.position_values) - 1))
        self.previous_position_button.setEnabled(index >= 0)

    def predefined_position_changed(self, position_name, offset=None):
        if self.position_values:
            for index, item in enumerate(self.position_values):
                if position_name == item:
                    self.positions_combo.setCurrentIndex(index)

    def select_previous_position(self):
        self.position_selected(self.positions_combo.currentIndex() - 1)

    def select_next_position(self):
        self.position_selected(self.positions_combo.currentIndex() + 1)
