# Made by yshinhar
import turtle
import random
import math
import time
import keyboard
import winsound
import os

class GameObject:
    def __init__(self, x, y, size, color, screen):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.screen = screen  
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
        
    def draw(self):
        self.t.clear()
        self.t.fillcolor(self.color)
        self.t.goto(self.x - self.size/2, self.y - self.size/2)
        self.t.pendown()
        self.t.begin_fill()
        for _ in range(4):
            self.t.forward(self.size)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()
    
    def cleanup(self):
        self.t.clear()
        self.t.hideturtle()

class Thread:
    def __init__(self, enemy1, enemy2):
        self.enemy1 = enemy1
        self.enemy2 = enemy2
        self.color = "gray"
        self.state = "normal"  # normal, red_danger, cyan_super
        self.effect_timer = 0
        self.effect_duration = 600  # 10 seconds at 60 FPS for red
        self.blink_timer = 0
        self.blink_duration = 180  # 3 seconds
        self.activation_timer = random.uniform(600, 2400)  # Random time before becoming active (10-20 seconds)
        self.is_active = False
        self.auto_reset_timer = 0
        self.auto_reset_duration = 480  # 6 seconds after activation to auto-reset if not touched
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
        
    def update(self, dt):
        # Handle activation timing
        if not self.is_active:
            self.activation_timer -= dt * 60
            if self.activation_timer <= 0:
                self.is_active = True
                # Only red threads spawn now
                self.state = "red_danger"
                self.color = "red"
                self.blink_timer = self.blink_duration
                self.auto_reset_timer = self.auto_reset_duration  # Start auto-reset timer
        
        # Handle blinking before activation
        if self.is_active and self.blink_timer > 0:
            self.blink_timer -= dt * 60
            # Blink effect      
            if int(self.blink_timer / 10) % 2:
                self.color = "black"
            else:
                if self.blink_timer <= 0:
                    self.color = "red"
                else:
                    self.color = "dark red" 
        
        if (self.is_active and self.state == "red_danger" and self.effect_timer == 0):
            
            self.auto_reset_timer -= dt * 60
            
            if self.auto_reset_timer <= 0:
                # Make thread blink before disappearing
                if self.auto_reset_timer > -30:  # Blink for 0.5 seconds
                    if int(abs(self.auto_reset_timer) / 5) % 2:
                        self.color = "black"
                    else:
                        self.color = "red"
                else:  # After blinking, reset the thread
                    self.reset_thread()
        
        # Handle effect duration (when thread has been activated by player)
        if self.effect_timer > 0:
            self.effect_timer -= dt * 60
            
            # Handle ending effects
            if self.effect_timer <= 30:  # Last 0.5 seconds
                if self.state == "red_danger":
                    self.color = "dark red" if int(self.effect_timer / 5) % 2 else "red"
            
            if self.effect_timer <= 0:
                self.reset_thread()
    
    def reset_thread(self):
        self.color = "gray"
        self.state = "normal"
        self.is_active = False
        self.effect_timer = 0
        self.blink_timer = 0
        self.auto_reset_timer = 0
        self.activation_timer = random.uniform(600, 1200)  # Reset for next spawn
        
        # Reset enemy colors and effects
        if hasattr(self.enemy1, 'temp_color'):
            delattr(self.enemy1, 'temp_color')
        if hasattr(self.enemy2, 'temp_color'):
            delattr(self.enemy2, 'temp_color')
        self.enemy1.is_gray_bonus = False
        self.enemy2.is_gray_bonus = False
        self.enemy1.gray_timer = 0
        self.enemy2.gray_timer = 0
    
    def get_distance_between_enemies(self):
        dx = self.enemy1.x - self.enemy2.x
        dy = self.enemy1.y - self.enemy2.y
        return math.sqrt(dx*dx + dy*dy)
    
    def activate_effect(self, player, energy_bar, combo_meter):
        # Only activate if thread is active and hasn't been activated yet
        if not self.is_active or self.effect_timer > 0:
            return False
            
        if self.state == "red_danger":
            self.enemy1.speed_multiplier = 1.8
            self.enemy2.speed_multiplier = 1.8
            self.enemy1.slowness = 0.65
            self.enemy2.slowness = 0.65
            self.enemy1.is_deadly = True
            self.enemy2.is_deadly = True
            self.enemy1.temp_color = "dark red"
            self.enemy2.temp_color = "dark red"
            self.effect_timer = self.effect_duration  # 10 seconds
            self.auto_reset_timer = 0  # Stop auto-reset since player activated it
            winsound.Beep(300, 100)
            return True
            
        return False
    
    def check_player_collision(self, player):
        # Thread can only be activated after blinking is complete
        if not self.is_active or self.effect_timer > 0 or self.blink_timer > 0:
            return False
            
        # Get line segment points
        x1, y1 = self.enemy1.x, self.enemy1.y
        x2, y2 = self.enemy2.x, self.enemy2.y
        px, py = player.x, player.y
        
        # Calculate distance from point to line segment
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            return False
            
        param = dot / len_sq
        
        if param < 0:
            xx, yy = x1, y1
        elif param > 1:
            xx, yy = x2, y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D
            
        dx = px - xx
        dy = py - yy
        distance = math.sqrt(dx*dx + dy*dy)
        
        return distance < player.size/2 + 10  # Thread collision threshold
    
    def draw(self):
        self.t.clear()
        if self.enemy1 and self.enemy2:
            self.t.color(self.color)
            self.t.pensize(3 if self.is_active else 2)
            self.t.goto(self.enemy1.x, self.enemy1.y)
            self.t.pendown()
            self.t.goto(self.enemy2.x, self.enemy2.y)
            self.t.penup()
    
    def cleanup(self):
        self.t.clear()

