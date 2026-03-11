import sys
import os
import importlib.util
from PyQt6 import QtWidgets, QtCore, QtGui


class Canvas(QtWidgets.QWidget):
    point_selected = QtCore.pyqtSignal(int, int, str)

    def __init__(self):
        super().__init__()
        self.grid_size = (50, 50)
        self.pixels = {}
        self.setMinimumSize(500, 500)
        self.next_click_is_start = True
        self.marker_start = None
        self.marker_end = None

    def set_grid_resolution(self, cols, rows):
        self.grid_size = (cols, rows)
        self.clear_canvas()

    def clear_canvas(self):
        self.pixels = {}
        self.marker_start = None
        self.marker_end = None
        self.update()

    def put_pixel(self, x, y, color):
        if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
            self.pixels[(int(x), int(y))] = color
            self.update()

    def mousePressEvent(self, event):
        cell_w = self.width() / self.grid_size[0]
        cell_h = self.height() / self.grid_size[1]

        lx = int(event.position().x() / cell_w)
        ly = int(event.position().y() / cell_h)

        if 0 <= lx < self.grid_size[0] and 0 <= ly < self.grid_size[1]:
            tipus = "start" if self.next_click_is_start else "end"
            self.point_selected.emit(lx, ly, tipus)

            if self.next_click_is_start:
                self.marker_start = (lx, ly)
            else:
                self.marker_end = (lx, ly)

            self.next_click_is_start = not self.next_click_is_start
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        cols, rows = self.grid_size
        cell_w, cell_h = self.width() / cols, self.height() / rows

        painter.setPen(QtGui.QColor(220, 220, 220))
        for i in range(cols + 1):
            x = int(i * cell_w)
            painter.drawLine(x, 0, x, self.height())
        for j in range(rows + 1):
            y = int(j * cell_h)
            painter.drawLine(0, y, self.width(), y)

        for (lx, ly), color in self.pixels.items():
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(QtCore.QRectF(lx * cell_w, ly * cell_h, cell_w, cell_h))

        if self.marker_start:
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 0, 150)))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(
                QtCore.QRectF(self.marker_start[0] * cell_w, self.marker_start[1] * cell_h, cell_w, cell_h))

        if self.marker_end:
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 165, 0, 150)))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(QtCore.QRectF(self.marker_end[0] * cell_w, self.marker_end[1] * cell_h, cell_w, cell_h))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Szoftveres Renderelő Keretrendszer")
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_step)
        self.current_generator = None

        self.init_ui()
        self.load_plugins()

    def init_ui(self):
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QHBoxLayout(main_widget)

        sidebar = QtWidgets.QVBoxLayout()

        sidebar.addWidget(QtWidgets.QLabel("<b>Rács felbontás (X, Y):</b>"))
        self.res_x = QtWidgets.QSpinBox();
        self.res_x.setValue(50);
        self.res_x.setRange(5, 200)
        self.res_y = QtWidgets.QSpinBox();
        self.res_y.setValue(50);
        self.res_y.setRange(5, 200)
        sidebar.addWidget(self.res_x);
        sidebar.addWidget(self.res_y)

        sidebar.addSpacing(10)
        sidebar.addWidget(QtWidgets.QLabel("<b>Kijelölt koordináták:</b>"))
        self.startX = QtWidgets.QSpinBox();
        self.startY = QtWidgets.QSpinBox()
        self.endX = QtWidgets.QSpinBox();
        self.endY = QtWidgets.QSpinBox()
        for sb in [self.startX, self.startY, self.endX, self.endY]:
            sb.setRange(0, 500)
            sidebar.addWidget(sb)

        sidebar.addSpacing(10)
        sidebar.addWidget(QtWidgets.QLabel("<b>Algoritmus választás:</b>"))
        self.algo_combo = QtWidgets.QComboBox()
        # --- ÚJ: Figyeljük, ha másikat választasz ---
        self.algo_combo.currentIndexChanged.connect(self.update_info_text)
        sidebar.addWidget(self.algo_combo)

        # --- ÚJ: Használati utasítás doboza ---
        self.info_box = QtWidgets.QTextBrowser()
        self.info_box.setMaximumHeight(120)
        self.info_box.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        sidebar.addWidget(self.info_box)

        sidebar.addSpacing(10)
        sidebar.addWidget(QtWidgets.QLabel("<b>Sebesség (ms):</b>"))
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 250);
        self.speed_slider.setValue(20);
        self.speed_slider.setInvertedAppearance(True)
        sidebar.addWidget(self.speed_slider)

        sidebar.addSpacing(10)
        self.check_clear = QtWidgets.QCheckBox("Törlés indítás előtt")
        self.check_clear.setChecked(True)
        sidebar.addWidget(self.check_clear)

        self.btn_run = QtWidgets.QPushButton("Futtatás / Rajzolás")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        self.btn_run.clicked.connect(self.start_algorithm)
        sidebar.addWidget(self.btn_run)

        self.btn_clear = QtWidgets.QPushButton("Vászon ürítése")
        self.btn_clear.clicked.connect(self.clear_canvas)
        sidebar.addWidget(self.btn_clear)

        sidebar.addStretch()
        layout.addLayout(sidebar, 1)

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

    # --- ÚJ: Szöveg frissítése a menü alapján ---
    def update_info_text(self):
        algo_module = self.algo_combo.currentData()
        if algo_module and hasattr(algo_module, "LEIRAS"):
            self.info_box.setText(algo_module.LEIRAS)
        else:
            self.info_box.setText("<i>Ehhez az algoritmushoz nincs megadva használati utasítás.</i>")

    def load_plugins(self):
        if not os.path.exists("plugins"):
            os.mkdir("plugins")

        for f in os.listdir("plugins"):
            if f.endswith(".py") and f != "__init__.py":
                try:
                    spec = importlib.util.spec_from_file_location(f[:-3], f"plugins/{f}")
                    m = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(m)
                    if hasattr(m, "NEV"):
                        self.algo_combo.addItem(f"[{getattr(m, 'TIPUS', 'Egyéb')}] {m.NEV}", m)
                except Exception as e:
                    print(f"Hiba a plugin betöltésekor ({f}): {e}")

        # Ha betöltött mindent, mutassa az első leírását
        if self.algo_combo.count() > 0:
            self.update_info_text()

    def clear_canvas(self):
        self.timer.stop()
        self.canvas.set_grid_resolution(self.res_x.value(), self.res_y.value())

    def start_algorithm(self):
        if self.check_clear.isChecked():
            self.clear_canvas()

        self.canvas.grid_size = (self.res_x.value(), self.res_y.value())
        algo_module = self.algo_combo.currentData()

        if algo_module:
            p1 = (self.startX.value(), self.startY.value())
            p2 = (self.endX.value(), self.endY.value())
            algo_module.PIXELS = self.canvas.pixels

            self.current_generator = algo_module.futtat(
                self.res_x.value(), self.res_y.value(), p1, p2
            )
            self.timer.start(self.speed_slider.value())

    def next_step(self):
        if self.current_generator:
            try:
                x, y, color_tuple = next(self.current_generator)
                self.canvas.put_pixel(x, y, QtGui.QColor(*color_tuple))
            except StopIteration:
                self.timer.stop()
            except Exception as e:
                print(f"Hiba futtatás közben: {e}")
                self.timer.stop()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())