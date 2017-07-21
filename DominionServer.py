
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
        time.sleep(.07)

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
        message = "Asking: "+ message
        self.send_message(message,client)
        return self.receive_message(client)

    def send_all(self, message):
        for i in range(len(self.clients)):
            self.send_message(message, i)

    def send_multi(self, message, clients):
        for index in clients:
            if index < len(self.clients) and index >= 0:
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
            if index < len(self.clients) and index >= 0:
                message_dict[index] = self.receive_message(index)
        return message_dict

    def recieve_other(self, client):
        return self.recieve_multi(self.get_other(client))

    def close_sockets(self):
        for client in self.clients:
            client[0].close()

server= Server('10.246.53.77', 5000)

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
            "Moat": 10,
            "Smithy" : 10,
            "Village": 10,
            "Chancellor": 10,
            "Workshop": 10,
            "Bureaucrat": 10,
            "Feast": 10} # initialize which cards are in the Game

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
        server.send_message("\nIt is now your turn!", player.index)
        server.send_other("\n{} is going!".format(player.name), player.index)

        server.send_message(player, player.index)

        server.send_message("\nEntering action phase ;)", player.index)
        self.display_supply(player)

        while player.actions > 0 and self.has_action_cards(player):
            server.send_message("\nYou have {} actions remaining...".format(player.actions), player.index)
            self.display_cards(player)
            index = self.play_input(player)
            if index == None:
                break
            player.play_action_card(self, player.hand[index - 1])

        server.send_message("\nEntering buy phase :)", player.index)
        player.calculate_money()
        self.display_supply(player)
        old_buys = player.buys
        while player.buys > 0:
            if player.buys != old_buys:
                self.display_supply(player)
                old_buys = player.buys
            server.send_message("\nYou have {} currency to spend :)".format(player.money), player.index)
            buy = self.buy_input(player)
            if buy != None:
                player.buy_card(self, buy)
            else:
                break

        server.send_message("\nEntering cleanup phase :|\n", player.index)
        player.reset()

        self.get_input_generic("\nHit ENTER to move on to next turn.", player)
        server.send_all("\n" + "-" * 60)

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
        server.send_all("\n~~ GAME OVER ~~\n")
        winner = self.players[0]
        for player in self.players:
            server.send_all("{}: {} Victory Points".format(player.name, player.victory_pts))
            if player.victory_pts > winner.victory_pts:
                winner = player
        server.send_message("\nCONGRATS!!! You won the game with {} victory points!".format(winner.victory_pts), winner.index)
        server.send_other("\n{} won the game with {} victory points!".format(winner.name, winner.victory_pts), winner.index)

    def is_gameover(self):
        return self.supply["Province"] == 0 or self.get_empty_supply() >= 3

    def get_empty_supply(self):
        return sum(x is 0 for x in self.supply.values())

    def has_action_cards(self, player):
        return any([card.type.startswith("Action") for card in player.hand])

    def play_input(self, player):

        message = "\nEnter the index (1-{}) of the card you want to play\nHit ENTER to exit action phase:".format(len(player.hand))

        index = self.get_input(message, player)

        while index != None and (index < 1 or index > len(player.hand)):
            server.send_message("\nThat index is not in your hand.", player.index)
            index = self.get_input(message, player)

        return index

    def buy_input(self, player):
        message = "Enter the index (1-{}) of the card you want to buy\nHit ENTER to exit buy phase:".format(len(self.supply))

        index = self.get_input(message, player)

        try:
            while index < 1 or index > len(self.supply) or self.supply[list(self.supply.keys())[index - 1]] == 0:
                if index < 1 or index > len(self.supply):
                    server.send_message("\nThat index is not in the supply.",player.index)
                else:
                    server.send_message("\nYou cannot buy that card. There are no cards remaining.", player.index)

                index = self.get_input(message, player)
            return list(self.supply.keys())[index - 1]
        except:
            return index

    def display_cards(self, player):
        # TODO: tfw catherine is lazy
        server.send_message("Cards in your hand: "+ str(player.hand), player.index)

    def display_supply(self, player):
        server.send_message("\n" + "SUPPLY".center(38), player.index)
        count = 1
        for card, num in self.supply.items():
            output = "#{} ".format(count).ljust(4) + card.ljust(15) + " ${} ".format(Card.card_dict[card][1]).ljust(12) + str(num).ljust(2) + " left"
            server.send_message(output, player.index)
            count += 1
        server.send_message("", player.index)

    def check_receive(self, message, player):
        message = message.title()
        if message.startswith("Help"):
            cardname = message.split(" ")[1]
            try:
                server.send_message(Card.card_dict[cardname][2], player.index)
                server.send_message(" ", player.index)
            except:
                server.send_message("Oops! {} is not a card in the game!\n".format(cardname), player.index)
            return True
        if message.startswith("Supply"):
            self.display_supply(player)
            server.send_message(" ", player.index)
            return True
        if message.startswith("Info"):
            server.send_message(player, player.index)
            server.send_message(" ", player.index)
            return True
        return False

    # generic input function that checks for HELP AND STASH
    def get_input_generic(self, message, player):
        received = True
        while received:
            instring = server.ask_message(message, player.index)
            received = self.check_receive(instring, player)
        return instring


    # forces input to be an integer
    # checks for HELP and STASH
    def get_input(self, message, player):
        correct = True
        while True:
            received = True
            while received:
                instring = server.ask_message(message, player.index)
                received = self.check_receive(instring, player)
            try:
                return int(instring)
            except:
                if instring == " ":
                    return None
                else:
                    server.send_message("\nThat was not an integer.", player.index)
                    correct = False
            if correct:
                return instring

    def check_int(self, message, index, input):
        while True:
            try:
                return int(input)
            except:
                server.send_message("\nThat was not an integer.", index)
                server.ask_message(message, index)

    def get_input_range(self, message, player, min, max):
        while True:
            index = self.get_input(message, player)
            if index == None:
                return None
            elif index >= min and index <= max:
                return index
            else:
                server.send_message("\nOops! You can't choose card #{}.", index)

    def input_yn(self, message, player):
        while True:
            received = True
            while received:
                instring = server.ask_message(message, player.index).lower()
                received = self.check_receive(instring, player)
            if instring in ["yes", "y"]:
                return True
            elif instring in ["no", "n"]:
                return False
            else:
                server.send_message("Please enter Y or N\n", player.index)

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
        return "\nDiscard: {}\nHand: {}\nYou currently have: {} actions, {} buys, {} victory points".format(self.discard, self.hand, self.actions, self.money, self.victory_pts)

    def money_effect(self, change):
        if change > 0:
            server.send_message("You have gained {} currency.".format(change), self.index)
            server.send_other("{} has gained {} currency.".format(change, self.name), self.index)
        else:
            server.send_message("You have lost {} currency.".format(-1 * change), self.index)
            server.send_other("{} has lost {} currency.".format(-1 * change, self.name), self.index)
        self.money += change
        server.send_message("Your currency is now {}.".format(self.money), self.index)

    def action_effect(self, change):
        if change > 0:
            server.send_message("You have gained {} action(s).".format(change), self.index)
            server.send_other("{} has gained {} action(s).".format(change, self.name), self.index)
        else:
            server.send_message("You have lost {} action(s).".format(-1 * change), self.index)
            server.send_other("{} has lost {} action(s).".format(-1 * change, self.name), self.index)
        self.actions += change
        server.send_message("You now have {} action(s).".format(self.actions), self.index)

    def buy_effect(self, change):
        if change > 0:
            server.send_message("You have gained {} buy(s).".format(change), self.index)
            server.send_other("{} has gained {} buy(s).".format(change, self.name), self.index)
        else:
            server.send_message("You have lost {} buy(s).".format(-1 * change), self.index)
            server.send_other("{} has lost {} buy(s).".format(-1 * change, self.name), self.index)
        self.buys += change
        server.send_message("You now have {} buy(s).".format(self.buys), self.index)

    def change_victory_pts(self, points):
        self.victory_pts += points

    def reset(self):
        for card in self.in_play:
            self.discard.append(card)
            self.in_play.remove(card)
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
            server.send_message("\nNot enough currency to purchase the card.", self.index)
        elif Card.card_dict[card][0] == "Curse":
            server.send_message("\nSorry, you cannot purchase curses.", self.index)
        else:
            self.gain_card(game.create_card(card))
            game.minus_supply(card)
            self.money -= Card.card_dict[card][1]
            self.buys -= 1

    # adds a card from supply to discard pile
    def gain_card(self, carditem):
        self.check_victory(carditem)
        self.discard.append(carditem)
        server.send_message("You have gained 1 {}! It has been added to your discard pile.".format(carditem.name), self.index)
        server.send_other("{} has gained 1 {}! It has been added to their discard pile.".format(self.name, carditem.name), self.index)

    # adds a card to from supply to hand
    def gain_hand_card(self, carditem):
        self.check_victory(carditem)
        self.hand.append(carditem)

        server.send_message("You have gained 1 {}! It has been added to your hand.\nYour hand is now: ".format(carditem.name, self.hand), self.index)
        server.send_other("{} has gained 1 {}! It has been added to their hand.".format(self.name, carditem.name), self.index)

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
        server.send_other("{} drew {} card(s)!".format(self.name, times), self.index)
        server.send_message("Your hand is now: {}".format(self.hand), self.index)

    # moves card from another part of player to hand
    def move_to_hand(self, cards, carditem):
        self.hand.append(carditem)
        cards.remove(carditem)

        server.send_other("{} moved 1 card to their hand.".format(self.name), self.index)
        server.send_message("{} has been moved to your hand.\nYour hand is now: {}".format(carditem.name, self.hand), self.index)

    def move_to_deck(self, cards, carditem):
        self.deck.insert(0, carditem)
        cards.remove(carditem)
        server.send_other("{} moved 1 card to the top of their deck.".format(self.name), self.index)
        server.send_message("{} has been moved to the top of your deck.".format(carditem.name), self.index)

    def discard_card(self, cards, carditem):
        self.discard.append(carditem)
        server.send_message("You have discarded 1 {}! It has been added to your discard pile.".format(carditem.name), self.index)
        server.send_other("{} has discarded 1 card! It has been added to their discard pile.".format(self.name), self.index)
        cards.remove(carditem)

    def discard_cards(self, cards, carditem_list):
        for carditem in carditem_list:
            self.discard.append(carditem)
            server.send_message("You have discarded 1 {}! It has been added to your discard pile.".format(carditem.name), self.index)
            cards.remove(carditem)
        server.send_other("{} has discarded {} card(s)! It has been added to their discard pile.".format(self.name, len(carditem_list)), self.index)

    def trash_card(self, cards, carditem):
        if carditem.name in Player.trash:
            Player.trash[carditem.name] += 1
        else:
            Player.trash[carditem.name] = 1
        server.send_message("You have trashed 1 {}! It has been added to the trash pile.".format(carditem.name), self.index)
        server.send_other("{} have trashed 1 {}! It has been added to the trash pile.".format(self.name, carditem.name), self.index)
        cards.remove(carditem)

    def play_action_card(self, game, carditem):
        if "Action" in carditem.type:
            server.send_message("\nYou played {}!\n".format(carditem.name), self.index)
            server.send_other("\n{} played {}!\n".format(self.name, carditem.name), self.index)
            self.in_play.append(carditem)
            self.hand.remove(carditem)
            carditem.effect(game, self)
            self.actions -= 1
        else:
            server.send_message("\nYou cannot play {}. It is not an action card!".format(carditem.name), self.index)

    def calculate_money(self):
        for card in self.hand:
            if card.type is "Treasure":
                self.money += card.value


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
        "Village": ["Action", 3, "+1 Card\n+2 Actions"],
        "Chancellor": ["Action", 3, "+$2\nYou may immediately put your deck into your discard pile."],
        "Woodcutter": ["Action", 3, "+1 Buy\n+$2"],
        "Workshop": ["Action", 3, "Gain a card costing up to $4."],
        "Bureaucrat": ["Action - Attack", 4, "Gain a silver card; put it on top of your deck\nEach other player reveals a Victory card from his hand and puts it on his deck."],
        "Feast": ["Action", 4, "Trash this card.\nGain a card costing up to $5."],
        "Gardens": ["Victory", 4, "Worth 1 Victory for every 10 cards in your deck.\n(Effect rounded down.)"]}

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
            player.money_effect(self.value)
        else:
            server.send_other("This card has no effect. It is not an action card.", player.index)
            server.send_message("This card has no effect. It is not an action card.", player.index)

    def obtain_card(self, game, player, cost):
        possible = [x for x in game.supply.keys() if game.supply[x] > 0 and Card.card_dict[x][1] <= cost]
        if possible:
            index = game.get_input_range("You can gain one of the following cards: {}\nPlease enter the card you would like to gain.\nIf none just press ENTER".format(print_list(possible)), player, 1, len(possible))
            if index != None:
                player.gain_card(game.create_card(possible[index - 1]))
                game.minus_supply(possible[index - 1])
            else:
                server.send_message("You choose not to gain a card.", player.index)
                server.send_other("{} choose not to gain a card.".format(player.name), player.index)
        else:
            server.send_message("There are no avaliable cards for you to gain.", player.index)
            server.send_other("There are no avaliable cards for {} to gain.".format(player.name), player.index)

    def check_react(self, other):
        prevented = False
        react = [x for x in other.hand if "Reaction" in x.type]
        if react:
            index = game.get_input_range("You have the following reaction cards: {}\nPlease enter the card you would like to react with.\nIf none just press ENTER".format(print_list(react)), other, 1, len(react))
            if index != None:
                prevented = react[index - 1].react()
            else:
                server.send_message("You choose not to react.", other.index)
        return prevented

