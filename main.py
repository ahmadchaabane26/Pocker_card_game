import random
from collections import Counter

# Card class
class Card:
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.value} of {self.suit}"

    def get_value_index(self):
        return Card.values.index(self.value)

# Deck class
class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in Card.suits for value in Card.values]
        random.shuffle(self.cards)

    def deal(self, num):
        dealt = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt

# Player class
class Player:
    def __init__(self, name, is_user=False):
        self.name = name
        self.hand = []
        self.is_user = is_user
        self.budget = 100 if is_user else None

    def receive_cards(self, cards):
        self.hand = cards

    def show_hand(self):
        return ', '.join(str(card) for card in self.hand)

    def evaluate_hand(self, community_cards):
        total = self.hand + community_cards
        values = [card.value for card in total]
        value_counts = Counter(values)

        # Check for pairs
        pairs = [val for val, count in value_counts.items() if count == 2]
        if pairs:
            highest_pair = max(pairs, key=lambda v: Card.values.index(v))
            return ('pair', Card.values.index(highest_pair))

        # Fallback to high card
        high_card = max(card.get_value_index() for card in total)
        return ('high_card', high_card)

# Game class
class PokerGame:
    def __init__(self, player1):
        self.deck = Deck()
        self.community_cards = []
        self.player1 = player1
        self.player2 = Player("Player 2")
        self.pot = 0
        self.last_budget = player1.budget

    def play(self):
        if self.player1.budget < 10:
            print("You don't have enough money to buy in. Game over.")
            return False

        self.last_budget = self.player1.budget
        self.pot = 20
        self.player1.budget -= 10

        self.player1.receive_cards(self.deck.deal(2))
        self.player2.receive_cards(self.deck.deal(2))

        print(f"\nYour hand: {self.player1.show_hand()}")
        print(f"{self.player2.name}'s hand: [Hidden Cards]")
        print(f"Your budget: ${self.player1.budget}")
        print(f"Pot: ${self.pot}")

        # Flop
        self.community_cards = self.deck.deal(3)
        print(f"\nFlop: {', '.join(str(card) for card in self.community_cards)}")
        if not self.bet_round("flop"): return True

        # Turn
        self.community_cards += self.deck.deal(1)
        print(f"Turn: {self.community_cards[3]}")
        if not self.bet_round("turn"): return True

        # River
        self.community_cards += self.deck.deal(1)
        print(f"River: {self.community_cards[4]}")
        if not self.bet_round("river"): return True

        print(f"\nCommunity Cards: {', '.join(str(card) for card in self.community_cards)}")
        print(f"{self.player2.name}'s hand revealed: {self.player2.show_hand()}\n")

        self.evaluate_winner()
        self.report_gain_or_loss()
        return True

    def bet_round(self, round_name):
        while True:
            action = input(f"\nAfter the {round_name}, do you want to raise ($10), stand, or fold? ").strip().lower()
            if action == 'raise':
                if self.player1.budget >= 10:
                    self.player1.budget -= 10
                    self.pot += 10
                    print(f"You raised. Pot is now ${self.pot}. Budget: ${self.player1.budget}")
                    print(f"\nCommunity Cards: {', '.join(str(card) for card in self.community_cards)}")
                    return True
                else:
                    print("You don't have enough to raise.")
            elif action == 'stand':
                print("You chose to stand.")
                print(f"\nCommunity Cards: {', '.join(str(card) for card in self.community_cards)}")
                return True
            elif action == 'fold':
                print("You folded. Player 2 wins this hand.\n")
                self.report_gain_or_loss(folded=True)
                return False
            else:
                print("Invalid input. Please type raise, stand, or fold.")

    def evaluate_winner(self):
        p1_rank, p1_score = self.player1.evaluate_hand(self.community_cards)
        p2_rank, p2_score = self.player2.evaluate_hand(self.community_cards)

        print(f"You have a {p1_rank.replace('_', ' ')}")
        print(f"{self.player2.name} has a {p2_rank.replace('_', ' ')}")

        rank_order = {'pair': 2, 'high_card': 1}
        if rank_order[p1_rank] > rank_order[p2_rank]:
            print(f"You win the pot of ${self.pot}!\n")
            self.player1.budget += self.pot
        elif rank_order[p2_rank] > rank_order[p1_rank]:
            print(f"{self.player2.name} wins the pot.\n")
        else:
            if p1_score > p2_score:
                print(f"You win with higher {p1_rank} and take ${self.pot}!\n")
                self.player1.budget += self.pot
            elif p2_score > p1_score:
                print(f"{self.player2.name} wins with higher {p2_rank}.\n")
            else:
                print("It's a tie! You get your $10 back.\n")
                self.player1.budget += 10  # Return initial buy-in

    def report_gain_or_loss(self, folded=False):
        change = self.player1.budget - self.last_budget
        if folded:
            print(f"You folded. Loss this round: ${-change}\n")
        elif change > 0:
            print(f"You gained ${change} this round.\n")
        elif change < 0:
            print(f"You lost ${-change} this round.\n")
        else:
            print("No gain or loss this round.\n")

# Main game loop
if __name__ == "__main__":
    print("♠ Welcome to Texas Hold'em Lite: Budget + Betting Rounds ♠")
    player1 = Player("You", is_user=True)

    while True:
        game = PokerGame(player1)
        continue_game = game.play()
        if continue_game is False:
            break
        again = input("Play another hand? (y/n): ").strip().lower()
        if again != 'y':
            print(f"You left the game with ${player1.budget}. Thanks for playing!")
            break