class AimArrow:
    def __init__(self):
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
        self.t.color("cyan3")
        self.angle = 0
        self.oscillating_up = True
        self.max_angle = 90
        self.angle_step = 3
        
        self.arc_t = turtle.Turtle()
        self.arc_t.hideturtle()
        self.arc_t.speed(0)
        self.arc_t.penup()
        self.arc_t.color("cyan3")

    def reset_angle(self):
        self.angle = 0
        self.oscillating_up = True

    def update(self):
        if self.oscillating_up:
            self.angle += self.angle_step
            if self.angle >= self.max_angle:
                self.oscillating_up = False
        else:
            self.angle -= self.angle_step
            if self.angle <= -self.max_angle:
                self.oscillating_up = True

    def draw(self, x, y, base_angle):
        self.t.clear()
        self.arc_t.clear()
        
        self.arc_t.penup()
        self.arc_t.goto(x, y)
        self.arc_t.setheading(base_angle - self.max_angle)  
        self.arc_t.pendown()
        self.arc_t.pensize(2)
        
        radius = 40
        self.arc_t.penup()
        self.arc_t.forward(40)
        self.arc_t.left(90)
        self.arc_t.pendown()
        self.arc_t.circle(radius, 180)  
        
        self.t.penup()
        self.t.goto(x, y)
        final_angle = base_angle + self.angle
        self.t.setheading(final_angle)
        self.t.pendown()
        self.t.pensize(3)
        self.t.forward(50)
        self.t.right(150)
        self.t.forward(15)
        self.t.backward(15)
        self.t.left(300)
        self.t.forward(15)
        self.t.penup()

    def cleanup(self):
        self.t.clear()
        self.arc_t.clear()
        
