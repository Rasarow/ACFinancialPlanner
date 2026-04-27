from models import db


def add_xp(user, amount):
    user.xp = (user.xp or 0) + amount

    while user.xp >= user.xp_needed:
        user.xp -= user.xp_needed
        user.level = (user.level or 1) + 1
        user.xp_needed = int((user.xp_needed or 100) * 1.3)

    db.session.commit()


def handle_leveling(user):
    # safety net
    while user.xp >= user.xp_needed:
        user.xp -= user.xp_needed
        user.level += 1
        user.xp_needed = int(user.xp_needed * 1.3)

    db.session.commit()