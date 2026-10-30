"""Gateway sandbox: thanh toán, vận chuyển, trợ lý AI, tìm kiếm (không cần CSDL)."""
import json

from abc_fashion.control.gateway import search_engine
from abc_fashion.control.gateway.assistant_engine import AssistantEngine, mask_personal_data
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.control.gateway.shipping_gateway import ShippingGateway
from abc_fashion.model.assistant import AssistantMode, GroundingCheck
from abc_fashion.model.catalogue import FitType, Measure, VariantStatus, MaterialComponent, ProductVariant, \
    SizeChartEntry, Style
from abc_fashion.model.customer_data import LinkedMethodType, PaymentMethod
from abc_fashion.model.fulfilment import ShipmentStatus, Shipment
from abc_fashion.model.review import FitVote, ReviewStatus, Review
from abc_fashion.model.sales import Order
from abc_fashion.model.user import Customer


def _style():
    s = Style(id=3, code="ST-M001", name="Áo thun cotton nam", fit_type=FitType.SLIM,
                 care_instructions="Giặt máy", model_info="Người mẫu cao 178 cm")
    v1 = ProductVariant(id=5, sku="M001-BLK-M", size_label="M", colour="Đen", price=250_000, status=VariantStatus.ACTIVE)
    v2 = ProductVariant(id=6, sku="M001-BLK-L", size_label="L", colour="Đen", price=250_000, status=VariantStatus.ACTIVE)
    v1.available, v2.available = 10, 0
    s.variants = [v1, v2]
    s.materials = [MaterialComponent(material="Cotton", percent=95), MaterialComponent(material="Spandex", percent=5)]
    s.size_chart = [SizeChartEntry(size_label="M", measure=Measure.CHEST, value_cm=96)]
    s.reviews = [Review(rating=4, body="Áo đẹp nhưng hơi chật", fit_vote=FitVote.RUNS_SMALL, status=ReviewStatus.APPROVED)]
    s.promotion = None
    return s


def test_payment_sandbox_declines_0002():
    gw = PaymentGateway()
    ok, ref = gw.charge(Order(grand_total=1), PaymentMethod(masked_number="**** 0002"))
    assert not ok and ref.startswith("SBX-")
    assert gw.charge(Order(grand_total=1), PaymentMethod(masked_number="**** 4242"))[0]
    assert gw.charge(Order(grand_total=1), None)[0]
    m = gw.link_method(Customer(id=1), "card", "Visa")
    assert m.method_type == LinkedMethodType.CARD and m.masked_number.startswith("**** ") and len(m.masked_number) == 9


def test_shipping_tracking_progresses():
    gw, s = ShippingGateway(), Shipment(id=7, status=ShipmentStatus.PICKED_UP)
    s.carrier, s.tracking_no = gw.create_shipment(s)
    assert s.tracking_no == "GHN00000007"
    assert gw.get_tracking(s)[0].status == ShipmentStatus.IN_TRANSIT
    s.status = ShipmentStatus.DELIVERED
    assert gw.get_tracking(s) == []


def test_mask_personal_data():
    text = mask_personal_data("Gọi 0901234567 hoặc mail an.nguyen@gmail.com")
    assert "0901234567" not in text and "@" not in text


def test_assistant_basic_answers_from_data():
    r = AssistantEngine().ask("Áo này chất liệu gì, còn size L không? sđt 0901234567", _style())
    assert r["mode"] == AssistantMode.BASIC and r["events"] == []
    assert "Cotton 95%" in r["answer"] and "Hết hàng: Đen/L" in r["answer"]
    assert "0901234567" not in r["question"]


def test_assistant_refuses_health_claims():
    r = AssistantEngine().ask("Áo này có chữa được bệnh không?", _style())
    assert "sức khoẻ" in r["answer"]


def test_grounding_removes_wrong_sentences():
    answer, events = AssistantEngine()._ground(
        "Áo giá 250.000 đ. Áo giá 199.000 đ. Áo có tác dụng kháng khuẩn. Đây là mẫu bán chạy nhất.", _style())
    assert answer == "Áo giá 250.000 đ."
    assert [e.check_name for e in events] == [GroundingCheck.PRICE, GroundingCheck.HEALTH, GroundingCheck.POPULARITY]


def test_moderation():
    eng = AssistantEngine()
    assert eng.moderate(Review(body="Áo đẹp, vải mát, đúng cỡ")) == (True, "")
    assert not eng.moderate(Review(body="Liên hệ 0987654321 để mua rẻ"))[0]
    assert not eng.moderate(Review(body="Shop vcl giao chậm"))[0]
    assert not eng.moderate(Review(body="Mua sỉ inbox zalo nhé"))[0]


def test_summarise_reviews():
    text = AssistantEngine().summarise_reviews(_style())
    assert "4.0/5" in text and "hơi chật" in text
    empty = _style()
    empty.reviews = []
    assert AssistantEngine().summarise_reviews(empty) == ""


def test_search_engine_sandbox(tmp_path, monkeypatch):
    index = tmp_path / "idx.json"
    index.write_text(json.dumps([{"id": 1, "colours": [[240, 238, 232]], "keywords": ["Áo sơ mi lụa nữ"]},
                                 {"id": 2, "colours": [[196, 40, 52]], "keywords": ["Váy liền midi hoa", "Đỏ"]}]),
                     encoding="utf-8")
    monkeypatch.setattr(search_engine, "INDEX_PATH", str(index))
    from PIL import Image
    img = tmp_path / "red.png"
    Image.new("RGB", (40, 40), (200, 30, 40)).save(img)
    eng = search_engine.SearchEngine()
    assert eng.search_by_image(img.read_bytes())[0] == 2
    assert eng.search_by_voice("tìm váy màu đỏ".encode("utf-8")) == [2]
