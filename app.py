
import streamlit as st
import streamlit.components.v1 as components

import time
import uuid
import json
import base64

from pathlib import Path
from html import escape
from threading import Lock


# ============================================================
# 1. APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Carbon Rush",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DURATION = 30


# ============================================================
# 2. APPLICATION APPEARANCE
# ============================================================

st.html("""
<style>

/* Hide Streamlit's top toolbar */

header[data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* General layout */

html {
    font-size: 16px !important;
}

.stApp {
    background-color: #F5F8F4;
    color: #17382C;
}

.block-container {
    max-width: 1800px;
    padding-top: 0.8rem !important;
    padding-bottom: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

[data-testid="stVerticalBlock"] {
    gap: 0.65rem;
}

.stMarkdown p,
.stMarkdown li,
.stText,
.stTextInput input,
.stAlert p {
    font-size: 16px !important;
    line-height: 1.4;
}

[data-testid="stWidgetLabel"] p {
    font-size: 16px !important;
    font-weight: 600;
}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    font-size: 14px !important;
    line-height: 1.4;
}

[data-testid="stExpander"] summary p {
    font-size: 15px !important;
}

h1 {
    font-size: 34px !important;
    color: #174638 !important;
}

h2 {
    font-size: 26px !important;
    color: #174638 !important;
    padding-top: 0.4rem !important;
    padding-bottom: 0.3rem !important;
}

h3 {
    font-size: 22px !important;
    color: #174638 !important;
}


/* Buttons and inputs */

div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 8px;
    font-size: 16px !important;
    font-weight: 600;
    min-height: 40px;
}

div[data-testid="stButton"] p,
div[data-testid="stFormSubmitButton"] p {
    font-size: 16px !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[role="option"] {
    font-size: 16px !important;
}


/* Compact main header */

.header-logo {
    width: 225px;
    height: auto;
    max-height: 50px;
    object-fit: contain;
    flex-shrink: 0;
}

.header-divider {
    width: 1px;
    height: 38px;
    background: rgba(255, 255, 255, 0.4);
}

.game-header {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    flex-wrap: wrap;
    gap: 22px;

    background: linear-gradient(
        120deg,
        #123D32,
        #20694D
    );

    padding: 12px 22px;
    border-radius: 12px;
    margin-bottom: 10px;
}

.game-header h1 {
    color: #FFFFFF !important;
    font-size: 32px !important;
    font-weight: 800;
    letter-spacing: 1px;
    margin: 0;
    padding: 0 !important;
}

.game-header p {
    color: #D2EBDD !important;
    font-size: 16px !important;
    margin: 0;
    padding: 0;
}


/* Participant name */

.participant-name {
    font-size: 16px;
    color: #496356;
    margin: 2px 0 6px 0;
}


/* Original footprint cards */

.footprint-card {
    background: #FFFFFF;
    border: 1px solid #D9E5DC;
    border-radius: 12px;
    padding: 12px;
    min-height: 120px;
    text-align: center;
}

.footprint-icon {
    font-size: 29px;
}

.footprint-category {
    font-size: 17px;
    font-weight: 700;
    color: #174638;
}

.footprint-value {
    font-size: 28px;
    font-weight: 800;
    color: #B94040;
    margin: 4px 0;
}

.footprint-name {
    font-size: 15px;
    line-height: 1.4;
    color: #496356;
}


/* Total original footprint */

.total-footprint {
    background: #FBE8E6;
    border: 1px solid #EBC0BC;
    border-radius: 12px;
    padding: 10px;
    margin-top: 4px;
    text-align: center;
}

.total-footprint-label {
    font-size: 17px;
    font-weight: 600;
    color: #993B3B;
}

.total-footprint-value {
    font-size: 36px;
    color: #B94040;
    font-weight: 800;
}


/* Combined results panel */

.result-panel {
    position: relative;
    overflow: hidden;

    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: 22px;

    background: #FFFFFF;
    border: 1px solid #D9E5DC;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 4px;
}


/* Achievement panel on the left */

.achievement-panel {
    text-align: center;
    padding: 10px 4px;
}

.achievement-emoji {
    font-size: 58px;
    line-height: 1.2;
    margin-bottom: 5px;
}

.achievement-title {
    font-size: 30px;
    color: #174638;
    font-weight: 800;
}

.score-number {
    font-size: 68px;
    font-weight: 900;
    line-height: 1.2;
    margin: 6px 0;
}

.score-label {
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.7px;
    color: #496356;
}

.score-message {
    font-size: 16px;
    margin-top: 12px;
    color: #17382C;
    line-height: 1.4;
}


/* Three coloured boxes on the right */

.summary-metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    align-items: stretch;
}

.result-metric {
    border-radius: 12px;
    padding: 12px 8px;
    min-height: 130px;
    text-align: center;
}

.result-metric:last-child {
    grid-column: 1 / 3;
    width: calc(50% - 5px);
    justify-self: center;
}

.result-metric-icon {
    font-size: 30px;
    line-height: 1.2;
    margin-bottom: 5px;
}

.result-metric-label {
    font-size: 16px;
    font-weight: 700;
    line-height: 1.3;
}

.result-metric-value {
    font-size: 32px;
    font-weight: 800;
    margin-top: 7px;
}

.result-metric-unit {
    font-size: 15px;
    font-weight: 500;
}


/* Individual category results */

.impact-card {
    background: #FFFFFF;
    border: 1px solid #D9E5DC;
    border-radius: 12px;
    padding: 12px;
    min-height: 320px;
}

.impact-title {
    font-size: 21px;
    color: #174638;
    font-weight: 800;
    text-align: center;
    margin-bottom: 10px;
}

.impact-label {
    font-size: 14px;
    color: #63786B;
    margin-top: 8px;
}

.impact-original {
    font-size: 16px;
    font-weight: 700;
    color: #B94040;
    line-height: 1.4;
}

.impact-solution {
    font-size: 16px;
    font-weight: 700;
    line-height: 1.4;
}

.impact-reduction {
    font-size: 32px;
    font-weight: 800;
    text-align: center;
    margin: 10px 0 0 0;
}

.impact-status {
    font-size: 15px;
    text-align: center;
    font-weight: 700;
    margin-bottom: 10px;
}

.impact-bar-label {
    font-size: 15px;
    font-weight: 600;
    margin-top: 8px;
    margin-bottom: 4px;
}

.impact-bar-background {
    background: #E6ECE7;
    height: 10px;
    border-radius: 6px;
    overflow: hidden;
}

.impact-bar-fill {
    height: 100%;
    border-radius: 6px;
}

.impact-saved {
    text-align: center;
    font-size: 16px;
    font-weight: 700;
    margin-top: 10px;
}

.impact-explanation {
    font-size: 14px;
    line-height: 1.45;
    color: #496356;
    margin-top: 10px;
    border-top: 1px solid #D9E5DC;
    padding-top: 9px;
}


/* Compact leaderboard */

.leaderboard-header {
    font-size: 27px;
    font-weight: 800;
    color: #174638;
}

.leaderboard-description {
    font-size: 14px;
    color: #63786B;
    margin-bottom: 10px;
}

.leaderboard-count {
    background: #FFFFFF;
    border: 1px solid #D9E5DC;
    border-radius: 10px;
    text-align: center;
    padding: 10px;
    margin-bottom: 8px;
}

.leaderboard-count-label {
    font-size: 16px;
    color: #496356;
}

.leaderboard-count-value {
    font-size: 29px;
    font-weight: 800;
    color: #174638;
}

.leaderboard-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 5px;
    table-layout: fixed;
}

.leaderboard-table th {
    font-size: 15px;
    font-weight: 700;
    color: #496356;
    padding: 6px;
    text-align: left;
}

.leaderboard-table td {
    background: #FFFFFF;
    padding: 9px 6px;
    font-size: 16px;
    font-weight: 600;
    overflow-wrap: anywhere;
}

.leaderboard-table td:first-child {
    border-radius: 7px 0 0 7px;
    text-align: center;
}

.leaderboard-table td:last-child {
    border-radius: 0 7px 7px 0;
    text-align: right;
    color: #258052;
    font-weight: 800;
}

.leaderboard-table .rank-one td {
    background: #FFF0C9;
}

.leaderboard-table .rank-two td {
    background: #E9EDF0;
}

.leaderboard-table .rank-three td {
    background: #F5E2D2;
}


/* Confetti inside the result panel */

.confetti-piece {
    position: absolute;
    top: -30px;
    width: 12px;
    height: 18px;
    border-radius: 2px;
    z-index: 999;
    pointer-events: none;
    animation-name: confetti-fall;
    animation-timing-function: linear;
    animation-fill-mode: both;
}

@keyframes confetti-fall {

    0% {
        transform: translateY(-30px) rotate(0deg);
        opacity: 0;
    }

    5% {
        opacity: 1;
    }

    90% {
        opacity: 1;
    }

    100% {
        transform: translateY(600px) rotate(1080deg);
        opacity: 0;
    }
}


/* Responsive layout */

@media (max-width: 900px) {

    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .game-header {
        gap: 6px;
    }

    .game-header h1 {
        font-size: 27px !important;
    }

    .result-panel {
        gap: 10px;
        padding: 12px;
    }

    .score-number {
        font-size: 52px;
    }

    .achievement-title {
        font-size: 24px;
    }

    .result-metric-value {
        font-size: 26px;
    }
}

@media (max-width: 600px) {

    .result-panel {
        grid-template-columns: 1fr;
    }
}

@media (prefers-reduced-motion: reduce) {

    .confetti-piece {
        display: none;
    }
}


/* Scrollable Top 30 leaderboard */

.leaderboard-scroll {
    max-height: 500px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #258052 #E7EFE8;
}

</style>
""")