class Player(GameObject):
    def __init__(self, x, y, screen):
        super().__init__(x, y, 50, "blue", screen)
        self.direction = None
        self.is_dashing = False
        self.is_aiming = False
        self.dash_speed = 30
        self.score = 0
        self.aim_arrow = AimArrow()
        self.last_movement_angle = 0
        self.aim_start_position = None
        self.steps_taken = 0
        self.base_step_limit = 20
        self.invincibility_timer = 0
        self.invincibility_duration = 1.0
        
    def get_current_step_limit(self):
        return self.base_step_limit

    def is_invincible(self):
        return self.invincibility_timer > 0

    def update_invincibility(self, dt):
        if self.invincibility_timer > 0:
            self.invincibility_timer = max(0, self.invincibility_timer - dt)

    def take_damage(self):
        self.invincibility_timer = self.invincibility_duration

    def move(self, dx, dy, grid_size):
        if not self.is_dashing and not self.is_aiming:
            if self.steps_taken >= self.get_current_step_limit():
                return
            
            new_x = self.x + dx * 10
            new_y = self.y + dy * 10
            
            half_grid = grid_size / 2
            
            buffer = 0.5
            if abs(new_x) < half_grid - self.size/2 - buffer and abs(new_y) < half_grid - self.size/2 - buffer:
                self.x = new_x
                self.y = new_y
                self.update_direction(dx, dy)
                if self.aim_start_position:
                    self.check_position_for_arrow()
                self.steps_taken += 1

    def execute_dash(self):
        winsound.Beep(500, 50)
        if self.is_aiming:
            self.aim_arrow.cleanup()  
            self.is_aiming = False
            self.is_dashing = True
            angle_rad = math.radians(self.last_movement_angle + self.aim_arrow.angle)
            self.direction = (math.cos(angle_rad), math.sin(angle_rad))
            self.aim_start_position = None
            self.steps_taken = 0  
                
    def update_direction(self, dx, dy):
        if dx != 0 or dy != 0:
            self.direction = (dx, dy)
            self.last_movement_angle = math.degrees(math.atan2(dy, dx))
            
    def aim_control(self, dx, dy):
        if self.is_aiming and (dx != 0 or dy != 0):
            if dx > 0:
                self.last_movement_angle = 0
            elif dx < 0:
                self.last_movement_angle = 180
            elif dy > 0:
                self.last_movement_angle = 90
            elif dy < 0:
                self.last_movement_angle = 270
            
    def update_direction(self, dx, dy):
        if dx != 0 or dy != 0:
            self.direction = (dx, dy)
            if not self.is_aiming:
                if dx > 0:
                    self.last_movement_angle = 0
                elif dx < 0:
                    self.last_movement_angle = 180
                elif dy > 0:
                    self.last_movement_angle = 90
                elif dy < 0:
                    self.last_movement_angle = 270
                    
    def start_aiming(self):
        if not self.is_dashing and not self.is_aiming and self.direction:
            self.is_aiming = True
            self.aim_start_position = (self.x, self.y)

    def update_dash(self, grid_size):
        if self.is_dashing:
            dx, dy = self.direction
            new_x = self.x + dx * self.dash_speed
            new_y = self.y + dy * self.dash_speed
            
            half_grid = grid_size / 2
            if abs(new_x) >= half_grid - self.size/2 or abs(new_y) >= half_grid - self.size/2:
                self.is_dashing = False
                self.x = max(min(new_x, half_grid - self.size/2 - 1), -half_grid + self.size/2 + 1)
                self.y = max(min(new_y, half_grid - self.size/2 - 1), -half_grid + self.size/2 + 1)
                return True
            else:
                self.x = new_x
                self.y = new_y
        return False
    
    def draw(self):
        self.t.clear()
        
        current_color = self.color
        if self.is_invincible():
            flash_rate = 10
            if int(time.time() * flash_rate) % 2:
                current_color = "lightblue"
        
        self.t.fillcolor(current_color)
        self.t.goto(self.x - self.size/2, self.y - self.size/2)
        self.t.pendown()
        self.t.begin_fill()
        for _ in range(4):
            self.t.forward(self.size)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()
        
        if self.is_aiming:
            self.aim_arrow.draw(self.x, self.y, self.last_movement_angle)
            
class Collectible(GameObject):
    def __init__(self, grid_size, screen):
        half_grid = grid_size / 2 - 25
        x = random.uniform(-half_grid, half_grid)
        y = random.uniform(-half_grid, half_grid)
        super().__init__(x, y, 50, "yellow", screen)
        
    def draw(self):
        self.t.clear()
        self.t.fillcolor("yellow")
        self.t.goto(self.x - self.size/2, self.y - self.size/2)
        self.t.pendown()
        self.t.begin_fill()
        for _ in range(4):
            self.t.forward(self.size)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()

