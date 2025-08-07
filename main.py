import pygame
import sys
import time
import random
import json
import math



class GAME_STATE:
    def __init__(self, cookies=0,total_cookies = 0, cps=0 ):
        self.cookies = cookies
        self.total_cookies = total_cookies
        # self.buildings = []
        self.shop_items = []
        self.cursors = []
        self.grandmas = []
        self.farms = []
        self.mines = []
        self.cps = cps

    def to_dict(self):
        return {
            "cookies": self.cookies,
            "total_cookies": self.total_cookies,
            "cps": self.cps,
            "cursors": len(self.cursors),
            "grandmas": len(self.grandmas),
            "farms": len(self.farms),
            "mines": len(self.mines),
        }
    def save(self, filename="savefile.txt"):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f)
    @classmethod
    def load(cls, filename="savefile.txt"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                state = cls()
                state.cookies = data.get("cookies", 0)
                state.total_cookies = data.get("total_cookies", 0)
                state.cps = data.get("cps", 0)
                c = Cursor()
                for i in range(data.get("cursors", 0)):
                    if not state.cursors:
                        state.cursors.append(c)
                    else:
                        c = c.copy()
                        state.cursors.append(c)
                for i in range(data.get("grandmas", 0)):
                    state.grandmas.append('c')
                return state
        except FileNotFoundError:
            return cls()
    

class Shop_Item:
    def __init__(self, name, cost, image_path, y, state):
        self.game_state = state
        self.name = name
        self.cost = cost
        self.amount = 0
        self.image_path = image_path
        self.image = self.resize_image()
        self.black_image = self.black_out_image()
        self.unlocked = False
        self.y = y
        self.rect = pygame.Rect(955, self.y, 310, 66)
        

    def set_rect(self):
        self.rect = pygame.Rect(955, self.y, 310, 66)
    
    def resize_image(self):
        # Target height
        target_height = 66
        image = pygame.image.load(self.image_path).convert_alpha()
        # Calculate aspect ratio and new width
        original_width, original_height = image.get_size()
        aspect_ratio = original_width / original_height
        new_width = int(target_height * aspect_ratio)

        # Resize the image
        return pygame.transform.smoothscale(image, (new_width, target_height))

    def black_out_image(self):
        black_image = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)

        # Fill it with black but keep the alpha from the original image
        width, height = self.image.get_size()
        for x in range(width):
            for y in range(height):
                r, g, b, a = self.image.get_at((x, y))
                black_image.set_at((x, y), (20, 26, 32, a))
        return black_image
    
    def unlock_next(self):
        pass
    
    def draw_box(self):
        #bx is 15px from bar
        if not self.unlocked:
            if state.total_cookies >= self.cost:
                self.unlocked = True
                self.unlock_next()


        image = self.image if self.unlocked else self.black_image
        name = self.name if self.unlocked else "???"
        cost_color = pygame.Color(91,255,83) if self.cost <= self.game_state.cookies else pygame.Color(147,66,75)

        cookie = pygame.image.load("images/Cookie.png").convert_alpha()
        cookie = pygame.transform.smoothscale(cookie, (15, 15))
        pygame.draw.rect(screen,(110, 107, 88),[955,self.y,310,66],0)
        pygame.draw.rect(screen,(161, 159, 144),[960,self.y+5,305,56],0)
        pygame.draw.rect(screen,(191, 187, 170),[960,self.y+5,306,56],1)
        pygame.draw.rect(screen,(21, 20, 14),[955,self.y,310,66],1)
        pygame.draw.line(screen,(191, 187, 170),[960,self.y+5],[955,self.y],1)

        name_font = pygame.font.SysFont("Georgia", 30, bold=True)
        cost_font = pygame.font.SysFont("Arial", 15, bold=True)
        amount_font = pygame.font.SysFont("Georgia", 55, bold=True)

        name_text = name_font.render(name, True, pygame.Color(255,255,255))
        cost_text = cost_font.render(str(self.cost), True, cost_color)

        name_text_shadow = name_font.render(name, True, pygame.Color(50,50,50))
        cost_text_shadow = cost_font.render(str(self.cost), True, pygame.Color(50,50,50))

        amount_text = amount_font.render(str(self.amount), True, pygame.Color(94,91,77))

        amount_text_rect = amount_text.get_rect()
        amount_text_rect.topright = (1250, self.y)

        screen.blit(image, (955,self.y))
        screen.blit(name_text_shadow, (1025+2,self.y+5+2))
        screen.blit(cost_text_shadow, (1025 + 20+2,self.y+40+2))
        screen.blit(name_text, (1025,self.y+5))
        screen.blit(cost_text, (1025 + 20,self.y+40))
        screen.blit(cookie, (1025,self.y+40))
        screen.blit(amount_text, amount_text_rect)

