import sys
import os
import json
import importlib.util
from PyQt6 import QtWidgets, QtCore, QtGui


class Canvas(QtWidgets.QWidget):
    point_selected = QtCore.pyqtSignal(int, int, str)
    mouse_moved = QtCore.pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.grid_size = (50, 50)
        self.pixels = {}
        self.setMinimumSize(500, 500)

        # Kattintás állapotok
        self.next_click_is_start = True
        self.marker_start = None
        self.marker_end = None
        self.setMouseTracking(True)

        # --- ÚJ: KAMERA ÉS PÁSZTÁZÁS ---
        self.zoom = 15.0  # Kezdeti cellaméret (15 pixel)
        self.camera_x = 0.0  # Kamera X eltolása
        self.camera_y = 0.0  # Kamera Y eltolása
        self.is_panning = False  # Épp húzzuk-e a vásznat?
        self.last_mouse_pos = None

    def set_grid_resolution(self, cols, rows):
        self.grid_size = (cols, rows)
        self.clear_canvas()

    def clear_canvas(self):
        self.pixels = {}
        self.marker_start = None
        self.marker_end = None
        self.next_click_is_start = True

        # Kamera középre állítása törléskor
        cols, rows = self.grid_size
        self.camera_x = ((cols * self.zoom) - self.width()) / 2
        self.camera_y = ((rows * self.zoom) - self.height()) / 2
        self.update()

    def put_pixel(self, x, y, color):
        if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
            self.pixels[(int(x), int(y))] = color
            self.update()

    # --- KOORDINÁTA KONVERTEREK ---
    def screen_to_grid(self, sx, sy):
        """Képernyő pixel -> Logikai rács koordináta"""
        lx = int((sx + self.camera_x) / self.zoom)
        ly = int((sy + self.camera_y) / self.zoom)
        return lx, ly

    def grid_to_screen(self, lx, ly):
        """Logikai rács koordináta -> Képernyő pixel"""
        sx = (lx * self.zoom) - self.camera_x
        sy = (ly * self.zoom) - self.camera_y
        return sx, sy

    # --- EGÉR ESEMÉNYEK (Nagyítás és Mozgás) ---
    def wheelEvent(self, event):
        """Egérgörgő a Zoomoláshoz (Kurzorhoz fókuszálva)"""
        old_zoom = self.zoom
        # Zoom mértéke (+10% vagy -10%)
        if event.angleDelta().y() > 0:
            self.zoom = min(100.0, self.zoom * 1.1)
        else:
            self.zoom = max(2.0, self.zoom / 1.1)

        # Hogy a kurzor alatt maradjon a rács (okos zoom)
        mouse_x = event.position().x()
        mouse_y = event.position().y()
        self.camera_x = (mouse_x + self.camera_x) * (self.zoom / old_zoom) - mouse_x
        self.camera_y = (mouse_y + self.camera_y) * (self.zoom / old_zoom) - mouse_y

        self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton or event.button() == QtCore.Qt.MouseButton.MiddleButton:
            # Jobb klikk vagy Görögő gomb: Pásztázás kezdete
            self.is_panning = True
            self.last_mouse_pos = event.position()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

        elif event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Bal klikk: Rajzolás/Pont lerakása
            cols, rows = self.grid_size
            lx, ly = self.screen_to_grid(event.position().x(), event.position().y())

            if 0 <= lx < cols and 0 <= ly < rows:
                tipus = "start" if self.next_click_is_start else "end"
                self.point_selected.emit(lx, ly, tipus)
                if self.next_click_is_start:
                    self.marker_start = (lx, ly)
                else:
                    self.marker_end = (lx, ly)
                self.next_click_is_start = not self.next_click_is_start
                self.update()

    def mouseMoveEvent(self, event):
        if self.is_panning:
            # Kamera mozgatása
            delta = event.position() - self.last_mouse_pos
            self.camera_x -= delta.x()
            self.camera_y -= delta.y()
            self.last_mouse_pos = event.position()
            self.update()
        else:
            # Élő koordináta frissítése mozgáskor
            cols, rows = self.grid_size
            lx, ly = self.screen_to_grid(event.position().x(), event.position().y())
            if 0 <= lx < cols and 0 <= ly < rows:
                self.mouse_moved.emit(lx, ly)
            else:
                self.mouse_moved.emit(-1, -1)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton or event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    # --- RAJZOLÁS ÉS MINIMAP ---
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        cols, rows = self.grid_size

        # 1. Háttér sötétre festése (munkaterület)
        painter.fillRect(event.rect(), QtGui.QColor(40, 40, 40))

        # 2. Fehér "Papírlap" megrajzolása a kamerához igazítva
        papir_x, papir_y = self.grid_to_screen(0, 0)
        papir_w = cols * self.zoom
        papir_h = rows * self.zoom
        painter.fillRect(QtCore.QRectF(papir_x, papir_y, papir_w, papir_h), QtGui.QColor(255, 255, 255))

        # 3. Rácsok megrajzolása (Kizárólag azokat rajzoljuk, amik a papíron vannak)
        painter.setPen(QtGui.QColor(220, 220, 220))
        for i in range(cols + 1):
            x = papir_x + (i * self.zoom)
            painter.drawLine(QtCore.QPointF(x, papir_y), QtCore.QPointF(x, papir_y + papir_h))
        for j in range(rows + 1):
            y = papir_y + (j * self.zoom)
            painter.drawLine(QtCore.QPointF(papir_x, y), QtCore.QPointF(papir_x + papir_w, y))

        # 4. Kiszámolt pixelek
        for (lx, ly), color in self.pixels.items():
            sx, sy = self.grid_to_screen(lx, ly)
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(QtCore.QRectF(sx, sy, self.zoom, self.zoom))

        # 5. UI Jelölők (Sárga és Narancs pöttyök)
        if self.marker_start:
            sx, sy = self.grid_to_screen(self.marker_start[0], self.marker_start[1])
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 0, 150)))
            painter.drawRect(QtCore.QRectF(sx, sy, self.zoom, self.zoom))

        if self.marker_end:
            sx, sy = self.grid_to_screen(self.marker_end[0], self.marker_end[1])
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 165, 0, 150)))
            painter.drawRect(QtCore.QRectF(sx, sy, self.zoom, self.zoom))

        # ==========================================
        # 6. MINIMAP (Pásztázó ablak) RAJZOLÁSA
        # ==========================================
        mm_size = 150  # Minimap mérete pixelben
        mm_margin = 20  # Margó a képernyő szélétől
        mm_x = self.width() - mm_size - mm_margin
        mm_y = mm_margin

        # Minimap háttere
        painter.fillRect(QtCore.QRectF(mm_x, mm_y, mm_size, mm_size), QtGui.QColor(30, 30, 30, 200))
        painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100), 1))
        painter.drawRect(QtCore.QRectF(mm_x, mm_y, mm_size, mm_size))

        # Skálázás kiszámítása a minimaphoz
        mm_scale = min(mm_size / cols, mm_size / rows)
        mm_w = cols * mm_scale
        mm_h = rows * mm_scale
        mm_offset_x = mm_x + (mm_size - mm_w) / 2
        mm_offset_y = mm_y + (mm_size - mm_h) / 2

        # A "papír" a minimapon
        painter.fillRect(QtCore.QRectF(mm_offset_x, mm_offset_y, mm_w, mm_h), QtGui.QColor(255, 255, 255, 150))

        # Pixelek a minimapon (nagyon piciben)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        for (lx, ly), color in self.pixels.items():
            painter.setBrush(QtGui.QBrush(color))
            painter.drawRect(
                QtCore.QRectF(mm_offset_x + (lx * mm_scale), mm_offset_y + (ly * mm_scale), mm_scale, mm_scale))

        # KÉPERNYŐ (KAMERA) KERETE A MINIMAPON (Piros keret)
        vx = mm_offset_x + (self.camera_x / self.zoom) * mm_scale
        vy = mm_offset_y + (self.camera_y / self.zoom) * mm_scale
        vw = (self.width() / self.zoom) * mm_scale
        vh = (self.height() / self.zoom) * mm_scale

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 50, 50), 2))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRect(QtCore.QRectF(vx, vy, vw, vh))

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

        # --- ÚJ: QGridLayout a táblázatos (2 oszlopos) elrendezéshez ---
        layout_actions = QtWidgets.QGridLayout()
        layout_actions.setSpacing(5)  # Egy kis térköz a gombok közé

        # --- ELSŐ SOR ---
        self.btn_run = QtWidgets.QPushButton("Futtatás / Rajzolás")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.btn_run.setToolTip("Elindítja az algoritmus futtatását. (Gyorsgomb: Enter)")
        self.btn_run.setShortcut("Return")
        self.btn_run.clicked.connect(self.start_algorithm)
        layout_actions.addWidget(self.btn_run, 0, 0)  # Sor 0, Oszlop 0

        self.btn_clear = QtWidgets.QPushButton("Vászon ürítése")
        self.btn_clear.setStyleSheet("padding: 8px;")  # Hogy ugyanolyan magas legyen, mint a futtatás
        self.btn_clear.setToolTip("Letörli a rajzokat és nullázza a kattintásokat. (Gyorsgomb: Delete)")
        self.btn_clear.setShortcut("Delete")
        self.btn_clear.clicked.connect(self.clear_canvas)
        layout_actions.addWidget(self.btn_clear, 0, 1)  # Sor 0, Oszlop 1

        # --- MÁSODIK SOR ---
        self.btn_save_proj = QtWidgets.QPushButton("Projekt mentése")
        self.btn_save_proj.setStyleSheet("background-color: #9C27B0; color: white; padding: 8px;")
        self.btn_save_proj.setToolTip("Elmenti a teljes rácsot, beállításokat és pixeleket.")
        self.btn_save_proj.clicked.connect(self.save_project)
        layout_actions.addWidget(self.btn_save_proj, 1, 0)  # Sor 1, Oszlop 0

        self.btn_load_proj = QtWidgets.QPushButton("Projekt betöltése")
        self.btn_load_proj.setStyleSheet("background-color: #673AB7; color: white; padding: 8px;")
        self.btn_load_proj.setToolTip("Betölt egy korábban elmentett munkát.")
        self.btn_load_proj.clicked.connect(self.load_project)
        layout_actions.addWidget(self.btn_load_proj, 1, 1)  # Sor 1, Oszlop 1

        # --- HARMADIK SOR ---
        # A Kép mentése gombot középre, alulra tesszük, úgy hogy átíveljen mindkét oszlopon
        self.btn_save = QtWidgets.QPushButton("Kép mentése (PNG)")
        self.btn_save.setStyleSheet("background-color: #2196F3; color: white; padding: 6px;")
        self.btn_save.setToolTip("Kimenti az aktuális rajzot egy képfájlba. (Gyorsgomb: Ctrl+S)")
        self.btn_save.setShortcut("Ctrl+S")
        self.btn_save.clicked.connect(self.save_image)
        # Érdekesség: A 2, 0, 1, 2 jelentése: 2. sor, 0. oszlop, de 1 sor magas és 2 oszlop széles legyen!
        layout_actions.addWidget(self.btn_save, 2, 0, 1, 2)

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

    def save_project(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Projekt mentése", "projekt.json", "JSON Fájl (*.json)")
        if not path:
            return

        # 1. Pixelek átalakítása (Szerializáció)
        # A Python dictionary-t (tuple kulcsokkal) nem érti a JSON, ezért átalakítjuk listává
        pixels_data = []
        for (x, y), color in self.canvas.pixels.items():
            pixels_data.append({
                "x": x,
                "y": y,
                "color": color.name()  # Hexadecimális kód, pl. #FF0000
            })

        # 2. A teljes állapot (State) becsomagolása
        project_data = {
            "grid_x": self.res_x.value(),
            "grid_y": self.res_y.value(),
            "start_x": self.startX.value(),
            "start_y": self.startY.value(),
            "end_x": self.endX.value(),
            "end_y": self.endY.value(),
            "algorithm": self.algo_combo.currentText(),  # Mentjük a plugin nevét is!
            "pixels": pixels_data
        }

        # 3. Kiírás fájlba
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=4, ensure_ascii=False)
            QtWidgets.QMessageBox.information(self, "Siker", "Projekt sikeresen elmentve!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hiba", f"Nem sikerült menteni:\n{e}")

    def load_project(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Projekt betöltése", "", "JSON Fájl (*.json)")
        if not path:
            return

        try:
            # 1. JSON beolvasása (Deszerializáció)
            with open(path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # 2. UI elemek értékének visszaállítása
            self.res_x.setValue(project_data.get("grid_x", 50))
            self.res_y.setValue(project_data.get("grid_y", 50))
            self.startX.setValue(project_data.get("start_x", 0))
            self.startY.setValue(project_data.get("start_y", 0))
            self.endX.setValue(project_data.get("end_x", 0))
            self.endY.setValue(project_data.get("end_y", 0))

            # Algoritmus (Plugin) kiválasztása a legördülőből
            algo_name = project_data.get("algorithm", "")
            index = self.algo_combo.findText(algo_name)
            if index >= 0:
                self.algo_combo.setCurrentIndex(index)

            # 3. Rács és Vászon (Canvas) felépítése az új mérettel
            self.canvas.set_grid_resolution(self.res_x.value(), self.res_y.value())

            # 4. Pixelek visszatöltése
            loaded_pixels = {}
            for p in project_data.get("pixels", []):
                # Visszaalakítjuk a HEX stringet QColor objektummá és a tuple kulcsot
                loaded_pixels[(p["x"], p["y"])] = QtGui.QColor(p["color"])

            self.canvas.pixels = loaded_pixels
            self.canvas.update()

            QtWidgets.QMessageBox.information(self, "Siker", "Projekt sikeresen betöltve!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hiba", f"Nem sikerült betölteni a fájlt:\n{e}")


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