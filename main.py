'''
Welcome to my poker simulator, this game was made for beginers to understand the simpliest form of poker. This includes the most common scenrios in poker including betting metrics,
card combinations, and mental fortitude. This poker game only evalutes high card and pairs. The way you play this game is simple: 

1. You are given a $100 budget (We do not encourage gambling addictions)
2. The dealer will give you your 2 cards, along with player 2 (The person you are versing)
3. Since there is an automatic buy in, $10 is taken from your $100 budget 
4. The flop is then shown to the player, and he is prompted to choose raise, stand, or fold (Mental Fortitude!)
    A. If the player is confident in his cards, he can raise the pot by $10.
    B. If the player is worried about his oponent, he can stand and keep the pot as it.
    C. If the player does not like what he sees, he can cut his losses and fold. The round ends here. 
8. Once the player decideds to advance then the next card in the flop will come out, prompting step 4 again. This will go on until 5 cards are in the flop, then the game will automatically end
9. Once the game is done, the winner will be annoucned along with your new budget. The game could keep going until you run out of money or leave the table. 

This game is known to be simple, but the mind complicates it. Good luck!

'''

import random
from collections import Counter

# Card class
class Card:
    # Establishing the deck of cards 
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']

    def __init__(self, suit, value):
        # Intilize the card number with it's suit 
        self.suit = suit
        self.value = value

    def __str__(self):
        # Returning the card number and it's suit 
        return f"{self.value} of {self.suit}"

    def get_value_index(self):
        # Refrencing the index of the card to later on compare its value 
        return Card.values.index(self.value)

# Deck class
class Deck:
    def __init__(self):
        # Creating all combination of cards, matching all the 4 suits to the 13 numbers. Which makes a 52 card deck
        self.cards = [Card(suit, value) for suit in Card.suits for value in Card.values]
        # Shuffle the cards to make them random when dealing
        random.shuffle(self.cards)

    def deal(self, num):
        # Dealing from the top of the deck 
        dealt = self.cards[:num]
        # Remove the cards that have been dealt from the deck 
        self.cards = self.cards[num:]
        # Return the dealt cards
        return dealt

# Player class
class Player:
    def __init__(self, name, is_user=False):
        # Display the players name
        self.name = name
        # Intilize list to store player 2's hand
        self.hand = []
        # boolean to distingish the User from player 2 
        self.is_user = is_user
        # Budget is set for the user and not player 2
        self.budget = 100 if is_user else None

    def receive_cards(self, cards):
        # Assign a new hand to the player
        self.hand = cards

    def show_hand(self):
        # Return the players hand as a string 
        return ', '.join(str(card) for card in self.hand)

    def evaluate_hand(self, community_cards):
        # Combine players hand with community cards to evalute best 5 card hand 
        total = self.hand + community_cards
        values = [card.value for card in total]
        value_counts = Counter(values)

        # Check for the highest pair in the combined 7 card combination 
        pairs = [val for val, count in value_counts.items() if count == 2]
        if pairs:
            # if there is a pair we return the hgihest ranked pair 
            highest_pair = max(pairs, key=lambda v: Card.values.index(v))
            return ('pair', Card.values.index(highest_pair))

        # if there is no paid, return the highest indivual card
        high_card = max(card.get_value_index() for card in total)
        return ('high_card', high_card)

