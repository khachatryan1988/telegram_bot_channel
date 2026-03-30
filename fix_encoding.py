from pathlib import Path

ROOT = Path(r"D:\python codes\domus_giveaway_bot")
EXTS = {".py", ".txt", ".md", ".json", ".env", ".yml", ".yaml", ".ini"}

def try_fix_text(text: str) -> str | None:
    candidates = []

    # РЎР°РјС‹Р№ С‡Р°СЃС‚С‹Р№ СЃР»СѓС‡Р°Р№: UTF-8 С‚РµРєСЃС‚ Р±С‹Р» РїСЂРѕС‡РёС‚Р°РЅ РєР°Рє cp1251
    try:
        fixed = text.encode("cp1251").decode("utf-8")
        candidates.append(fixed)
    except Exception:
        pass

    # РРЅРѕРіРґР° Р±С‹РІР°РµС‚ С‚Р°Рє
    try:
        fixed = text.encode("latin1").decode("utf-8")
        candidates.append(fixed)
    except Exception:
        pass

    # Р РµР¶Рµ
    try:
        fixed = text.encode("cp1252").decode("utf-8")
        candidates.append(fixed)
    except Exception:
        pass

    for c in candidates:
        if any(ch in c for ch in "ХЎХўХЈХ¤ХҐХ¦Х§ХЁХ©ХЄХ«Х¬Х­Х®ХЇХ°Х±ХІХіХґХµХ¶Х·ХёХ№ХєХ»ХјХЅХѕХїЦЂЦЃЦ‚ЦѓЦ„Ц…Ц†"):
            return c

    return None

def main():
    changed = 0

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in EXTS:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        fixed = try_fix_text(text)
        if fixed and fixed != text:
            path.write_text(fixed, encoding="utf-8", newline="")
            print(f"FIXED: {path}")
            changed += 1

    print(f"\nDone. Fixed files: {changed}")

if __name__ == "__main__":
    main()
