"""本地名单测试（契约 §4.2 / §6.2）—— 落盘 / 加载 / 命中查询（离线放行）。"""

from src.roster import Roster, load_roster, save_roster

_STUDENTS = [
    {
        "student_id": "s-1",
        "student_number": "10023",
        "name": "山田太郎",
        "card_uids": ["04A1B2C3D4E5F6"],
    },
    {
        "student_id": "s-2",
        "student_number": "10024",
        "name": "鈴木花子",
        "card_uids": ["aabbccddeeff00", "11223344556677"],
    },
]


def test_find_by_uid_case_insensitive():
    r = Roster()
    r.replace("2026-07-17T00:00:00+09:00", _STUDENTS)
    # 存的是大写，查小写也应命中（契约字段 card_uid 小写，索引统一 lower）
    hit = r.find_by_uid("04a1b2c3d4e5f6")
    assert hit is not None
    assert hit["student_number"] == "10023"


def test_find_by_student_id():
    r = Roster()
    r.replace("t", _STUDENTS)
    assert r.find_by_student_id("s-2")["name"] == "鈴木花子"


def test_multiple_uids_per_student():
    r = Roster()
    r.replace("t", _STUDENTS)
    assert r.find_by_uid("11223344556677")["student_id"] == "s-2"


def test_miss_returns_none():
    r = Roster()
    r.replace("t", _STUDENTS)
    assert r.find_by_uid("deadbeefdeadbe") is None
    assert r.find_by_student_id("nope") is None


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "roster.json"
    save_roster(path, "2026-07-17T00:00:00+09:00", _STUDENTS)
    loaded = load_roster(path)
    assert loaded.size() == 2
    assert loaded.find_by_uid("aabbccddeeff00")["student_number"] == "10024"


def test_load_missing_file_returns_empty(tmp_path):
    loaded = load_roster(tmp_path / "nope.json")
    assert loaded.size() == 0


def test_replace_drops_old_students():
    # 后端只下发 active 名单，覆盖式替换 → 毕业生自然消失
    r = Roster()
    r.replace("t1", _STUDENTS)
    r.replace("t2", [_STUDENTS[0]])
    assert r.find_by_student_id("s-2") is None
    assert r.size() == 1
