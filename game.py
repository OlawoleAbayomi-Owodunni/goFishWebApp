import cards
import random


deck = cards.build_deck()

computer = []
player = []
player_pairs = []
computer_pairs = []

for _ in range(7):
    computer.append(deck.pop())
    player.append(deck.pop())

player, pairs = cards.identify_remove_pairs(player)
player_pairs.extend(pairs)
computer, pairs = cards.identify_remove_pairs(computer)
computer_pairs.extend(pairs)


def show_player_hand():
    print("\nPlayers hand:")
    for n, card in enumerate(player):
        print(f"\tSelect {n} for {card}")


while True:
    player.sort()
    
    show_player_hand()
    choice = input(
        "\nPlease select the number for the card you want from the above list"
    )
    choice = int(choice)
    selection = player[int(choice)]
    value = selection[: selection.find(" ")]

    found_it = False
    for n, card in enumerate(computer):
        if card.startswith(value):
            found_it = n
            break

    if isinstance(found_it, bool):
        print("\nGo Fish!\n")
        player.append(deck.pop())
        print(f"You drew a {player[-1]}.")
        if len(deck) == 0:
            break
    else:
        print(f"Here is your card from the computer: {computer[n]}.")
        player.append(computer.pop(n))

    player, pairs = cards.identify_remove_pairs(player)
    player_pairs.extend(pairs)
    show_player_hand()

    if len(player) == 0:
        print("The Game is over. The player won.")
        break
    if len(computer) == 0:
        print("The Game is over. The computer won.")
        break

    card = random.choice(computer)
    value = card[: card.find(" ")]

    choice = input(f"\nFrom the computer: Do you have a {value}? (y/n) ")

    if choice in ["y", "Y", "yes", "YES", "Yes"]:
        for n, card in enumerate(player):
            if card.startswith(value):
                break
        computer.append(player.pop(n))
    else:
        computer.append(deck.pop())
        if len(deck) == 0:
            break

    computer, pairs = cards.identify_remove_pairs(computer)
    computer_pairs.extend(pairs)

    if len(computer) == 0:
        print("The Game is over. The computer won.")
        break
    if len(player) == 0:
        print("The Game is over. The player won.")
        break

if len(deck) == 0:
    print("Game over.")
    if len(player_pairs) == len(computer_pairs):
        print("It's a draw.")
    elif len(player_pairs) > len(computer_pairs):
        print("The Game is over. The player won.")
    else:
        print("The Game is over. The computer won.")
