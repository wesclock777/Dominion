
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
        self.viewable = []
        self.inplay = []

        self.actions = 1
        self.money = 0
        self.buys = 1

    def buyCard(self, carditem):
        if self.buys < 1:
            print("Not enough buys left.")
        elif self.money < carditem.value:
            print("Not enough money to purchase the card.")
        else:
            self.gainCard(carditem)
            self.money -= carditem.value
            self.buys -= 1

    # adds a card to discard pile
    def gainCard(self, carditem):
        self.discard.append(carditem)

    # peeks at n number of cards on top of the pile
    def setView(self, times):
        for i in range(times):
            self.viewable.insert(0, self.deck.pop(0))

    def resetView(self):
        for i in range(len(self.viewable)):
            self.deck.insert(0, self.viewable.pop(0))

    def drawCard(self, times):
        for i in range(times):
            self.hand.append(self.deck.pop(0))

    def addToHand(self, cards, carditem):
        self.hand.append(carditem)
        cards.remove(carditem)

    def returnDeck(self, cards, carditem):
        self.deck.insert(0, carditem)
        cards.remove(carditem)

    def discard(self, cards, carditem):
        self.discard.append(carditem)
        cards.remove(carditem)

    def trashCard(self, cards, carditem):
        self.trash.append(carditem)
        cards.remove(carditem)

    def playCard(self, cards, carditem):
        if carditem.type.contains("Currency"):
            carditem.effect()
            self.inplay.append(carditem)
            cards.remove(carditem)
        elif self.actions == 0:
            print("Fuck you, you don't have enough actions!")
        else:
            carditem.effect()
            self.inplay.append(carditem)
            cards.remove(carditem)
            self.actions -= 1

    def playReact(self, carditem):
        if carditem.type.contains("Reaction"):
            carditem.react()
        else:
            print("Fuck you, that is not a Reaction card!")

class Card(object):

    cards = ["Cellar", "Chapel", "Moat", "Chancellor", "Village", "Woodcutter", "Workshop", "Bureaucrat", "Feast"\
    "Gardens", "Moneylender", "Remodel", "Smithy", "Spy", "Thief", "Throne Room", "Council Room", "Festival", "Laboratory"\
    "Library", "Market", "Mine", "Witch", "Adventurer"]

    def __init__(self, name, player, otherplayers):

        self.name = name
        self.text = ""
        self.type = None
        self.value = 0
        self.player = player
        self.otherplayers = otherplayers

    def effect(self):
        print("This card has no effect.")

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

class Moat(Card):
    def __init__(self, player, otherplayers):
        self.name =  "Moat"
        self.text = "+2 Cards\nWhen another player plays an Attack card, you may reveal this from your hand. If you do, you are unaffected by that Attack."
        self.value = 2
        self.player = player
        self.otherplayers = otherplayers
        self.type = "Action Reaction"

    def effect(self):
        self.player.drawCArd

class Moat(Card):
    def __init__(self, player, otherplayers):
        self.name =  ""
        self.text = ""
        self.value = 2
        self.player = player
        self.otherplayers = otherplayers
        self.type = "Action"

    def effect(self):

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
