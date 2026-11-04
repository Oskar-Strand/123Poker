from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def make(**kw):
    body = {"name": "T", "max_seats": 4, "private": False, "password": None, **kw}
    return client.post("/api/tables", json=body).json()["id"]


def join(tid, name="a", pw=None):
    return client.post(f"/api/tables/{tid}/join", json={"name": name, "password": pw})


def test_private_table_needs_password():
    assert client.post("/api/tables", json={"name": "x", "private": True}).status_code == 400
    tid = make(private=True, password="s3cret")
    assert join(tid).status_code == 403
    assert join(tid, pw="nope").status_code == 403
    assert join(tid, pw="s3cret").status_code == 200


def test_listing_shows_seated_over_max_and_hides_password():
    tid = make(private=True, password="pw")
    t1 = join(tid, "a", "pw").json()["token"]
    with client.websocket_connect(f"/ws/{tid}?token={t1}") as w:
        w.receive_json()
        w.send_json({"type": "sit", "seat": 0})
        assert w.receive_json()["my_seat"] == 0
        row = next(r for r in client.get("/api/tables").json() if r["id"] == tid)
        assert (row["seated"], row["max_seats"], row["private"]) == (1, 4, True)
        assert "password" not in row and "pw_hash" not in row


def test_hole_cards_only_visible_to_owner():
    tid = make()
    ta, tb = (join(tid, n).json()["token"] for n in "ab")
    with client.websocket_connect(f"/ws/{tid}?token={ta}") as a, \
         client.websocket_connect(f"/ws/{tid}?token={tb}") as b:
        a.receive_json(); b.receive_json(); a.receive_json()
        a.send_json({"type": "sit", "seat": 0}); a.receive_json(); b.receive_json()
        b.send_json({"type": "sit", "seat": 1}); b.receive_json(); a.receive_json()
        a.send_json({"type": "start"})
        sa, sb = a.receive_json(), b.receive_json()
        assert len(sa["seats"][0]["cards"]) == 2 and sa["seats"][1]["cards"] is None
        assert len(sb["seats"][1]["cards"]) == 2 and sb["seats"][0]["cards"] is None
        assert sa["seats"][1]["card_count"] == 2
