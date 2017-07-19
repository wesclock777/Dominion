
# Created By Wesley Klock 2017
# All rights reserved
import sys
import pygame
import socket
import random
import time


class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket()
        self.s.bind((host,port))
        self.clients = []

    def send_message(self,message,client):
        message = str(message)
        client = self.clients[client][0]
        client.send(message.encode('utf-8'))
        print ("Sent:", message)
        time.sleep(.005)

    def receive_message(self, client):
        client = self.clients[client][0]
        message = client.recv(8192)
        message = message.decode('utf-8')
        if message == "q":
            print("User has disconnected!")
            return message

        print ("Received:", str(message))
        return message

    def ask_message(self, message, client):
        message = "Asking : "+ message
        self.send_message(message,client)
        return self.receive_message(client)

    def send_all(self, message):
        for i in range(len(self.clients)):
            self.send_message(message, i)

    def send_multi(self, message, clients):
        for index in clients:
            if index < len(self.clients) and index > 0:
                self.send_message(message, index)

    def send_other(self, message, client):
        self.send_multi(message, self.get_other(client))

    def get_other(self, client):
        indexes = []
        for i in range(len(self.clients)):
            if i != client:
                indexes.append(i)
        return indexes

    # returns list of messages by index of all clients
    def receive_all(self):
        message_dict = {}
        for i in range(len(self.clients)):
            messages[i] = self.receive_message(i)
        return messages

    def receive_multi(self, clients):
        message_dict = {}
        for index in clients:
            if index < len(self.clients) and index > 0:
                message_dict[index] = self.receive_message(index)
        return message_dict

    def recieve_other(self, client):
        return self.recieve_multi(self.get_other(client))

    def close_sockets(self):
        for client in self.clients:
            client[0].close()

server= Server('192.168.0.42', 5000)

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
            server.send_message("Your currency is now {}!".format(player.money), player.index)
        else:
            server.send_message("This card has no effect. It is not an action card.", player.index)

class Copper(Card): pass
class Silver(Card): pass
class Gold(Card): pass
class Estate(Card): pass
class Duchy(Card): pass
class Province(Card): pass
class Curse(Card): pass

class Cellar(Card):
    def effect(self, game, player):
        server.send_message("Your current hand is:", player.index)
        test_receive = True
        while test_receive == True:
            instring = server.ask_message(("Enter the cards you would like to discard \n If none just press enter \n-> "), player.index).strip("\n")
            test_receive = game.check_receive(instring, player)

        indexes = instring.split()
        count = 0
        discard_list = []
        for index in indexes:
            try:
                num = int(index)
                discard_list.append(player.hand[num - 1])
            except:
                server.send_message("This card is not in your hand!", player.index)
        for card in discard_list:
            player.discard_card(player.hand, card)
        player.draw_card(len(indexes))