class Cursor_shop(Shop_Item):
    def __init__(self, state, y=0):
        super().__init__("Cursor", 15, "images/CursorIcon.webp", y, state)
        self.amount = len(state.cursors)
        if self.amount > 0:
            for i in range(self.amount):
                self.cost = math.ceil(self.cost * 1.15)

    def unlock_next(self):
        state.shop_items.append(Farm_shop(self.game_state, y = self.y + 130))


class Grandma_shop(Shop_Item):
    def __init__(self, state, y=0):
        super().__init__("Grandma", 100, "images/Grandma.webp", y, state)
        self.amount = len(state.grandmas)
        if self.amount > 0:
            for i in range(self.amount):
                self.cost = math.ceil(self.cost * 1.15)
    
    def unlock_next(self):
        state.shop_items.append(Mine_shop(self.game_state, y = self.y + 130))

class Farm_shop(Shop_Item):
    def __init__(self, state, y=0):
        super().__init__("Farm", 1100, "images/FarmIcon.webp", y, state)
        self.amount = len(state.farms)
        if self.amount > 0:
            for i in range(self.amount):
                self.cost = math.ceil(self.cost * 1.15)

class Mine_shop(Shop_Item):
    def __init__(self, state, y=0):
        super().__init__("Mine", 12000,"images/MineIcon.webp", y, state)
        self.amount = len(state.mines)
        if self.amount > 0:
            for i in range(self.amount):
                self.cost = math.ceil(self.cost * 1.15)


class CPS_UPGARDE:
    def __init__(self):
        self.price = 0
        self.cps = 0

    def click(self, state):
        state.cookies += self.cps
        state.total_cookies += self.cps

class Cursor(CPS_UPGARDE):
    def __init__(self, ):
        CPS_UPGARDE.__init__(self)
        self.cps = 0.1
        self.image = pygame.image.load("images/cursor small.webp").convert_alpha()
        self.rotated_image = pygame.transform.rotate(self.image, 0)
        self.rect = self.rotated_image.get_rect()
        self.center_x = 200
        self.center_y = 260
        self.radius = 140
        self.speed = -0.005
        self.angle = math.radians(270)-180

        self.click_delay = 1000 # cahnge to 1 second
        self.last_click = pygame.time.get_ticks()
        

    def copy(self):
        #print("making copy")
        c = Cursor()
        c.price = self.price
        c.cps = self.cps
        c.angle = self.angle
        c.radius = self.radius
        c.set_start()
        return c

    def move(self):
        self.angle += self.speed
        x = self.center_x + int(self.radius * math.cos(self.angle))
        y = self.center_y + int(self.radius * math.sin(self.angle))

        dx = self.center_x - x
        dy = self.center_y - y

        center_angle = math.degrees(math.atan2(-dy, dx)) - 90

        self.rotated_image = pygame.transform.rotate(self.image, center_angle)
        self.rect = self.rotated_image.get_rect(center=(x,y))

    def set_start(self):
        self.angle -= 0.12
        self.move()

    def render(self, screen):
        #added this to stagger clicks
        now = pygame.time.get_ticks()
        if now - self.last_click >= self.click_delay:
            self.last_click = now
            pygame.event.post(pygame.event.Event(CURSOR_CLICK_EVENT))
        self.move()
        screen.blit(self.rotated_image, self.rect)



def get_ring_capacity(radius, spacing=17.5):
    circumference = 2 * math.pi * radius
    return max(1, int(circumference // spacing))

pygame.init()

USERNAME = ""
CURSOR_CLICK_EVENT = pygame.USEREVENT + 1
#pygame.time.set_timer(CURSOR_CLICK_EVENT, 5000) 
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1250,650))

