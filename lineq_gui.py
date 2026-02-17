import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
                             QWidget, QPushButton)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from linear_equations_solver import LinearEquationSolver as LES
from linear_equations_solver import ColumnSpaceError

width = 700
height = 500

RESIZE_MARGIN = 8

class Header(QFrame):

    #Header drag only logic

    def mousePressEvent(self, event):

        #Set left mouse click event
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()                                      #Set drag position
            event.accept()

    def mouseMoveEvent(self, event):

        #Set left mouse drag event
        if event.buttons() == Qt.LeftButton:
            self.window().move(
                self.window().pos() + event.globalPos() - self._drag_pos            #Move window according to mouse on
            )                                                                       #header position
            self._drag_pos = event.globalPos()
            event.accept()

class HintLineEdit(QLineEdit):

    #Custom Line Edit with better hint

    def __init__(self, hint, parent=None):
        super().__init__(parent)

        self.setAlignment(Qt.AlignCenter)

        self._hint_label = QLabel(hint, self)                                       #Hint Label Style Sheet
        self._hint_label.setStyleSheet("color: #888888;"
                                       "border: none;"
                                       "background: transparent;")
        self._hint_label.setAttribute(Qt.WA_TransparentForMouseEvents)              #Hint is transparent for mouse events

        self.textChanged.connect(self._update_hint)                                 #Connect and update when text entered
        self._update_hint()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        hint_width = self._hint_label.sizeHint().width()                            #Centering of cursor and hint label
        hint_height = self._hint_label.sizeHint().height()

        x = (self.width() - hint_width) // 2
        y = (self.height() - hint_height) // 2

        self._hint_label.move(x, y)

    def _update_hint(self):

        self._hint_label.setVisible(not self.text())                                #Set the hint visible when there is no text



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #Main Window Definition

        #Window Definition and Style Sheet
        self.setWindowTitle("Linear Equations Solver")
        self.setGeometry(int((1920 - width)/2), int((1080 - height)/2), int(width), int(height))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""QMainWindow { background-color: #F5F5DC;
                                        border: 8px solid black;}""")
        self.setMinimumSize(400, 300)

        #Header Definition and Style Sheet
        self.header = Header(self)
        self.header.setFixedHeight(40)
        self.header.setStyleSheet("background-color: #2b2b2b;")

        #Header Buttons
        self.min_btn = QPushButton("–")
        self.close_btn = QPushButton("✕")

        #Required Layouts
        self.v_main_layout = QVBoxLayout()                                          #Main Layout
        self.general_v_layout = QVBoxLayout()                                       #General Widget Layout
        self.v_in_layout = QVBoxLayout()                                            #Vertical Input Line Edit Layout
        self.button_layout = QVBoxLayout()                                          #Button Layouts
        self.h_in_layout = QHBoxLayout()                                            #Horizontal Input Line Edit Layout
        self.coeff_layout = QGridLayout()                                           #Coefficient Grid Layout
        self.header_grid_h_layout = QHBoxLayout(self.header)                        #Header Layout
        self.header_grid_h_layout.setContentsMargins(10, 0, 5, 0)
        self.header_grid_h_layout.setSpacing(5)

        self.intro_text = QLabel

        #Input Line Edit Definitions
        self.input_m = HintLineEdit("Enter number of variables", self)
        self.input_n = HintLineEdit("Enter number of equations", self)

        #Button Definitions
        self.submit_button = QPushButton(self, text = "Submit")
        self.coeff_submit_button = QPushButton(self, text = "Solve")
        self.reset_button = QPushButton(self, text = "Reset")

        #Title Label Definition
        self.name_label = QLabel("Linear Equations Solver", self)

        #Intro Text Label Definition
        self.intro_text = QLabel("Welcome to Linear Equations Solver!\n\n"
                                 "Enter the number of variables and number\nof equations to begin:\n")

        #Invalid Input Error Label Definition
        self.var_eq_err = QLabel("Please enter a valid number")

        #Coefficient Intro Text Definition
        self.coeff_text = QLabel("Enter the coefficients of the equation:")

        #Variable Definitions
        self.n_eqs = None
        self.n_vars = None
        self.coeff_boxes = None
        self.variable_labels = None
        self.equals_labels = None
        self.plus_labels = None
        self.ans_boxes = None
        self.A_matrix = None
        self.B_matrix = None
        self.x = None

        self.solution_widgets = []

        #Mouse Movement Variable Definitions
        self._drag_pos = None
        self._mouse_pos = None
        self._resize_dir = None
        self._geom = None

        self.setMouseTracking(True)

        self.initUI()

    def initUI(self):

        #UI for Main Window

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
        self.header_grid_h_layout.addWidget(self.name_label)
        self.header_grid_h_layout.addStretch()
        self.header_grid_h_layout.addWidget(self.min_btn)
        self.min_btn.setFixedSize(30, 28)
        self.min_btn.setFocusPolicy(Qt.NoFocus)
        self.min_btn.clicked.connect(self.showMinimized)
        self.min_btn.setStyleSheet(""" QPushButton { color: white;
                                                     background: transparent;
                                                     border: none;
                                                     font-size: 16px;
                                                    }
                                       QPushButton:hover { background: #444;
                                                         } """)
        self.close_btn.setFixedSize(30, 28)
        self.close_btn.setFocusPolicy(Qt.NoFocus)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet(""" QPushButton { color: white;
                                                       background: transparent;
                                                       border: none;
                                                       font-size: 14px;
                                                      }
                                         QPushButton:hover { background: #d32f2f;
                                                            } """)
        self.header_grid_h_layout.addWidget(self.close_btn)
        self.v_main_layout.addWidget(self.header)

        #Intro Text
        self.intro_text.setFont(QFont("Arial", 20))
        self.intro_text.setStyleSheet("color: black;"
                                      "font-weight: bold;")
        self.general_v_layout.addWidget(self.intro_text)
        self.intro_text.show()

        #Invalid Input Error Text
        self.var_eq_err.setFont(QFont("Arial", 20))
        self.var_eq_err.setStyleSheet("color: red;"
                                      "font-weight: bold;")
        self.var_eq_err.setAlignment(Qt.AlignCenter)
        self.general_v_layout.addWidget(self.var_eq_err)
        self.var_eq_err.hide()

        #Coefficient Intro Text
        self.coeff_text.setFont(QFont("Arial", 20))
        self.coeff_text.setStyleSheet("color: black;"
                                      "font-weight: bold;")
        self.general_v_layout.addWidget(self.coeff_text)
        self.coeff_text.hide()

        #Input Line Edit Style Sheets and Visibility
        self.h_in_layout.addWidget(self.input_n)
        self.input_n.setStyleSheet("background-color: #FFFFFF; border: 2px solid black;")
        self.input_n.show()

        self.h_in_layout.addWidget(self.input_m)
        self.input_m.setStyleSheet("background-color: #FFFFFF; border: 2px solid black;")
        self.input_m.show()

        self.h_in_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        #Button Style Sheets and Visibility
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

        #Adding Widgets to Main Layout
        for i in [self.general_v_layout, self.v_in_layout, self.h_in_layout, self.coeff_layout, self.button_layout]:
            self.v_main_layout.addLayout(i)

        #Set Central Widget Layout
        central_widget.setLayout(self.v_main_layout)

        #Connect Button Signals
        self.submit_button.clicked.connect(self.lineqUI)
        self.coeff_submit_button.clicked.connect(self.solver)
        self.reset_button.clicked.connect(self.resetUI)

        #Mouse Position Tracking
        self.centralWidget().setMouseTracking(True)
        self.header.setMouseTracking(True)

    def _get_resize_direction(self, pos):
        rect = self.rect()
        x, y = pos.x(), pos.y()

        # Header block resize except top edge margin
        if RESIZE_MARGIN < y <= self.header.height():
            return None

        #Set directions
        left = x < RESIZE_MARGIN
        right = x > rect.width() - RESIZE_MARGIN
        top = y < RESIZE_MARGIN
        bottom = y > rect.height() - RESIZE_MARGIN

        #Return value based on position
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

        #Set left mouse click event
        if event.button() == Qt.LeftButton:
            self._resize_dir = self._get_resize_direction(event.pos())              #Set resizing direction
            self._mouse_pos = event.globalPos()                                     #Find mouse position
            self._geom = self.geometry()                                            #Set geometry
            event.accept()

    def mouseMoveEvent(self, event):

        #Set left mouse drag event

        if not self._resize_dir:                                                    #Cursor Style Change based on Position
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

        if self._resize_dir:                                                        #Resizing window
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

        #Set left mouse release event

        self._resize_dir = None                                                     #Reset resize direction

    def lineqUI(self):

        #UI for Coefficient Input Window

        self.n_eqs = self.input_n.text()                                           #Extract text from line edits
        self.n_vars = self.input_m.text()

        if not self.n_vars.isdigit() or not self.n_eqs.isdigit():                   #Check if text is valid
            self.var_eq_err.show()
        else:
            self.var_eq_err.hide()
            self.submit_button.hide()                                                   # Adjust widget visibility
            self.input_n.hide()
            self.input_m.hide()
            self.coeff_submit_button.show()
            self.intro_text.hide()
            self.coeff_text.show()

            self.n_vars = int(self.n_vars)                                              #Set text to int datatype
            self.n_eqs = int(self.n_eqs)

            self.coeff_boxes = []                                                       #Initialize coefficient widget storage
            self.ans_boxes = []
            self.variable_labels = []
            self.equals_labels = []
            self.plus_labels = []

            for row in range(self.n_eqs):                                               #Coefficient widget logic
                row_boxes = []

                for col in range(self.n_vars):
                    coeff_box = HintLineEdit(f"a{row*self.n_vars + col + 1}", self)
                    variable_label = QLabel(f"x{col + 1}")
                    plus_label = QLabel("+")

                    coeff_box.setStyleSheet("background-color: #FFFFFF;"
                                            "border-color: black;")
                    variable_label.setStyleSheet("color : black;")
                    plus_label.setStyleSheet("Color : black;")

                    coeff_box.setFixedSize(100, 80)
                    
                    coeff_h_layout = QHBoxLayout()
                    coeff_h_layout.setContentsMargins(0, 0, 0, 0)
                    coeff_h_layout.setSpacing(2)
                    
                    if col != 0:
                        coeff_h_layout.addWidget(plus_label)
                        self.plus_labels.append(plus_label)
                    coeff_h_layout.addWidget(coeff_box)
                    coeff_h_layout.addWidget(variable_label)

                    self.coeff_layout.addLayout(coeff_h_layout, row, col, alignment = Qt.AlignLeft)

                    row_boxes.append(coeff_box)
                    self.variable_labels.append(variable_label)

                ans_box = HintLineEdit(f"b{row + 1}", self)                        #RHS widget logic
                ans_box.setStyleSheet("background-color: #FFFFFF;")

                ans_box.setFixedSize(100, 80)

                equals_label = QLabel("=")
                equals_label.setStyleSheet("color : black;")

                ans_h_layout = QHBoxLayout()
                ans_h_layout.setContentsMargins(0, 0, 0, 0)
                ans_h_layout.setSpacing(2)

                ans_h_layout.addWidget(equals_label)
                ans_h_layout.addWidget(ans_box)

                self.coeff_layout.addLayout(ans_h_layout, row, self.n_vars + 1, alignment = Qt.AlignLeft)

                self.coeff_boxes.append(row_boxes)
                self.ans_boxes.append(ans_box)
                self.equals_labels.append(equals_label)

    def solver(self):

        #Linear Equations Solver Unit

        def safe_float(box):

            #Converts to float and checks for empty entry

            text = box.text().strip()
            if not text:
                return 0.0
            return float(text)

        A = []
        for row in self.coeff_boxes:
            A.append([safe_float(coeff_box) for coeff_box in row])                  #Form Coefficient Matrix

        B = [[safe_float(ans_box)] for ans_box in self.ans_boxes]                   #Form RHS Matrix

        try:
            obj = LES(A, B)                                                         #Solve using LES
            self.x = obj.solve()
            self.solutionUI()
        except ColumnSpaceError:                                                    #Set flag for no solution
            self.solutionUI(cse = True)


    def solutionUI(self, cse = False):

        #UI for Solution Display

        self.clear_layout(self.coeff_layout)
        self.coeff_submit_button.hide()
        self.coeff_text.hide()
        self.reset_button.show()

        if cse:
            label = QLabel("No solution exists for this system")
            label.setFont(QFont("Arial", 20))
            label.setStyleSheet("color: red; font-weight: bold;")
            label.setAlignment(Qt.AlignCenter)
            self.general_v_layout.addWidget(label)
            self.solution_widgets.append(label)
        else:
            xp = QLabel(f"Particular solution xp = {self.x[0]}")
            xn = QLabel(f"Nullspace basis xn = {self.x[1]}")
            x  = QLabel(f"Complete solution x = {self.x[0]} + c{self.x[1]}")

            for lbl in (xp, xn, x):
                lbl.setFont(QFont("Arial", 20))
                lbl.setStyleSheet("color: black; font-weight: bold;")
                lbl.setAlignment(Qt.AlignCenter)
                self.general_v_layout.addWidget(lbl)
                self.solution_widgets.append(lbl)

    def clear_layout(self, layout):

        #Logic for Clearing Layouts

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

        self.clear_layout(self.coeff_layout)

        for w in self.solution_widgets:
            w.deleteLater()
        self.solution_widgets.clear()

        self.coeff_text.hide()
        self.var_eq_err.hide()
        self.intro_text.show()

        self.input_n.clear()
        self.input_m.clear()
        self.input_n.show()
        self.input_m.show()

        self.submit_button.show()
        self.coeff_submit_button.hide()
        self.reset_button.hide()

        self.coeff_boxes = []
        self.ans_boxes = []
        self.variable_labels = []
        self.equals_labels = []
        self.plus_labels = []
        self.n_eqs = None
        self.n_vars = None

        self.input_n.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())