import streamlit as st
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

import random
import pathlib
import time


# List of all possible cards
suits = ['♠', '♥', '♦', '♣']
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
all_cards = [f"{rank}{suit}" for suit in suits for rank in ranks]

# Deck class
class Deck:
    def __init__(self):
        self.cards = all_cards.copy()
        self.shuffle()
    def shuffle(self):
        random.shuffle(self.cards)
    def draw(self, n):
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn
    def put_back(self, cards):
        self.cards.extend(cards)
        self.shuffle()


st.title("🃏 Mind-Reading Card Trick!")


# Session state to track progress
if 'step' not in st.session_state:
    st.session_state.step = 0  # 0: not started, 1: showing first cards, 2: showing second cards
if 'deck' not in st.session_state:
    st.session_state.deck = Deck()
if 'first_cards' not in st.session_state:
    st.session_state.first_cards = []
if 'second_cards' not in st.session_state:
    st.session_state.second_cards = []
if 'reveal_count' not in st.session_state:
    st.session_state.reveal_count = 0
if 'reveal_count2' not in st.session_state:
    st.session_state.reveal_count2 = 0
if 'camera_on' not in st.session_state:
    st.session_state.camera_on = False


# File path variables
CSS_FILE = "magic_style.css"
DECK_IMAGE_URL = "https://deckofcardsapi.com/static/img/back.png"
CARD_IMAGE_BASE_URL = "https://deckofcardsapi.com/static/img/"