title_img = pygame.image.load("images/cookie clicker title.png")
scale_title = pygame.transform.scale(title_img,(1250, 650)).convert_alpha()
title_rect = scale_title.get_rect()
title_rect.center = (625, 325)
a = 255
title_time = 300

#setup text input
input_screen = True
input_active = True
input_value = ""

#button rects
confirm_btn = pygame.Rect(450,370,110,45)
random_btn = pygame.Rect(570,370,110,45)
cancel_btn = pygame.Rect(690,370,110,45)

input_title_font = pygame.font.SysFont("Georgia", 35, bold=True)
input_title_text = input_title_font.render("Name Your Bakery", True, pygame.Color(232,221,167))
input_title_shadow = input_title_font.render("Name Your Bakery", True, pygame.Color(74,45,21))
input_title_text_rect = input_title_text.get_rect(center = (625,175))
input_title_shadow_rect = input_title_shadow.get_rect(center = (627,178))

input_font = pygame.font.SysFont("Arial", 30)
input_prompt = input_font.render("Enter your username", True, pygame.Color(255,255,255))
input_prompt_rect = input_prompt.get_rect(center = (625, 225))

button_font = pygame.font.SysFont("Arial", 25)
confirm_text = button_font.render("Confirm", True, pygame.Color(255,255,255))
random_text = button_font.render("Random", True, pygame.Color(255,255,255))
cancel_text = button_font.render("Cancel", True, pygame.Color(255,255,255))
confirm_text_rect = confirm_text.get_rect(center = (505, 392))
random_text_rect = random_text.get_rect(center = (625, 392))
cancel_text_rect = cancel_text.get_rect(center = (745, 392))

bakery_left = pygame.image.load("images/bakery-left.png")
bakery_left_rect = bakery_left.get_rect(center = (415, 175))
bakery_right = pygame.image.load("images/bakery-right.png")
bakery_right_rect = bakery_right.get_rect(center = (835, 178))


#Splash screen
while a >=0:
    scale_title.set_alpha(a)
    screen.fill((29, 71, 106))

    screen.blit(scale_title, title_rect)
    a-=2
    clock.tick(60)
    pygame.display.update()

#Username input

while input_screen:
    screen.fill(pygame.Color(29, 71, 106))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            print(pos)
            if confirm_btn.collidepoint(pos):
                USERNAME = input_value
                input_screen = False
                print(f"retrieving save data for {USERNAME}")
            elif random_btn.collidepoint(pos):
                print("random is not implemented yet!")
            elif cancel_btn.collidepoint(pos):
                pygame.quit()
                print("closing pygame")
        if event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_RETURN:
                print("User input:", input_text)
                input_value = ""
            elif event.key == pygame.K_BACKSPACE:
                input_value = input_value[:-1]
            else:
                input_value += event.unicode
                print(input_value)
        


    #container
    pygame.draw.rect(screen,(25, 25, 25),[325,125,600,350],0)
    pygame.draw.rect(screen,(215, 174, 137),[325,125,600,350],5)
    pygame.draw.line(screen,(115, 68, 29),[923,125],[923,473],2)
    pygame.draw.line(screen,(115, 68, 29),[924,473],[325,473],2)

    screen.blit(input_title_shadow, input_title_shadow_rect)
    screen.blit(input_title_text, input_title_text_rect)
    screen.blit(bakery_left, bakery_left_rect)
    screen.blit(bakery_right, bakery_right_rect)
    screen.blit(input_prompt, input_prompt_rect)


    #input
    pygame.draw.rect(screen,(255, 255, 255),[400,285,450,45],width = 0, border_radius=5)
    pygame.draw.rect(screen,(215, 174, 137),[400,285,450,45],width = 2, border_radius=5)

    input_text = input_font.render(input_value, True, pygame.Color(0,0,0))
    screen.blit(input_text, (410, 290))

    #buttons
    pygame.draw.rect(screen,(25, 25, 25),[450,370,110,45],0, border_radius=3)
    pygame.draw.rect(screen,(215, 174, 137),[450,370,110,45],2, border_radius=3)

    pygame.draw.rect(screen,(25, 25, 25),[570,370,110,45],0, border_radius=3)
    pygame.draw.rect(screen,(215, 174, 137),[570,370,110,45],2, border_radius=3)

    pygame.draw.rect(screen,(25, 25, 25),[690,370,110,45],0, border_radius=3)
    pygame.draw.rect(screen,(215, 174, 137),[690,370,110,45],2, border_radius=3)

    screen.blit(confirm_text, confirm_text_rect)
    screen.blit(random_text, random_text_rect)
    screen.blit(cancel_text, cancel_text_rect)

    pygame.display.update()