# ============================================================
# 3. TRANSPORT FOOTPRINT DATABASE
# ============================================================

# Name, distance, emission factor, distance category

TRANSPORT = {
    "T01": ("Petrol car (1 km)", 1, 0.16, "Short"),
    "T02": ("Motorcycle (2 km)", 2, 0.09, "Short"),
    "T03": ("GrabCar (3 km)", 3, 0.20, "Short"),
    "T04": ("Electric car (4 km)", 4, 0.13, "Short"),
    "T05": ("Hybrid car (5 km)", 5, 0.12, "Short"),
    "T06": ("Petrol car (5 km)", 5, 0.16, "Short"),

    "T07": ("Petrol car (15 km)", 15, 0.16, "Medium"),
    "T08": ("Motorcycle (20 km)", 20, 0.09, "Medium"),
    "T09": ("GrabCar (25 km)", 25, 0.20, "Medium"),
    "T10": ("Electric car (30 km)", 30, 0.13, "Medium"),
    "T11": ("Hybrid car (40 km)", 40, 0.12, "Medium"),
    "T12": ("Petrol car (50 km)", 50, 0.16, "Medium"),

    "T13": ("Domestic flight (250 km)", 250, 0.14, "Long"),
    "T14": ("Domestic flight (350 km)", 350, 0.14, "Long"),
    "T15": ("Domestic flight (450 km)", 450, 0.14, "Long")
}


TRANSPORT_ACTIONS = {
    "TA01": ("Walking", 0.00, ["Short"]),

    "TA02": ("Cycling", 0.00, ["Short"]),

    "TA03": (
        "Motorcycle", 0.09,
        ["Short", "Medium"]
    ),

    "TA04": (
        "Public bus", 0.10,
        ["Short", "Medium"]
    ),

    "TA05": (
        "Carpool (4 people)", 0.04,
        ["Short", "Medium", "Long"]
    ),

    "TA06": (
        "MRT", 0.04,
        ["Short", "Medium"]
    ),

    "TA07": (
        "Electric car", 0.13,
        ["Short", "Medium", "Long"]
    ),

    "TA08": (
        "Hybrid car", 0.12,
        ["Short", "Medium", "Long"]
    ),

    "TA09": ("Express bus", 0.03, ["Long"]),

    "TA10": ("ETS train", 0.04, ["Long"])
}


# ============================================================
# 4. FOOD FOOTPRINT DATABASE
# ============================================================

FOOD = {
    "F01": ("Beef rendang + rice", 10.45, "Meal"),
    "F02": ("Lamb curry + rice", 4.47, "Meal"),
    "F03": ("Nasi lemak + chicken", 1.49, "Meal"),
    "F04": ("Air-flown salmon + rice", 3.90, "Meal"),
    "F05": ("Prawn fried rice", 3.19, "Meal"),
    "F06": ("Beef steak + potatoes", 20.40, "Meal"),
    "F07": ("Mutton briyani", 6.46, "Meal"),
    "F08": ("Beef burger", 10.45, "Meal"),
    "F09": ("Cheese pizza (2 slices)", 2.41, "Meal"),
    "F10": ("Chicken chop + fries", 1.98, "Meal"),

    "F11": ("Dark chocolate (50 g)", 2.33, "Snack"),
    "F12": ("Cheese sandwich", 1.15, "Snack"),
    "F13": ("Air-flown strawberries (150 g)", 1.50, "Snack"),

    "F14": ("Iced latte", 1.02, "Drink"),
    "F15": ("Milkshake", 1.30, "Drink")
}


FOOD_ACTIONS = {
    "FA01": ("Chicken rice", 1.49, "Meal"),
    "FA02": ("Fish + rice", 1.86, "Meal"),
    "FA03": ("Egg fried rice", 0.97, "Meal"),
    "FA04": ("Tofu + rice", 0.97, "Meal"),
    "FA05": ("Vegetarian nasi campur", 0.80, "Meal"),

    "FA06": ("Local fresh fruit", 0.15, "Snack"),
    "FA07": ("Peanut butter sandwich", 0.35, "Snack"),

    "FA08": ("Plain water", 0.01, "Drink"),
    "FA09": ("Soy milk", 0.25, "Drink"),
    "FA10": ("Black tea", 0.05, "Drink")
}


# ============================================================
# 5. ACTIVITY FOOTPRINT DATABASE
# ============================================================

