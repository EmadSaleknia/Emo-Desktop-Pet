import time
import random
import os
import psutil
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QApplication
from PyQt5.QtCore import Qt, QTimer
from pynput import keyboard, mouse
from renderers import EmoRenderer
from PyQt5.QtGui import QColor
from send2trash import send2trash

class PetEngine(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 200, 220) 
        
        self.setAcceptDrops(True) 
        
        self.renderer = EmoRenderer()
        
        self.state = "idle" 
        self.last_state_tracker = "idle"
        self.state_time = 0.0 
        
        self.last_activity_time = time.time()
        self.poke_count = 0
        self.last_poke_time = 0
        self.cpu_usage = 0
        self.time_counter = 0.0
        self.base_color = QColor(0, 255, 255) 
        
        self.screen_rect = QApplication.primaryScreen().geometry()
        self.direction = 1 
        self.drag_position = None
        
        self.state_timer = QTimer()
        self.state_timer.setSingleShot(True)
        self.state_timer.timeout.connect(self.reset_to_idle)
        
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(30)

        self.cpu_timer = QTimer()
        self.cpu_timer.timeout.connect(self.update_cpu)
        self.cpu_timer.start(2000)

        self.action_timer = QTimer()
        self.action_timer.timeout.connect(self.random_ai)
        self.action_timer.start(2500) 

        self.key_listener = keyboard.Listener(on_press=self.on_press)
        self.key_listener.start()
        
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
        self.mouse_listener.start()

        self.move_to_corner()

    def move_to_corner(self):
        self.move(self.screen_rect.width() - 250, self.screen_rect.height() - 280)

    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_eaten = False
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    
                    file_path = os.path.normpath(file_path)
                    
                    if os.path.exists(file_path):
                        try:
                            send2trash(file_path) 
                            file_eaten = True
                        except Exception as e:
                            print(f"Error eating file: {e}")
            
            if file_eaten:
                self.state = "eating"
                self.state_timer.stop()
                self.wake_up(force=True)
                self.state_timer.start(4000) 
            
        event.accept()

    def register_click(self):
        if self.state == "trip":
            return
            
        current_time = time.time()
        if current_time - self.last_poke_time < 0.6:
            self.poke_count += 1
        else:
            self.poke_count = 1
        self.last_poke_time = current_time

        if self.poke_count >= 4:
            self.state = "trip"
            self.last_state_tracker = "" 
            self.poke_count = 0 
            self.state_timer.start(4000) 
        elif self.poke_count == 2:
            self.state = "love"
            self.wake_up(force=True)
            self.state_timer.start(3000)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.register_click()
            event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.state == "trip":
                event.accept()
                return

            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.wake_up(force=True)
            
            if "roam" in self.state:
                self.state = "idle"
                
            self.register_click()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            self.wake_up(force=True)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            if self.state == "typing":
                self.state = "idle"
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #222; color: #0ff; border: 1px solid #0ff; border-radius: 5px; } QMenu::item:selected { background-color: #444; }")
        color_action = QAction("color", self)
        color_action.triggered.connect(self.change_color)
        menu.addAction(color_action)
        menu.addSeparator()
        exit_action = QAction("shut down", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_action)
        menu.exec_(event.globalPos())
        
    def change_color(self):
        colors = [QColor(0, 255, 255), QColor(255, 50, 255), QColor(50, 255, 50), QColor(255, 200, 0)]
        self.base_color = random.choice([c for c in colors if c != self.base_color])
        self.wake_up(force=True)

    def on_press(self, key):
        self.state = "typing"
        self.state_timer.stop() 
        self.poke_count = 0
        self.wake_up()

    def on_mouse_move(self, x, y):
        if time.time() - self.last_activity_time > 1.0:
            self.wake_up()

    def on_mouse_click(self, x, y, button, pressed):
        self.wake_up()

    def wake_up(self, force=False):
        self.last_activity_time = time.time()
        if self.state == "sleeping" or (force and self.state not in ["idle", "typing", "roam_left", "roam_right", "trip", "love", "eating"]):
            self.state = "idle"
            self.state_timer.stop()

    def random_ai(self):
        if self.cpu_usage > 70 or self.drag_position is not None or self.state == "eating":
            return
            
        if self.state in ["idle", "roam_left", "roam_right"]:
            actions = [
                "roam_left", "roam_right", "roam_left", "roam_right", 
                "reading", "rubik", "playing", "happy"
            ]
            
            rand_val = random.random()
            if rand_val < 0.02: 
                self.state = "cold"
                self.state_timer.start(8000)
            elif rand_val < 0.03: 
                self.state = "sad"
                self.state_timer.start(8000)
            elif rand_val < 0.10: 
                self.state = "clean"
                self.state_timer.start(6000)
            elif rand_val < 0.13: 
                self.state = "disco"
                self.state_timer.start(6000)
            else:
                self.state = random.choice(actions)
                
                if "left" in self.state:
                    self.direction = -1
                elif "right" in self.state:
                    self.direction = 1

                if self.state in ["reading", "rubik", "playing", "happy"]:
                    self.state_timer.start(10000) 

    def reset_to_idle(self):
        if self.state not in ["sleeping", "roam_left", "roam_right"]:
            self.state = "idle"
            self.state_timer.stop()

    def update_physics(self):
        if self.drag_position is not None:
            return
            
        speed = 0
        if "roam" in self.state:
            speed = 1.8 * self.direction 
            
        if speed != 0:
            new_x = self.x() + speed
            max_x = self.screen_rect.width() - self.width()
            
            if new_x <= 0:
                new_x = 0
                self.direction = 1
                self.state = self.state.replace("left", "right")
            elif new_x >= max_x:
                new_x = max_x
                self.direction = -1
                self.state = self.state.replace("right", "left")
                
            self.move(int(new_x), self.y())

    def update_animation(self):
        current_time = time.time()
        
        if self.state != self.last_state_tracker:
            self.state_time = 0.0
            self.last_state_tracker = self.state
        self.state_time += 0.03
        
        self.update_physics()
            
        if self.state == "typing" and current_time - self.last_activity_time > 0.3:
            self.state = "idle"

        if current_time - self.last_activity_time > 60 and self.cpu_usage <= 70 and self.state == "idle":
            self.state = "sleeping"

        self.time_counter += 0.05 if self.state == "sleeping" else 0.15
        self.update()

    def update_cpu(self):
        self.cpu_usage = psutil.cpu_percent()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        self.renderer.draw(
            painter, self.width()/2, self.height()/2, 
            self.state, self.time_counter, self.cpu_usage, self.base_color, self.direction, self.state_time
        )