class EnergyBar:
    def __init__(self, x, y):
        self.value = 250
        self.max_value = 250
        self.decay_rate = 0.7
        self.is_frozen = False
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.penup()
        self.t.goto(x, y)
        self.last_update = time.time()
        self.width = 300
        self.height = 15
    
    def update(self, is_aiming=False):
        if self.is_frozen:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_update
        
        current_decay = self.decay_rate * (0.3 if is_aiming else 1.0)
        self.value = max(0, self.value - current_decay * time_diff * 60)
        
        self.last_update = current_time
    
    def lose_energy(self):
        if not self.is_frozen:
            self.value = max(0, self.value - self.max_value/2)
    
    def gain_energy(self):
        self.value = min(self.max_value, self.value + self.max_value/2)
    
    def is_empty(self):
        return self.value <= 0
    
    def unfreeze(self):
        self.is_frozen = False
    
    def draw(self):
        self.t.clear()
        
        self.t.goto(-self.width/2, 320)
        self.t.pendown()
        self.t.fillcolor("gray")
        self.t.begin_fill()
        for _ in range(2):
            self.t.forward(self.width)
            self.t.left(90)
            self.t.forward(self.height)
            self.t.left(90)
        self.t.end_fill()
        
        energy_width = (self.value / self.max_value) * self.width
        
        if self.is_frozen:
            color = "gold"
        elif self.value > 75*2.5:
            color = "cyan"
        elif self.value > 50*2.5:
            color = "light blue"
        elif self.value > 25*2.5:
            color = "cyan3"
        else:
            color = "dark blue"
        
        self.t.fillcolor(color)
        self.t.begin_fill()
        for _ in range(2):
            self.t.forward(energy_width)
            self.t.left(90)
            self.t.forward(self.height)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()

class ComboMeter:
    def __init__(self, x, y):
        self.value = 0
        self.max_value = 100
        self.decay_rate = 0.5 
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.penup()
        self.t.goto(x, y)
        self.multiplier = 1
        self.last_update = time.time()
    
    def update(self, is_aiming=False):
        current_time = time.time()
        time_diff = current_time - self.last_update
        
        current_decay = self.decay_rate * (0.3 if is_aiming else 1.0)
        self.value = max(0, self.value - current_decay * time_diff * 60)
        
        if self.value <= 0:
            self.multiplier = 1
            
        self.last_update = current_time

    def add_value(self, amount):
        self.value = min(self.max_value, self.value + amount)
    
    def get_bonus_points(self):
        return (self.multiplier - 1) * 25
    
    def collect_coin(self):
        self.value = self.max_value
        self.multiplier += 1
    
    def draw(self):
        self.t.clear()
        self.t.goto(-self.max_value/2, 250)
        self.t.pendown()
        self.t.fillcolor("gray")
        self.t.begin_fill()
        for _ in range(2):
            self.t.forward(self.max_value)
            self.t.left(90)
            self.t.forward(20)
            self.t.left(90)
        self.t.end_fill()
        
        self.t.fillcolor("cyan3")
        if self.multiplier > 3:
            self.t.fillcolor("light blue")
        if self.multiplier > 5:
            self.t.fillcolor("cyan")
        if self.multiplier > 7:
            self.t.fillcolor("blue")
        if self.multiplier > 10:
            self.t.fillcolor("dark blue")
        self.t.begin_fill()
        for _ in range(2):
            self.t.forward(self.value)
            self.t.left(90)
            self.t.forward(20)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()
        
        self.t.goto(0, 280)
        self.t.write(f"Combo: x{self.multiplier}", align="center", font=("Arial", 16, "bold"))