ACTIVITY = {
    "A01": ("Use air conditioning for 8 hours", 5.33),

    "A02": ("Leave lights on for 8 hours", 0.95),

    "A03": ("Take a 15-minute hot shower", 0.65),

    "A04": ("Dry clothes using a dryer (1 load)", 1.85),

    "A05": ("Buy a new polyester T-shirt", 5.00),

    "A06": ("Buy a new pair of cotton jeans", 20.00),

    "A07": (
        "Buy 5 plastic bottles of water (500 mL each)",
        0.70
    ),

    "A08": ("Buy 5 canned drinks", 0.65),

    "A09": ("Print 100 sheets of notes", 0.60),

    "A10": ("Buy a new nylon backpack", 15.00),

    "A11": ("Buy a new smartphone", 40.00),

    "A12": ("Buy a new iPad", 60.00),

    "A13": ("Buy a new smartwatch", 15.00),

    "A14": ("Order food delivery twice", 0.72),

    "A15": ("Order 3 items online separately", 2.64)
}


ACTIVITY_ACTIONS = {
    "AA01": "Use a fan",
    "AA02": "Shorten usage time",
    "AA03": "Use energy-efficient appliances",
    "AA04": "Sun-dry clothes",
    "AA05": "Reuse or repair",
    "AA06": "Buy second-hand",
    "AA07": "Buy products with recycled content",
    "AA08": "Recycle after use",
    "AA09": "Combine orders",
    "AA10": "Walk to the store"
}


# ============================================================
# 6. ACTIVITY EMISSION MATRIX
# ============================================================

# Remaining emissions in kg CO2e.
# Missing combinations = Not practical.

ACTIVITY_MATRIX = {

    "A01": {
        "AA01": 0.41,
        "AA02": 2.67,
        "AA03": 3.55
    },

    "A02": {
        "AA02": 0.48,
        "AA03": 0.21
    },

    "A03": {
        "AA02": 0.33
    },

    "A04": {
        "AA03": 0.89,
        "AA04": 0.00
    },

    "A05": {
        "AA05": 0.10,
        "AA06": 0.50,
        "AA07": 3.00,
        "AA08": 4.50
    },

    "A06": {
        "AA05": 0.50,
        "AA06": 1.50,
        "AA07": 12.00,
        "AA08": 18.50
    },

    "A07": {
        "AA05": 0.05,
        "AA07": 0.50,
        "AA08": 0.45
    },

    "A08": {
        "AA05": 0.05,
        "AA07": 0.35,
        "AA08": 0.25
    },

    "A09": {
        "AA05": 0.10,
        "AA07": 0.40,
        "AA08": 0.35
    },

    "A10": {
        "AA05": 0.50,
        "AA06": 1.00,
        "AA07": 10.00,
        "AA08": 14.00
    },

    "A11": {
        "AA05": 5.00,
        "AA06": 12.00,
        "AA08": 38.00
    },

    "A12": {
        "AA05": 8.00,
        "AA06": 18.00,
        "AA08": 57.00
    },

    "A13": {
        "AA05": 2.00,
        "AA06": 4.50,
        "AA08": 14.25
    },

    "A14": {
        "AA09": 0.36,
        "AA10": 0.00
    },

    "A15": {
        "AA09": 0.88,
        "AA10": 0.00
    }
}


# ============================================================
# 7. EDUCATIONAL EXPLANATIONS
# ============================================================

EXPLANATIONS = {

    "AA01":
        "A fan consumes much less electricity than AC.",

    "AA02":
        "Shorter usage reduces electricity consumption.",

    "AA03":
        "Efficient appliances provide similar services "
        "using less electricity.",

    "AA04":
        "Sun-drying avoids electricity consumption "
        "by the dryer.",

    "AA05":
        "Reusing or repairing products avoids or delays "
        "new product manufacturing.",

    "AA06":
        "Buying second-hand can displace new production "
        "when equivalent service is provided.",

    "AA07":
        "Recycled materials can reduce demand for "
        "virgin material production.",

    "AA08":
        "Recycling can displace virgin materials but "
        "does not eliminate manufacturing emissions.",

    "AA09":
        "Combining orders can reduce separate "
        "delivery journeys.",

    "AA10":
        "Walking to a nearby store avoids motorised "
        "delivery emissions in this scenario."
}


SPECIFIC_EXPLANATIONS = {

    ("A07", "AA05"):
        "Refill an existing bottle instead of buying "
        "new plastic bottles.",

    ("A08", "AA05"):
        "Use an existing reusable cup at a "
        "beverage dispenser.",

    ("A09", "AA05"):
        "Print on the unused sides of existing paper.",

    ("A02", "AA03"):
        "LED lighting consumes less electricity "
        "than conventional bulbs.",

    ("A03", "AA02"):
        "A shorter hot shower requires less energy "
        "to heat water."
}


# ============================================================
# 8. DATABASE GROUPS
# ============================================================

FOOTPRINT_DATABASES = {
    "Transport": TRANSPORT,
    "Food": FOOD,
    "Activity": ACTIVITY
}

ACTION_DATABASES = {
    "Transport": TRANSPORT_ACTIONS,
    "Food": FOOD_ACTIONS,
    "Activity": ACTIVITY_ACTIONS
}

ICONS = {
    "Transport": "🚗",
    "Food": "🍽️",
    "Activity": "🛍️"
}


# ============================================================
# 9. CALCULATION FUNCTIONS
# ============================================================

def original_emissions(category, card_id):

    if category == "Transport":

        _, distance, factor, _ = TRANSPORT[card_id]

        return round(distance * factor, 2)

    return FOOTPRINT_DATABASES[category][card_id][1]


def action_name(category, action_id):

    if action_id == "NONE":

        return "No action selected"

    value = ACTION_DATABASES[category][action_id]

    if isinstance(value, str):

        return value

    return value[0]


def calculate_category(category, card_id, action_id):

    original_name = (
        FOOTPRINT_DATABASES[category][card_id][0]
    )

    original = original_emissions(
        category, card_id
    )

    practical = False
    new = original

    explanation = (
        "This action is not a practical alternative "
        "to the original activity."
    )

    # No action selected

    if action_id == "NONE":

        explanation = (
            "No alternative was selected. "
            "Original emissions remain unchanged."
        )

    # Transport

    elif category == "Transport":

        _, distance, _, group = TRANSPORT[card_id]

        _, factor, allowed = (
            TRANSPORT_ACTIONS[action_id]
        )

        practical = group in allowed

        if practical:

            new = distance * factor

            explanation = (
                f"Assumed emission factor: "
                f"{factor:.3f} kg CO₂e "
                f"per passenger-km."
            )

        else:

            explanation = (
                f"This transport mode is not practical "
                f"for a {group.lower()}-distance journey "
                f"under the game assumptions."
            )

    # Food

    elif category == "Food":

        _, _, group = FOOD[card_id]

        _, alternative, action_group = (
            FOOD_ACTIONS[action_id]
        )

        practical = group == action_group

        if practical:

            new = alternative

            explanation = (
                "Different ingredients and production "
                "systems result in different "
                "carbon footprints."
            )

        else:

            explanation = (
                f"A {action_group.lower()} is not a "
                f"practical substitute for a "
                f"{group.lower()} in this game."
            )

    # Activity

    else:

        matrix = ACTIVITY_MATRIX[card_id]

        practical = action_id in matrix

        if practical:

            new = matrix[action_id]

            explanation = SPECIFIC_EXPLANATIONS.get(
                (card_id, action_id),
                EXPLANATIONS[action_id]
            )

    new = round(new, 2)

    if not practical:

        new = original

    saved = round(original - new, 2)

    reduction = (
        saved / original * 100
        if original > 0
        else 0.0
    )

    if action_id == "NONE":

        status = "No action selected"

    elif not practical:

        status = "Not practical"

    elif saved > 0:

        status = "Emissions reduced"

    elif saved < 0:

        status = "Emissions increased"

    else:

        status = "No improvement"

    return {
        "category": category,
        "card_id": card_id,
        "original_name": original_name,
        "action_name": action_name(category, action_id),
        "original": original,
        "new": new,
        "saved": saved,
        "reduction": reduction,
        "practical": practical,
        "status": status,
        "explanation": explanation
    }