state = GAME_STATE.load(f"{USERNAME}_savefile.txt")

cookie = pygame.image.load("images/PerfectCookie.png")
big_cookie = pygame.transform.scale_by(cookie,(1.25,1.25))
cookie_rect = big_cookie.get_rect()
cookie_rect.center = (200,260)
cookie_count = 0

cursor_capacity = 50#get_ring_capacity(140)

# font = pygame.font.Font(None, 100)
font = pygame.font.SysFont("Georgia", 35, bold=True)
small_font = pygame.font.SysFont("Georgia", 15, bold=True)
mid_font = pygame.font.SysFont("Georgia", 25, bold=True)
bakery_text = mid_font.render(f"{USERNAME}'s bakery", True, pygame.Color(255,255,255))
bakery_text_rect = bakery_text.get_rect(center = (190,35))
store_text = font.render("Store", True, pygame.Color(255,255,255))

cookie_text = font.render(str(math.floor(state.cookies)), True, pygame.Color(255,255,255))
cookie_text_rect = cookie_text.get_rect(center = (190,70))

text_surface = pygame.Surface((380, 100), pygame.SRCALPHA)
text_surface.fill((0, 0, 0, 128))

shop_item_y = 140
state.shop_items += [Cursor_shop(state), Grandma_shop(state)]
print(state.shop_items)

for item in state.shop_items:
    item.y = shop_item_y
    item.set_rect()
    shop_item_y += 65

#Main game
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.save(f"{USERNAME}_savefile.txt")
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            #print(pos)

            if cookie_rect.collidepoint(pos):
                state.cookies += 1
                state.total_cookies += 1
                cookie_text = font.render(str(math.floor(state.cookies)), True, pygame.Color(255,255,255))
                print("clicked on cookie!!!!!")

            for shop in state.shop_items:
                if isinstance(shop, Cursor_shop) and state.cookies >= shop.cost and shop.rect.collidepoint(pos): 
                    if not state.cursors:
                        c = Cursor()
                        state.cursors.append(c)
                    else:
                        # print(cursors[-1].radius)
                        if len(state.cursors) >= cursor_capacity:
                            c = state.cursors[-1].copy()
                            c.radius += 20
                            cursor_capacity += 50#get_ring_capacity(c.radius)
                            print(cursor_capacity)
                            state.cursors.append(c)
                            print(c.radius)
                        else:
                            c = state.cursors[-1].copy()
                            state.cursors.append(c)
                    shop.amount += 1
                    shop.cost = math.ceil(shop.cost * 1.15)
                    state.cookies -= shop.cost
                    cookie_text = font.render(str(math.floor(state.cookies)), True, pygame.Color(255,255,255))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                state.save(f"{USERNAME}_savefile.txt")
        if event.type == CURSOR_CLICK_EVENT:
            state.cookies += state.cursors[0].cps
            state.total_cookies += state.cursors[0].cps
            cookie_text = font.render(str(math.floor(state.cookies)), True, pygame.Color(255,255,255))
            # for c in cursors:
            #     c.click(state)
            #     cookie_text = font.render(str(state.cookies), True, pygame.Color(255,255,255))

    screen.fill(pygame.Color(29, 71, 106))
    for c in state.cursors:
        c.render(screen)
    screen.blit(text_surface, (0, 15))
    
    screen.blit(big_cookie, cookie_rect)
    screen.blit(bakery_text, bakery_text_rect)
    screen.blit(cookie_text, cookie_text_rect)
    screen.blit(store_text, (1050,25))
    pygame.draw.rect(screen,(66, 38, 27),[380,0,15,650],0)
    pygame.draw.rect(screen,(66, 38, 27),[925,0,15,650],0)
    pygame.draw.rect(screen,(29, 71, 106),[395,0,530,650],0)




    for box in state.shop_items:
        box.draw_box()
   


    #print(clock.get_time())
    clock.tick(60)
    pygame.display.flip()