class Copper(Card): pass
class Silver(Card): pass
class Gold(Card): pass
class Estate(Card): pass
class Duchy(Card): pass
class Province(Card): pass
class Curse(Card): pass

class Cellar(Card):
    def effect(self, game, player):
        server.send_message("Your current hand is: {}".format(player.hand), player.index)
        instring = game.get_input_generic("Enter the cards you would like to discard \nIf none just press ENTER", player).strip("\n")
        server.send_message(" ", player.index)

        if instring == " ":
            return
        else:
            indexes = instring.split()

        count = 0
        discard_list = []
        for index in indexes:
            try:
                num = int(index) - 1
                if num >= len(player.hand) or num < 0:
                    server.send_message("Did not process {}. It is not in your hand!".format(index), player.index)
                else:
                    discard_list.append(player.hand[num])
            except:
                server.send_message("{} is not an integer!".format(index), player.index)
        server.send_message(" ".format(index), player.index)
        player.discard_cards(player.hand, discard_list)
        player.draw_card(len(discard_list))

class Chapel(Card):
    def effect(self, game, player):
        count = 0

        while True:
            if count > 4 or not player.hand:
                break

            server.send_message("You can trash " + str(4 - count) + " more cards.", player.index)
            server.send_message("Your current hand is: {}".format(player.hand), player.index)

            instring = game.get_input_generic("Enter the cards you would like to trash \nIf none just press ENTER", player).strip("\n")
            server.send_message(" ", player.index)

            if instring == " ":
                return
            else:
                indexes = instring.split()

            if indexes:
                trash_list = []
                for index in indexes:
                    try:
                        num = int(index) - 1
                        if num >= len(player.hand) or num < 0:
                            server.send_message("Did not process {}. It is not in your hand!".format(index), player.index)
                        else:
                            trash_list.append(player.hand[num])
                    except:
                        server.send_message("{} is not an integer!".format(index), player.index)

                if len(trash_list) > 4:
                    server.send_message("You tried to trash more than 4 cards, the first 4 trashable cards will be trashed.",player.index)
                    trash_list = trash_list[0, 4]
                for card in trash_list:
                    player.trash_card(player.hand, card)
                    count += 1

            else:
                break

            server.send_message(" ", player.index)