def calculate_total(footprints, actions):

    rows = [
        calculate_category(
            category,
            footprints[category],
            actions[category]
        )

        for category in FOOTPRINT_DATABASES
    ]

    original = round(
        sum(row["original"] for row in rows), 2
    )

    new = round(
        sum(row["new"] for row in rows), 2
    )

    saved = round(original - new, 2)

    score = (
        round(saved / original * 100, 1)
        if original > 0
        else 0.0
    )

    return {
        "rows": rows,
        "original": original,
        "new": new,
        "saved": saved,
        "score": score
    }


def best_solutions(category, card_id):

    results = [
        calculate_category(
            category, card_id, action_id
        )

        for action_id in ACTION_DATABASES[category]
    ]

    practical = [
        row for row in results
        if row["practical"]
    ]

    if not practical:

        return []

    minimum = min(
        row["new"] for row in practical
    )

    return [
        row for row in practical
        if abs(row["new"] - minimum) < 0.000001
    ]


def signed_emission_change(saved):

    # Positive savings are displayed as
    # negative emission changes.

    if saved > 0:

        return f"−{saved:.2f}"

    elif saved < 0:

        return f"+{abs(saved):.2f}"

    return "0.00"


# ============================================================
# 10. ACHIEVEMENT LEVELS
# ============================================================

def achievement(score):

    # Carbon Master: above 80%

    if score > 80:

        return (
            "Carbon Master",
            "🎉 🏆 🎉",
            "Outstanding! You are a Carbon Master!"
        )

    # Carbon Champion: 60% to 80%

    elif score >= 60:

        return (
            "Carbon Champion",
            "😄 👍",
            "Excellent choices! Keep making a difference."
        )

    # Carbon Explorer: 40% to below 60%

    elif score >= 40:

        return (
            "Carbon Explorer",
            "👍",
            "Great effort! Keep exploring greener choices."
        )

    # Carbon Learner: below 40%

    return (
        "Carbon Learner",
        "🌱 💪",
        "Every small step matters. Keep learning!"
    )


# ============================================================
# 11. TEMPORARY ONLINE LEADERBOARD
# ============================================================

@st.cache_resource
def leaderboard_storage():

    return {
        "scores": [],
        "count": 0,
        "lock": Lock()
    }


board = leaderboard_storage()


def save_score(
    nickname,
    score,
    selection_time,
    player_id
):

    with board["lock"]:

        if any(
            item["id"] == player_id
            for item in board["scores"]
        ):

            return

        board["count"] += 1

        board["scores"].append({
            "id": player_id,
            "name": nickname,
            "score": score,
            "time": selection_time,
            "order": board["count"]
        })

        board["scores"].sort(
            key=lambda item: (
                -item["score"],
                item["time"],
                item["order"]
            )
        )

        # Only retain the Top 30.

        board["scores"] = board["scores"][:30]


def get_leaderboard():

    with board["lock"]:

        return (
            [dict(item) for item in board["scores"]],
            board["count"]
        )


def reset_leaderboard():

    with board["lock"]:

        board["scores"].clear()

        board["count"] = 0


# ============================================================
# 12. SESSION STATE
# ============================================================

def default_state():

    return {
        "stage": "registration",
        "nickname": "",
        "player_id": "",
        "footprints": {},
        "actions": {},
        "result": None,
        "timer_start": None,
        "elapsed": 0.0,
        "selection_time": 0.0,
        "confetti": False,
        "score_saved": False
    }


for key, value in default_state().items():

    if key not in st.session_state:

        st.session_state[key] = value


def go_to(stage):

    st.session_state.stage = stage

    st.rerun()


def next_participant():

    for key, value in default_state().items():

        st.session_state[key] = value

    st.rerun()


# ============================================================
# 13. TIMER BACKEND
# ============================================================

def elapsed_time():

    elapsed = st.session_state.elapsed

    if st.session_state.timer_start is not None:

        elapsed += (
            time.monotonic()
            - st.session_state.timer_start
        )

    return min(elapsed, DURATION)


def start_timer():

    st.session_state.elapsed = 0.0

    st.session_state.timer_start = time.monotonic()


def pause_timer():

    st.session_state.elapsed = elapsed_time()

    st.session_state.timer_start = None


def resume_timer():

    if (
        elapsed_time() < DURATION
        and st.session_state.timer_start is None
    ):

        st.session_state.timer_start = time.monotonic()


def finish_timer():

    st.session_state.selection_time = round(
        elapsed_time(), 1
    )

    pause_timer()

    go_to("actions")


# ============================================================
# 14. CIRCULAR COUNTDOWN WITH AUTOMATIC SOUND
# ============================================================

