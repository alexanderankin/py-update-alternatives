# noinspection PyUnusedLocal,SpellCheckingInspection
def pytest_sessionstart(session):
    import update_alternatives

    update_alternatives.OPTIONS_LOCATIONS = []
