import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QWidget, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from linear_equations_solver import LinearEquationSolver as LES
from linear_equations_solver import ColumnSpaceError

width = 700
height = 500

RESIZE_MARGIN = 8

class Header(QFrame):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.window().move(
                self.window().pos() + event.globalPos() - self._drag_pos
            )
            self._drag_pos = event.globalPos()
            event.accept()

class HintLineEdit(QLineEdit):
    def __init__(self, hint, parent=None):
        super().__init__(parent)

        self.setAlignment(Qt.AlignCenter)

        # DO NOT change QLineEdit style
        self._hint_label = QLabel(hint, self)
        self._hint_label.setStyleSheet("color: #888888;"
                                       "border: none;"
                                       "background: transparent;")
        self._hint_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.textChanged.connect(self._update_hint)
        self._update_hint()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # ---- PERFECT CENTERING ----
        hint_width = self._hint_label.sizeHint().width()
        hint_height = self._hint_label.sizeHint().height()

        x = (self.width() - hint_width) // 2
        y = (self.height() - hint_height) // 2

        self._hint_label.move(x, y)

    def _update_hint(self):
        self._hint_label.setVisible(not self.text())



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Linear Equations Solver")
        self.setGeometry(int((1920 - width)/2), int((1080 - height)/2), int(width), int(height))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""QMainWindow { background-color: #F5F5DC;
                                        border: 8px solid black;}""")
        self.setMinimumSize(400, 300)

        self.header = Header(self)
        self.header.setFixedHeight(40)
        self.header.setStyleSheet("background-color: #2b2b2b;")
        self.min_btn = QPushButton("–")
        self.close_btn = QPushButton("✕")

        self.v_main_layout = QVBoxLayout()
        self.general_v_layout = QVBoxLayout()

        self.header_h_layout = QHBoxLayout(self.header)
        self.header_h_layout.setContentsMargins(10, 0, 5, 0)
        self.header_h_layout.setSpacing(5)
        self.v_main_layout.addWidget(self.header)

        self.v_in_layout = QVBoxLayout()
        self.button_layout = QVBoxLayout()
        self.h_in_layout = QHBoxLayout()
        self.coeff_layout = QGridLayout()

        self.input_m = HintLineEdit("Enter number of variables", self)
        self.input_n = HintLineEdit("Enter number of equations", self)
        self.submit_button = QPushButton(self, text = "Submit")
        self.coeff_submit_button = QPushButton(self, text = "Solve")
        self.reset_button = QPushButton(self, text = "Reset")
        self.name_label = QLabel("Linear Equations Solver", self)

        self._drag_pos = None

        self.coeff_boxes = None
        self.ans_boxes = None
        self.n_eqs = None
        self.n_vars = None

        self.A_matrix = None
        self.B_matrix = None
        self.x = None
        self.particular_soln = None
        self.nullspace_basis = None
        self.complete_soln = None
        self.error_label = None

        self._mouse_pos = None
        self._resize_dir = None
        self._geom = None

        self.setMouseTracking(True)

        self.initUI()

    def initUI(self):

        #Central widget reset
        if self.centralWidget():
            self.centralWidget().deleteLater()

        #Central Widget definition
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        #Title Bar
        self.name_label.setFont(QFont("Arial", 14))
        self.name_label.setStyleSheet("color: #FFFFFF;"
                                      "font-weight: bold;"
                                      "text-decoration: underline;")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.header_h_layout.addWidget(self.name_label)
        self.header_h_layout.addStretch()
        self.header_h_layout.addWidget(self.min_btn)
        self.min_btn.setFixedSize(30, 28)
        self.min_btn.setFocusPolicy(Qt.NoFocus)
        self.min_btn.clicked.connect(self.showMinimized)
        self.min_btn.setStyleSheet("""
        QPushButton {
            color: white;
            background: transparent;
            border: none;
            font-size: 16px;
        }
        QPushButton:hover {
            background: #444;
        }
        """)
        self.close_btn.setFixedSize(30, 28)
        self.close_btn.setFocusPolicy(Qt.NoFocus)
        self.close_btn.clicked.connect(self.close)

        self.close_btn.setStyleSheet("""
        QPushButton {
            color: white;
            background: transparent;
            border: none;
            font-size: 14px;
        }
        QPushButton:hover {
            background: #d32f2f;
        }
        """)
        self.header_h_layout.addWidget(self.close_btn)

        #Inputs for Equation and Variable Nos.
        self.h_in_layout.addWidget(self.input_n)
        self.input_n.setStyleSheet("background-color: #FFFFFF; border: 2px solid black;")
        self.input_n.show()

        self.h_in_layout.addWidget(self.input_m)
        self.input_m.setStyleSheet("background-color: #FFFFFF; border: 2px solid black;")
        self.input_m.show()

        self.h_in_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        #Buttons
        self.button_layout.addWidget(self.submit_button)
        self.button_layout.addWidget(self.coeff_submit_button)
        self.button_layout.addWidget(self.reset_button)
        self.submit_button.setStyleSheet("background-color: #FFFFFF;")
        self.coeff_submit_button.setStyleSheet("background-color: #FFFFFF;")
        self.reset_button.setStyleSheet("background-color: #FFFFFF;")
        self.button_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.submit_button.show()
        self.coeff_submit_button.hide()
        self.reset_button.hide()

        #Add to main layout
        for i in [self.general_v_layout, self.v_in_layout, self.h_in_layout, self.coeff_layout, self.button_layout]:
            self.v_main_layout.addLayout(i)

        #Set central widget layout
        central_widget.setLayout(self.v_main_layout)

        #Connect button signals
        self.submit_button.clicked.connect(self.lineqUI)
        self.coeff_submit_button.clicked.connect(self.solver)
        self.reset_button.clicked.connect(self.resetUI)

        #Reset state
        self.coeff_boxes = []
        self.ans_boxes = []

        self.centralWidget().setMouseTracking(True)
        self.header.setMouseTracking(True)

    def _get_resize_direction(self, pos):
        rect = self.rect()
        x, y = pos.x(), pos.y()

        # Header: block resize except top edge margin
        if RESIZE_MARGIN < y <= self.header.height():
            return None

        left = x < RESIZE_MARGIN
        right = x > rect.width() - RESIZE_MARGIN
        top = y < RESIZE_MARGIN
        bottom = y > rect.height() - RESIZE_MARGIN

        if left and top: return "top_left"
        if right and top: return "top_right"
        if left and bottom: return "bottom_left"
        if right and bottom: return "bottom_right"
        if left: return "left"
        if right: return "right"
        if top: return "top"
        if bottom: return "bottom"
        return None


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._resize_dir = self._get_resize_direction(event.pos())
            self._mouse_pos = event.globalPos()
            self._geom = self.geometry()
            event.accept()

    def mouseMoveEvent(self, event):

        if not self._resize_dir:
            direction = self._get_resize_direction(event.pos())
            cursors = {
                "left": Qt.SizeHorCursor,
                "right": Qt.SizeHorCursor,
                "top": Qt.SizeVerCursor,
                "bottom": Qt.SizeVerCursor,
                "top_left": Qt.SizeFDiagCursor,
                "bottom_right": Qt.SizeFDiagCursor,
                "top_right": Qt.SizeBDiagCursor,
                "bottom_left": Qt.SizeBDiagCursor,
            }
            self.setCursor(cursors.get(direction, Qt.ArrowCursor))

        if self._resize_dir:
            delta = event.globalPos() - self._mouse_pos
            g = self.geometry()

            if "right" in self._resize_dir:
                g.setWidth(max(self.minimumWidth(), g.width() + delta.x()))
            if "bottom" in self._resize_dir:
                g.setHeight(max(self.minimumHeight(), g.height() + delta.y()))
            if "left" in self._resize_dir:
                g.setLeft(g.left() + delta.x())
            if "top" in self._resize_dir:
                g.setTop(g.top() + delta.y())

            self.setGeometry(g)
            self._mouse_pos = event.globalPos()
            return


    def mouseReleaseEvent(self, event):
        self._resize_dir = None

    def lineqUI(self):
        self.submit_button.hide()
        self.input_n.hide()
        self.input_m.hide()
        self.coeff_submit_button.show()

        self.n_vars = self.input_n.text()
        self.n_eqs = self.input_m.text()

        if not self.n_vars.isdigit() or not self.n_eqs.isdigit():
            raise ValueError("Number of variables and equations must be numerical")

        self.n_vars = int(self.n_vars)
        self.n_eqs = int(self.n_eqs)

        self.coeff_boxes = []
        self.ans_boxes = []

        for row in range(self.n_eqs):
            row_boxes = []

            for col in range(self.n_vars):
                coeff_box = HintLineEdit(f"a{row*self.n_vars + col + 1}", self)
                coeff_box.setStyleSheet("background-color: #FFFFFF;"
                                        "border-color: black;")
                self.coeff_layout.addWidget(coeff_box, row, col)
                row_boxes.append(coeff_box)

            ans_box = HintLineEdit(f"b{row + 1}", self)
            ans_box.setStyleSheet("background-color: #FFFFFF;")
            self.coeff_layout.addWidget(ans_box, row, self.n_vars + 1)

            self.coeff_boxes.append(row_boxes)
            self.ans_boxes.append(ans_box)

    def solver(self):

        def safe_float(box):
            text = box.text().strip()
            if not text:
                return 0.0
            return float(text)

        A = []
        for row in self.coeff_boxes:
            A.append([safe_float(coeff_box) for coeff_box in row])

        B = [[safe_float(ans_box)] for ans_box in self.ans_boxes]

        try:
            obj = LES(A, B)
            self.x = obj.solve()
            self.solutionUI()
        except ColumnSpaceError:
            self.solutionUI(cse = True)


    def solutionUI(self, cse = False):
        self.clear_layout(self.coeff_layout)
        self.coeff_submit_button.hide()
        self.reset_button.show()

        if cse:
            self.error_label = QLabel(f"No solution exists for this system")
            self.error_label.setFont(QFont("Arial", 20))
            self.error_label.setStyleSheet("color: red;"
                                           "font-weight: bold;")
            self.error_label.setAlignment(Qt.AlignCenter)
            self.general_v_layout.addWidget(self.error_label)
        else:
            xp = QLabel(f"Particular solution xp = {self.x[0]}")
            xn = QLabel(f"Nullspace basis is xn = {self.x[1]}")
            x = QLabel(f"Complete solution is x = {self.x[0]} + c{self.x[1]}")
            xp.setFont(QFont("Arial", 20))
            xp.setStyleSheet("color: black;"
                             "font-weight: bold;")
            xn.setFont(QFont("Arial", 20))
            xn.setStyleSheet("color: black;"
                             "font-weight: bold;")
            x.setFont(QFont("Arial", 20))
            x.setStyleSheet("color: black;"
                            "font-weight: bold;")
            xp.setAlignment(Qt.AlignCenter)
            xn.setAlignment(Qt.AlignCenter)
            x.setAlignment(Qt.AlignCenter)
            self.general_v_layout.addWidget(xp)
            self.general_v_layout.addWidget(xn)
            self.general_v_layout.addWidget(x)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    self.clear_layout(sub_layout)

    def resetUI(self):
        # ----- Clear dynamic layouts -----
        self.clear_layout(self.coeff_layout)
        self.clear_layout(self.general_v_layout)

        # ----- Reset inputs -----
        self.input_n.clear()
        self.input_m.clear()
        self.input_n.show()
        self.input_m.show()

        # ----- Reset visibility -----
        self.submit_button.show()
        self.coeff_submit_button.hide()
        self.reset_button.hide()

        # ----- Reset internal state -----
        self.coeff_boxes = []
        self.ans_boxes = []
        self.n_eqs = None
        self.n_vars = None

        self.input_n.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())