class Chapel(Card):
    def effect(self, game, player):
        count = 0

        while True:
            if count > 4 or not player.hand:
                break

            server.send_message("You can trash "+(4 - count)+" more cards.", player.index)
            server.send_message("Your current hand is: "+ str(player.hand) + str(player.index))
            test_receive = True
            while test_receive == True:
                instring = server.ask_message("Enter the cards you would like to trash. \nIf none just press enter\n-> ", player.index).strip("\n")
                test_receive = game.check_receive(instring, player)

            server.send_message("",player.index)
            indexes = instring.split()

            if indexes:
                trash_list = []
                for index in indexes:
                    try:
                        num = int(index)
                        trash_list.append(player.hand[num - 1])
                    except:
                        server.send_message("This card is not in your hand!", player.index)
                if len(trash_list) > 4:
                    server.send_message("You tried to trash more than 4 cards, the first 4 trashable cards will be trashed.",player.index)
                    trash_list = trash_list[0, 4]
                for card in trash_list:
                    player.trash_card(player.hand, card)
                    count += 1
            else:
                break

            server.send_message("", player.index)

        server.send_message("The trash is now:", Player.trash)

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

    def __init__(self):
        self.players = []

        print("Waiting for first player to connect...")
        server.s.listen(1)
        c, addr = server.s.accept()
        server.clients.append((c, addr))
        name = server.ask_message("Enter name of player 1: ", 0)
        self.players.append(Player(name, 0))
        num_players = int(server.ask_message("How many players are there?", 0))

        i = 1
        while(len(server.clients) < num_players):
            print("Waiting for clients.......Currently connected:", str(len(server.clients)))
            server.s.listen(1)
            c, addr = server.s.accept()
            print("Connection from :" + str(addr))
            server.clients.append((c,addr))
            name = server.ask_message("Enter name of player {}: ".format(i + 1), i)
            self.players.append(Player(name, i))
            i += 1

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
        self.current_index = random.randint(0, num_players - 1)

        # deal cards to players
        starting_cards = {"Copper": 7, "Estate" : 3}
        self.initial_hand = []
        for card, num in starting_cards.items():
            for i in range(num):
                self.initial_hand.append(self.create_card(card))
            # check if card is a Victory Card
            if card not in [x for x in Card.card_dict.keys() if Card.card_dict[x][0] is "Victory"]:
                self.supply[card] -= num

    def minus_supply(self, card):
        self.supply[card] -= 1
        if self.is_gameover():
            self.print_gameover()
            server.close_sockets()
            sys.exit()

    def __str__(self):
        return "Players: {}\nSupply: {}\nTrash: {}".format(self.players, self.supply, Player.trash)

    def create_card(self, card):
        return eval(card + "('" + card + "')")

    def turn(self):
        player = self.players[self.current_index]
        server.send_all("\n{} is going!\n".format(player.name))

        self.display_supply(player)

        server.send_message("\nEntering action phase ;)", player.index)
        while player.actions > 0 and self.has_action_cards(player):
            server.send_message("You have {} actions remaining...".format(player.actions), player.index)
            self.display_cards(player)
            index = self.play_input(player)
            player.play_action_card(self, player.hand[index - 1])

        server.send_message("\nEntering buy phase :)", player.index)
        player.calculate_money()
        while player.buys > 0:
            self.display_supply(player)
            server.send_message("You have {} currency to spend :)".format(player.money), player.index)
            buy = self.buy_input(player)
            player.buy_card(self, buy)

        server.send_message("\nEntering cleanup phase :|\n", player.index)
        player.reset()
        server.send_message(player, player.index)

        test_receive = True
        while test_receive == True:
            instring = server.ask_message("Hit ENTER to move on to next turn: ", player.index)
            test_receive = self.check_receive(instring, player)

    def play_game(self):
        server.send_all("\n\nSTARTING GAME\n")

        for player in self.players:
            random.shuffle(self.initial_hand)
            player.deal_cards(self.initial_hand)
            player.draw_card(5)

        while True:
            self.turn()
            self.current_index = (self.current_index + 1) % len(self.players)

    def print_gameover(self):
        server.send_all("\nGAME OVER\n")
        winner = self.players[0]
        for player in self.players:
            server.send_all("{}: {} Victory Points".format(player.name, player.victory_pts))
            if player.victory_pts > winner.victory_pts:
                winner = player
        server.send_message("\nCONGRATS!!! You won the game with {} victory points!".format(winner.victory_pts), winner.index)
        server.send_other("\n{} won the game with {} victory points!".format(winner.name, winner.victory_pts), winner.index)

    def is_gameover(self):
        return self.supply["Province"] == 0 or sum(x is 0 for x in self.supply.values()) >= 3

    def has_action_cards(self, player):
        return any([card.type.startswith("Action") for card in player.hand])

    def play_input(self, player):

        test_receive = True
        while test_receive == True:
            instring = server.ask_message("Enter the index (1-{}) of the card you want to play: ".format(len(player.hand)), player.index)
            test_receive = self.check_receive(instring, player)
        index = int(instring)

        while index < 1 or index > len(player.hand):
            server.send_message("\nThat index is not in your hand.", player.index)
            test_receive = True
            while test_receive == True:
                instring = server.ask_message("Enter the index (1-{}) of the card you want to play: ".format(len(player.hand)), player.index)
                test_receive = self.check_receive(instring, player)
            index = int(instring)

        return index

    def buy_input(self, player):
        test_receive = True
        while test_receive == True:
            instring = server.ask_message("Enter the index (1-{}) of the card you want to buy: ".format(len(self.supply)), player.index)
            test_receive = self.check_receive(instring, player)
        index = int(instring)

        while index < 1 or index > len(self.supply) or self.supply[list(self.supply.keys())[index - 1]] == 0:
            if index < 1 or index > len(self.supply):
                server.send_message("\nThat index is not in the supply.",player.index)
            else:
                server.send_message("\nYou cannot buy that card. There are no cards remaining.", player.index)

            while test_receive == True:
                instring = server.ask_message("Enter the index (1-{}) of the card you want to buy: ".format(len(self.supply)), player.index)
                test_receive = self.check_receive(instring, player)
            index = int(instring)

        return list(self.supply.keys())[index - 1]

    def display_cards(self, player):
        # TODO: tfw catherine is lazy
        server.send_message("Cards in your hand: "+ str(player.hand), player.index)

    def display_supply(self, player):
        server.send_message("", player.index)
        server.send_message("\nSUPPLY".center(38), player.index)
        count = 1
        for card, num in self.supply.items():
            output = "#{} ".format(count).ljust(4) + card.ljust(15) + " ${} ".format(Card.card_dict[card][1]).ljust(12) + str(num).ljust(2) + " left"
            server.send_message(output, player.index)
            count += 1
        server.send_message("", player.index)

    def check_receive(self, message, player):
        message= message.title()
        if message.startswith("Help"):
            cardname = message.split(" ")[1]
            server.send_message(Card.card_dict[cardname][2], player.index)
            server.send_message("", player.index)
            return True
        if message.startswith("Supply"):
            self.display_supply(player)
            server.send_message("", player.index)
            return True
        return False


