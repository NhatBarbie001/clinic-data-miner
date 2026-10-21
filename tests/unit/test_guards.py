"""P1.4 - Guard tất định theo token. #1-#12 khớp mục 5 của docs/phases/P1/P1.4_plan.md."""

import pytest

from dataminer.ingest.guards import GlossaryIndex, apply_guarded_fix, similarity

GLOSSARY = GlossaryIndex(["Helicobacter", "pylori", "omeprazol", "mg", "g", "corticoid"])


def guard(original: str, proposed: str):  # type: ignore[no-untyped-def]
    return apply_guarded_fix(original, proposed, GLOSSARY)


def test_01_diacritics_accepted() -> None:
    r = guard("viêm khop dạng thấp", "viêm khớp dạng thấp")
    assert r.text == "viêm khớp dạng thấp"
    assert [(f.before, f.after, f.accepted, f.rule) for f in r.fixes] == [
        ("khop", "khớp", True, "ok")
    ]
    assert r.flags == []


def test_02_misread_dose_rejected_and_flagged() -> None:
    r = guard("- Paracetamol 5OO mg mỗi lần", "- Paracetamol 500 mg mỗi lần")
    assert r.text == "- Paracetamol 5OO mg mỗi lần"  # KHÔNG tự sửa
    (fix,) = r.fixes
    assert (fix.accepted, fix.rule, fix.suggestion) == (False, "G-num", "500")
    assert "dose_suspect" in r.flags


def test_03_real_number_change_rejected_without_suggestion() -> None:
    r = guard("omeprazol 20 mg uống", "omeprazol 200 mg uống")
    assert r.text == "omeprazol 20 mg uống"
    assert r.fixes[0].suggestion is None
    assert "number_change_rejected" in r.flags
    assert "dose_suspect" not in r.flags


def test_04_letter_before_unit_flagged() -> None:
    r = guard("l g", "1 g")
    assert r.text == "l g"
    assert r.fixes[0].suggestion == "1"
    assert "dose_suspect" in r.flags


def test_05_protected_term_kept() -> None:
    r = guard("vi khuẩn Helicobacter pylori", "vi khuẩn Helicobacte pylori")
    assert r.text == "vi khuẩn Helicobacter pylori"
    assert r.fixes[0].rule == "G-protect"


def test_05b_protected_unit_cannot_become_other_unit() -> None:
    """mg → g: cả hai đều trong glossary, nhưng đổi đơn vị là đổi liều - phải chặn."""
    r = guard("uống 20 mg mỗi", "uống 20 g mỗi")
    assert r.text == "uống 20 mg mỗi"
    assert r.fixes[0].rule == "G-protect"


def test_05c_corrupted_drug_name_can_be_fixed() -> None:
    """Tên thuốc bị OCR làm sai không nằm trong glossary → được sửa về đúng."""
    r = guard("vi khuẩn Helicobaeter pylori gây loét", "vi khuẩn Helicobacter pylori gây loét")
    assert r.text == "vi khuẩn Helicobacter pylori gây loét"


def test_06_latin_hyphen_term_protected() -> None:
    r = guard(
        "người mang kháng thể anti-CCP dương tính", "người mang kháng thể anti-CPP dương tính"
    )
    assert r.text == "người mang kháng thể anti-CCP dương tính"
    assert r.fixes[0].rule == "G-protect"


def test_07_split_merged_word_accepted() -> None:
    r = guard("kèm theo phảnứng của xương", "kèm theo phản ứng của xương")
    assert r.text == "kèm theo phản ứng của xương"
    assert r.fixes[0].rule == "split_merge"


def test_07b_split_with_punctuation() -> None:
    """Dính từ qua dấu câu (P0.5 seed 2) được tách; vùng có CHỮ SỐ thì không tự tách/dính."""
    r = guard("trong 14 ngày(Bảng 2.1).", "trong 14 ngày (Bảng 2.1).")
    assert r.text == "trong 14 ngày (Bảng 2.1)."
    r2 = guard("uống 500mg mỗi lần", "uống 500 mg mỗi lần")
    assert r2.text == "uống 500mg mỗi lần"
    assert r2.fixes[0].rule == "G-num"


