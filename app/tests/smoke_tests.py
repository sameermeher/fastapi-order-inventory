import os, json, time, hmac, hashlib, requests, random

BASE = os.getenv("BASE_URL", "http://localhost:8000")

def must_ok(r, code):
    assert r.status_code == code, f"Expected {code}, got {r.status_code}: {r.text}"
    return r

def sign(secret: str, body: dict) -> str:
    raw = json.dumps(body, separators=(',', ':')).encode()
    return hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()

def main():
    # 1. Create product
    sku = f"SKU-{random.randint(1000,9999)}"
    p = {"sku": sku, "name": "Test Widget", "price": 9.99, "stock": 5}
    r = requests.post(f"{BASE}/products", json=p); must_ok(r, 201)
    prod = r.json(); print("Product:", prod)
    pid = prod["id"]

    # 2. Create order
    o = {"product_id": pid, "quantity": 2}
    r = requests.post(f"{BASE}/orders", json=o); must_ok(r, 201)
    order = r.json(); print("Order:", order)
    oid = order["id"]

    # 3. Webhook: mark paid
    body = {"order_id": oid, "event": "payment.succeeded"}
    sig = sign(os.getenv("WEBHOOK_SECRET", "supersecret"), body)
    r = requests.post(f"{BASE}/webhooks/payment", headers={"X-Signature": sig}, json=body)
    must_ok(r, 200); print("Webhook:", r.json())

    # 4. Ship order
    r = requests.put(f"{BASE}/orders/{oid}", json={"status": "SHIPPED"}); must_ok(r, 200)
    print("Shipped:", r.json())

    # 5. Try to delete shipped order (should 409)
    r = requests.delete(f"{BASE}/orders/{oid}")
    assert r.status_code == 409, f"Expected 409, got {r.status_code}"
    print("Delete after shipped as expected 409")

if __name__ == "__main__":
    main()