import os
from urllib.parse import urlencode

def create_gateway_paylink(token: str, amount_aed: int, description: str) -> str:
    """
    IMPORTANT:
    - Do NOT collect Tabby/card details yourself.
    - This function must return a hosted checkout URL from your payment gateway
      (PayTabs/Telr/etc.) where Tabby + OTP happens.
    """
    mode = os.getenv("GATEWAY_MODE", "stub").lower()

    # STUB MODE: for testing the flow (redirect + return)
    if mode == "stub":
        params = urlencode({"token": token, "amount": amount_aed, "desc": description})
        return f"/stub-checkout?{params}"

    # PLACEHOLDER for PayTabs/Telr integration (we will fill once you have merchant creds)
    raise RuntimeError("Gateway not configured. Set GATEWAY_MODE=stub or provide gateway credentials.")