def circular_countdown():

    remaining = max(
        0.0,
        DURATION - elapsed_time()
    )

    running = (
        st.session_state.timer_start is not None
        and remaining > 0
    )

    settings = json.dumps({
        "remaining": remaining,
        "duration": DURATION,
        "running": running
    })

    timer_html = """
    <!DOCTYPE html>
    <html>

    <head>
    <meta charset="UTF-8">

    <style>

    body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        background: transparent;
        text-align: center;
        color: #174638;
    }

    .timer-wrapper {
        display: flex;
        align-items: center;
        flex-direction: column;
    }

    svg {
        width: 250px;
        max-width: 95%;
        height: auto;
    }

    #timer-number {
        font-size: 66px;
        font-weight: 900;
    }

    #timer-caption {
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    #timer-message {
        font-size: 21px;
        font-weight: 800;
        margin-top: 3px;
        margin-bottom: 8px;
    }

    #ring {
        transition: stroke 0.2s;
    }

    #audio-status {
        font-size: 13px;
        color: #63786B;
        margin-top: 4px;
    }

    #audio-fallback {
        display: none;
        background: #FFFFFF;
        color: #174638;
        border: 1px solid #B8CEC0;
        border-radius: 8px;
        padding: 7px 14px;
        font-size: 14px;
        cursor: pointer;
    }

    .pulse {
        animation: pulse 0.5s infinite alternate;
    }

    @keyframes pulse {

        from {
            opacity: 1;
        }

        to {
            opacity: 0.45;
        }
    }

    @media (prefers-reduced-motion: reduce) {

        .pulse {
            animation: none;
        }
    }

    </style>
    </head>

    <body>

    <div class="timer-wrapper">

        <svg viewBox="0 0 280 280">

            <circle
                cx="140"
                cy="140"
                r="120"
                fill="#FFFFFF"
                stroke="#DFE9E0"
                stroke-width="14"
            />

            <circle
                id="ring"
                cx="140"
                cy="140"
                r="120"
                fill="none"
                stroke="#258052"
                stroke-width="14"
                stroke-linecap="round"
                transform="rotate(-90 140 140)"
            />

            <text
                id="timer-number"
                x="140"
                y="149"
                text-anchor="middle"
                fill="#258052"
            >00:30</text>

            <text
                id="timer-caption"
                x="140"
                y="180"
                text-anchor="middle"
                fill="#63786B"
            >TIME LEFT</text>

        </svg>

        <div id="timer-message">
            Think fast. Choose wisely!
        </div>

        <div id="audio-status">
            🔊 Activating countdown sound...
        </div>

        <button id="audio-fallback">
            Enable sound
        </button>

    </div>

    <script>

    const config = __TIMER_SETTINGS__;

    const duration = config.duration;
    const startRemaining = config.remaining;
    const running = config.running;

    const startTime = performance.now();

    const ring = document.getElementById("ring");

    const number = document.getElementById(
        "timer-number"
    );

    const message = document.getElementById(
        "timer-message"
    );

    const audioStatus = document.getElementById(
        "audio-status"
    );

    const audioFallback = document.getElementById(
        "audio-fallback"
    );

    const circumference = 2 * Math.PI * 120;

    ring.style.strokeDasharray = circumference;

    let previousSecond = Math.ceil(startRemaining);

    let completed = false;
    let audioContext = null;
    let animationID = null;
    let startSoundPlayed = false;


    // ========================================================
    // SOUND GENERATOR
    // ========================================================

    function playTone(
        frequency,
        toneDuration = 0.1,
        delay = 0,
        volume = 0.12,
        waveType = "sine"
    ) {

        if (
            !audioContext ||
            audioContext.state !== "running"
        ) {
            return;
        }

        const oscillator =
            audioContext.createOscillator();

        const gain =
            audioContext.createGain();

        const now =
            audioContext.currentTime + delay;

        oscillator.type = waveType;

        oscillator.frequency.setValueAtTime(
            frequency,
            now
        );

        gain.gain.setValueAtTime(
            0.0001,
            now
        );

        gain.gain.exponentialRampToValueAtTime(
            volume,
            now + 0.008
        );

        gain.gain.exponentialRampToValueAtTime(
            0.0001,
            now + toneDuration
        );

        oscillator.connect(gain);

        gain.connect(
            audioContext.destination
        );

        oscillator.start(now);

        oscillator.stop(
            now + toneDuration + 0.03
        );
    }


    // ========================================================
    // STARTING CHIME
    // ========================================================

    function startSound() {

        playTone(
            550, 0.12, 0, 0.13
        );

        playTone(
            850, 0.20, 0.15, 0.15
        );
    }


    // ========================================================
    // REGULAR COUNTDOWN TICK
    // 29 TO 16 SECONDS
    // ========================================================

    function normalTick() {

        playTone(
            650,
            0.065,
            0,
            0.09,
            "triangle"
        );
    }


    // ========================================================
    // WARNING TICK
    // 15 TO 6 SECONDS
    // ========================================================

    function warningTick() {

        playTone(
            950,
            0.09,
            0,
            0.12,
            "triangle"
        );
    }


    // ========================================================
    // PANIC SOUND
    // LAST 5 SECONDS
    // ========================================================

    function panicSound(second) {

        const frequency =
            1100 + (5 - second) * 150;

        playTone(
            frequency,
            0.10,
            0,
            0.17,
            "triangle"
        );

        playTone(
            frequency + 200,
            0.10,
            0.18,
            0.17,
            "triangle"
        );

        // Triple beeps for the final two seconds.

        if (second <= 2) {

            playTone(
                frequency + 400,
                0.12,
                0.36,
                0.18,
                "triangle"
            );
        }
    }


    // ========================================================
    // TIME-UP ALARM
    // ========================================================

    function timeUpSound() {

        playTone(
            1200, 0.22, 0, 0.20, "triangle"
        );

        playTone(
            1200, 0.22, 0.30, 0.20, "triangle"
        );

        playTone(
            550, 0.65, 0.60, 0.18, "triangle"
        );
    }


    // ========================================================
    // AUTOMATIC AUDIO INITIALISATION
    // ========================================================

    async function enableAudio() {

        if (!running || getRemaining() <= 0) {
            return;
        }

        try {

            if (!audioContext) {

                const AudioContextClass =
                    window.AudioContext ||
                    window.webkitAudioContext;

                audioContext =
                    new AudioContextClass();
            }

            await audioContext.resume();

            if (audioContext.state === "running") {

                audioStatus.textContent =
                    "🔊 Sound enabled";

                audioFallback.style.display =
                    "none";

                if (
                    !startSoundPlayed &&
                    getRemaining() > 27
                ) {

                    startSound();

                    startSoundPlayed = true;
                }

            }

        } catch (error) {

            audioStatus.textContent =
                "Automatic sound blocked";

            audioFallback.style.display =
                "inline-block";
        }
    }


    // Automatically attempt to enable sound.

    if (running) {

        enableAudio();

        // Check whether browser autoplay was blocked.

        setTimeout(function () {

            if (
                !completed &&
                (
                    !audioContext ||
                    audioContext.state !== "running"
                )
            ) {

                audioStatus.textContent =
                    "Automatic sound blocked by browser";

                audioFallback.style.display =
                    "inline-block";
            }

        }, 1000);

    } else {

        audioStatus.textContent = "";
    }


    // Fallback only if the browser blocks autoplay.

    audioFallback.addEventListener(
        "click",
        enableAudio
    );


    // ========================================================
    // COUNTDOWN CALCULATION
    // ========================================================

    function getRemaining() {

        if (!running) {

            return startRemaining;
        }

        const elapsed = (
            performance.now() - startTime
        ) / 1000;

        return Math.max(
            0,
            startRemaining - elapsed
        );
    }


    function updateTimer() {

        const remaining = getRemaining();

        const second = Math.ceil(remaining);

        const minutes = Math.floor(second / 60);

        const seconds = second % 60;

        number.textContent =
            String(minutes).padStart(2, "0") +
            ":" +
            String(seconds).padStart(2, "0");

        ring.style.strokeDashoffset =
            circumference *
            (1 - remaining / duration);


        // ====================================================
        // COLOUR AND MESSAGE
        // ====================================================

        let color = "#258052";

        if (second <= 5) {

            color = "#D64444";

            message.textContent =
                "HURRY UP!";

        } else if (second <= 15) {

            color = "#D99024";

            message.textContent =
                "Time is running out!";

        } else {

            message.textContent =
                "Think fast. Choose wisely!";
        }

        ring.style.stroke = color;

        number.style.fill = color;

        message.style.color = color;


        // ====================================================
        // PLAY SOUND EVERY SECOND
        // ====================================================

        if (
            running &&
            second !== previousSecond &&
            second > 0
        ) {

            if (second <= 5) {

                panicSound(second);

            } else if (second <= 15) {

                warningTick();

            } else {

                normalTick();
            }
        }


        // ====================================================
        // FLASHING EFFECT FOR FINAL 5 SECONDS
        // ====================================================

        if (
            running &&
            second <= 5 &&
            second > 0
        ) {

            number.classList.add("pulse");

            ring.classList.add("pulse");

        } else {

            number.classList.remove("pulse");

            ring.classList.remove("pulse");
        }


        // ====================================================
        // TIME IS UP
        // ====================================================

        if (remaining <= 0) {

            number.textContent = "00:00";

            number.classList.remove("pulse");

            ring.classList.remove("pulse");

            message.textContent =
                "TIME'S UP! Stop selecting cards!";

            message.style.color = "#D64444";

            audioStatus.textContent = "";

            audioFallback.style.display = "none";

            if (!completed && running) {

                completed = true;

                timeUpSound();
            }

            return;
        }


        // ====================================================
        // PAUSED TIMER
        // ====================================================

        if (!running) {

            message.textContent = "TIMER PAUSED";

            return;
        }

        previousSecond = second;

        animationID = requestAnimationFrame(
            updateTimer
        );
    }


    updateTimer();


    // ========================================================
    // CLEAN UP WHEN LEAVING TIMER SCREEN
    // ========================================================

    window.addEventListener(
        "pagehide",

        function () {

            if (animationID !== null) {

                cancelAnimationFrame(animationID);
            }

            if (audioContext) {

                audioContext.close().catch(
                    function () {}
                );
            }
        }
    );

    </script>

    </body>
    </html>
    """

    timer_html = timer_html.replace(
        "__TIMER_SETTINGS__",
        settings
    )

    components.html(
        timer_html,
        height=335,
        scrolling=False
    )


