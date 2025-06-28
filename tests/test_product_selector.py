from product_selector import recommend_brand

def test_recommend_brand():
    assert recommend_brand({"location": "Bursa", "type": "fabrika"}) == "X"
    assert recommend_brand({"location": "Urfa", "type": "avm"}) == "Y"
    assert recommend_brand({"location": "Izmir", "type": "ev"}) == "X"
