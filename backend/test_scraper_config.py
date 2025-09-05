import json
from copy import deepcopy
from fastapi.testclient import TestClient
from backend import main
from backend.config import DEFAULT_SCRAPER_CONFIG

def test_post_scraper_config_persists_class(tmp_path, monkeypatch):
    temp_dir = tmp_path
    cfg_file = temp_dir / "scraper_config.json"
    monkeypatch.setattr(main, "DATA_DIR", str(temp_dir))
    monkeypatch.setattr(main, "SCRAPER_CONFIG_FILE", str(cfg_file))

    client = TestClient(main.app)

    payload = deepcopy(DEFAULT_SCRAPER_CONFIG)
    for sel, detail in payload["selectors"].items():
        if "class" in detail:
            detail["class_name"] = detail.pop("class")

    response = client.post("/api/scraper_config", json=payload)
    assert response.status_code == 200

    saved = json.loads(cfg_file.read_text())
    assert saved["selectors"]["load_more_button"]["class"] == "hotdeal-tab__load-more__btn"
    assert "class_name" not in saved["selectors"]["load_more_button"]