# ============================================================
# 15. COMPACT CONFETTI ANIMATION
# ============================================================

def confetti_html():

    colors = [
        "#FF1744",
        "#FFD600",
        "#2979FF",
        "#00C853",
        "#FF9100",
        "#D500F9",
        "#00B8D4",
        "#FF4081"
    ]

    pieces = []

    for i in range(150):

        left = (i * 37) % 100

        delay = (i % 25) * 0.08

        duration = 3.5 + (i % 10) * 0.15

        color = colors[i % len(colors)]

        pieces.append(
            f"""
            <span class="confetti-piece"
                  style="
                    left:{left}%;
                    background:{color};
                    animation-delay:{delay}s;
                    animation-duration:{duration}s;
                  ">
            </span>
            """
        )

    return "".join(pieces)


# ============================================================
# 16. CARD SELECTION FUNCTIONS
# ============================================================

def select_footprint(category):

    database = FOOTPRINT_DATABASES[category]

    return st.selectbox(
        f"{ICONS[category]} {category} card",

        options=list(database.keys()),

        index=None,

        placeholder="Select physical card ID",

        format_func=lambda card_id: (
            f"{card_id} — {database[card_id][0]}"
        ),

        key=f"widget_footprint_{category}"
    )


def select_action(category):

    database = ACTION_DATABASES[category]

    return st.selectbox(
        f"{ICONS[category]} {category} solution",

        options=list(database.keys()) + ["NONE"],

        index=None,

        placeholder="Select physical solution card",

        format_func=lambda action_id: (
            "No action selected"

            if action_id == "NONE"

            else (
                f"{action_id} — "
                f"{action_name(category, action_id)}"
            )
        ),

        key=f"widget_solution_{category}"
    )


# ============================================================
# 17. ORIGINAL FOOTPRINT DISPLAY
# ============================================================

def show_original_footprint():

    total = 0.0

    columns = st.columns(3)

    for column, category in zip(
        columns,
        FOOTPRINT_DATABASES
    ):

        card_id = (
            st.session_state.footprints[category]
        )

        name = (
            FOOTPRINT_DATABASES[category][card_id][0]
        )

        emissions = original_emissions(
            category, card_id
        )

        total += emissions

        with column:

            st.html(
                f"""
                <div class="footprint-card">

                    <div class="footprint-icon">
                        {ICONS[category]}
                    </div>

                    <div class="footprint-category">
                        {category}
                    </div>

                    <div class="footprint-value">
                        {emissions:.2f} kg
                    </div>

                    <div class="footprint-name">
                        {escape(name)}
                    </div>

                </div>
                """
            )

    st.html(
        f"""
        <div class="total-footprint">

            <div class="total-footprint-label">
                👣 TOTAL ORIGINAL CARBON FOOTPRINT
            </div>

            <div class="total-footprint-value">
                {total:.2f} kg CO₂e
            </div>

        </div>
        """
    )


# ============================================================
# 18. REGISTRATION SCREEN
# ============================================================

def registration_screen():

    st.header(
        "🌍 Ready to challenge your carbon footprint?"
    )

    st.write(
        "Make three smart choices and compete "
        "for the top spot!"
    )

    with st.form("registration_form"):

        nickname = st.text_input(
            "Participant nickname",

            max_chars=30,

            placeholder="Enter your nickname",

            key="widget_nickname"
        )

        submitted = st.form_submit_button(
            "Start challenge",

            type="primary",

            use_container_width=True
        )

        if submitted:

            if not nickname.strip():

                st.warning(
                    "Please enter a nickname."
                )

            else:

                st.session_state.nickname = (
                    nickname.strip()
                )

                st.session_state.player_id = (
                    uuid.uuid4().hex
                )

                go_to("footprints")

    st.divider()

    st.subheader("How to play")

    st.markdown("""
1. Draw one footprint card from each category.
2. Discover your total carbon footprint.
3. Choose three climate solutions in 30 seconds.
4. Reveal your carbon reduction and ranking!
    """)

    st.caption(
        "Your nickname and score may appear "
        "on the event leaderboard."
    )


# ============================================================
# 19. FOOTPRINT SELECTION SCREEN
# ============================================================

def footprint_screen():

    st.header(
        "Step 1 — Draw your footprint cards"
    )

    st.write(
        "Draw one physical card from Transport, "
        "Food and Activity."
    )

    with st.form("footprint_selection_form"):

        selected = {
            category: select_footprint(category)
            for category in FOOTPRINT_DATABASES
        }

        submitted = st.form_submit_button(
            "Calculate original footprint",

            type="primary",

            use_container_width=True
        )

        if submitted:

            if None in selected.values():

                st.warning(
                    "Please select all three cards."
                )

            else:

                st.session_state.footprints = selected

                go_to("ready")


# ============================================================
# 20. READY SCREEN
# ============================================================

def ready_screen():

    st.header(
        "Step 2 — Your carbon footprint"
    )

    show_original_footprint()

    st.subheader("Your mission")

    st.write(
        "Choose one solution for each category "
        "to achieve the greatest carbon reduction."
    )

    st.info(
        "You have 30 seconds to select "
        "three physical solution cards."
    )

    if st.button(
        "▶ Start 30-second challenge",

        type="primary",

        use_container_width=True,

        key="button_start_challenge"
    ):

        start_timer()

        go_to("timer")

    with st.expander(
        "⚙️ Facilitator controls",
        expanded=False
    ):

        if st.button(
            "Correct footprint selection",

            key="button_correct_footprints"
        ):

            go_to("footprints")