class Moat(Card):
    def effect(self, game, player):
        player.draw_card(2)

class Smithy(Card):
    def effect(self, game, player):
        player.draw_card(3)

class Village(Card):
    def effect(self, game, player):
        player.draw_card(1)
        player.action_effect(2)

class Chancellor(Card):
    def effect(self, game, player):
        player.money_effect(2)
        input = game.input_yn("Immediately put your deck into your discard pile? (Y/N)", player)
        if input:
            player.discard.extend(player.deck)
            player.deck = []
            server.send_message("You have put your deck into your discard pile.", player.index)
            server.send_other("{} has put their deck into their discard pile.".format(player.name), player.index)

class Woodcutter(Card):
    def effect(self, game, player):
        player.buy_effect(1)
        player.money_effect(2)

class Workshop(Card):
    def effect(self, game, player):
        self.obtain_card(game, player, 4)

class Bureaucrat(Card):
    def effect(self, game, player):
        player.gain_card(game.create_card("Silver"))
        game.minus_supply("Silver")
        for other in [x for x in game.players if x != player]:
            prevented = self.check_react(other)
            while not prevented:
                victory = [x for x in other.hand if x.type == "Victory"]
                if len(victory) == 0:
                    server.send_message("You have no Victory cards.", other.index)
                    server.send_other("{} revealed a hand with no Victory cards.", other.index)
                elif len(victory) == 1:
                    other.move_to_deck(victory[0])
                else:
                    index = game.get_input_range("You have the following victory cards: {}\nPlease enter the card you would like to put on your deck.".format(print_list(victory)), other, 1, len(victory))
                    other.move_to_deck(victory[index - 1])

class Feast(Card):
    def effect(self, game, player):
        player.trash_card(player.in_play, self)
        self.obtain_card(5)

def print_list(items):
    output = ""
    for i in range(len(items)):
        output += "#{}: {}\n".format(i + 1, items[i])
    return output

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