class Enemy(GameObject):
    def __init__(self, x, y, screen, is_bouncing=False, enemy_type=''):
        super().__init__(x, y, 50, "red", screen)
        self.speed = 2.5
        self.slowness = 0.3
        self.speed_multiplier = 1.0
        self.is_bouncing = is_bouncing
        self.enemy_type = enemy_type
        self.is_deadly = False
        self.is_bonus = False
        self.is_gray_bonus = False
        self.gray_timer = 0
        self.gray_duration = 300  # 5 seconds at 60 FPS
        self.temp_color = "red"
        if is_bouncing:
            self.angle = random.uniform(0, 360)
            self.speed = 4

    def reset_effects(self):
        self.speed_multiplier = 1.0
        self.is_deadly = False
        self.is_bonus = False
        self.is_gray_bonus = False
        self.gray_timer = 0
        self.temp_color = None

    def update_gray_bonus(self, dt):
        if self.is_gray_bonus:
            self.gray_timer -= dt * 60
            if self.gray_timer <= 0:
                self.is_gray_bonus = False
                self.gray_timer = 0

    def make_gray_bonus(self):
        self.is_gray_bonus = True
        self.gray_timer = self.gray_duration

    def draw(self):
        self.t.clear()
        
        # Determine color based on effects
        draw_color = self.color
        if self.is_gray_bonus:
            draw_color = "gray"
        elif self.is_deadly:
            draw_color = "dark red"
        elif self.is_bonus:
            draw_color = "yellow"
            
        self.t.fillcolor(draw_color)
        self.t.goto(self.x - self.size/2, self.y - self.size/2)
        self.t.pendown()
        self.t.begin_fill()
        for _ in range(4):
            self.t.forward(self.size)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()
        
    def chase(self, player, grid_size, time_slowed):
        # Gray bonus enemies can't move
        if self.is_gray_bonus:
            return
            
        speed_multiplier = self.slowness if time_slowed else 1.0
        total_speed_multiplier = speed_multiplier * self.speed_multiplier
        
        if self.is_bouncing:
            self.bounce(grid_size, total_speed_multiplier)
        else:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                new_x = self.x + (dx/dist) * self.speed * total_speed_multiplier
                new_y = self.y + (dy/dist) * self.speed * total_speed_multiplier
                
                half_grid = grid_size / 2
                self.x = max(min(new_x, half_grid - self.size/2), -half_grid + self.size/2)
                self.y = max(min(new_y, half_grid - self.size/2), -half_grid + self.size/2)
    
    def bounce(self, grid_size, speed_multiplier=1.0):
        # Gray bonus enemies can't move
        if self.is_gray_bonus:
            return
            
        angle_rad = math.radians(self.angle)
        dx = math.cos(angle_rad) * self.speed * speed_multiplier
        dy = math.sin(angle_rad) * self.speed * speed_multiplier
        
        half_grid = grid_size / 2
        new_x = self.x + dx
        new_y = self.y + dy
        
        bounced = False
        
        if abs(new_x) >= half_grid - self.size/2:
            self.angle = 180 - self.angle
            if self.angle < 0:
                self.angle += 360
            bounced = True
            new_x = max(min(new_x, half_grid - self.size/2), -half_grid + self.size/2)
        
        if abs(new_y) >= half_grid - self.size/2:
            self.angle = 360 - self.angle
            if self.angle >= 360:
                self.angle -= 360
            bounced = True
            new_y = max(min(new_y, half_grid - self.size/2), -half_grid + self.size/2)
        
        if bounced:
            self.angle += random.uniform(-10, 10)
            if self.angle < 0:
                self.angle += 360
            elif self.angle >= 360:
                self.angle -= 360
        
        self.x = new_x
        self.y = new_y

