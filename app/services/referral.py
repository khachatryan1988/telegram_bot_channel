from config import Settings
from app.repositories.referrals import get_verified_referral_count
from app.repositories.status import set_eligible


def recalc_referral_progress(settings: Settings, user_id: int) -> tuple[int, int, bool]:
    count = get_verified_referral_count(settings, user_id)
    target = settings.referral_target
    eligible = count >= target
    set_eligible(settings, user_id, eligible)
    return count, target, eligible




