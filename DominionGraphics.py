import sys
import pygame
import gc

class Button():
    def __init__(self, imagename, x,y, width, height, text):
        self.image = imagename
        self. image = pygame.image.load(imagename)
        self. imgage = pygame.transform.scale(self.image,(width,height))
        self.x = x
        self.y = y
        self.width =width
        self.height = height
        self.myfont = pygame.font.SysFont("monospace", 20, True, True)
        self.text = text

    def draw(self, screen):
        screen.blit(self.image, (self.x,self.y))
        largeText = pygame.font.Font('freesansbold.ttf',30)
        TextSurf, Text Rect = text_objects(self.text, largeText)
        TextRect.center =(self.x + self.width/2, self.y +self.height/2)
        screen.blit(TextSurf,TextRect )


    def listener(self,screen):
        mouse = pygame.mouse.get_pos()

        if (self.x+self.width > mouse[0] > self.x and self.y + \
        self.height >mouse[1]> self.y) and pygame.mouse.getpressed()[0] \
        == "MOUSEBUTTONDOWN":
            #button clicked
            #do something here


class CardGraphic():
    def __init__(self, imagename, x, y):
        self.image = imagename
        self.number = 8
        self.image = pygame.image.load(imagename).convert()
        self.image = pygame.transform.scale(self.image, (94,150))
        self.x = x
        self.y = y
        self.myfont =pygame.font.SysFont("monospace", 15, True, False)

    def draw(self, screen):
        screen.blit(self.image, (self.x,self.y))
        #remaining = self.myfont.render(str(self.number), 1, (218,165,32))
        remaining = self.myfont.render(str(self.number), 1, (255,0,0))
        pygame.draw.rect(screen,(255,255,255),(self.x+5,self.y+5,15,15))
        #pygame.draw.circle(screen, (105,105,105), (self.x+13, self.y+13), 10, 0)
        screen.blit(remaining, (self.x+5,self.y+5))


    def move(self, x, y):
        self.position = position.move(x,y)

def Checkbuttons():
    for obj in gc.get_objects():
        if isinstance(obj, Button):
            obj.draw(screen)
            obj.listener(screen)


def main():
    pygame.init()
    size = width, height = 1200, 600
    grey = 105, 105, 105
    screen = pygame.display.set_mode(size)
    cardsize = cardwidth, cardheight = 94 , 150

    background = pygame.image.load("ForestBackground.png")
    screen.blit(background, (0,0))

    ValidCards= ["Copper", "Curse", "Estate", "Silver", "Duchy", "Gold", "Province"\
    "Cellar", "Chapel", "Moat", "Harbinger", "Merchant", "Vassal", "Village", "Workshop"\
    , "Bureaucrat", "Gardens", "Militia", "Moneylender", "Poacher", "Remodel", "Smithy"\
    ,"Throne Room", "Bandit", "Council Room", "Festival", "Laboratory", "Library","Market"\
    "Mine", "Sentry", "Witch", "Artisan"]

    copper = CardGraphic("Copper.jpg", 0, 0)
    silver = CardGraphic("Silver.jpg", 0, 155)
    gold = CardGraphic("Gold.jpg", 0, 310)
    estate = CardGraphic("Estate.jpg", 125 ,0)
    duchy = CardGraphic("Duchy.jpg", 125 ,155)
    province = CardGraphic("Province.jpg",125 , 310)
    curse = CardGraphic("Curse.jpg", 250 ,0)
    inpt = ""

    while inpt !="q":
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        #screen.fill(grey)
        for obj in gc.get_objects():
            if isinstance(obj, CardGraphic):
                obj.draw(screen)
        pygame.display.update()
        pygame.time.wait(10)
        inpt= input("-->")
main()