# ============================================================
# 21. TIMER SCREEN
# ============================================================

def timer_screen():

    st.header(
        "Step 3 — Carbon Challenge"
    )

    st.markdown(
        "**Find your best three climate solutions!**"
    )

    show_original_footprint()

    circular_countdown()

    if st.button(
        "Finish / Enter selected solutions",

        type="primary",

        use_container_width=True,

        key="button_finish_timer"
    ):

        finish_timer()

    with st.expander(
        "⚙️ Facilitator timer controls",
        expanded=False
    ):

        remaining = max(
            0,
            DURATION - elapsed_time()
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            if st.button(
                "⏸ Pause",

                disabled=(
                    st.session_state.timer_start is None
                    or remaining <= 0
                ),

                use_container_width=True,

                key="button_pause_timer"
            ):

                pause_timer()

                st.rerun()

        with c2:

            if st.button(
                "▶ Resume",

                disabled=(
                    st.session_state.timer_start is not None
                    or remaining <= 0
                ),

                use_container_width=True,

                key="button_resume_timer"
            ):

                resume_timer()

                st.rerun()

        with c3:

            if st.button(
                "↻ Reset",

                use_container_width=True,

                key="button_reset_timer"
            ):

                start_timer()

                st.rerun()


# ============================================================
# 22. SOLUTION SELECTION SCREEN
# ============================================================

def solution_screen():

    st.header(
        "Step 4 — Enter selected solutions"
    )

    st.caption(
        f"Selection time: "
        f"{st.session_state.selection_time:.1f} seconds"
    )

    show_original_footprint()

    with st.form("solution_selection_form"):

        selected = {
            category: select_action(category)
            for category in ACTION_DATABASES
        }

        submitted = st.form_submit_button(
            "Reveal my carbon reduction!",

            type="primary",

            use_container_width=True
        )

        if submitted:

            if None in selected.values():

                st.warning(
                    "Please enter all three solutions. "
                    "Choose 'No action selected' "
                    "for any missing cards."
                )

            else:

                result = calculate_total(
                    st.session_state.footprints,
                    selected
                )

                st.session_state.actions = selected

                st.session_state.result = result

                if not st.session_state.score_saved:

                    save_score(
                        st.session_state.nickname,
                        result["score"],
                        st.session_state.selection_time,
                        st.session_state.player_id
                    )

                    st.session_state.score_saved = True

                # Confetti is only activated for Carbon Master.

                st.session_state.confetti = (
                    result["score"] > 80
                )

                go_to("results")


# ============================================================
# 23. COLOURED RESULT BOXES
# ============================================================

def result_metric_html(
    icon,
    label,
    value,
    background,
    border,
    text_color
):

    return f"""
    <div class="result-metric"
         style="
            background:{background};
            border:1px solid {border};
            color:{text_color};
         ">

        <div class="result-metric-icon">
            {icon}
        </div>

        <div class="result-metric-label">
            {escape(label)}
        </div>

        <div class="result-metric-value">
            {escape(str(value))}
        </div>

        <div class="result-metric-unit">
            kg CO₂e
        </div>

    </div>
    """


def combined_result_panel(result):

    score = result["score"]

    title, emoji, message = achievement(score)

    color = (
        "#258052" if score > 0
        else "#B94040" if score < 0
        else "#63786B"
    )

    # Original footprint: red.

    original_box = result_metric_html(
        icon="👣",

        label="Original footprint",

        value=f"{result['original']:.2f}",

        background="#FBE6E4",

        border="#E9B5B0",

        text_color="#B94040"
    )

    # Remaining footprint: blue.

    remaining_box = result_metric_html(
        icon="🌍",

        label="Remaining footprint",

        value=f"{result['new']:.2f}",

        background="#E2EEF9",

        border="#B9D5F0",

        text_color="#3269A8"
    )

    # Avoided emissions: negative sign.
    # Increased emissions: positive sign.

    signed_value = signed_emission_change(
        result["saved"]
    )

    if result["saved"] >= 0:

        avoided_box = result_metric_html(
            icon="🌿",

            label="CO₂e avoided",

            value=signed_value,

            background="#DDF2E2",

            border="#B3DCC0",

            text_color="#258052"
        )

    else:

        avoided_box = result_metric_html(
            icon="⚠️",

            label="Additional CO₂e",

            value=signed_value,

            background="#FBE6E4",

            border="#E9B5B0",

            text_color="#B94040"
        )

    # Show confetti only once per participant.

    celebration = ""

    if st.session_state.confetti:

        celebration = confetti_html()

        st.session_state.confetti = False

    # Achievement on the left.
    # Three emission boxes on the right.

    st.html(
        f"""
        <div class="result-panel">

            {celebration}

            <div class="achievement-panel">

                <div class="achievement-emoji">
                    {emoji}
                </div>

                <div class="achievement-title">
                    {title}
                </div>

                <div class="score-number"
                     style="color:{color};">

                    {score:.1f}%

                </div>

                <div class="score-label">
                    CARBON REDUCTION
                </div>

                <div class="score-message">
                    {message}
                </div>

            </div>

            <div class="summary-metrics">

                {original_box}

                {remaining_box}

                {avoided_box}

            </div>

        </div>
        """
    )


# ============================================================
# 24. INDIVIDUAL CARBON IMPACT CARDS
# ============================================================

def category_result(row):

    category = row["category"]

    original = row["original"]

    new = row["new"]

    saved = row["saved"]

    reduction = row["reduction"]

    original_name = escape(
        row["original_name"]
    )

    solution_name = escape(
        row["action_name"]
    )

    explanation = escape(
        row["explanation"]
    )

    if not row["practical"]:

        color = "#B94040"

        status = (
            "❌ No action selected"

            if row["status"] == "No action selected"

            else "❌ Not practical"
        )

    elif reduction > 0:

        color = "#258052"

        status = "✅ Emissions reduced"

    elif reduction < 0:

        color = "#B94040"

        status = "⚠️ Emissions increased"

    else:

        color = "#63786B"

        status = "No improvement"

    maximum = max(
        original,
        new,
        0.000001
    )

    original_width = (
        original / maximum * 100
    )

    new_width = (
        new / maximum * 100
    )

    new_bar_color = (
        "#359568" if new < original
        else "#B94040" if new > original
        else "#9AA89E"
    )

    solution_color = (
        "#258052"

        if row["practical"] and reduction > 0

        else "#B94040"

        if not row["practical"] or reduction < 0

        else "#63786B"
    )

    signed_value = signed_emission_change(saved)

    saved_text = (
        f"{signed_value} kg CO₂e avoided"

        if saved >= 0

        else f"{signed_value} kg CO₂e added"
    )

    st.html(
        f"""
        <div class="impact-card">

            <div class="impact-title">
                {ICONS[category]} {category}
            </div>

            <div class="impact-label">
                Original activity
            </div>

            <div class="impact-original">
                {original_name}
            </div>

            <div class="impact-label">
                Your solution
            </div>

            <div class="impact-solution"
                 style="color:{solution_color};">

                {solution_name}

            </div>

            <div class="impact-reduction"
                 style="color:{color};">

                {reduction:.1f}%

            </div>

            <div class="impact-status"
                 style="color:{color};">

                {status}

            </div>

            <div class="impact-bar-label">
                Before: {original:.2f} kg
            </div>

            <div class="impact-bar-background">

                <div class="impact-bar-fill"
                     style="
                         width:{original_width:.2f}%;
                         background:#CE6464;
                     ">
                </div>

            </div>

            <div class="impact-bar-label">
                After: {new:.2f} kg
            </div>

            <div class="impact-bar-background">

                <div class="impact-bar-fill"
                     style="
                         width:{new_width:.2f}%;
                         background:{new_bar_color};
                     ">
                </div>

            </div>

            <div class="impact-saved"
                 style="color:{color};">

                {saved_text}

            </div>

            <div class="impact-explanation">
                {explanation}
            </div>

        </div>
        """
    )

    best = best_solutions(
        category,
        row["card_id"]
    )

    if best:

        best_names = " / ".join(
            item["action_name"]
            for item in best
        )

        with st.expander(
            "💡 Best possible solution",

            expanded=False
        ):

            st.write(
                f"**{best_names}**"
            )

            st.write(
                f"Maximum reduction: "
                f"**{best[0]['reduction']:.1f}%**"
            )

            st.caption(
                f"Remaining emissions: "
                f"{best[0]['new']:.2f} kg CO₂e"
            )


# ============================================================
# 25. FINAL RESULTS SCREEN
# ============================================================

def results_screen():

    result = st.session_state.result

    # Compact combined achievement and
    # coloured footprint boxes.

    combined_result_panel(result)

    scores, count = get_leaderboard()

    rank = next(
        (
            i + 1

            for i, item in enumerate(scores)

            if item["id"] ==
            st.session_state.player_id
        ),

        None
    )

    if rank is not None:

        st.success(
            f"🏅 Your current ranking: #{rank} "
            f"out of {count} participants"
        )

    else:

        st.info(
            "Keep exploring! You are currently "
            "outside the Top 30."
        )

    st.caption(
        f"Selection time: "
        f"{st.session_state.selection_time:.1f} seconds"
    )

    st.header(
        "Discover your carbon impact"
    )

    # Transport, Food and Activity in three columns.

    columns = st.columns(
        3,
        gap="small"
    )

    for column, row in zip(
        columns,
        result["rows"]
    ):

        with column:

            category_result(row)

    if st.button(
        "➕ Next participant",

        type="primary",

        use_container_width=True,

        key="button_next_participant"
    ):

        next_participant()


# ============================================================
# 26. TOP-30 LEADERBOARD
# ============================================================

def leaderboard_panel():

    scores, count = get_leaderboard()

    st.html(
        f"""
        <div class="leaderboard-header">
            🏆 TOP 30
        </div>

        <div class="leaderboard-description">
            Ranked by carbon reduction percentage
        </div>

        <div class="leaderboard-count">

            <div class="leaderboard-count-label">
                Total participants
            </div>

            <div class="leaderboard-count-value">
                {count}
            </div>

        </div>
        """
    )

    if not scores:

        st.info(
            "No scores yet. Become our first "
            "Carbon Champion!"
        )

    else:

        table_rows = []

        for i, item in enumerate(scores):

            if i == 0:

                rank = "🥇"

                row_class = "rank-one"

            elif i == 1:

                rank = "🥈"

                row_class = "rank-two"

            elif i == 2:

                rank = "🥉"

                row_class = "rank-three"

            else:

                rank = str(i + 1)

                row_class = ""

            safe_name = escape(
                item["name"]
            )

            score_color = (
                "#258052"
                if item["score"] >= 0
                else "#B94040"
            )

            table_rows.append(
                f"""
                <tr class="{row_class}">

                    <td>{rank}</td>

                    <td>{safe_name}</td>

                    <td style="color:{score_color};">
                        {item['score']:.1f}%
                    </td>

                </tr>
                """
            )

        rows_html = "".join(table_rows)

        st.html(
            f"""
            <div class="leaderboard-scroll">

                <table class="leaderboard-table">

                    <colgroup>

                        <col style="width:24%">

                        <col style="width:43%">

                        <col style="width:33%">

                    </colgroup>

                    <thead>

                        <tr>

                            <th style="text-align:center;">
                                Rank
                            </th>

                            <th>Name</th>

                            <th style="text-align:right;">
                                Score
                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {rows_html}

                    </tbody>

                </table>

            </div>
            """
        )

        st.caption(
            "Tie-breaker: shorter selection time."
        )

    # Reset controls only available
    # on the registration screen.

    if st.session_state.stage == "registration":

        with st.expander(
            "⚙️ Facilitator controls",

            expanded=False
        ):

            st.caption(
                "Reset only when starting "
                "a new competition."
            )

            confirmed = st.checkbox(
                "Confirm leaderboard reset",

                key="widget_confirm_reset"
            )

            if st.button(
                "Reset leaderboard",

                disabled=(
                    not confirmed
                    or count == 0
                ),

                use_container_width=True,

                key="button_reset_leaderboard"
            ):

                reset_leaderboard()

                st.rerun()


# ============================================================
# 27. COMPACT APPLICATION HEADER WITH LOGO
# ============================================================

logo_path = (
    Path(__file__).resolve().parent
    / "ukm_mylca_logo.svg"
)

logo_html = ""

if logo_path.exists():

    logo_base64 = base64.b64encode(
        logo_path.read_bytes()
    ).decode("utf-8")

    logo_html = f"""
    <img
        class="header-logo"
        src="data:image/svg+xml;base64,{logo_base64}"
        alt="UKM IPI OpenFest Logo"
    >
    <div class="header-divider"></div>
    """

st.html(f"""
<div class="game-header">

    {logo_html}

    <h1>CARBON RUSH</h1>

    <p>
        30 seconds. 3 choices. How low can you go?
    </p>

</div>
""")


# ============================================================
# 28. MAIN APPLICATION LAYOUT
# ============================================================

# Main game panel + permanent leaderboard.

main_column, leaderboard_column = st.columns(
    [3.2, 1],
    gap="medium"
)

with main_column:

    stage = st.session_state.stage

    if stage != "registration":

        safe_nickname = escape(
            st.session_state.nickname
        )

        st.html(
            f"""
            <div class="participant-name">
                Participant: <strong>{safe_nickname}</strong>
            </div>
            """
        )

    if stage == "registration":

        registration_screen()

    elif stage == "footprints":

        footprint_screen()

    elif stage == "ready":

        ready_screen()

    elif stage == "timer":

        timer_screen()

    elif stage == "actions":

        solution_screen()

    elif stage == "results":

        results_screen()

with leaderboard_column:

    leaderboard_panel()


# ============================================================
# 29. APPLICATION FOOTER
# ============================================================

st.divider()

st.caption(
    "Carbon Rush | Count it. Cut it. Zero it! | "
    "UKM IPI Open Fest 2026"
)
