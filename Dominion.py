
# Created By Wesley Klock 2017
# All rights reserved
import sys
import pygame
import socket
import random

class Card(object):

    card_dict = {
        "Copper": ["Treasure", 0, "+1 Currency", 1],
        "Silver": ["Treasure", 3, "+2 Currency", 2],
        "Gold": ["Treasure", 6, "+3 Currency", 3],
        "Estate": ["Victory", 2, "+1 Victory Points", 1],
        "Duchy": ["Victory", 5, "+3 Victory Points", 3],
        "Province": ["Victory", 8, "+6 Victory Points", 6],
        "Curse": ["Victory", 0, "-1 Victory Points", -1],
        "Cellar": ["Action", 2, "+1 Action \n Discard any number of cards. \n+1 Card per card discarded."],
        "Chapel": ["Action", 2, "Trash up to 4 cards from your hand."],
        "Moat": ["Action Reaction", 2, "+2 Cards\nWhen another player plays an Attack card, you may reveal this from your hand. If you do, you are unaffected by that Attack."],
        "Smithy": ["Action", 4, "+3 Cards"],
        "Village": ["Action", 3, "+2 Cards\n+1 Action"]}

    def __init__(self, name):
        self.name = name
        self.type = Card.card_dict[name][0]
        self.price = Card.card_dict[name][1]
        self.text = Card.card_dict[name][2]
        if self.type is "Treasure":
            self.value = Card.card_dict[name][3] # nice
        if self.type is "Victory":
            self.points = Card.card_dict[name][3]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def effect(self, game, player):
        if self.type == "Treasure":
            player.money += self.value
            print("Your currency is now {}!".format(player.money))
        else:
            print("This card has no effect. It is not an action card.")

class Copper(Card): pass
class Silver(Card): pass
class Gold(Card): pass
class Estate(Card): pass
class Duchy(Card): pass
class Province(Card): pass
class Curse(Card): pass

class Cellar(Card):
    def effect(self, game, player):
        print("Your current hand is:", player.hand)
        instring = input("Enter the cards you would like to discard \n If none just press enter \n-> ").strip("\n")
        indexes = instring.split()
        count = 0
        discard_list = []
        for index in indexes:
            try:
                num = int(index)
                discard_list.append(player.hand[num - 1])
            except:
                print("This card is not in your hand!")
        for card in discard_list:
            player.discard_card(player.hand, card)
        player.draw_card(len(indexes))

class Chapel(Card):
    def effect(self, game, player):
        count = 0

        while True:
            if count > 4 or not player.hand:
                break

            print("You can trash", 4 - count, "more cards.")
            print("Your current hand is:", player.hand)
            instring = input("Enter the cards you would like to trash. \nIf none just press enter\n-> ").strip("\n")
            print()
            indexes = instring.split()

            if indexes:
                trash_list = []
                for index in indexes:
                    try:
                        num = int(index)
                        trash_list.append(player.hand[num - 1])
                    except:
                        print("This card is not in your hand!")
                if len(trash_list) > 4:
                    print("You tried to trash more than 4 cards, the first 4 trashable cards will be trashed.")
                    trash_list = trash_list[0, 4]
                for card in trash_list:
                    player.trash_card(player.hand, card)
                    count += 1
            else:
                break

            print()

        print("The trash is now:", Player.trash)

class Moat(Card):
    def effect(self, game, player):
        player.draw_card(2)

class Smithy(Card):
    def effect(self, game, player):
        player.draw_card(3)

class Village(Card):
    def effect(self, game, player):
        player.draw_card(2)
        player.actions += 1