class Player(object):

    trash = {}

    def __init__(self, name, index):
        self.name = name
        self.index = index

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
        server.send_message("Name:{}\nDeck: {}\nDiscard: {}\nViewable: {}\nIn Play: {}\nHand: {}\nYou currently have: {} actions, {} buys, {} victory points".format(self.name, self.deck, self.discard, \
        self.viewable, self.in_play, self.hand, self.actions, self.money, self.victory_pts), self.index)

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
            server.send_message("\nNot enough currency to purchase the card.\n", self.index)
        else:
            self.gain_card(game.create_card(card))
            game.minus_supply(card)
            self.money -= Card.card_dict[card][1]
            self.buys -= 1

    # adds a card to discard pile
    def gain_card(self, carditem):
        self.check_victory(carditem)
        self.discard.append(carditem)
        server.send_message("You have gained 1 {}! It has been added to your discard pile.".format(carditem.name), self.index)
        server.send_other("{} has gained 1 {}! It has been added to their discard pile.".format(self.name, carditem.name), self.index)

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
            server.send_message("You drew 1 {}!".format(self.hand[-1]), self.index)
        server.send_other("{} drew {} cards!".format(self.name, times), self.index)
        server.send_message("Your hand is now: {}".format(self.hand), self.index)

    def add_to_hand(self, cards, carditem):
        self.check_victory(carditem)
        self.hand.append(carditem)
        cards.remove(carditem)

    def return_deck(self, cards, carditem):
        self.deck.insert(0, carditem)
        cards.remove(carditem)

    def discard_card(self, cards, carditem):
        self.discard.append(carditem)
        server.send_message("You have discarded 1 {}! It has been added to your discard pile.".format(carditem.name), self.index)
        server.other("{} has discarded 1 card! It has been added to their discard pile.".format(self.name), self.index)
        cards.remove(carditem)

    def trash_card(self, cards, carditem):
        if carditem.name in Player.trash:
            Player.trash[carditem.name] += 1
        else:
            Player.trash[carditem.name] = 1
        server.send_message("You have trashed 1 {}! It has been added to the trash pile.".format(carditem.name), self.index)
        server.send_other("{} have trashed 1 {}! It has been added to the trash pile.".format(self.name, carditem.name), self.index)
        cards.remove(carditem)

    def play_action_card(self, game, carditem):
        server.send_message("\nYou played {}!\n".format(carditem.name), self.index)
        server.send_message("\n{} played {}!\n".format(self.name, carditem.name), self.index)
        self.in_play.append(carditem)
        self.hand.remove(carditem)
        carditem.effect(game, self)
        self.actions -= 1

    def play_react(self, carditem):
        if carditem.type.contains("Reaction"):
            carditem.react()
        else:
            server.send_message("Fuck you, that is not a Reaction card!", self.index)

    def calculate_money(self):
        for card in self.hand:
            if card.type is "Treasure":
                self.money += card.value

def main():

    game = Game()
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
