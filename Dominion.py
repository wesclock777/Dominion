
# Created By Wesley Klock 2017
# All rights reserved
import sys
import pygame
import socket

class Player(object):
    trash = []

    def __init__(self, name):
        self.name = name
        self.deck = []
        self.discard = []
        self.hand = []
        self.actions = 1
        self.money = 0
        self.buys = 1

    def buyCard(self, carditem):
        if self.money < carditem.value:
            print("Not enough money to purchase the card.")
        else:
            self.addCard(carditem)
            self.money -= carditem.value

    def addCard(self , carditem):
        self.discard.append(carditem)

    def drawCard(self):
        drawn = self.deck.pop(0)
        return drawn

    def discard(self, carditem):
        self.hand.remove(carditem)
        self.discard.append(carditem)

    def trashCard(self, carditem):
        Player.trash.append(carditem)
        del carditem

    def playCard(self, carditem):
        if carditem.type.contains("Currency"):
            carditem.effect()
        elif self.actions == 0:
            print("Fuck you, you don't have enough actions!")
        else:
            carditem.effect()
            self.actions -= 1

    def playReact(self, carditem):
        if carditem.type.contains("Reaction"):
            carditem.effect()
        else:
            print("Fuck you, that is not a Reaction card!")

class Card(object):
    def __init__(self, name, player, otherplayers):

        self.name = name
        self.text = ""
        self.type = None
        self.value = 0
        self.player = player
        self.otherplayers = otherplayers

        cards = ["Cellar", "Chapel", "Moat", "Chancellor", "Village", "Woodcutter", "Workshop", "Bureaucrat", "Feast"\
        "Gardens", "Moneylender", "Remodel", "Smithy", "Spy", "Thief", "Throne Room", "Council Room", "Festival", "Laboratory"\
        "Library", "Market", "Mine", "Witch", "Adventurer"]
    def effect(self):

        '''
        if type=="Cellar":
            self.text = "+1 Action \n Discard any number of cards. \n +1 Card per card discarded."
            self.type = "Action"
        elif type =="Chapel":
            self.text = "Trash up to 4 cards from your hand."
            self.type = "Action"
        elif type =="Moat":
            self.text = "+2 Cards \n When another player plays an Attack card, you may reveal this from your hand. If you do, you are unaffected by that Attack."
            self.type "Action Reaction"
        elif type =="Chancellor"
        '''
class Cellar(Card):
    def __init__(self, player, otherplayers):
        self.name =  "Cellar"
        self.text = "+1 Action \n Discard any number of cards. \n +1 Card per card discarded."
        self.value = 2
        self.player = player
        self.otherplayers = otherplayers
        self.type = "Action"

    def effect(self):
        instring = input("Enter the cards you would like to discard \n If none just press enter \n-> ")
        indexs = instring.split(" ")
        count = 0
        for index in indexs:
            try:
                num = int(index)
                card = player.hand[num-1]
                player.discard(card)
                count+=1
            except:
                print("This card is not in your hand!")
        while count>0:
            player.drawCard()
            count-=1

class Chapel(Card):

    def __init__(self, player, otherplayers):
        self.name =  "Chapel"
        self.text = "Trash up to 4 cards from your hand."
        self.value = 2
        self.player = player
        self.otherplayers = otherplayers
        self.type = "Action"

    def effect(self):
        instring = input("Enter the cards you would like to trash \n If none just press enter \n-> ")
        indexs = instring.split(" ")
        while len(indexs) > 4 and len(indexs) != 0:
            print("You tried to trash more than 4 cards.")
            instring = input("Enter the cards you would like to trash \n If none just press enter \n-> ")
            indexs = instring.split(" ")
        for index in indexs:
            try:
                num = int(index)
                card = player.hand[num-1]
                player.trash(card)
                count+=1
            except:
                print("This card is not in your hand!")

def main():
    pygame.init()

    size = width, height = 600, 400
    speed = [5, 5]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    ball = pygame.image.load("ball.bmp")
    ballrect = ball.get_rect()

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        ballrect = ballrect.move(speed)
        if ballrect.left < 0 or ballrect.right > width:
            speed[0] = -speed[0]*(.999)
        if ballrect.top < 0 or ballrect.bottom > height:
            speed[1] = -speed[1]*(.999)

        screen.fill(black)
        screen.blit(ball, ballrect)
        pygame.display.flip()

main()