class Game(object):

    def __init__(self, num_players):
        self.supply = {
            "Copper": 60,
            "Silver": 40,
            "Gold": 30,
            "Estate": 8 if num_players <= 2 else 12,
            "Duchy": 8 if num_players <= 2 else 12,
            "Province": 8 if num_players <= 2 else 12,
            "Curse": (num_players - 1) * 10,
            "Cellar": 10,
            "Chapel": 10,
            "Moat": 1,
            "Smithy" : 0,
            "Village": 0} # initialize which cards are in the Game

        self.trash = Player.trash
        self.players = []
        self.current_index = 0

        for i in range(num_players):
            name = input("Enter name of player: ")
            self.players.append(Player(name))

        random.shuffle(self.players)

        # deal cards to players
        starting_cards = {"Copper": 7, "Estate" : 3}
        initial_hand = []
        for card, num in starting_cards.items():
            for i in range(num):
                initial_hand.append(self.create_card(card))
            # check if card is a Victory Card
            if card not in [x for x in Card.card_dict.keys() if Card.card_dict[x][0] is "Victory"]:
                self.supply[card] -= num

        for player in self.players:
            random.shuffle(initial_hand)
            player.deal_cards(initial_hand)
            player.draw_card(5)

    def __str__(self):
        return "Players: {}\nSupply: {}\nTrash: {}".format(self.players, self.supply, Player.trash)

    def create_card(self, card):
        return eval(card + "('" + card + "')")

    def turn(self):
        player = self.players[self.current_index]
        print("\n{} is going!".format(player.name))
        print(player)

        self.display_supply()

        print("Entering action phase ;)")
        while player.actions > 0 and self.has_action_cards(player):
            print("You have {} actions remaining...".format(player.actions))
            self.display_cards(player)
            index = self.play_input(player)
            player.play_action_card(self, player.hand[index - 1])
            if self.is_gameover(): return

        print("\nEntering buy phase :)")
        player.calculate_money()
        while player.buys > 0:
            self.display_supply()
            print("You have", player.money, "currency to spend :)")
            buy = self.buy_input(player)
            player.buy_card(self, buy)
            if self.is_gameover(): return

        print("Entering cleanup phase :|")
        player.reset()
        print(player)

        input("Hit ENTER to move on to next turn: ")

    def play_game(self):
        print("\n\nSTARTING GAME")
        while not self.is_gameover():
            self.turn()
            self.current_index = (self.current_index + 1) % len(self.players)
        self.print_gameover()

    def print_gameover(self):
        print("\nGAME OVER\n")
        winner = self.players[0]
        for player in self.players:
            print("{}: {} Victory Points".format(player.name, player.victory_pts))
            if player.victory_pts > winner.victory_pts:
                winner = player
        print("\n{} won the game with {} victory points!".format(winner.name, winner.victory_pts))

    def is_gameover(self):
        return self.supply["Province"] == 0 or sum(x is 0 for x in self.supply.values()) >= 3

    def has_action_cards(self, player):
        return any([card.type.startswith("Action") for card in player.hand])

    def play_input(self, player):
        index = int(input("Enter the index (1-{}) of the card you want to play: ".format(len(player.hand))))

        while index < 1 or index > len(player.hand):
            print("\nThat index is not in your hand.")
            index = int(input("Enter the index (1-{}) of the card you want to play: ".format(len(player.hand))))
        return index

    def buy_input(self, player):
        index = int(input("Enter the index (1-{}) of the card you want to buy: ".format(len(self.supply))))

        while index < 1 or index > len(self.supply) or self.supply[list(self.supply.keys())[index - 1]] == 0:
            if index < 1 or index > len(self.supply):
                print("\nThat index is not in the supply.")
            else:
                print("\nYou cannot buy that card. There are no cards remaining.")
            index = int(input("Enter the index (1-{}) of the card you want to buy: ".format(len(self.supply))))

        return list(self.supply.keys())[index - 1]

    def display_cards(self, player):
        # TODO: tfw catherine is lazy
        print("Cards in your hand: ", player.hand)

    def display_supply(self):
        print()
        print("SUPPLY".center(38))
        count = 1
        for card, num in self.supply.items():
            print("#{}".format(count).ljust(3), card.ljust(15), "${}".format(Card.card_dict[card][1]).ljust(10), str(num).ljust(2), "left")
            count += 1
        print()


