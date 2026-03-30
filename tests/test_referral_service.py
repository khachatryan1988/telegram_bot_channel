from app.repositories.referrals import set_referrer
from app.repositories.status import ensure_status_row, set_verified
from app.repositories.users import create_user
from app.services.referral import recalc_referral_progress


def _create_user(settings, tg_id: int) -> int:
    user_id = create_user(
        settings,
        tg_id=tg_id,
        username=f"user{tg_id}",
        first_name=f"User{tg_id}",
        last_name=None,
    )
    ensure_status_row(settings, user_id)
    return user_id


def test_recalc_referral_progress_counts_only_verified_referrals(settings) -> None:
    referrer_id = _create_user(settings, 100)
    invited_a = _create_user(settings, 101)
    invited_b = _create_user(settings, 102)
    invited_c = _create_user(settings, 103)

    assert set_referrer(settings, referrer_id, invited_a) is True
    assert set_referrer(settings, referrer_id, invited_b) is True
    assert set_referrer(settings, referrer_id, invited_c) is True

    set_verified(settings, invited_a, True)
    set_verified(settings, invited_b, True)

    count, target, eligible = recalc_referral_progress(settings, referrer_id)

    assert count == 2
    assert target == 3
    assert eligible is False


def test_recalc_referral_progress_marks_user_eligible_at_target(settings) -> None:
    referrer_id = _create_user(settings, 200)
    invited_ids = [_create_user(settings, tg_id) for tg_id in (201, 202, 203)]

    for invited_id in invited_ids:
        assert set_referrer(settings, referrer_id, invited_id) is True
        set_verified(settings, invited_id, True)

    count, target, eligible = recalc_referral_progress(settings, referrer_id)

    assert count == 3
    assert target == 3
    assert eligible is True


def test_referral_binding_is_idempotent(settings) -> None:
    referrer_a = _create_user(settings, 300)
    referrer_b = _create_user(settings, 301)
    invited_id = _create_user(settings, 302)

    assert set_referrer(settings, referrer_a, invited_id) is True
    assert set_referrer(settings, referrer_b, invited_id) is False




