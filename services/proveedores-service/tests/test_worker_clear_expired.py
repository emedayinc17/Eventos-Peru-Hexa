import importlib
import pathlib
import sys

from types import SimpleNamespace


def load_worker_module():
    repo_root = pathlib.Path(__file__).resolve().parents[3]
    service_dir = repo_root / "services" / "proveedores-service"
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    ev_shared_path = repo_root / "libs" / "shared"
    if str(ev_shared_path) not in sys.path:
        sys.path.insert(0, str(ev_shared_path))
    if str(service_dir) not in sys.path:
        sys.path.insert(0, str(service_dir))

    return importlib.import_module("app.workers.clear_expired_holds")


def test_clear_expired_holds_calls_liberar(monkeypatch):
    mod = load_worker_module()

    # fake repo with list_expired_holds and liberar_hold
    class FakeRepo:
        def __init__(self):
            self.released = []

        def list_expired_holds(self, s):
            return [SimpleNamespace(id="h1"), SimpleNamespace(id="h2")]

        def liberar_hold(self, s, hold_id: str):
            self.released.append(hold_id)

    fake = FakeRepo()

    # Monkeypatch repository class used inside worker
    monkeypatch.setattr(mod, "MySQLHoldsRepository", lambda: fake)

    # Monkeypatch session_scope to provide a single dummy session via contextmanager
    from contextlib import contextmanager

    @contextmanager
    def fake_session_scope(settings=None):
        yield object()

    monkeypatch.setattr(mod, "session_scope", fake_session_scope)

    released = mod.clear_expired_holds()
    assert released == 2
    assert fake.released == ["h1", "h2"]
