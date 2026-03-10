import sys
import os
import importlib.util
from PyQt6 import QtWidgets, QtCore, QtGui


class Canvas(QtWidgets.QWidget):
    # Jelzés a főablaknak: (x, y, "start" vagy "end")
    point_selected = QtCore.pyqtSignal(int, int, str)

    def __init__(self):
        super().__init__()
        self.grid_size = (30, 30)
        self.pixels = {}  # (x, y) -> QColor
        self.setMinimumSize(500, 500)
        self.next_click_is_start = True

    def set_grid_resolution(self, cols, rows):
        self.grid_size = (cols, rows)
        self.clear_canvas()

    def clear_canvas(self):
        self.pixels = {}
        self.update()

    def put_pixel(self, x, y, color):
        if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
            self.pixels[(x, y)] = color
            self.update()

    def mousePressEvent(self, event):
        # Kiszámoljuk a logikai koordinátát a kattintás helyéből
        cell_w = self.width() / self.grid_size[0]
        cell_h = self.height() / self.grid_size[1]

        lx = int(event.position().x() / cell_w)
        ly = int(event.position().y() / cell_h)

        if 0 <= lx < self.grid_size[0] and 0 <= ly < self.grid_size[1]:
            tipus = "start" if self.next_click_is_start else "end"
            self.point_selected.emit(lx, ly, tipus)

            # Vizuális visszajelzés (sárga pont a kattintás helyén)
            self.put_pixel(lx, ly, QtGui.QColor(255, 255, 0))
            self.next_click_is_start = not self.next_click_is_start

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        cols, rows = self.grid_size
        cell_w, cell_h = self.width() / cols, self.height() / rows

        # Rács rajzolása
        painter.setPen(QtGui.QColor(220, 220, 220))
        for i in range(cols + 1):
            painter.drawLine(int(i * cell_w), 0, int(i * cell_w), self.height())
        for j in range(rows + 1):
            painter.drawLine(0, int(j * cell_h), self.width(), int(j * cell_h))

        # "Pixelek" (cellák) színezése
        for (lx, ly), color in self.pixels.items():
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(QtCore.QRectF(lx * cell_w, ly * cell_h, cell_w, cell_h))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raszteres Rajzoloprogram")
        self.plugins = []
        self.current_generator = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_step)
        self.init_ui()
        self.load_plugins()

    def init_ui(self):
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QHBoxLayout(main_widget)

        # Vezérlőpult (Bal oldal)
        sidebar = QtWidgets.QVBoxLayout()

        sidebar.addWidget(QtWidgets.QLabel("Rács méret (X, Y):"))
        self.res_x = QtWidgets.QSpinBox();
        self.res_x.setValue(30)
        self.res_y = QtWidgets.QSpinBox();
        self.res_y.setValue(30)
        sidebar.addWidget(self.res_x);
        sidebar.addWidget(self.res_y)

        sidebar.addWidget(QtWidgets.QLabel("--- Kattints a rácsra! ---"))
        self.startX = QtWidgets.QSpinBox();
        self.startY = QtWidgets.QSpinBox()
        self.endX = QtWidgets.QSpinBox();
        self.endY = QtWidgets.QSpinBox()
        for sb in [self.startX, self.startY, self.endX, self.endY]:
            sb.setRange(0, 999)
            sidebar.addWidget(sb)

        sidebar.addWidget(QtWidgets.QLabel("Algoritmus:"))
        self.algo_combo = QtWidgets.QComboBox()
        sidebar.addWidget(self.algo_combo)

        sidebar.addWidget(QtWidgets.QLabel("Sebesség (ms):"))
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 500);
        self.speed_slider.setValue(50);
        self.speed_slider.setInvertedAppearance(True)
        sidebar.addWidget(self.speed_slider)

        self.btn_run = QtWidgets.QPushButton("Rajzolás indítása")
        self.btn_run.clicked.connect(self.start_algorithm)
        sidebar.addWidget(self.btn_run)

        self.btn_clear = QtWidgets.QPushButton("Vászon törlése")
        self.btn_clear.clicked.connect(self.clear_canvas)
        sidebar.addWidget(self.btn_clear)

        sidebar.addStretch()
        layout.addLayout(sidebar, 1)

        # Vászon (Jobb oldal)
        self.canvas = Canvas()
        self.canvas.point_selected.connect(self.update_coords)
        layout.addWidget(self.canvas, 4)

    def update_coords(self, x, y, tipus):
        if tipus == "start":
            self.startX.setValue(x);
            self.startY.setValue(y)
        else:
            self.endX.setValue(x);
            self.endY.setValue(y)

    def load_plugins(self):
        if not os.path.exists("plugins"): os.mkdir("plugins")
        for f in os.listdir("plugins"):
            if f.endswith(".py") and f != "__init__.py":
                spec = importlib.util.spec_from_file_location(f[:-3], f"plugins/{f}")
                m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m)
                if hasattr(m, "NEV"):
                    self.algo_combo.addItem(m.NEV, m)

    def clear_canvas(self):
        self.timer.stop()
        self.canvas.set_grid_resolution(self.res_x.value(), self.res_y.value())

    def start_algorithm(self):
        self.clear_canvas()
        algo_module = self.algo_combo.currentData()
        if algo_module:
            p1 = (self.startX.value(), self.startY.value())
            p2 = (self.endX.value(), self.endY.value())
            self.current_generator = algo_module.futtat(self.res_x.value(), self.res_y.value(), p1, p2)
            self.timer.start(self.speed_slider.value())

    def next_step(self):
        try:
            x, y, color = next(self.current_generator)
            self.canvas.put_pixel(x, y, QtGui.QColor(*color))
        except StopIteration:
            self.timer.stop()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())