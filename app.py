import streamlit as st
import streamlit.components.v1 as components

import time
import math
import uuid
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

st.markdown("""
<style>
.stApp {
    background: #F5F8F4;
    color: #17382C;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #174638 !important;
}

.game-header {
    background: #123D32;
    padding: 24px;
    border-radius: 18px;
    margin-bottom: 20px;
}

.game-header h1 {
    color: white !important;
    font-size: 42px;
    margin: 0;
}

.game-header p {
    color: #C5E2D2;
    font-size: 17px;
    margin-bottom: 0;
}

div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #D9E5DC;
    border-radius: 14px;
    padding: 12px;
}

div[data-testid="stMetricValue"] {
    color: #174638;
    font-weight: bold;
}

div[data-testid="stButton"] > button {
    border-radius: 10px;
    font-weight: 600;
    min-height: 42px;
}

.score-box {
    background: white;
    border: 1px solid #D9E5DC;
    padding: 25px;
    border-radius: 18px;
    text-align: center;
}

.score-number {
    font-size: 82px;
    font-weight: 800;
}

.achievement-emoji {
    font-size: 60px;
}

.timer-box {
    text-align: center;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. TRANSPORT FOOTPRINT DATABASE
# ============================================================

# Name, distance (km), emission factor, distance category

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
    "TA03": ("Motorcycle", 0.09, ["Short", "Medium"]),
    "TA04": ("Public bus", 0.10, ["Short", "Medium"]),

    "TA05": (
        "Carpool (4 people)",
        0.04,
        ["Short", "Medium", "Long"]
    ),

    "TA06": ("MRT", 0.04, ["Short", "Medium"]),

    "TA07": (
        "Electric car",
        0.13,
        ["Short", "Medium", "Long"]
    ),

    "TA08": (
        "Hybrid car",
        0.12,
        ["Short", "Medium", "Long"]
    ),

    "TA09": ("Express bus", 0.03, ["Long"]),
    "TA10": ("ETS train", 0.04, ["Long"])
}

# ============================================================
# 3. FOOD FOOTPRINT DATABASE
# ============================================================

# Name, kg CO2e, food category

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
# 4. ACTIVITY FOOTPRINT DATABASE
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
# 5. ACTIVITY EMISSION MATRIX
# ============================================================

# Values = remaining emissions in kg CO2e.
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
# 6. EDUCATIONAL EXPLANATIONS
# ============================================================

EXPLANATIONS = {
    "AA01": (
        "A fan consumes considerably less electricity "
        "than air conditioning."
    ),

    "AA02": (
        "Shortening usage time reduces "
        "electricity consumption."
    ),

    "AA03": (
        "Energy-efficient appliances provide a similar "
        "service using less electricity."
    ),

    "AA04": (
        "Sun-drying clothes avoids electricity "
        "consumption by the dryer."
    ),

    "AA05": (
        "Reusing or repairing existing products "
        "avoids or delays new product manufacturing."
    ),

    "AA06": (
        "Buying second-hand can displace new "
        "production when equivalent service is provided."
    ),

    "AA07": (
        "Recycled materials can reduce demand "
        "for virgin material production."
    ),

    "AA08": (
        "Recycling can displace virgin materials, "
        "but does not eliminate the original "
        "manufacturing emissions."
    ),

    "AA09": (
        "Combining orders can reduce separate "
        "delivery journeys."
    ),

    "AA10": (
        "Walking to a nearby store avoids "
        "motorised delivery emissions."
    )
}

SPECIFIC_EXPLANATIONS = {
    ("A07", "AA05"):
        "Refill an existing bottle instead of buying new bottles.",

    ("A08", "AA05"):
        "Use an existing cup at a beverage dispenser.",

    ("A09", "AA05"):
        "Print on the unused sides of existing paper.",

    ("A02", "AA03"):
        "LED lighting consumes less electricity than conventional bulbs."
}

# ============================================================
# 7. CALCULATION FUNCTIONS
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

    original_name = FOOTPRINT_DATABASES[
        category
    ][card_id][0]

    original = original_emissions(
        category, card_id
    )

    practical = False
    new = original

    explanation = (
        "This action is not considered a practical "
        "alternative to the original activity."
    )

    if action_id == "NONE":

        explanation = (
            "No alternative was selected. "
            "Original emissions remain unchanged."
        )

    elif category == "Transport":

        _, distance, _, group = TRANSPORT[card_id]

        _, factor, allowed = (
            TRANSPORT_ACTIONS[action_id]
        )

        practical = group in allowed

        if practical:

            new = distance * factor

            explanation = (
                f"This alternative uses an assumed "
                f"emission factor of {factor:.3f} "
                f"kg CO₂e per passenger-km."
            )

        else:

            explanation = (
                f"This mode of transport is not considered "
                f"practical for a {group.lower()}-distance "
                f"journey under the game assumptions."
            )

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
                "systems result in different food "
                "carbon footprints."
            )

        else:

            explanation = (
                f"A {action_group.lower()} is not "
                f"considered a practical substitute "
                f"for a {group.lower()} in this game."
            )

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

    reduction = saved / original * 100

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

    score = round(
        saved / original * 100, 1
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
            category,
            card_id,
            action_id
        )

        for action_id in ACTION_DATABASES[category]
    ]

    practical = [
        row for row in results
        if row["practical"]
    ]

    minimum = min(
        row["new"] for row in practical
    )

    return [
        row for row in practical
        if abs(row["new"] - minimum) < 0.000001
    ]

# ============================================================
# 8. ACHIEVEMENT LEVELS
# ============================================================

def achievement(score):

    if score >= 90:

        return (
            "Carbon Master",
            "🎉 🏆 🎉",
            "Outstanding! You are a Carbon Master!"
        )

    elif score >= 70:

        return (
            "Carbon Champion",
            "😄 👍",
            "Excellent choices! Keep making a difference."
        )

    elif score >= 40:

        return (
            "Carbon Explorer",
            "👍",
            "Great effort! Keep exploring greener choices."
        )

    return (
        "Carbon Learner",
        "🌱 💪",
        "Every small step matters. Keep learning!"
    )

# ============================================================
# 9. TEMPORARY ONLINE LEADERBOARD
# ============================================================

# Shared server memory.
# No SQLite, Supabase, database or participant history.
# Only the current top 10 scores are retained.

@st.cache_resource
def leaderboard_storage():

    return {
        "scores": [],
        "count": 0,
        "lock": Lock()
    }

board = leaderboard_storage()

def save_score(nickname, score, selection_time, player_id):

    with board["lock"]:

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

        # Retain only the best 10 participants.

        board["scores"] = board["scores"][:10]

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
# 10. SESSION STATE
# ============================================================

DEFAULTS = {
    "stage": "registration",
    "nickname": "",
    "player_id": "",
    "footprints": {},
    "actions": {},
    "result": None,
    "timer_start": None,
    "elapsed": 0.0,
    "selection_time": 0.0,
    "confetti": False
}

for key, value in DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = value

def go_to(stage):

    st.session_state.stage = stage
    st.rerun()

def next_participant():

    for key, value in DEFAULTS.items():
        st.session_state[key] = value

    st.rerun()

# ============================================================
# 11. COUNTDOWN FUNCTIONS
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

    if elapsed_time() < DURATION:
        st.session_state.timer_start = time.monotonic()

def finish_timer():

    st.session_state.selection_time = round(
        elapsed_time(), 1
    )

    pause_timer()

    go_to("actions")

# ============================================================
# 12. COUNTDOWN INTERFACE
# ============================================================

@st.fragment(
    run_every=(
        0.5
        if st.session_state.stage == "timer"
        and st.session_state.timer_start is not None
        else None
    )
)
def countdown():

    elapsed = elapsed_time()

    if (
        elapsed >= DURATION
        and st.session_state.timer_start is not None
    ):

        pause_timer()
        st.rerun()

    remaining = max(
        0,
        math.ceil(DURATION - elapsed)
    )

    if remaining > 15:
        color = "#359568"

    elif remaining > 5:
        color = "#D99B32"

    else:
        color = "#D84C4C"

    circumference = 2 * math.pi * 100

    progress = (
        circumference * remaining / DURATION
    )

    if remaining == 0:
        message = "TIME'S UP!"

    elif st.session_state.timer_start is None:
        message = "TIMER PAUSED"

    else:
        message = "Think fast. Choose wisely."

    st.html(
        f"""
        <div class="timer-box">

            <svg width="260" height="260"
                 viewBox="0 0 240 240">

                <circle cx="120" cy="120" r="100"
                    fill="none"
                    stroke="#DDE6DF"
                    stroke-width="12"/>

                <circle cx="120" cy="120" r="100"
                    fill="none"
                    stroke="{color}"
                    stroke-width="12"
                    stroke-linecap="round"
                    stroke-dasharray="{progress} {circumference}"
                    transform="rotate(-90 120 120)"/>

                <text x="120" y="130"
                    text-anchor="middle"
                    font-size="62"
                    font-weight="bold"
                    fill="{color}">
                    00:{remaining:02d}
                </text>

                <text x="120" y="155"
                    text-anchor="middle"
                    font-size="12"
                    fill="#527064">
                    SECONDS LEFT
                </text>

            </svg>

            <h2>{message}</h2>

        </div>
        """
    )

    st.progress(
        remaining / DURATION
    )

    if remaining == 0:

        st.error("Stop selecting cards!")

    if st.button(
        "Enter selected solutions"
        if remaining == 0
        else "Finished selecting",

        type="primary",
        use_container_width=True
    ):

        finish_timer()

    with st.expander("⚙️ Facilitator timer controls"):

        c1, c2, c3 = st.columns(3)

        with c1:

            if st.button(
                "Pause",
                disabled=(
                    st.session_state.timer_start is None
                ),
                use_container_width=True
            ):

                pause_timer()
                st.rerun()

        with c2:

            if st.button(
                "Resume",
                disabled=(
                    st.session_state.timer_start is not None
                    or remaining == 0
                ),
                use_container_width=True
            ):

                resume_timer()
                st.rerun()

        with c3:

            if st.button(
                "Reset timer",
                use_container_width=True
            ):

                start_timer()
                st.rerun()

# ============================================================
# 13. CONFETTI ANIMATION
# ============================================================

def show_confetti():

    components.html("""
    <html>
    <body style="margin:0; overflow:hidden;">

    <canvas id="confetti"></canvas>

    <script>

    const canvas = document.getElementById("confetti");
    const ctx = canvas.getContext("2d");

    canvas.width = window.innerWidth;
    canvas.height = 150;

    const colors = [
        "#359568",
        "#E7B942",
        "#4A90E2",
        "#F26D78",
        "#94D6A2"
    ];

    let particles = [];

    if (!window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches) {

        for (let i = 0; i < 130; i++) {

            particles.push({
                x: Math.random() * canvas.width,
                y: -Math.random() * 180,
                size: 4 + Math.random() * 8,
                speed: 1 + Math.random() * 4,
                drift: Math.random() * 2 - 1,
                rotation: Math.random() * 6,
                color: colors[
                    Math.floor(Math.random() * colors.length)
                ]
            });
        }
    }

    const start = performance.now();

    function animate(now) {

        ctx.clearRect(
            0, 0, canvas.width, canvas.height
        );

        for (const p of particles) {

            p.y += p.speed;
            p.x += p.drift;
            p.rotation += 0.05;

            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation);
            ctx.fillStyle = p.color;
            ctx.fillRect(
                0, 0, p.size, p.size * 0.65
            );
            ctx.restore();
        }

        particles = particles.filter(
            p => p.y < canvas.height + 20
        );

        if (
            now - start < 3500
            && particles.length > 0
        ) {
            requestAnimationFrame(animate);
        }
    }

    requestAnimationFrame(animate);

    </script>
    </body>
    </html>
    """, height=155)

# ============================================================
# 14. CARD SELECTION
# ============================================================

ICONS = {
    "Transport": "🚗",
    "Food": "🍽️",
    "Activity": "🛍️"
}

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
        key=f"footprint_{category}"
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
            else f"{action_id} — "
                 f"{action_name(category, action_id)}"
        ),
        key=f"solution_{category}"
    )

def show_original_footprint():

    total = 0

    columns = st.columns(3)

    for column, category in zip(
        columns, FOOTPRINT_DATABASES
    ):

        card_id = st.session_state.footprints[category]

        emissions = original_emissions(
            category, card_id
        )

        total += emissions

        with column:

            st.metric(
                f"{ICONS[category]} {category}",
                f"{emissions:.2f} kg"
            )

            st.caption(
                FOOTPRINT_DATABASES[category][card_id][0]
            )

    st.metric(
        "Total original carbon footprint",
        f"{total:.2f} kg CO₂e"
    )

# ============================================================
# 15. REGISTRATION SCREEN
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
            placeholder="Enter your nickname"
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

    st.write("""
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
# 16. FOOTPRINT SELECTION SCREEN
# ============================================================