def test_08_synonym_rejected() -> None:
    r = guard("bệnh nhân đau đầu nhiều", "bệnh nhân nhức đầu nhiều")
    assert r.text == "bệnh nhân đau đầu nhiều"
    assert r.fixes[0].rule == "G-sim"


def test_09_inserted_word_rejected() -> None:
    r = guard("sốt cao kéo dài", "sốt cao thường kéo dài")
    assert r.text == "sốt cao kéo dài"
    assert r.fixes[0].rule == "G-insdel"


def test_09b_deleted_word_rejected() -> None:
    r = guard("sốt cao kéo dài nhiều ngày", "sốt cao kéo dài ngày")
    assert r.text == "sốt cao kéo dài nhiều ngày"


def test_10_rewritten_sentence_rejects_whole_block() -> None:
    r = guard(
        "Bệnh gặp chủ yếu ở nữ giới tuổi trung niên",
        "Phụ nữ trung niên là nhóm thường mắc bệnh nhất",
    )
    assert r.text == "Bệnh gặp chủ yếu ở nữ giới tuổi trung niên"
    assert r.fixes[0].rule == "G-ratio"
    assert "fix_rejected" in r.flags


def test_10b_many_diacritic_fixes_are_not_a_rewrite() -> None:
    """Sửa dấu thuần túy không tính vào tỉ lệ thay đổi: câu mất dấu toàn bộ vẫn được sửa."""
    r = guard("benh nhan bi sot cao keo dai", "bệnh nhân bị sốt cao kéo dài")
    assert r.text == "bệnh nhân bị sốt cao kéo dài"
    assert "fix_rejected" not in r.flags


def test_10c_short_cell_diacritic_fix() -> None:
    """Ô bảng 1 từ: đổi 1/1 từ không bị coi là viết lại (đối chứng dương phát hiện lỗi này)."""
    assert guard("Thuộc", "Thuốc").text == "Thuốc"
    assert guard("14 ngảy", "14 ngày").text == "14 ngày"


def test_11_mixed_block_partial_accept() -> None:
    r = guard(
        "- Paracetamol 5OO mg rnỗi lần, khong quá 3 g",
        "- Paracetamol 500 mg mỗi lần, không quá 3 g",
    )
    assert r.text == "- Paracetamol 5OO mg mỗi lần, không quá 3 g"
    accepted = {(f.before, f.after) for f in r.fixes if f.accepted}
    assert accepted == {("rnỗi", "mỗi"), ("khong", "không")}
    assert "dose_suspect" in r.flags
    assert "fix_partially_rejected" in r.flags


def test_12_fix_records_complete() -> None:
    r = guard("cho 1à kết quả, tbuốc lá", "cho là kết quả. thuốc lá")
    rules = {(f.before, f.after): (f.accepted, f.rule) for f in r.fixes}
    assert rules[("1à", "là")] == (True, "digit_letter")  # ngoại lệ hẹp của G-num
    assert rules[("quả,", "quả.")] == (False, "G-punct")
    assert rules[("tbuốc", "thuốc")] == (True, "ok")
    assert all(f.position >= 0 for f in r.fixes)


@pytest.mark.parametrize(
    ("before", "after", "ok"),
    [
        ("1à", "là", True),
        ("1 giờ", "l giờ", False),
        ("10", "lo", False),
        ("1à", "1a", False),
        ("2à", "là", False),
    ],
)
def test_digit_letter_exception_is_narrow(before: str, after: str, ok: bool) -> None:
    r = guard(f"x {before} y", f"x {after} y")
    assert (r.text == f"x {after} y") is ok


def test_rn_m_confusion_similarity() -> None:
    assert similarity("rnỗi", "mỗi") == 1.0
    assert similarity("viêrn", "viêm") == 1.0
    assert similarity("đau", "nhức") < 0.6


def test_identical_text_no_fixes() -> None:
    r = guard("Không có lỗi.", "Không có lỗi.")
    assert (r.text, r.fixes, r.flags) == ("Không có lỗi.", [], [])
