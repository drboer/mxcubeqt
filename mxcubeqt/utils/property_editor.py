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

import os
import weakref
import logging

from mxcubeqt.utils import icons, property_bag, colors, qt_import


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class ConfigurationTable(qt_import.QTableWidget):

    propertyChangedSignal = qt_import.pyqtSignal(str, object, object)

    def __init__(self, parent):

        qt_import.QTableWidget.__init__(self, parent)

        self.display_hwobj = False
        self.property_bag = None

        self.setObjectName("configurationTable")
        self.setFrameShape(qt_import.QFrame.StyledPanel)
        self.setFrameShadow(qt_import.QFrame.Sunken)
        self.setContentsMargins(0, 3, 0, 3)
        self.setColumnCount(4)
        self.setSelectionMode(qt_import.QTableWidget.NoSelection)

        # self.setHorizontalHeaderLabels([self.trUtf8('Property'),
        #                                self.trUtf8('Value'),
        #                                self.trUtf8(''),
        #                                self.trUtf8('Comment')])
        self.setHorizontalHeaderLabels(["Property", "Value", "", "Comment"])

        self.setSizePolicy(
            qt_import.QSizePolicy.MinimumExpanding, qt_import.QSizePolicy.Fixed
        )
        self.setHorizontalScrollBarPolicy(qt_import.Qt.ScrollBarAlwaysOff)

        self.cellChanged.connect(self.on_cell_changed)

    def clear(self):
        for i in range(self.rowCount()):
            self.removeRow(i)
        self.setRowCount(0)
        self.property_bag = None

    def set_property_bag(self, property_bag, show_hidden=False, display_hwobj=False):
        self.display_hwobj = display_hwobj
        self.clear()

        if self.property_bag is not None:
            for prop in self.property_bag:
                prop._editor = None

        self.property_bag = property_bag

        if self.property_bag is not None:
            i = 0
            for prop in self.property_bag:
                prop._editor = weakref.ref(self)
                prop_name = prop.get_name()

                if not show_hidden and prop.hidden:
                    continue

                if display_hwobj:
                    if not prop_name.startswith("hwobj_"):
                        continue
                    else:
                        prop_name = prop_name.replace("hwobj_", "")
                else:
                    if prop_name.startswith("hwobj_"):
                        continue

                self.setRowCount(i + 1)
                temp_table_item = qt_import.QTableWidgetItem(prop_name)
                temp_table_item.setFlags(qt_import.Qt.ItemIsEnabled)
                self.blockSignals(True)
                self.setItem(i, 0, temp_table_item)
                self.set_widget_from_property(i, prop)

                temp_table_item = qt_import.QTableWidgetItem(prop.comment)
                temp_table_item.setFlags(qt_import.Qt.ItemIsEnabled)
                self.setItem(i, 3, temp_table_item)

                self.blockSignals(False)

                validation_panel = ValidationTableItem(self)
                self.setCellWidget(i, 2, validation_panel)
                validation_panel.ok_button.clicked.connect(self.on_validate_click)
                validation_panel.cancel_button.clicked.connect(self.on_invalidate_click)
                validation_panel.reset_button.clicked.connect(self.on_reset_click)
                i += 1
            self.setEnabled(i > 0)
        self.resizeColumnsToContents()
        self.setFixedHeight((self.rowCount() + 1) * (self.rowHeight(0) + 2))
        # self.adjustSize()
        self.parent().adjustSize()
        # self.parent().resize(self.parent().sizeHint())

    def set_widget_from_property(self, row, prop):
        """Adds new property to the propery table

        :param row: selected row
        :type row: int
        :param prop: property
        :type prop: dict
        """
        if prop.get_type() == "boolean":
            new_property_item = qt_import.QTableWidgetItem("")
            self.setItem(row, 1, new_property_item)
            if prop.get_user_value():
                self.item(row, 1).setCheckState(qt_import.Qt.Checked)
            else:
                self.item(row, 1).setCheckState(qt_import.Qt.Unchecked)
        elif prop.get_type() == "combo":
            choices_list = []
            choices = prop.get_choices()
            for choice in choices:
                choices_list.append(choice)
            new_property_item = ComboBoxTableItem(self, row, 1, choices_list)
            new_property_item.setCurrentIndex(
                new_property_item.findText(prop.get_user_value())
            )
            self.setCellWidget(row, 1, new_property_item)
        elif prop.get_type() == "file":
            new_property_item = FileTableItem(
                self, row, 1, prop.get_user_value(), prop.getFilter()
            )
            self.setCellWidget(row, 1, new_property_item)
        elif prop.get_type() == "color":
            new_property_item = ColorTableItem(self, row, 1, prop.get_user_value())
            self.setCellWidget(row, 1, new_property_item)
        else:
            if prop.get_user_value() is None:
                temp_table_item = qt_import.QTableWidgetItem("")
            else:
                temp_table_item = qt_import.QTableWidgetItem(str(prop.get_user_value()))
            self.setItem(row, 1, temp_table_item)
        self.resizeColumnsToContents()
        # self.parent().adjustSize()

    def on_cell_changed(self, row, col):
        """Assignes new value to the property, clicked on the the
           property table
        """
        col += 1
        prop_name = str(self.item(row, 0).text())
        if self.display_hwobj:
            prop_name = "hwobj_" + prop_name

        item_property = self.property_bag.get_property(prop_name)
        old_value = item_property.get_user_value()

        if item_property.get_type() == "boolean":
            item_property.set_value(self.item(row, 1).checkState())
        elif item_property.get_type() == "combo":
            item_property.set_value(self.cellWidget(row, 1).currentText())
        elif item_property.get_type() == "file":
            item_property.set_value(self.cellWidget(row, 1).get_filename())
        elif item_property.get_type() == "color":
            item_property.set_value(self.cellWidget(row, 1).color)
        else:
            try:
                item_property.set_value(str(self.item(row, 1).text()))
            except BaseException:
                logging.getLogger().error(
                    "Cannot assign value %s to property %s"
                    % (str(self.item(row, 1).text()), prop_name)
                )

            if item_property.get_user_value() is None:
                self.item(row, 1).setText("")
            else:
                self.item(row, 1).setText(str(item_property.get_user_value()))

        if not old_value == item_property.get_user_value():
            self.propertyChangedSignal.emit(
                prop_name, old_value, item_property.get_user_value()
            )

    def on_validate_click(self):
        # current row, col 1, accept = 1, replace = 0
        self.endEdit(self.currentRow(), 1, 1, 0)
        self.activateNextCell()

    def on_invalidate_click(self):
        # current row, col 1, accept = 0, replace = 0
        self.endEdit(self.currentRow(), 1, 0, 0)

    def on_reset_click(self):
        self.endEdit(self.currentRow(), 1, 0, 0)
        prop_name = str(self.item(self.currentRow(), 0).text())
        if self.display_hwobj:
            prop_name = "hwobj_" + prop_name

        prop = self.property_bag.get_property(prop_name)

        default_value = prop.getDefaultValue()
        if not default_value is None:
            prop.set_value(default_value)

        self.set_widget_from_property(self.currentRow(), prop)

    def beginEdit(self, row, col, replace):
        if col == 1 and row >= 0:
            self.item(row, 2).setEnabled(1)

        return qt_import.QTableWidget.beginEdit(self, row, col, replace)

    def endEdit(self, row, col, accept, replace):
        if col == 1 and row >= 0:
            self.item(row, 2).setEnabled(0)

            if accept:
                prop_name = str(self.item(row, 0).text())
                if self.display_hwobj:
                    prop_name = "hwobj_" + prop_name
                prop = self.property_bag.get_property(prop_name)

                old_value = prop.get_user_value()

                if prop.get_type() == "boolean":
                    prop.set_value(self.item(row, 1).isChecked())
                elif prop.get_type() == "combo":
                    prop.set_value(self.item(row, 1).currentText())
                else:
                    try:
                        prop.set_value(str(self.text(row, 1)))
                    except BaseException:
                        logging.getLogger().error(
                            "Cannot assign value to property %s" % prop_name
                        )

                    if prop.get_user_value() is None:
                        self.setText(row, 1, "")
                    else:
                        self.setText(row, 1, str(prop.get_user_value()))

                if not old_value == prop.get_user_value():
                    self.propertyChangedSignal.emit(
                        prop_name, old_value, prop.get_user_value()
                    )
                    # self.emit(QtCore.SIGNAL('propertyChanged'),
                    # (prop_name, old_value, prop.get_user_value(), ))

        return qt_import.QTableWidget.endEdit(self, row, col, accept, replace)


