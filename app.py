from flask import Flask, render_template, session, request, redirect, url_for, flash
import cards
import random
import dbconfig

app = Flask(__name__)
app.secret_key = "fdhghdfjghndfhgdlfgnh'odfahngldakfngdfljka"

def reset_state(username):
    session["deck"] = cards.build_deck()
    session["computer"] = []
    session["player"] = []
    session["player_pairs"] = []
    session["computer_pairs"] = []
    session["score"] = 0  # Initialize score
    session["multiplier"] = 1  # Initialize multiplier
    session["username"] = username  # Store username
    for _ in range(7):
        session["computer"].append(session["deck"].pop())
        session["player"].append(session["deck"].pop())
    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)

def update_score(pairs, player=True, go_fish=False, gave_computer=False):
    if pairs:
        session["multiplier"] += 1
    else:
        session["multiplier"] = 1

    if go_fish:
        session["score"] -= 2
    elif gave_computer:
        session["score"] += 2

    if player:
        session["score"] += 10 * session["multiplier"]
    else:
        session["score"] -= 5

    if session["score"] < 0:
        session["score"] = 0

def check_game_over():
    if len(session["player"]) == 0:
        flash("Game Over! The player won!")
        dbconfig.add_scores(session["username"], session["score"])
        return True
    elif len(session["computer"]) == 0:
        flash("Game Over! The computer won!")
        return True
    elif len(session["deck"]) == 0 and (len(session["player"]) == 0 or len(session["computer"]) == 0):
        flash("Game Over! The deck is empty and no more cards can be drawn.")
        return True
    return False

@app.get("/")
def start_menu():
    return render_template("startmenu.html", title="Welcome to Go Fish for the Web!")

usernames = []
@app.get("/startgame")
def start():
    username = request.args.get("username")
    if not username:
        username = usernames[0]
        usernames.clear
    usernames.append(username)
    reset_state(username)
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
    return render_template(
        "startgame.html",
        title="Welcome to GoFish for the Web!",
        cards=card_images,
        n_computer=len(session["computer"]),
        score=session["score"],
        multiplier=session["multiplier"],
    )

@app.route("/select/<value>", methods=["GET"])
def process_card_selection(value):
    found_it = False
    for n, card in enumerate(session["computer"]):
        if card.startswith(value):
            found_it = n
            break
    if isinstance(found_it, bool):
        flash("Go Fish!")
        if session["deck"]:
            session["player"].append(session["deck"].pop())
            flash(f"You drew a {session['player'][-1]}.")
            update_score([], player=True, go_fish=True)
        else:
            flash("The deck is empty, no card was drawn.")
    else:
        flash(f"Here is your card from the computer: {session['computer'][n]}.")
        session["player"].append(session["computer"].pop(n))
        update_score([], player=True)
    
    session["current_round_pairs"] = []

    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)
    session["current_round_pairs"].extend(pairs)
    update_score(pairs, player=True)

    if check_game_over():
        top_scores = dbconfig.get_top_scores()
        return render_template("gameover.html", title="Game Over", top_scores=top_scores, enumerate=enumerate)
    
    card = random.choice(session["computer"])
    the_value = card[: card.find(" ")]
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
    return render_template(
        "pickcard.html",
        title="The computer wants to know",
        value=the_value,
        cards=card_images,
        score=session["score"],
        multiplier=session["multiplier"],
    )

@app.route("/pick/<value>", methods=["GET"])
def process_the_picked_card(value):
    if value == "0":
        if session["deck"]:
            session["computer"].append(session["deck"].pop())
            update_score([], player=False, go_fish=True)
        else:
            flash("The deck is empty, no card was drawn.")
    else:
        for n, card in enumerate(session["player"]):
            if card.startswith(value.title()):
                break
        # flash(f"DEBUG: The picked card was at location {n}.")
        session["computer"].append(session["player"].pop(n))
        update_score([], player=False, gave_computer=True)
    
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)
    update_score(pairs, player=False)

    if check_game_over():
        top_scores = dbconfig.get_top_scores()
        return render_template("gameover.html", title="Game Over", top_scores=top_scores, enumerate=enumerate)
    
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]
    return render_template(
        "startgame.html",
        title="Keep playing!",
        cards=card_images,
        n_computer=len(session["computer"]),
        score=session["score"],
        multiplier=session["multiplier"],
    )

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    top_scores = dbconfig.get_top_scores()
    return render_template("leaderboard.html", title = "leaderboard", top_scores=top_scores, enumerate=enumerate)

if __name__ == "__main__":
    app.run(debug=True)
