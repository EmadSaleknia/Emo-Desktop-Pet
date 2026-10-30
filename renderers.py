import math
import random
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QBrush, QPainterPath

class EmoRenderer:
    def draw(self, painter, cx, cy, state, time_counter, cpu_usage, base_color, direction, state_time):
        painter.save()
        if direction == -1: 
            painter.translate(cx, cy)
            painter.scale(-1, 1)
            painter.translate(-cx, -cy)

        is_disco = (state == "disco")
        
        is_tripping = (state == "trip")
        is_falling = (is_tripping and state_time >= 1.5)
        
        if is_falling:
            painter.translate(cx, cy + 40)
            painter.rotate(85)
            painter.translate(-cx, -(cy + 40))
            cy += 15
        
        waddle_tilt = 0
        leg_l_y, leg_r_y = 0, 0
        breathe_y = 0
        
        if is_tripping and not is_falling:
            waddle_tilt = math.sin(time_counter * 10) * 8 
            leg_l_y = 15
            cy -= 5
        elif "roam" in state:
            waddle_tilt = math.sin(time_counter * 5) * 8
            leg_l_y = max(0, math.sin(time_counter * 5) * 12)
            leg_r_y = max(0, -math.sin(time_counter * 5) * 12)
        elif is_disco:
            breathe_y = math.sin(time_counter * 4) * 3 
            waddle_tilt = math.sin(time_counter * 2) * 3
        else:
            breathe_y = math.sin(time_counter) * (1 if state == "sleeping" else 2)
            
        cy += breathe_y

        eye_color = base_color
        shake_x = 0
        
        if state == "angry" or cpu_usage > 75:
            eye_color = QColor(255, 50, 50) 
            shake_x = random.randint(-1, 1)
        elif state == "happy":
            eye_color = QColor(50, 255, 50) 
        elif state == "cold":
            eye_color = QColor(150, 200, 255) 
        elif is_tripping and not is_falling:
            shake_x = random.randint(-1, 1) 
        elif is_disco:
            disco_colors = [QColor(255, 50, 50), QColor(50, 255, 50), QColor(50, 100, 255), QColor(255, 255, 50)]
            eye_color = disco_colors[int(time_counter * 1.5) % len(disco_colors)]

        painter.setBrush(QBrush(QColor(30, 30, 32)))
        painter.setPen(Qt.NoPen)
        
        painter.drawRoundedRect(int(cx - 35), int(cy + 45 - leg_l_y), 30, 20, 6, 6)
        painter.setPen(QPen(QColor(100, 50, 150), 2)) 
        painter.drawLine(int(cx - 25), int(cy + 60 - leg_l_y), int(cx - 15), int(cy + 60 - leg_l_y))
        
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(int(cx + 5), int(cy + 45 - leg_r_y), 30, 20, 6, 6)
        painter.setPen(QPen(QColor(100, 50, 150), 2))
        painter.drawLine(int(cx + 15), int(cy + 60 - leg_r_y), int(cx + 25), int(cy + 60 - leg_r_y))
        
        painter.setPen(Qt.NoPen)
        painter.drawRect(int(cx - 25), int(cy + 15 - leg_l_y), 14, 35)
        painter.drawRect(int(cx + 11), int(cy + 15 - leg_r_y), 14, 35)

        painter.translate(cx, cy + 15)
        painter.rotate(waddle_tilt)
        painter.translate(-cx, -(cy + 15))
        cx += shake_x

        painter.setPen(QPen(QColor(60, 50, 100), 8, Qt.SolidLine, Qt.RoundCap))
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(int(cx - 52), int(cy - 75), 104, 100, 0, 180 * 16)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(60, 50, 100))) 
        painter.drawRoundedRect(int(cx - 60), int(cy - 40), 15, 45, 7, 7)
        painter.drawRoundedRect(int(cx + 45), int(cy - 40), 15, 45, 7, 7)
        
        painter.setPen(QPen(eye_color, 2))
        painter.drawLine(int(cx - 52), int(cy - 30), int(cx - 52), int(cy - 5))
        painter.drawLine(int(cx + 52), int(cy - 30), int(cx + 52), int(cy - 5))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(40, 40, 45)))
        painter.drawRoundedRect(int(cx - 48), int(cy - 65), 96, 85, 30, 30)
        painter.setBrush(QBrush(QColor(180, 180, 190)))
        painter.drawRoundedRect(int(cx - 44), int(cy - 61), 88, 77, 26, 26)
        painter.setBrush(QBrush(QColor(15, 15, 15)))
        painter.drawRoundedRect(int(cx - 40), int(cy - 57), 80, 69, 22, 22)
        painter.setBrush(QBrush(QColor(5, 5, 5)))
        painter.drawEllipse(int(cx - 3), int(cy - 52), 6, 6)

        painter.setPen(Qt.NoPen)

        if state == "sleeping":
            painter.setPen(QPen(eye_color, 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(int(cx - 22), int(cy - 25), int(cx - 10), int(cy - 25))
            painter.drawLine(int(cx + 10), int(cy - 25), int(cx + 22), int(cy - 25))
            painter.setPen(Qt.NoPen)
            font = painter.font()
            font.setPixelSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(eye_color.red(), eye_color.green(), eye_color.blue(), 180))
            painter.drawText(int(cx + 10), int(cy - 35 - (time_counter*10)%15), "Z")
            
        elif state == "love":
            pulse = 1.0 + math.sin(time_counter * 8) * 0.2
            size = 10 * pulse
            painter.setBrush(QBrush(QColor(255, 50, 100))) 
            
            def draw_heart(hx, hy):
                path = QPainterPath()
                path.moveTo(hx, hy)
                path.cubicTo(hx - size*1.2, hy - size*1.2, hx - size*1.5, hy + size*0.5, hx, hy + size*1.5)
                path.cubicTo(hx + size*1.5, hy + size*0.5, hx + size*1.2, hy - size*1.2, hx, hy)
                painter.drawPath(path)
                
            draw_heart(cx - 17, cy - 35)
            draw_heart(cx + 17, cy - 35)
            
        elif state == "eating":
            painter.setPen(QPen(eye_color, 4, Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(int(cx - 26), int(cy - 40), 20, 15, 0, 180 * 16)
            painter.drawArc(int(cx + 6), int(cy - 40), 20, 15, 0, 180 * 16)
            
            feed_y = math.sin(time_counter * 15) * 3 
            file_y = cy - 12 + feed_y
            
            painter.setBrush(QBrush(QColor(240, 240, 240)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(cx - 10), int(file_y), 20, 16, 2, 2)
            painter.setPen(QPen(QColor(150, 150, 150), 2))
            painter.drawLine(int(cx - 5), int(file_y + 5), int(cx + 5), int(file_y + 5))
            painter.drawLine(int(cx - 5), int(file_y + 10), int(cx + 5), int(file_y + 10))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(eye_color))
            painter.drawEllipse(int(cx - 15), int(file_y + 4), 8, 8)
            painter.drawEllipse(int(cx + 7), int(file_y + 4), 8, 8)

            chew_h = abs(math.sin(time_counter * 40)) * 14
            chew_w = 22 + abs(math.cos(time_counter * 40)) * 8
            painter.drawRoundedRect(int(cx - chew_w/2), int(cy - 24 - chew_h/2), int(chew_w), int(4 + chew_h), 4, 4)

        elif state == "clean":
            painter.setPen(QPen(eye_color, 4, Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(int(cx - 26), int(cy - 35), 20, 15, 0, 180 * 16)
            painter.drawArc(int(cx + 6), int(cy - 35), 20, 15, 0, 180 * 16)
            
            painter.setPen(Qt.NoPen)
            for i in range(4):
                bx = cx - 25 + i * 16
                by = cy - 45 + (i%2)*15
                bubble_scale = abs(math.sin(time_counter * 3 + i))
                painter.setBrush(QBrush(QColor(200, 240, 255, int(150 * bubble_scale))))
                painter.drawEllipse(int(bx), int(by), int(4 + 3*bubble_scale), int(4 + 3*bubble_scale))
                
            wiper_x = math.sin(time_counter * 3.5) * 20
            
            painter.save()
            painter.translate(cx + wiper_x, cy - 20)
            
            painter.setPen(QPen(QColor(60, 60, 60), 4, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(0, -4, 0, 18)
            painter.setPen(QPen(QColor(200, 200, 200), 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(-14, -4, 14, -4)
            painter.setPen(QPen(QColor(0, 200, 255), 4, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(-14, -8, 14, -8)
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(eye_color))
            painter.drawEllipse(-6, 12, 12, 12)
            painter.restore()
                
        elif state == "trip":
            if is_falling:
                painter.setPen(QPen(eye_color, 4, Qt.SolidLine, Qt.RoundCap))
                painter.drawLine(int(cx - 25), int(cy - 35), int(cx - 15), int(cy - 25))
                painter.drawLine(int(cx - 25), int(cy - 25), int(cx - 15), int(cy - 35))
                painter.drawLine(int(cx + 10), int(cy - 35), int(cx + 20), int(cy - 25))
                painter.drawLine(int(cx + 10), int(cy - 25), int(cx + 20), int(cy - 35))
            else:
                painter.setBrush(QBrush(eye_color))
                painter.drawEllipse(int(cx - 26), int(cy - 35), 18, 18)
                painter.drawEllipse(int(cx + 8), int(cy - 35), 18, 18)
                
        elif state == "cold":
            painter.setBrush(QBrush(eye_color))
            painter.drawRoundedRect(int(cx - 28), int(cy - 25), 22, 10, 4, 4)
            painter.drawRoundedRect(int(cx + 6), int(cy - 25), 22, 10, 4, 4)
            
            tissue_y = cy - 10 + math.sin(time_counter * 2) * 3
            painter.setBrush(QBrush(QColor(240, 240, 240)))
            painter.drawRoundedRect(int(cx - 15), int(tissue_y), 30, 15, 5, 5)
            painter.setBrush(QBrush(eye_color))
            painter.drawEllipse(int(cx - 20), int(tissue_y + 5), 8, 8)
            painter.drawEllipse(int(cx + 12), int(tissue_y + 5), 8, 8)
            
        elif state == "sad":
            painter.setPen(QPen(eye_color, 6, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(int(cx - 28), int(cy - 25), int(cx - 10), int(cy - 35))
            painter.drawLine(int(cx + 10), int(cy - 35), int(cx + 28), int(cy - 25))
            
            tear_y = cy - 20 + (time_counter * 15) % 25
            tear_alpha = max(0, 255 - int(((time_counter * 15) % 25) * 10))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(0, 200, 255, tear_alpha)))
            painter.drawEllipse(int(cx - 20), int(tear_y), 4, 6)
            
        elif state == "happy":
            painter.setPen(QPen(eye_color, 4, Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(int(cx - 26), int(cy - 35), 20, 15, 0, 180 * 16)
            painter.drawArc(int(cx + 6), int(cy - 35), 20, 15, 0, 180 * 16)
            
        elif state == "angry" or cpu_usage > 75:
            painter.setPen(QPen(eye_color, 6, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(int(cx - 25), int(cy - 35), int(cx - 10), int(cy - 20))
            painter.drawLine(int(cx + 10), int(cy - 20), int(cx + 25), int(cy - 35))
            
        elif state == "reading":
            painter.setBrush(QBrush(eye_color))
            painter.drawRoundedRect(int(cx - 28), int(cy - 30), 22, 12, 4, 4)
            painter.drawRoundedRect(int(cx + 6), int(cy - 30), 22, 12, 4, 4)
            
            painter.setPen(QPen(eye_color, 2, Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            book_y = cy - 8
            path = QPainterPath()
            path.moveTo(cx - 20, book_y - 4)
            path.lineTo(cx, book_y)
            path.lineTo(cx + 20, book_y - 4)
            path.lineTo(cx + 15, book_y + 12)
            path.lineTo(cx, book_y + 15)
            path.lineTo(cx - 15, book_y + 12)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawLine(int(cx), int(book_y), int(cx), int(book_y + 15))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(eye_color))
            painter.drawEllipse(int(cx - 22), int(book_y + 6), 7, 7)
            painter.drawEllipse(int(cx + 15), int(book_y + 6), 7, 7)
            
        elif state == "playing":
            painter.setBrush(QBrush(eye_color))
            painter.drawRoundedRect(int(cx - 28), int(cy - 40), 22, 22, 6, 6)
            painter.drawRoundedRect(int(cx + 6), int(cy - 35), 22, 16, 5, 5) 
            
            pad_y = cy - 8
            painter.setPen(QPen(eye_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(int(cx - 18), int(pad_y), 36, 12, 5, 5) 
            painter.drawRoundedRect(int(cx - 20), int(pad_y + 4), 10, 14, 4, 4) 
            painter.drawRoundedRect(int(cx + 10), int(pad_y + 4), 10, 14, 4, 4) 
            painter.drawEllipse(int(cx - 13), int(pad_y + 3), 4, 4) 
            painter.drawEllipse(int(cx + 9), int(pad_y + 3), 4, 4) 
            
            shake_l = math.sin(time_counter * 15) * 2
            shake_r = math.cos(time_counter * 20) * 2
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(eye_color))
            painter.drawEllipse(int(cx - 22 + shake_l), int(pad_y + 12), 7, 7)
            painter.drawEllipse(int(cx + 15 + shake_r), int(pad_y + 12), 7, 7)
            
        elif state == "rubik":
            painter.setBrush(QBrush(eye_color))
            painter.drawRoundedRect(int(cx - 26), int(cy - 45), 18, 18, 5, 5)
            painter.drawRoundedRect(int(cx + 8), int(cy - 45), 18, 18, 5, 5)
            
            rubik_y = cy - 8
            painter.save()
            painter.translate(cx, rubik_y)
            painter.rotate(time_counter * 40) 
            colors = [QColor(255, 50, 50), QColor(50, 255, 50), QColor(50, 100, 255), QColor(255, 255, 50)]
            size = 8
            for i in range(-1, 2):
                for j in range(-1, 2):
                    c = colors[(i*3 + j + int(time_counter*4)) % 4]
                    painter.setBrush(QBrush(c))
                    painter.setPen(QPen(QColor(15, 15, 15), 1))
                    painter.drawRect(int(i * size - size/2), int(j * size - size/2), size, size)
            painter.restore()
            
            hand_shake = math.sin(time_counter * 20) * 3
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(cx - 25), int(rubik_y - 2 + hand_shake), 8, 8)
            painter.drawEllipse(int(cx + 17), int(rubik_y - 2 - hand_shake), 8, 8)

        elif state == "typing":
            key_y = cy - 4
            painter.setPen(QPen(eye_color, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(int(cx - 18), int(key_y), 36, 12)
            painter.drawLine(int(cx - 18), int(key_y + 6), int(cx + 18), int(key_y + 6)) 
            painter.drawLine(int(cx - 6), int(key_y), int(cx - 6), int(key_y + 12)) 
            painter.drawLine(int(cx + 6), int(key_y), int(cx + 6), int(key_y + 12)) 
            
            tap_l = math.sin(time_counter * 25) * 4
            tap_r = math.cos(time_counter * 30) * 4
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(eye_color))
            painter.drawEllipse(int(cx - 15), int(key_y - 2 + tap_l), 7, 7)
            painter.drawEllipse(int(cx + 8), int(key_y - 2 + tap_r), 7, 7)
            
            read_y = math.sin(time_counter * 10) * 2
            painter.drawRoundedRect(int(cx - 28), int(cy - 40 + read_y), 22, 10, 4, 4)
            painter.drawRoundedRect(int(cx + 6), int(cy - 40 - read_y), 22, 10, 4, 4)

        elif is_disco:
            font = painter.font()
            font.setPixelSize(14)
            painter.setFont(font)
            painter.setPen(eye_color)
            note_y = cy - 30 - (time_counter * 10) % 20
            painter.drawText(int(cx - 20), int(note_y), "♪")
            painter.drawText(int(cx + 10), int(note_y + 10), "♫")
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(eye_color))
            for i in range(4):
                bar_h = 5 + abs(math.sin(time_counter * 5 + i)) * 12
                painter.drawRect(int(cx - 22 + i * 12), int(cy - 25 - bar_h/2), 8, int(bar_h))
                
        else:
            blink = 2 if (int(time_counter * 2) % 40 < 2) else 22
            painter.setBrush(QBrush(eye_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(cx - 28), int(cy - 35 + (22-blink)/2), 22, blink, 6, 6)
            painter.drawRoundedRect(int(cx + 6), int(cy - 35 + (22-blink)/2), 22, blink, 6, 6)

        painter.restore()