class ValidationTableItem(qt_import.QWidget):
    def __init__(self, parent=None):

        qt_import.QWidget.__init__(self, parent)

        self.ok_button = qt_import.QToolButton(parent)
        self.ok_button.setAutoRaise(True)
        self.ok_button.setIcon(icons.load_icon("button_ok_small"))
        self.cancel_button = qt_import.QToolButton(parent)
        self.cancel_button.setAutoRaise(True)
        self.cancel_button.setIcon(icons.load_icon("button_cancel_small"))
        self.reset_button = qt_import.QToolButton(parent)
        self.reset_button.setIcon(icons.load_icon("button_default_small"))
        self.reset_button.setAutoRaise(True)
        self.setEnabled(False)

        _main_layout = qt_import.QHBoxLayout(self)
        _main_layout.addWidget(self.ok_button)
        _main_layout.addWidget(self.cancel_button)
        _main_layout.addWidget(self.reset_button)
        _main_layout.setSpacing(0)
        _main_layout.setContentsMargins(0, 0, 0, 0)

    def setEnabled(self, enabled):
        if enabled:
            self.reset_button.setEnabled(True)
            self.ok_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
        else:
            self.reset_button.setEnabled(False)
            self.ok_button.setEnabled(False)
            self.cancel_button.setEnabled(False)


