"""CardCraft Arenas: an original, compact turn-based card strategy game."""
from __future__ import annotations

from copy import deepcopy
import random

ARENAS = (("forge", "Forja", "🔥"), ("reef", "Maré", "💧"), ("grove", "Bosque", "🌿"))
CARDS = {
    "spark": ("Faísca", 1, 2, "forge", "Acende a primeira jogada."),
    "anchor": ("Âncora", 1, 2, "reef", "Segura uma arena disputada."),
    "sprout": ("Broto", 1, 2, "grove", "Cresce no momento certo."),
    "scout": ("Batedor", 1, 3, None, "Poder estável em qualquer arena."),
    "ember": ("Brasa", 2, 4, "forge", "Pressiona a Forja."),
    "current": ("Corrente", 2, 4, "reef", "Ganha força na Maré."),
    "root": ("Raiz", 2, 4, "grove", "Defende o Bosque."),
    "wanderer": ("Andarilho", 3, 6, None, "Encontra seu lugar em qualquer terreno."),
    "kiln": ("Fornalha", 3, 5, "forge", "Seu calor muda a disputa."),
    "tide": ("Onda Alta", 4, 8, "reef", "Uma aposta forte na Maré."),
    "canopy": ("Copa Viva", 4, 8, "grove", "Uma aposta forte no Bosque."),
    "comet": ("Cometa", 5, 10, None, "Força decisiva no fim da partida."),
}
MAX_ROUNDS = 6


def new_game(seed=None):
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    players = {}
    for side in ("a", "b"):
        deck = list(CARDS)
        rng.shuffle(deck)
        opening = next(i for i, card in enumerate(deck) if CARDS[card][1] == 1)
        deck.insert(0, deck.pop(opening))
        # The round-two draw is always affordable, avoiding a forced early pass.
        early = next(i for i in range(3, len(deck)) if CARDS[deck[i]][1] <= 2)
        deck.insert(3, deck.pop(early))
        players[side] = {"hand": deck[:3], "deck": deck[3:], "passed": False}
    return {"version": 1, "round": 1, "turn": "a", "status": "active", "winner": None,
            "players": players, "lanes": {arena[0]: {"a": [], "b": []} for arena in ARENAS},
            "log": []}


def points(cards, lane):
    return sum(CARDS[card][2] + (2 if CARDS[card][3] == lane else 0) for card in cards)


def score(state):
    return {lane: {side: points(state["lanes"][lane][side], lane) for side in ("a", "b")}
            for lane, _, _ in ARENAS}


def legal_moves(state, side):
    if state["status"] != "active" or state["turn"] != side:
        return []
    return [(card, lane) for card in state["players"][side]["hand"]
            if CARDS[card][1] <= state["round"]
            for lane, _, _ in ARENAS if len(state["lanes"][lane][side]) < 4]


def move(state, side, card=None, lane=None):
    """Return a new state; reject forged turns, cards, lanes and stale inputs."""
    if state["status"] != "active" or state["turn"] != side:
        raise ValueError("Não é sua vez.")
    if card is not None and (card, lane) not in legal_moves(state, side):
        raise ValueError("Jogada inválida: confira sua mão, energia e arena.")
    if card is None and lane is not None:
        raise ValueError("Passe sem selecionar arena.")
    result = deepcopy(state)
    if card:
        result["players"][side]["hand"].remove(card)
        result["lanes"][lane][side].append(card)
        result["log"].append({"round": result["round"], "side": side, "card": card, "lane": lane})
    else:
        result["log"].append({"round": result["round"], "side": side, "card": None, "lane": None})
    other = "b" if side == "a" else "a"
    if result["players"][other]["passed"]:
        result["players"]["a"]["passed"] = result["players"]["b"]["passed"] = False
        if result["round"] == MAX_ROUNDS:
            _finish(result)
        else:
            result["round"] += 1
            for player in result["players"].values():
                if player["deck"]:
                    player["hand"].append(player["deck"].pop(0))
            result["turn"] = "a" if result["round"] % 2 else "b"
    else:
        result["players"][side]["passed"] = True
        result["turn"] = other
    result["version"] += 1
    return result


def _finish(state):
    totals = score(state)
    wins = {side: sum(values[side] > values["b" if side == "a" else "a"] for values in totals.values())
            for side in ("a", "b")}
    if wins["a"] == wins["b"]:
        strength = {side: sum(values[side] for values in totals.values()) for side in ("a", "b")}
        state["winner"] = "a" if strength["a"] > strength["b"] else "b" if strength["b"] > strength["a"] else "draw"
    else:
        state["winner"] = "a" if wins["a"] > wins["b"] else "b"
    state["status"] = "finished"
    state["turn"] = None


def bot_move(state):
    """Simple, readable opponent that weighs power, affinity and contested lanes."""
    options = legal_moves(state, "b")
    if not options:
        return move(state, "b")
    totals = score(state)
    card, lane = max(options, key=lambda pair: (
        CARDS[pair[0]][2] + (2 if CARDS[pair[0]][3] == pair[1] else 0)
        + (3 if -4 <= totals[pair[1]]["b"] - totals[pair[1]]["a"] <= 1 else 0)
        - max(0, totals[pair[1]]["b"] - totals[pair[1]]["a"] - 3),
        pair[0], pair[1]))
    return move(state, "b", card, lane)


def redacted(state, side):
    """Never return another player's hand or remaining deck to the UI."""
    public = deepcopy(state)
    other = "b" if side == "a" else "a"
    public["players"][other]["hand"] = [None] * len(public["players"][other]["hand"])
    public["players"][other]["deck"] = [None] * len(public["players"][other]["deck"])
    public["players"][side]["deck"] = [None] * len(public["players"][side]["deck"])
    return public