class Game:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.getcanvas().winfo_toplevel().attributes("-fullscreen", True)
        self.screen.bgcolor("black")
        
        self.screen.tracer(0, 0)
        turtle.tracer(0, 0)
        
        self.window = self.screen.getcanvas().winfo_toplevel()
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        turtle.speed(0)
        
        self.grid_size = min(self.screen_width, self.screen_height) - 100
        
        self.game_state = "start"
        self.running = True
        self.last_frame_time = time.time()
        
        self.initialize_game()

    def initialize_game(self):
        self.is_running = True
        self.player = Player(0, 0, self.screen)
        self.player.move(1, 1, self.grid_size)    
        self.player.move(0, 0, self.grid_size) 
        self.player.t.speed(0)
        self.player.t._tracer(0)
        
        self.enemies = [
            Enemy(-200, -200, self.screen, is_bouncing=True, enemy_type='rokia'),
            Enemy(200, 200, self.screen, is_bouncing=True, enemy_type='ranji'),
            Enemy(0, 200, self.screen, is_bouncing=False, enemy_type='ichigo')
        ]
        for enemy in self.enemies:
            enemy.t.speed(0)

        # Create threads between enemies
        self.threads = [
            Thread(self.enemies[0], self.enemies[2]),  # bouncing to following
            Thread(self.enemies[1], self.enemies[2]),  # bouncing to following  
            Thread(self.enemies[0], self.enemies[1])   # bounce to bounce
        ]

        self.collectible = None
        
        self.score_label = turtle.Turtle()
        self.score_label.speed(0)
        self.score_label.hideturtle()
        self.score_label.penup()
        self.score_label.goto(self.grid_size/2 + 30, 20)
        
        self.score_number = turtle.Turtle()
        self.score_number.speed(0)
        self.score_number.hideturtle()
        self.score_number.penup()
        self.score_number.goto(self.grid_size/2 + 30, -20)
        self.score_number.color("red")
        
        self.energy_bar = EnergyBar(0, 0)
        self.energy_bar.t.speed(0)
        
        self.combo_meter = ComboMeter(0, 0)
        self.combo_meter.t.speed(0)
        
        self.clear_square = turtle.Turtle()
        self.clear_square.speed(0)
        self.clear_square.hideturtle()
        self.clear_square.penup()
        
        self.step_display = turtle.Turtle()
        self.step_display.speed(0)
        self.step_display.hideturtle()
        self.step_display.penup()

    def draw_start_screen(self):
        self.screen.clear()
        self.screen.bgcolor("black")
        
        start_text = turtle.Turtle()
        start_text.speed(0)
        start_text.hideturtle()
        start_text.penup()
        start_text.color("white")
        
        start_text.goto(-100, 0)
        start_text.write("press           ", align="center", font=("Arial", 36, "normal"))
        start_text.color("cyan3")
        start_text.write("SPACE            ", font=("Arial", 36, "bold"))
        start_text.color("white")
        start_text.write("              to start", font=("Arial", 36, "normal"))
        
        start_text.goto(-50, -50)
        start_text.write("press    ", align="center", font=("Arial", 18, "normal"))
        start_text.color("cyan3")
        start_text.write("   ESC                 ", font=("Arial", 18, "normal"))
        start_text.color("white")
        start_text.write("           to exit", font=("Arial", 18, "normal"))
        
        self.screen.update()

    def draw_game_over_screen(self):
        self.screen.clear()
        self.screen.bgcolor("black")
        
        game_over = turtle.Turtle()
        game_over.speed(0)
        game_over.hideturtle()
        game_over.color("white")
        game_over.penup()
        
        game_over.goto(0, 50)
        game_over.write("Game Over!", align="center", font=("Arial", 36, "bold"))
        
        game_over.goto(0, -20)
        game_over.write(f"Score: {self.player.score}", align="center", font=("Arial", 24, "normal"))
        
        game_over.goto(0, -150)
        game_over.write("PRESS SPACE TO PLAY AGAIN", align="center", font=("Arial", 18, "normal"))
        
        game_over.goto(0, -200)
        game_over.write("press ESC to exit", align="center", font=("Arial", 18, "normal"))
        
        self.screen.update()

    def exit_fullscreen(self):
        self.running = False  
        self.window.destroy()  
        import sys
        sys.exit()

    def draw_grid(self):
        grid = turtle.Turtle()
        grid.speed(0)
        grid.hideturtle()
        
        grid.penup()
        grid.goto(-self.grid_size/2 - 10, -self.grid_size/2 - 10)
        grid.pendown()
        grid.fillcolor("black")
        grid.begin_fill()
        for _ in range(4):
            grid.forward(self.grid_size + 20)
            grid.left(90)
        grid.end_fill()
        
        grid.penup()
        grid.goto(-self.grid_size/2, -self.grid_size/2)
        grid.pendown()
        grid.fillcolor("white")
        grid.begin_fill()
        for _ in range(4):
            grid.forward(self.grid_size)
            grid.left(90)
        grid.end_fill()
        
        self.screen.update()

    def update_score_display(self):
        self.score_label.clear()
        self.score_number.clear()
        self.score_label.color("white")
        self.score_label.write("Score:", align="left", font=("Arial", 20, "bold"))
        self.score_number.color("cyan3")
        self.score_number.write(f"{self.player.score}", align="left", font=("Arial", 20, "bold"))

    def check_thread_collisions(self):
        if self.player.is_dashing:
            for thread in self.threads:
                if thread.check_player_collision(self.player):
                    thread.activate_effect(self.player, self.energy_bar, self.combo_meter)

    def check_collisions(self):
        if not self.player.is_invincible():
            for enemy in self.enemies:
                dx = self.player.x - enemy.x
                dy = self.player.y - enemy.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < (self.player.size + enemy.size)/2:
                    if enemy.is_gray_bonus:
                        # Gray bonus collision - give enhanced coin effects
                        self.combo_meter.add_value(50)  # More combo than regular coin
                        self.player.score += 750  # More points than regular coin
                        self.energy_bar.value = min(self.energy_bar.max_value, self.energy_bar.value + self.energy_bar.max_value * 0.75)  # More energy
                        enemy.is_gray_bonus = False
                        enemy.gray_timer = 0
                        winsound.Beep(1500, 150)
                    elif enemy.is_bonus:
                        # Yellow bonus collision - give points instead of damage
                        self.combo_meter.add_value(25)
                        self.player.score += 500
                        # Make enemy gray bonus for a while
                        enemy.make_gray_bonus()
                        enemy.is_bonus = False  # Remove yellow bonus status
                        winsound.Beep(1200, 100)
                    else:
                        # Normal collision
                        self.energy_bar.lose_energy()
                        self.combo_meter.multiplier = 1
                        self.player.take_damage()
                        winsound.Beep(300, 200)
                        
                        if self.energy_bar.is_empty():
                            self.is_running = False
                    break
        
        if self.collectible:
            dx = self.player.x - self.collectible.x
            dy = self.player.y - self.collectible.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < (self.player.size + self.collectible.size)/2:
                bonus_points = self.combo_meter.get_bonus_points()
                self.player.score += 100 + bonus_points
                self.combo_meter.collect_coin()
                self.energy_bar.gain_energy()
                winsound.Beep(1000, 100)
                self.remove_collectible()

    def check_movement(self):
        dx = dy = 0
        if keyboard.is_pressed('w'): dy = 1
        if keyboard.is_pressed('s'): dy = -1
        if keyboard.is_pressed('a'): dx = -1
        if keyboard.is_pressed('d'): dx = 1
        
        if dx != 0 or dy != 0:
            if self.player.is_aiming:
                self.player.aim_control(dx, dy)
            else:
                self.player.move(dx, dy, self.grid_size)  
                self.combo_meter.value = max(0, self.combo_meter.value - 0.5)
        
        if keyboard.is_pressed('space'):
            if self.game_state == "start" or self.game_state == "game_over":
                self.start_new_game()
            elif not self.player.is_aiming:
                self.player.start_aiming()
        elif keyboard.is_pressed('escape'):
                self.exit_fullscreen()
        elif self.player.is_aiming:
            self.player.execute_dash()
            self.combo_meter.add_value(20)
            self.energy_bar.value += 10
    
    def reset_thread_effects(self):
        """Reset all thread effects on enemies and energy bar"""
        for enemy in self.enemies:
            enemy.reset_effects()
        self.energy_bar.unfreeze()
        
    def start_new_game(self):
        self.game_state = "playing"
        self.screen.clear()
        self.screen.bgcolor("black")
        self.draw_grid()  
        self.initialize_game()  

    def spawn_collectible(self):
        if self.collectible is None:
            self.collectible = Collectible(self.grid_size, self.screen)
            self.collectible.t.speed(0)
            
    def clear_collectible_visual(self, x, y, size):
        self.clear_square.clear()
        self.clear_square.fillcolor("white")
        
        extra_space = 5  
        self.clear_square.goto(x - size/2 - extra_space, y - size/2 - extra_space)
        self.clear_square.begin_fill()
        for _ in range(4):
            self.clear_square.forward(size + 2 * extra_space)
            self.clear_square.left(90)
        self.clear_square.end_fill()

    def remove_collectible(self):
        if self.collectible:
            self.clear_collectible_visual(self.collectible.x, self.collectible.y, self.collectible.size)
            self.collectible.cleanup()
            self.collectible = None
                
    def run(self):
        self.draw_start_screen()

        while self.running:
            current_time = time.time()
            dt = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            if self.game_state == "start":
                self.check_movement()
            
            elif self.game_state == "playing":
                self.step_display.clear()
                current_step_limit = self.player.get_current_step_limit()
                steps_remaining = current_step_limit - self.player.steps_taken
                self.step_display.goto(-self.grid_size/2 + 30, self.grid_size/2 - 40)
                self.step_display.color("black")
                self.step_display.write("          Steps:        ", align="center", font=("Arial", 16, "normal"))
                self.step_display.color("cyan3")
                self.step_display.write(f"       {steps_remaining}          ", font=("Arial", 16, "normal"))
                self.step_display.color("black")
                self.step_display.write(f"           /{current_step_limit}", font=("Arial", 16, "normal"))
                
                self.check_movement()
                
                if self.player.is_aiming:
                    self.player.aim_arrow.update()
                
                if self.player.update_dash(self.grid_size):
                    self.spawn_collectible()
                
                # Update threads - now they can become cyan when enemies are close
                for thread in self.threads:
                    thread.update(dt)
                
                # Check if any thread effects have ended
                any_thread_active = any(thread.effect_timer > 0 for thread in self.threads)
                if not any_thread_active:
                    self.reset_thread_effects()
                
                # Update enemies and their gray bonus timers
                for enemy in self.enemies:
                    enemy.chase(self.player, self.grid_size, self.player.is_aiming)
                    enemy.update_gray_bonus(dt)
                    
                self.player.update_invincibility(dt)
                self.energy_bar.update(self.player.is_aiming)
                self.combo_meter.update(self.player.is_aiming)
                
                # Check if energy is depleted (game over condition)
                if self.energy_bar.is_empty():
                    self.is_running = False
                
                # Clear all turtle graphics
                self.player.t.clear()
                for enemy in self.enemies:
                    enemy.t.clear()
                if self.collectible:
                    self.collectible.t.clear()
                if hasattr(self.player, 'aim_arrow'):
                    self.player.aim_arrow.t.clear()
                self.combo_meter.t.clear()
                self.energy_bar.t.clear()
                for thread in self.threads:
                    thread.t.clear()
                
                # Draw all game objects
                self.player.draw()
                for enemy in self.enemies:
                    enemy.draw()
                if self.collectible:
                    self.collectible.draw()
                self.combo_meter.draw()
                self.energy_bar.draw()
                
                # Draw threads
                for thread in self.threads:
                    thread.draw()
                
                self.check_thread_collisions()
                self.check_collisions()
                self.update_score_display()
                
                # Update screen
                self.screen.update()
                
                if not self.is_running:
                    self.game_state = "game_over"
                    self.draw_game_over_screen()
            
            elif self.game_state == "game_over":
                self.check_movement()
            
            time.sleep(0.016)

if __name__ == "__main__":
    game = Game()
    game.run()