class Player(object):

    trash = {}

    def __init__(self, name):
        self.name = name

        self.deck = []
        self.discard = []
        self.hand = []
        self.viewable = []
        self.in_play = []

        self.actions = 1
        self.money = 0
        self.buys = 1
        self.victory_pts = 0

    def print_all(self):
        print("Name:{}\nDeck: {}\nDiscard: {}\nViewable: {}\nIn Play: {}\nHand: {}\nYou currently have: {} actions, {} buys, {} victory points".format(self.name, self.deck, self.discard, self.viewable, self.in_play, self.hand, self.actions, self.money, self.victory_pts))

    def __str__(self):
        return "Discard: {}\nHand: {}\nYou currently have: {} actions, {} buys, {} victory points".format(self.discard, self.hand, self.actions, self.money, self.victory_pts)

    def change_victory_pts(self, points):
        self.victory_pts += points

    def reset(self):
        for card in self.in_play:
            self.discard_card(self.in_play, card)
        while len(self.hand) > 0:
            self.discard.append(self.hand.pop())
        self.draw_card(5)

        self.actions = 1
        self.money = 0
        self.buys = 1

    def check_victory(self, card):
        if card.type == "Victory":
            self.victory_pts += card.points

    def deal_cards(self, cards):
        for card in cards:
            self.check_victory(card)
            self.deck.append(card)

    def add_to_deck(self, cards):
        for card in cards:
            self.deck.insert(0, card)

    def shuffle_cards(self):
        random.shuffle(self.discard)

    def buy_card(self, game, card):
        if self.money < Card.card_dict[card][1]:
            print("\nNot enough money to purchase the card.\n")
        else:
            self.gain_card(game.create_card(card))
            game.supply[card] -= 1
            self.money -= Card.card_dict[card][1]
            self.buys -= 1

    # adds a card to discard pile
    def gain_card(self, carditem):
        self.check_victory(carditem)
        self.discard.append(carditem)
        # needs to be changed to account for other players and differences in message
        print("You have gained 1 {}! It has been added to your discard pile.".format(carditem.name))

    # peeks at n number of cards on top of the pile
    def set_view(self, times):
        for i in range(times):
            self.viewable.insert(0, self.deck.pop(0))

    def reset_view(self):
        for i in range(len(self.viewable)):
            self.deck.insert(0, self.viewable.pop(0))

    def draw_card(self, times):
        for i in range(times):
            if len(self.deck) == 0:
                self.shuffle_cards()
                self.deck = self.discard
                self.discard = []
            self.hand.append(self.deck.pop(0))
            print("You drew 1 {}!".format(self.hand[-1]))
        print("Your hand is now: {}".format(self.hand))

    def add_to_hand(self, cards, carditem):
        self.check_victory(carditem)
        self.hand.append(carditem)
        cards.remove(carditem)

    def return_deck(self, cards, carditem):
        self.deck.insert(0, carditem)
        cards.remove(carditem)

    def discard_card(self, cards, carditem):
        self.discard.append(carditem)
        print("You have discarded 1 {}! It has been added to your discard pile.".format(carditem.name))
        cards.remove(carditem)

    def trash_card(self, cards, carditem):
        if carditem.name in Player.trash:
            Player.trash[carditem.name] += 1
        else:
            Player.trash[carditem.name] = 1
        print("You have trashed 1 {}! It has been added to the trash pile.".format(carditem.name))
        cards.remove(carditem)

    def play_action_card(self, game, carditem):
        print("\nYou played {}!\n".format(carditem.name))
        self.in_play.append(carditem)
        self.hand.remove(carditem)
        carditem.effect(game, self)
        self.actions -= 1

    def play_react(self, carditem):
        if carditem.type.contains("Reaction"):
            carditem.react()
        else:
            print("Fuck you, that is not a Reaction card!")

    def calculate_money(self):
        for card in self.hand:
            if card.type is "Treasure":
                self.money += card.value

def main():

    game = Game(2)
    game.play_game()


    '''
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
    '''

main()
