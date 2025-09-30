import streamlit as st
import json
import os
import math

LEADERBOARD_FILE = "leaderboard.json"

# ---------------- Leaderboard Helpers ---------------- #
def init_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_leaderboard(lb):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f, indent=4)

def update_leaderboard(winner, player1, player2):
    lb = init_leaderboard()
    for p in [player1, player2]:
        if p not in lb:
            lb[p] = {"Wins": 0, "Losses": 0, "Ties": 0}

    if winner == "Tie":
        lb[player1]["Ties"] += 1
        lb[player2]["Ties"] += 1
    else:
        lb[winner]["Wins"] += 1
        loser = player2 if winner == player1 else player1
        lb[loser]["Losses"] += 1

    save_leaderboard(lb)
    return lb

# ---------------- Game Logic ---------------- #
def check_winner(board, player):
    return any(all(cell == player for cell in row) for row in board) or \
           any(all(board[r][c] == player for r in range(3)) for c in range(3)) or \
           all(board[i][i] == player for i in range(3)) or \
           all(board[i][2 - i] == player for i in range(3))

def is_full(board):
    return all(cell != " " for row in board for cell in row)

def minimax(board, depth, is_maximizing):
    if check_winner(board, "O"):  # Computer wins
        return 1
    if check_winner(board, "X"):  # Human wins
        return -1
    if is_full(board):
        return 0

    if is_maximizing:
        best_score = -math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] == " ":
                    board[r][c] = "O"
                    score = minimax(board, depth + 1, False)
                    board[r][c] = " "
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] == " ":
                    board[r][c] = "X"
                    score = minimax(board, depth + 1, True)
                    board[r][c] = " "
                    best_score = min(score, best_score)
        return best_score

def best_move(board):
    best_score = -math.inf
    move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == " ":
                board[r][c] = "O"
                score = minimax(board, 0, False)
                board[r][c] = " "
                if score > best_score:
                    best_score = score
                    move = (r, c)
    return move

# ---------------- Streamlit App ---------------- #
def tic_tac_toe():
    st.set_page_config(page_title="Smart Tic-Tac-Toe", page_icon="⭕")
    st.title("⭕❌ Smart Tic-Tac-Toe")
    st.markdown("Play against a friend or the computer AI (unbeatable!) with a live leaderboard.")

    # Game mode
    mode = st.radio("Choose Mode:", ["Two Players", "Play vs Computer"])

    if "board" not in st.session_state:
        st.session_state.board = [[" " for _ in range(3)] for _ in range(3)]
        st.session_state.current = "X"
        st.session_state.winner = None
        st.session_state.player1 = ""
        st.session_state.player2 = ""
        st.session_state.mode = mode
        st.session_state.game_started = False

    if st.session_state.mode != mode:  # Reset if mode changed
        st.session_state.board = [[" " for _ in range(3)] for _ in range(3)]
        st.session_state.current = "X"
        st.session_state.winner = None
        st.session_state.player1 = ""
        st.session_state.player2 = ""
        st.session_state.mode = mode
        st.session_state.game_started = False

    # Player setup
    if mode == "Two Players":
        if not st.session_state.game_started:
            p1 = st.text_input("Enter Player 1 (X) Name:", "")
            p2 = st.text_input("Enter Player 2 (O) Name:", "")
            if st.button("Start Game"):
                if p1.strip() and p2.strip():
                    st.session_state.player1 = p1.strip()
                    st.session_state.player2 = p2.strip()
                    st.session_state.game_started = True
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter names for both players.")
        else:
            player1 = st.session_state.player1
            player2 = st.session_state.player2
    else:
        st.session_state.player1 = "You (X)"
        st.session_state.player2 = "Computer (O)"
        st.session_state.game_started = True
        player1, player2 = st.session_state.player1, st.session_state.player2

    # If game hasn't started yet, stop rendering
    if not st.session_state.game_started:
        return

    board = st.session_state.board
    current = st.session_state.current
    player1, player2 = st.session_state.player1, st.session_state.player2

    st.subheader(f"🎮 {player1 if current=='X' else player2}'s Turn ({current})")

    # Game board
    for r in range(3):
        cols = st.columns(3)
        for c in range(3):
            if cols[c].button(board[r][c] if board[r][c] != " " else "-", key=f"{r}{c}"):
                if board[r][c] == " " and not st.session_state.winner:
                    board[r][c] = current
                    if check_winner(board, current):
                        st.session_state.winner = player1 if current == "X" else player2
                        update_leaderboard(st.session_state.winner, player1, player2)
                    elif is_full(board):
                        st.session_state.winner = "Tie"
                        update_leaderboard("Tie", player1, player2)
                    else:
                        st.session_state.current = "O" if current == "X" else "X"
                    st.rerun()

    # Computer AI move
    if mode == "Play vs Computer" and current == "O" and not st.session_state.winner:
        move = best_move(board)
        if move:
            r, c = move
            board[r][c] = "O"
            if check_winner(board, "O"):
                st.session_state.winner = player2
                update_leaderboard(player2, player1, player2)
            elif is_full(board):
                st.session_state.winner = "Tie"
                update_leaderboard("Tie", player1, player2)
            else:
                st.session_state.current = "X"
            st.rerun()

    # Show results
    if st.session_state.winner:
        if st.session_state.winner == "Tie":
            st.success("🤝 It's a Tie!")
        else:
            st.success(f"🏆 {st.session_state.winner} Wins!")

    # Restart button
    if st.button("🔄 Restart Game"):
        st.session_state.board = [[" " for _ in range(3)] for _ in range(3)]
        st.session_state.current = "X"
        st.session_state.winner = None
        st.session_state.game_started = False
        st.rerun()

    # Leaderboard
    st.subheader("📊 Leaderboard")
    leaderboard = init_leaderboard()
    if leaderboard:
        st.table(leaderboard)
    else:
        st.info("No games played yet.")

if __name__ == "__main__":
    tic_tac_toe()