def footprint_screen():

    st.header("Step 1 — Draw your footprint cards")

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
# 17. READY SCREEN
# ============================================================

def ready_screen():

    st.header("Step 2 — Your carbon footprint")

    show_original_footprint()

    st.divider()

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
        use_container_width=True
    ):

        start_timer()
        go_to("timer")

    with st.expander("⚙️ Facilitator controls"):

        if st.button(
            "Correct footprint selection"
        ):

            go_to("footprints")

# ============================================================
# 18. TIMER SCREEN
# ============================================================

def timer_screen():

    st.header("Step 3 — Carbon Challenge")

    st.markdown(
        "**Find your best three climate solutions!**"
    )

    show_original_footprint()

    countdown()

# ============================================================
# 19. SOLUTION SELECTION SCREEN
# ============================================================

def solution_screen():

    st.header("Step 4 — Enter selected solutions")

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

                save_score(
                    st.session_state.nickname,
                    result["score"],
                    st.session_state.selection_time,
                    st.session_state.player_id
                )

                st.session_state.confetti = (
                    result["score"] >= 90
                )

                go_to("results")

# ============================================================
# 20. CATEGORY RESULTS
# ============================================================

def category_result(row):

    category = row["category"]

    st.subheader(
        f"{ICONS[category]} {category}"
    )

    st.write(
        f"**Original activity:** {row['original_name']}"
    )

    st.write(
        f"**Your solution:** {row['action_name']}"
    )

    if not row["practical"]:

        st.error(
            f"❌ {row['status']} — 0% reduction"
        )

    elif row["reduction"] > 0:

        st.success(
            f"✅ {row['reduction']:.1f}% reduction"
        )

    elif row["reduction"] < 0:

        st.error(
            "⚠️ Emissions increased by "
            f"{abs(row['reduction']):.1f}%"
        )

    else:

        st.info("No improvement — 0% reduction")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Before",
            f"{row['original']:.2f} kg"
        )

    with c2:

        st.metric(
            "After",
            f"{row['new']:.2f} kg"
        )

    with c3:

        st.metric(
            "CO₂e avoided",
            f"{row['saved']:.2f} kg"
        )

    st.caption(
        row["explanation"]
    )

    best = best_solutions(
        category,
        row["card_id"]
    )

    best_names = " / ".join(
        item["action_name"] for item in best
    )

    with st.expander(
        "💡 What was the best possible solution?"
    ):

        st.write(f"**{best_names}**")

        st.write(
            "Maximum reduction: "
            f"**{best[0]['reduction']:.1f}%**"
        )

        st.caption(
            f"Remaining emissions: "
            f"{best[0]['new']:.2f} kg CO₂e"
        )

    st.divider()

