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

from mxcubeqt.utils import icons, qt_import

#if hasattr(qt_import, "QWebView"):
#    QWEBVIEW_AVAILABLE = True
#else:
QWEBVIEW_AVAILABLE = False


class WebViewWidget(qt_import.QWidget):
    def __init__(self, parent):

        qt_import.QWidget.__init__(self, parent)

        self.home_url = None

        self.navigation_bar = qt_import.QWidget(self)
        self.url_ledit = qt_import.QLineEdit(self.navigation_bar)
        self.url_ledit.setReadOnly(True)
        self.home_button = qt_import.QPushButton(self.navigation_bar)
        self.back_button = qt_import.QPushButton(self.navigation_bar)
        self.forward_button = qt_import.QPushButton(self.navigation_bar)

        self.home_button.setIcon(icons.load_icon("Home2"))
        self.back_button.setIcon(icons.load_icon("Left2"))
        self.forward_button.setIcon(icons.load_icon("Right2"))

        #if QWEBVIEW_AVAILABLE:
        #    self.web_page_viewer = qt_import.QWebView(self)
        #    self.web_page_viewer.settings().setObjectCacheCapacities(0, 0, 0)
        #else:
        self.web_page_viewer = qt_import.QTextBrowser(self)

        _navigation_bar_hlayout = qt_import.QHBoxLayout(self.navigation_bar)
        _navigation_bar_hlayout.addWidget(self.home_button)
        _navigation_bar_hlayout.addWidget(self.back_button)
        _navigation_bar_hlayout.addWidget(self.forward_button)
        _navigation_bar_hlayout.addWidget(self.url_ledit)
        _navigation_bar_hlayout.setSpacing(2)
        _navigation_bar_hlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.navigation_bar)
        _main_vlayout.addWidget(self.web_page_viewer)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        self.web_page_viewer.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )

        self.home_button.clicked.connect(self.go_to_home_page)
        self.back_button.clicked.connect(self.go_back)
        self.forward_button.clicked.connect(self.go_forward)

    def set_url(self, url):
        #if QWEBVIEW_AVAILABLE:
        #    self.home_url = url
        #    self.navigation_bar.setEnabled(True)
        #    self.go_to_home_page()
        #else:
        self.web_page_viewer.setSource(qt_import.QUrl(url))

    def set_static_page(self, html_text):
        if QWEBVIEW_AVAILABLE:
            self.web_page_viewer.setHtml(html_text)
            self.navigation_bar.setEnabled(False)

    def go_to_home_page(self):
        self.url_ledit.setText(self.home_url)
        self.web_page_viewer.load(qt_import.QUrl(self.home_url))
        self.web_page_viewer.show()

    def go_back(self):
        if QWEBVIEW_AVAILABLE:
            self.web_page_viewer.back()

    def go_forward(self):
        if QWEBVIEW_AVAILABLE:
            self.web_page_viewer.forward()
