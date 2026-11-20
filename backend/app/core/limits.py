from app.config import FREE_CARDS, FREE_DECKS


def deck_allowed(is_prem: bool, deck_count: int) -> bool:
    return is_prem or deck_count < FREE_DECKS


def cards_allowed(is_prem: bool, current: int, adding: int) -> bool:
    return is_prem or current + adding <= FREE_CARDS