# Game class
class PokerGame:
    # Setting up the requirments for the game 
    def __init__(self, player1):
        # create a new shuffled deck 
        self.deck = Deck()
        # List to hold the flop and the following cards 
        self.community_cards = []
        # Assign the players
        self.player1 = player1
        self.player2 = Player("Player 2")
        # Total pot for the current hand starts at 0 
        self.pot = 0
        # Intilizing budget for user
        self.last_budget = player1.budget
    # Allowing the user to play 
    def play(self):
        # Checking if the users budget is lower than 10 
        if self.player1.budget < 10:
            print("You don't have enough money to buy in. Game over.")
            return False
        #  Check the last budget of the player which is updated after every game
        self.last_budget = self.player1.budget
        # the pot is automatically at 20 at the start of the game due to buy in
        self.pot = 20
        # Subtracting 10 from the user budget
        self.player1.budget -= 10

        # Deal 2 cards to each player
        self.player1.receive_cards(self.deck.deal(2))
        self.player2.receive_cards(self.deck.deal(2))

        # Make the user hand visiable
        print(f"\nYour hand: {self.player1.show_hand()}")
        # Showcase budget to allow the user to raise, stand, or fold
        print(f"Your budget: ${self.player1.budget}")
        # Showcase pot to show total amount in
        print(f"Pot: ${self.pot}")

        # Showcase flop 
        self.community_cards = self.deck.deal(3)
        # Join the flop with the new cards that have been shown
        print(f"\nFlop: {', '.join(str(card) for card in self.community_cards)}")
        # handle betting round, stop if use folded
        if not self.bet_round("flop"): return True

        # Next card appears
        self.community_cards += self.deck.deal(1)
        print(f"Next Card: {self.community_cards[3]}")
        if not self.bet_round("turn"): return True

        # Next Card appears
        self.community_cards += self.deck.deal(1)
        print(f"River: {self.community_cards[4]}")
        if not self.bet_round("river"): return True

        # Combine all the cards and showcase full flop as community cards
        print(f"\nCommunity Cards: {', '.join(str(card) for card in self.community_cards)}")
        # Reveal the second players hand to showcase the winner
        print(f"{self.player2.name}'s hand revealed: {self.player2.show_hand()}\n")

        # call evaluate_winner to evaluate the two hands to compare them
        self.evaluate_winner()
        # Call report_gain_or_loss to see the new budget
        self.report_gain_or_loss()
        return True

    def bet_round(self, round_name):
        while True:
            # Prompt the player if they want to raise ($10), stand or fold
            action = input(f"\nAfter the {round_name}, do you want to raise ($10), stand, or fold? ").strip().lower()
            # if the user raises
            if action == 'raise':
                # check if the budget allows them to raise
                if self.player1.budget >= 10:
                    # Subtract from the budget
                    self.player1.budget -= 10
                    # Add 10 to the pot after subtracting from the user
                    self.pot += 10
                    # showcase new pot 
                    print(f"You raised. Pot is now ${self.pot}. Budget: ${self.player1.budget}")
                    #Showcase the new flop 
                    print(f"\nCommunity Cards: {', '.join(str(card) for card in self.community_cards)}")
                    return True
                else:
                    # If the budget is not within range they can not raise
                    print("You don't have enough to raise.")
            # If they stand
            elif action == 'stand':
                print("You chose to stand.")
                # showcase flop 
                print(f"\nCommunity Cards: {', '.join(str(card) for card in self.community_cards)}")
                return True
            # If they fold the rounds ends
            elif action == 'fold':
                print("You folded. Player 2 wins this hand.\n")
                # calculare how much the new budget 
                self.report_gain_or_loss(folded=True)
                return False
            else:
                # If the input is invalid prompt it again 
                print("Invalid input. Please type raise, stand, or fold.")

    def evaluate_winner(self):
        # Evaluate each players hand using the full flop, keep track of each score
        p1_rank, p1_score = self.player1.evaluate_hand(self.community_cards)
        p2_rank, p2_score = self.player2.evaluate_hand(self.community_cards)

        # Showcase what the user's results are (Pair or high rank or nothing)
        print(f"You have a {p1_rank.replace('_', ' ')}")
        # Showcase what player 2 results are
        print(f"{self.player2.name} has a {p2_rank.replace('_', ' ')}")

        # Intilize the differntial between a pair and high card
        rank_order = {'pair': 2, 'high_card': 1}
        # If the user's rank is above the player 2's rank
        if rank_order[p1_rank] > rank_order[p2_rank]:
            # The user wins the pot
            print(f"You win the pot of ${self.pot}!\n")
            # the pot is updated
            self.player1.budget += self.pot
        # if player 2's rank is higher than the user
        elif rank_order[p2_rank] > rank_order[p1_rank]:
            # player 2 wins the pot
            print(f"{self.player2.name} wins the pot.\n")
        # if its a tie then we comapre the strengh of the ranks of both 
        else:
            # if the user has a higher count than than player 2
            if p1_score > p2_score:
                # the user wins
                print(f"You win with higher {p1_rank} and take ${self.pot}!\n")
                self.player1.budget += self.pot
            elif p2_score > p1_score:
                # If player 2 score is better than the users, player 2 wins
                print(f"{self.player2.name} wins with higher {p2_rank}.\n")
            else:
                # its a tie and the money is split
                print("It's a tie! You get your $10 back.\n")
                self.player1.budget += 10  # Return initial buy-in
    # Calulating the neww budget
    def report_gain_or_loss(self, folded=False):
        # Calculate the net change in the users budget for this round
        change = self.player1.budget - self.last_budget
        if folded:
            # if folded just subtract that amount 
            print(f"You folded. Loss this round: ${-change}\n")
        elif change > 0:
            # If user won then they spent
            print(f"You gained ${change} this round.\n")
        elif change < 0:
            # if the user lost subtract it
            print(f"You lost ${-change} this round.\n")
        else:
            print("No gain or loss this round.\n")


if __name__ == "__main__":
    print("♠ Welcome to Poker - remember, your playing the player")
    # Labeling player 1 as you
    player1 = Player("You", is_user=True)

    # Turn the game into a loop 
    while True:
        # selecting the user as player 1 
        game = PokerGame(player1)
        # Start the game
        continue_game = game.play()
        # if they leave the game
        if continue_game is False:
            break
        # After sequence is done ask to stay on the table 
        again = input("Stay on the table? (y/n): ").strip().lower()
        # if not yet leave the table and end the game
        if again != 'y':
            print(f"You left the game with ${player1.budget}. Thanks for playing!")
            break
