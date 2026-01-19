import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QWidget, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from linear_equations_solver import LinearEquationSolver as LES
from linear_equations_solver import ColumnSpaceError

width = 700
height = 500

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Linear Equations Solver")
        self.setGeometry(int((1920 - width)/2), int((1080 - height)/2), int(width), int(height))

        self.general_v_layout = QVBoxLayout()
        self.v_main_layout = QVBoxLayout()
        self.v_in_layout = QVBoxLayout()
        self.button_layout = QVBoxLayout()
        self.h_in_layout = QHBoxLayout()
        self.coeff_layout = QGridLayout()

        self.input_m = QLineEdit(self)
        self.input_n = QLineEdit(self)
        self.submit_button = QPushButton(self, text = "Submit")
        self.coeff_submit_button = QPushButton(self, text = "Solve")
        self.reset_button = QPushButton(self, text = "Reset")
        self.name_label = QLabel("Linear Equations Solver", self)

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

        self.initUI()

    def initUI(self):

        #Central widget reset
        if self.centralWidget():
            self.centralWidget().deleteLater()

        #Central Widget definition
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        #Title
        self.general_v_layout.addWidget(self.name_label)
        self.name_label.setFont(QFont("Arial", 30))
        self.name_label.setStyleSheet("color: blue;"
                                      "font-weight: bold;"
                                      "text-decoration: underline;")
        self.name_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        #Inputs for Equation and Variable Nos.
        self.h_in_layout.addWidget(self.input_n)
        self.input_n.setPlaceholderText("Enter the number of variables")
        self.input_n.setAlignment(Qt.AlignHCenter)
        self.input_n.show()

        self.h_in_layout.addWidget(self.input_m)
        self.input_m.setPlaceholderText("Enter the number of equations")
        self.input_m.setAlignment(Qt.AlignHCenter)
        self.input_m.show()

        self.h_in_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        #Buttons
        self.button_layout.addWidget(self.submit_button)
        self.button_layout.addWidget(self.coeff_submit_button)
        self.button_layout.addWidget(self.reset_button)
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
                coeff_box = QLineEdit(self)
                coeff_box.setPlaceholderText(f"a{row*self.n_vars + col + 1}")
                self.coeff_layout.addWidget(coeff_box, row, col)
                row_boxes.append(coeff_box)

            ans_box = QLineEdit(self)
            ans_box.setPlaceholderText(f"b{row + 1}")
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
            self.general_v_layout.addWidget(self.error_label)
        else:
            xp = QLabel(f"Particular solution xp = {self.x[0]}")
            xn = QLabel(f"Nullspace basis is xn = {self.x[1]}")
            x = QLabel(f"Complete solution is x = {self.x[0]} + c{self.x[1]}")
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
        #Button disconnection
        self.submit_button.clicked.disconnect(self.lineqUI)
        self.coeff_submit_button.clicked.disconnect(self.solver)
        self.reset_button.clicked.disconnect(self.resetUI)

        # Layout reset
        self.general_v_layout = QVBoxLayout()
        self.v_main_layout = QVBoxLayout()
        self.v_in_layout = QVBoxLayout()
        self.button_layout = QVBoxLayout()
        self.h_in_layout = QHBoxLayout()
        self.coeff_layout = QGridLayout()

        self.initUI()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())