class ComboBoxTableItem(qt_import.QComboBox):
    def __init__(self, parent, row, col, items_list=None):
        qt_import.QComboBox.__init__(self)
        if items_list is not None:
            self.addItems(items_list)
        self.col = col
        self.row = row
        self.parent = parent
        self.currentIndexChanged.connect(self.current_index_changed)

    def current_index_changed(self, index):
        self.parent.cellChanged.emit(self.row, self.col)


class FileTableItem(qt_import.QWidget):
    def __init__(self, parent, row, col, filename, file_filter):
        qt_import.QWidget.__init__(self)

        self.file_filter = file_filter
        self.parent = parent
        self.col = col
        self.row = row

        self.cmdBrowse = qt_import.QPushButton("Browse", self.parent.viewport())

        main_layout = qt_import.QHBoxLayout()
        main_layout.addWidget(self.cmdBrowse)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.cmdBrowse.clicked.connect(self.browse_clicked)
        self.set_filename(filename)

    def set_filename(self, filename):
        self.filename = str(filename)

        if self.cmdBrowse is not None:
            self.cmdBrowse.setToolTip(self.filename)

        self.parent.cellChanged.emit(self.row, self.col)

    def get_filename(self):
        return self.filename

    def browse_clicked(self):
        new_filename = qt_import.QFileDialog.getOpenFileName(
            self,
            os.path.dirname(self.filename) or os.getcwd(),
            self.file_filter,
            "",
            "Select a file",
        )

        if len(new_filename) > 0:
            self.set_filename(new_filename)


class ColorTableItem(qt_import.QWidget):

    # cellChangedSignal = QtCore.pyqtSignal(int, int)

    def __init__(self, parent, row, col, color):
        qt_import.QWidget.__init__(self, parent)

        self.col = col
        self.row = row
        self.parent = parent

        self.change_color_button = qt_import.QPushButton("Color...", parent)
        self.reset_color_button = qt_import.QPushButton("reset", parent)

        main_layout = qt_import.QHBoxLayout(self)
        main_layout.addWidget(self.change_color_button)
        main_layout.addWidget(self.reset_color_button)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.change_color_button.clicked.connect(self.change_color_clicked)
        self.reset_color_button.clicked.connect(self.reset_color_clicked)
        self.set_color(color)

        # main_layout = QtGui.QVBoxLayout()
        # main_layout.addWidget(hbox)
        # self.setLayout(main_layout)

    def set_color(self, color):
        if not color:
            self.qtcolor = None
            self.color = None
            colors.set_widget_color(
                self.change_color_button,
                colors.BUTTON_ORIGINAL,
                qt_import.QPalette.Button,
            )
        else:
            try:
                rgb = color.rgb()
            except BaseException:
                try:
                    self.qtcolor = qt_import.QColor(color)
                except BaseException:
                    self.qtcolor = qt_import.QColor(qt_import.Qt.green)
                    self.color = self.qtcolor.rgb()
                else:
                    self.color = self.qtcolor.rgb()
            else:
                self.qtcolor = color
                self.color = rgb

            colors.set_widget_color(
                self.change_color_button, self.qtcolor, qt_import.QPalette.Button
            )
        self.parent.cellChanged.emit(self.row, self.col)

    def change_color_clicked(self):
        """Opens color dialog to choose color"""

        new_color = qt_import.QColorDialog.getColor(
            self.qtcolor or qt_import.QColor("white"), None, "Select a color"
        )
        if new_color.isValid():
            self.set_color(new_color)

    def reset_color_clicked(self):
        """Resets color"""

        self.set_color(None)