# Helper to map card code to Deck of Cards API code
def card_to_api_code(card):
    rank_map = {'A': 'A', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': '0', 'J': 'J', 'Q': 'Q', 'K': 'K'}
    suit_map = {'♠': 'S', '♥': 'H', '♦': 'D', '♣': 'C'}
    # 10 is '0' in API
    if card[:-1] == '10':
        rank = '0'
    else:
        rank = rank_map[card[:-1]]
    suit = suit_map[card[-1]]
    return f"{rank}{suit}"

def show_deck_and_cards_grid(cards, reveal_count, empty_slots=0, deck_empty=False):
        # Inject external CSS file
        css_path = pathlib.Path("magic_style.css")
        if css_path.exists():
                with open(css_path) as f:
                        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        # 1x2 grid: left for deck, right for cards (2:5 ratio)
        st.markdown("""
        <div class='main-grid'>
            <div class='deck-col'>
                {deck_html}
            </div>
            <div class='cards-col'>
                <div class='card-row'>
                    {row1}
                </div>
                <div class='card-row'>
                    {row2}
                </div>
            </div>
        </div>
        """.format(
                deck_html=(
                        "<div class='deck-box empty'></div><div class='deck-label'>Deck</div>"
                        if deck_empty else
                        f"<div class='deck-box'><img src='{DECK_IMAGE_URL}' alt='Deck' class='deck-img'/></div><div class='deck-label'>Deck</div>"
                ),
                row1=''.join([
                    "<div class='card-box'>" + (f"<img src='{CARD_IMAGE_BASE_URL}{card_to_api_code(cards[i])}.png' alt='' class='card-img'/>" if i < reveal_count else '') + "</div>"
                    for i in range(5)
                ]),
                row2=''.join([
                    "<div class='card-box'>" + (f"<img src='{CARD_IMAGE_BASE_URL}{card_to_api_code(cards[i])}.png' alt='' class='card-img'/>" if i < reveal_count else '') + "</div>"
                    for i in range(5, 10)
                ]),
        ), unsafe_allow_html=True)

def render_grid(deck_html, card_html):
    st.markdown(f"""
    <div class='main-grid'>
        <div class='deck-col'>
            {deck_html}
        </div>
        <div class='cards-col'>
            <div class='card-row'>
                {card_html[0]}
            </div>
            <div class='card-row'>
                {card_html[1]}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if 'put_back_phase' not in st.session_state:
    st.session_state.put_back_phase = False
if 'put_back_count' not in st.session_state:
    st.session_state.put_back_count = 0


# Step 0: Start button, then Camera, then shuffle and show cards
if st.session_state.step == 0:
    st.write("Welcome to the Mind-Reading Card Trick!")
    if 'start_clicked' not in st.session_state:
        st.session_state.start_clicked = False
    if 'camera_img' not in st.session_state:
        st.session_state.camera_img = None
    if 'deck_fadein' not in st.session_state:
        st.session_state.deck_fadein = 0  # 0: transparent, 1-10: fade in steps

    if not st.session_state.start_clicked:
        if st.button("Start the Trick"):
            st.session_state.start_clicked = True
            st.rerun()
    elif not st.session_state.camera_on:
        if st.button("Turn On Camera"):
            st.session_state.camera_on = True
            st.rerun()
    elif st.session_state.camera_on:
        # Show empty grid first
        st.write('<div style="text-align:center;font-size:1.3em;font-weight:bold;margin-bottom:16px;">Chosen deck of 10 random</div>', unsafe_allow_html=True)
        empty_deck_html = "<div class='deck-box empty'></div>"
        empty_card_row = "".join(["<div class='card-box empty'></div>" for _ in range(5)])
        if 'empty_grid_phase' not in st.session_state:
            st.session_state.empty_grid_phase = 0
        if st.session_state.empty_grid_phase == 0:
            render_grid(empty_deck_html, [empty_card_row, empty_card_row])
            if st.button("Show Deck"):
                st.session_state.empty_grid_phase = 1
                st.rerun()
        else:
            deck_html = f"<div class='deck-box empty'><img src='{DECK_IMAGE_URL}' alt='Deck' class='deck-img'/></div>"
            render_grid(deck_html, [empty_card_row, empty_card_row])
            time.sleep(0.5)
            # Reset and shuffle deck, draw first 10 cards
            st.session_state.deck = Deck()
            st.session_state.first_cards = st.session_state.deck.draw(10)
            st.session_state.step = 1
            st.session_state.reveal_count = 0
            st.session_state.empty_grid_phase = 0
            st.rerun()

# Step 1: Reveal first set of cards slowly
elif st.session_state.step == 1:
    with st.expander(""):
        cam_placeholder = st.empty()
        img = cam_placeholder.camera_input("")
        st.markdown(
            """
            <div class='cover-camera-opaque'></div>
            """,
            unsafe_allow_html=True
        )
    st.write("Look at the cards below and just **glare** at one card. Don't click or type anything, just remember it in your mind!")
    if not st.session_state.put_back_phase:
        show_deck_and_cards_grid(st.session_state.first_cards, st.session_state.reveal_count)
        if st.session_state.reveal_count < 10:
            time.sleep(0.7)
            st.session_state.reveal_count += 1
            st.rerun()
        else:
            if st.button("I've chosen my card!"):
                st.session_state.put_back_phase = True
                st.session_state.put_back_count = 0
                st.session_state.camera_on = False
                # Simulate processing with a random delay
                processing_time = random.uniform(1.2, 2.8)
                with st.spinner('Processing...'):
                    time.sleep(processing_time)
                st.rerun()
    else:
        # Animate putting back cards (empty slots)
        if (
            st.session_state.put_back_count < 10
        ):
            show_deck_and_cards_grid(
                st.session_state.first_cards,
                0,
                empty_slots=st.session_state.put_back_count,
                deck_empty=(st.session_state.put_back_count == 10)
            )
            time.sleep(0.3)
            st.session_state.put_back_count += 1
            st.rerun()
        else:
            # Remove last card box after processing
            if 'show_9_boxes' not in st.session_state or not st.session_state.show_9_boxes:
                empty_card_row_1 = "".join(["<div class='card-box empty'></div>" for _ in range(5)])
                empty_card_row_2 = "".join(["<div class='card-box empty'></div>" for _ in range(4)])  # Only 4 boxes in second row
                deck_html = "<div class='deck-box empty'></div>"
                render_grid(deck_html, [empty_card_row_1, empty_card_row_2])
                st.session_state.show_9_boxes = True
                st.rerun()
            else:
                # Now proceed to next step
                st.session_state.deck.put_back(st.session_state.first_cards)
                if 'second_cards' not in st.session_state or not st.session_state.second_cards:
                    # Remove the 10 shown cards from the deck, then draw 9
                    remaining_cards = [c for c in all_cards if c not in st.session_state.first_cards]
                    st.session_state.second_cards = random.sample(remaining_cards, 9)
                st.session_state.step = 2
                st.session_state.reveal_count2 = 0
                st.session_state.put_back_phase = False
                st.session_state.put_back_count = 0
                st.session_state.deck_fadeout = 10
                st.session_state.show_9_boxes = False
                st.rerun()

# Step 2: Reveal second set of cards slowly
elif st.session_state.step == 2:
    st.write("Let me read your mind... 🔮")
    st.write("I have magically removed your card!")
    show_deck_and_cards_grid(st.session_state.second_cards, st.session_state.reveal_count2)
    if st.session_state.reveal_count2 < 9:
        time.sleep(0.7)
        st.session_state.reveal_count2 += 1
        st.rerun()
    else:
        if st.button("Try Again"):
            st.session_state.step = 0
            st.session_state.reveal_count = 0
            st.session_state.reveal_count2 = 0
            st.session_state.first_cards = random.sample(all_cards, 9)
            st.session_state.second_cards = []
            st.rerun()
            st.stop()