# ============================================================
# 21. FINAL RESULTS SCREEN
# ============================================================

def results_screen():

    result = st.session_state.result

    score = result["score"]

    title, emoji, message = achievement(score)

    if st.session_state.confetti:

        show_confetti()

        st.session_state.confetti = False

    color = (
        "#258052"
        if score > 0
        else "#C84848"
        if score < 0
        else "#52685C"
    )

    st.html(
        f"""
        <div class="score-box">
            <div class="achievement-emoji">{emoji}</div>
            <h2>{title}</h2>
            <div class="score-number" style="color:{color};">
                {score:.1f}%
            </div>
            <p style="font-size:18px; font-weight:600;">
                CARBON REDUCTION
            </p>
            <p style="font-size:18px;">
                {message}
            </p>
        </div>
        """
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Original footprint",
            f"{result['original']:.2f} kg"
        )

    with c2:

        st.metric(
            "Remaining footprint",
            f"{result['new']:.2f} kg"
        )

    with c3:

        st.metric(
            "CO₂e avoided",
            f"{result['saved']:.2f} kg"
        )

    scores, count = get_leaderboard()

    rank = next(
        (
            i + 1
            for i, item in enumerate(scores)
            if item["id"] == st.session_state.player_id
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
            "outside the Top 10."
        )

    st.caption(
        f"Selection time: "
        f"{st.session_state.selection_time:.1f} seconds"
    )

    st.divider()

    st.header("Discover your carbon impact")

    for row in result["rows"]:

        category_result(row)

    if st.button(
        "➕ Next participant",
        type="primary",
        use_container_width=True
    ):

        next_participant()

# ============================================================
# 22. TOP-10 LEADERBOARD PANEL
# ============================================================

def leaderboard_panel():

    st.header("🏆 Top 10")

    st.caption(
        "Ranked by carbon reduction percentage"
    )

    scores, count = get_leaderboard()

    st.metric(
        "Total participants",
        count
    )

    if not scores:

        st.info(
            "No scores yet. Become our first "
            "Carbon Champion!"
        )

    else:

        rows = []

        for i, item in enumerate(scores):

            rank = (
                "🥇" if i == 0
                else "🥈" if i == 1
                else "🥉" if i == 2
                else str(i + 1)
            )

            rows.append({
                "Rank": rank,
                "Name": item["name"],
                "Reduction": f"{item['score']:.1f}%"
            })

        st.dataframe(
            rows,
            hide_index=True,
            use_container_width=True,
            height=min(
                420,
                38 + len(rows) * 35
            )
        )

        st.caption(
            "Tie-breaker: shorter selection time."
        )

    # Controls hidden during active play.

    if st.session_state.stage == "registration":

        st.divider()

        with st.expander(
            "⚙️ Facilitator controls"
        ):

            st.caption(
                "Reset only when starting "
                "a new competition."
            )

            confirmed = st.checkbox(
                "Confirm leaderboard reset"
            )

            if st.button(
                "Reset leaderboard",
                disabled=not confirmed or count == 0,
                use_container_width=True
            ):

                reset_leaderboard()
                st.rerun()

# ============================================================
# 23. MAIN APPLICATION INTERFACE
# ============================================================

st.html("""
<div class="game-header">
    <h1>🌍 CARBON RUSH</h1>
    <p>30 seconds. 3 choices. How low can you go?</p>
</div>
""")

main_column, leaderboard_column = st.columns(
    [2.3, 1],
    gap="large"
)

with main_column:

    stage = st.session_state.stage

    if stage != "registration":

        st.text(
            f"Participant: {st.session_state.nickname}"
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

st.divider()

st.caption(
    "Carbon Rush | Learn. Choose. Reduce. | "
    "Educational scenario estimates in kg CO₂e."
)
