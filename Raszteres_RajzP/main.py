import sys
import os
import importlib.util
from PyQt6 import QtWidgets, QtCore, QtGui


class Canvas(QtWidgets.QWidget):
    point_selected = QtCore.pyqtSignal(int, int, str)
    mouse_moved = QtCore.pyqtSignal(int, int)  # Élő koordináta jelzés

    def __init__(self):
        super().__init__()
        self.grid_size = (50, 50)
        self.pixels = {}
        self.setMinimumSize(500, 500)
        self.next_click_is_start = True
        self.marker_start = None
        self.marker_end = None
        self.setMouseTracking(True)  # Bekapcsoljuk az egérkövetést

    def set_grid_resolution(self, cols, rows):
        self.grid_size = (cols, rows)
        self.clear_canvas()

    def clear_canvas(self):
        self.pixels = {}
        self.marker_start = None
        self.marker_end = None
        self.next_click_is_start = True
        self.update()

    def put_pixel(self, x, y, color):
        if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
            self.pixels[(int(x), int(y))] = color
            self.update()

    def mouseMoveEvent(self, event):
        """Folyamatosan küldi a logikai rácskoordinátákat, ahogy mozog az egér."""
        cols, rows = self.grid_size
        cell_size = min(self.width() / cols, self.height() / rows)
        offset_x = (self.width() - (cols * cell_size)) / 2
        offset_y = (self.height() - (rows * cell_size)) / 2

        real_x = event.position().x() - offset_x
        real_y = event.position().y() - offset_y

        # Ha a rácson kívül van az egér, negatív értékeket küldünk
        if real_x < 0 or real_y < 0 or real_x >= (cols * cell_size) or real_y >= (rows * cell_size):
            self.mouse_moved.emit(-1, -1)
            return

        lx = int(real_x / cell_size)
        ly = int(real_y / cell_size)
        self.mouse_moved.emit(lx, ly)

    def mousePressEvent(self, event):
        cols, rows = self.grid_size

        cell_size = min(self.width() / cols, self.height() / rows)
        offset_x = (self.width() - (cols * cell_size)) / 2
        offset_y = (self.height() - (rows * cell_size)) / 2

        real_x = event.position().x() - offset_x
        real_y = event.position().y() - offset_y

        if real_x < 0 or real_y < 0 or real_x >= (cols * cell_size) or real_y >= (rows * cell_size):
            return

        lx = int(real_x / cell_size)
        ly = int(real_y / cell_size)

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

        # 1. Sötét munkaterület
        painter.fillRect(event.rect(), QtGui.QColor(45, 45, 45))

        # 2. Középre igazítás és cellaméret számítás
        cell_size = min(self.width() / cols, self.height() / rows)
        offset_x = (self.width() - (cols * cell_size)) / 2
        offset_y = (self.height() - (rows * cell_size)) / 2

        # 3. Fehér rajzlap
        painter.fillRect(QtCore.QRectF(offset_x, offset_y, cols * cell_size, rows * cell_size),
                         QtGui.QColor(255, 255, 255))

        # 4. Rácsok
        painter.setPen(QtGui.QColor(220, 220, 220))
        for i in range(cols + 1):
            x = offset_x + (i * cell_size)
            painter.drawLine(QtCore.QPointF(x, offset_y), QtCore.QPointF(x, offset_y + (rows * cell_size)))
        for j in range(rows + 1):
            y = offset_y + (j * cell_size)
            painter.drawLine(QtCore.QPointF(offset_x, y), QtCore.QPointF(offset_x + (cols * cell_size), y))

        # 5. Rajzadatok
        for (lx, ly), color in self.pixels.items():
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(
                QtCore.QRectF(offset_x + (lx * cell_size), offset_y + (ly * cell_size), cell_size, cell_size))

        # 6. UI Jelölők
        if self.marker_start:
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 0, 150)))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(QtCore.QRectF(offset_x + (self.marker_start[0] * cell_size),
                                           offset_y + (self.marker_start[1] * cell_size), cell_size, cell_size))

        if self.marker_end:
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 165, 0, 150)))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(
                QtCore.QRectF(offset_x + (self.marker_end[0] * cell_size), offset_y + (self.marker_end[1] * cell_size),
                              cell_size, cell_size))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raszteres Rajzoló Program")
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_step)
        self.current_generator = None
        self.all_plugins = []

        self.current_color = QtGui.QColor(30, 144, 255)

        self.init_ui()
        self.load_plugins()

    def init_ui(self):
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QHBoxLayout(main_widget)

        # --- BAL OLDALI SÁV ---
        sidebar = QtWidgets.QVBoxLayout()
        sidebar.setSpacing(10)

        # 1. DOBOZ
        group_coords = QtWidgets.QGroupBox("1. Pozíció és Rács")
        layout_coords = QtWidgets.QVBoxLayout()

        layout_coords.addWidget(QtWidgets.QLabel("Rács felbontás (X, Y):"))
        res_layout = QtWidgets.QHBoxLayout()
        self.res_x = QtWidgets.QSpinBox();
        self.res_x.setValue(50);
        self.res_x.setRange(1, 200)
        self.res_y = QtWidgets.QSpinBox();
        self.res_y.setValue(50);
        self.res_y.setRange(1, 200)
        res_layout.addWidget(self.res_x);
        res_layout.addWidget(self.res_y)
        layout_coords.addLayout(res_layout)

        layout_coords.addWidget(QtWidgets.QLabel("Kattintási koordináták:"))
        coord_layout = QtWidgets.QGridLayout()
        self.startX = QtWidgets.QSpinBox();
        self.startY = QtWidgets.QSpinBox()
        self.endX = QtWidgets.QSpinBox();
        self.endY = QtWidgets.QSpinBox()
        for sb in [self.startX, self.startY, self.endX, self.endY]: sb.setRange(0, 500)
        coord_layout.addWidget(QtWidgets.QLabel("Start:"), 0, 0)
        coord_layout.addWidget(self.startX, 0, 1);
        coord_layout.addWidget(self.startY, 0, 2)
        coord_layout.addWidget(QtWidgets.QLabel("Vége:"), 1, 0)
        coord_layout.addWidget(self.endX, 1, 1);
        coord_layout.addWidget(self.endY, 1, 2)
        layout_coords.addLayout(coord_layout)

        self.btn_reset_coords = QtWidgets.QPushButton("Koordináták nullázása (0, 0)")
        self.btn_reset_coords.setStyleSheet(
            "background-color: #f0ad4e; color: white; border-radius: 3px; padding: 4px;")
        self.btn_reset_coords.clicked.connect(self.reset_coords)
        layout_coords.addWidget(self.btn_reset_coords)

        group_coords.setLayout(layout_coords)
        sidebar.addWidget(group_coords)

        # 2. DOBOZ
        group_algo = QtWidgets.QGroupBox("2. Algoritmus Választás")
        layout_algo = QtWidgets.QVBoxLayout()

        radio_layout = QtWidgets.QHBoxLayout()
        self.radio_2d = QtWidgets.QRadioButton("2D")
        self.radio_3d = QtWidgets.QRadioButton("3D")
        self.radio_2d.setChecked(True)
        self.radio_2d.toggled.connect(self.filter_plugins)
        self.radio_3d.toggled.connect(self.filter_plugins)
        radio_layout.addWidget(self.radio_2d);
        radio_layout.addWidget(self.radio_3d)
        layout_algo.addLayout(radio_layout)

        self.algo_combo = QtWidgets.QComboBox()
        self.algo_combo.currentIndexChanged.connect(self.update_info_text)
        layout_algo.addWidget(self.algo_combo)

        self.info_box = QtWidgets.QTextBrowser()
        self.info_box.setMaximumHeight(100)
        self.info_box.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc; font-size: 11px;")
        layout_algo.addWidget(self.info_box)
        group_algo.setLayout(layout_algo)
        sidebar.addWidget(group_algo)

        # 3. DOBOZ
        group_render = QtWidgets.QGroupBox("3. Renderelési Beállítások")
        layout_render = QtWidgets.QVBoxLayout()

        color_layout = QtWidgets.QHBoxLayout()
        self.btn_color = QtWidgets.QPushButton()
        self.btn_color.setFixedSize(25, 25)
        self.btn_color.clicked.connect(self.choose_color)
        self.update_color_btn()

        self.check_override_color = QtWidgets.QCheckBox("Egyedi szín")
        self.check_override_color.setChecked(True)

        color_layout.addWidget(QtWidgets.QLabel("Rajzolás színe:"))
        color_layout.addWidget(self.btn_color)
        color_layout.addWidget(self.check_override_color)
        layout_render.addLayout(color_layout)

        layout_render.addWidget(QtWidgets.QLabel("Animáció sebessége (ms):"))
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 200);
        self.speed_slider.setValue(20)
        self.speed_slider.setInvertedAppearance(True)
        layout_render.addWidget(self.speed_slider)

        self.check_instant = QtWidgets.QCheckBox("Azonnali rajzolás (Nincs animáció)")
        layout_render.addWidget(self.check_instant)

        self.check_clear = QtWidgets.QCheckBox("Törlés indítás előtt")
        self.check_clear.setChecked(True)
        layout_render.addWidget(self.check_clear)

        group_render.setLayout(layout_render)
        sidebar.addWidget(group_render)

        # 4. DOBOZ: Műveletek (Súgókkal és Gyorsgombokkal)
        group_actions = QtWidgets.QGroupBox("4. Műveletek")
        layout_actions = QtWidgets.QVBoxLayout()

        self.btn_run = QtWidgets.QPushButton("Futtatás / Rajzolás")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.btn_run.setToolTip("Elindítja az algoritmus futtatását. (Gyorsgomb: Enter)")
        self.btn_run.setShortcut("Return")
        self.btn_run.clicked.connect(self.start_algorithm)
        layout_actions.addWidget(self.btn_run)

        self.btn_clear = QtWidgets.QPushButton("Vászon ürítése")
        self.btn_clear.setToolTip("Letörli a rajzokat és nullázza a kattintásokat. (Gyorsgomb: Delete)")
        self.btn_clear.setShortcut("Delete")
        self.btn_clear.clicked.connect(self.clear_canvas)
        layout_actions.addWidget(self.btn_clear)

        self.btn_save = QtWidgets.QPushButton("Kép mentése (PNG)")
        self.btn_save.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        self.btn_save.setToolTip("Kimenti az aktuális rajzot egy képfájlba. (Gyorsgomb: Ctrl+S)")
        self.btn_save.setShortcut("Ctrl+S")
        self.btn_save.clicked.connect(self.save_image)
        layout_actions.addWidget(self.btn_save)

        group_actions.setLayout(layout_actions)
        sidebar.addWidget(group_actions)

        sidebar.addStretch()

        # Élő koordináta kijelző
        self.status_label = QtWidgets.QLabel("Egér pozíció: -")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        sidebar.addWidget(self.status_label)

        layout.addLayout(sidebar, 1)

        # --- JOBB OLDALI SÁV ---
        self.canvas = Canvas()
        self.canvas.point_selected.connect(self.update_coords)
        self.canvas.mouse_moved.connect(self.update_live_coords)  # Rákötjük az egeret
        layout.addWidget(self.canvas, 4)

    def update_live_coords(self, x, y):
        if x == -1 and y == -1:
            self.status_label.setText("Egér pozíció: (Kívül)")
        else:
            self.status_label.setText(f"Egér pozíció: X: {x}, Y: {y}")

    def reset_coords(self):
        self.startX.setValue(0);
        self.startY.setValue(0)
        self.endX.setValue(0);
        self.endY.setValue(0)
        self.canvas.marker_start = None
        self.canvas.marker_end = None
        self.canvas.next_click_is_start = True
        self.canvas.update()

    def choose_color(self):
        color = QtWidgets.QColorDialog.getColor(self.current_color, self, "Színválasztás")
        if color.isValid():
            self.current_color = color
            self.update_color_btn()
            self.check_override_color.setChecked(True)

    def update_color_btn(self):
        self.btn_color.setStyleSheet(
            f"background-color: {self.current_color.name()}; border: 1px solid gray; border-radius: 3px;")

    def save_image(self):
        pixmap = self.canvas.grab()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Kép mentése", "render_kimenet.png",
                                                        "PNG Kép (*.png);;Minden fájl (*)")
        if path:
            pixmap.save(path)

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
                try:
                    spec = importlib.util.spec_from_file_location(f[:-3], f"plugins/{f}")
                    m = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(m)
                    if hasattr(m, "NEV"):
                        self.all_plugins.append({"name": m.NEV, "type": getattr(m, 'TIPUS', '2D'), "module": m})
                except Exception as e:
                    print(f"Hiba a plugin betöltésekor ({f}): {e}")
        self.filter_plugins()

    def filter_plugins(self):
        self.algo_combo.clear()
        target_type = "2D" if self.radio_2d.isChecked() else "3D"
        for p in self.all_plugins:
            if p["type"] == target_type:
                self.algo_combo.addItem(p["name"], p["module"])
        self.update_info_text()

    def update_info_text(self):
        algo_module = self.algo_combo.currentData()
        if algo_module and hasattr(algo_module, "LEIRAS"):
            self.info_box.setText(algo_module.LEIRAS)
        else:
            self.info_box.setText("<i>Nincs leírás megadva ehhez az algoritmushoz.</i>")

    def clear_canvas(self):
        self.timer.stop()
        uj_x = self.res_x.value()
        uj_y = self.res_y.value()
        self.canvas.set_grid_resolution(uj_x, uj_y)

    def start_algorithm(self):
        if self.check_clear.isChecked(): self.clear_canvas()

        self.canvas.grid_size = (self.res_x.value(), self.res_y.value())
        algo_module = self.algo_combo.currentData()

        if algo_module:
            p1 = (self.startX.value(), self.startY.value())
            p2 = (self.endX.value(), self.endY.value())
            algo_module.PIXELS = self.canvas.pixels

            self.current_generator = algo_module.futtat(self.res_x.value(), self.res_y.value(), p1, p2)

            if self.check_instant.isChecked():
                for x, y, orig_color in self.current_generator:
                    final_color = self.current_color if self.check_override_color.isChecked() else QtGui.QColor(
                        *orig_color)
                    if 0 <= x < self.canvas.grid_size[0] and 0 <= y < self.canvas.grid_size[1]:
                        self.canvas.pixels[(int(x), int(y))] = final_color
                self.canvas.update()
            else:
                self.timer.start(self.speed_slider.value())

    def next_step(self):
        if self.current_generator:
            try:
                x, y, orig_color = next(self.current_generator)
                final_color = self.current_color if self.check_override_color.isChecked() else QtGui.QColor(*orig_color)
                self.canvas.put_pixel(x, y, final_color)
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