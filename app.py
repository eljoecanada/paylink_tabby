import os, secrets
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from db import init_db, conn
from gateway import create_gateway_paylink

load_dotenv()
init_db()

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000").rstrip("/")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/admin/create", response_class=HTMLResponse)
def admin_create(request: Request,
                 amount_aed: int = Form(...),
                 description: str = Form(...)):
    description = (description or "").strip()
    if amount_aed <= 0 or not description:
        raise HTTPException(400, "Invalid amount/description")

    token = secrets.token_urlsafe(10)

    with conn() as c:
        c.execute(
            "INSERT INTO paylinks(token, amount_aed, description, status) VALUES(?,?,?,?)",
            (token, amount_aed, description, "PENDING")
        )

    pay_url = f"{APP_BASE_URL}/p/{token}"
    return templates.TemplateResponse("status.html", {
        "request": request,
        "title": "Payment Link Created ✅",
        "message": "Copy and send this link to the customer:",
        "link": pay_url
    })

@app.get("/p/{token}", response_class=HTMLResponse)
def customer_pay_page(request: Request, token: str):
    with conn() as c:
        row = c.execute(
            "SELECT amount_aed, description, status FROM paylinks WHERE token=?",
            (token,)
        ).fetchone()

    if not row:
        raise HTTPException(404, "Link not found")

    amount_aed, description, status = row
    return templates.TemplateResponse("pay.html", {
        "request": request,
        "token": token,
        "amount_aed": amount_aed,
        "description": description,
        "status": status
    })

@app.post("/p/{token}/pay")
def customer_pay_redirect(token: str):
    with conn() as c:
        row = c.execute(
            "SELECT amount_aed, description, status FROM paylinks WHERE token=?",
            (token,)
        ).fetchone()

    if not row:
        raise HTTPException(404, "Link not found")

    amount_aed, description, status = row
    if status == "PAID":
        return RedirectResponse(url=f"/p/{token}", status_code=303)

    gateway_url = create_gateway_paylink(token, amount_aed, description)

    with conn() as c:
        c.execute("UPDATE paylinks SET gateway_url=? WHERE token=?", (gateway_url, token))

    return RedirectResponse(url=gateway_url, status_code=303)

# --- STUB CHECKOUT (for testing only) ---
@app.get("/stub-checkout", response_class=HTMLResponse)
def stub_checkout(request: Request, token: str, amount: int, desc: str):
    # Simulates "OTP + success" page.
    return templates.TemplateResponse("status.html", {
        "request": request,
        "title": "STUB CHECKOUT (Test Only)",
        "message": f"Simulating gateway-hosted checkout for: {desc} — {amount} AED",
        "link": f"/stub-success?token={token}"
    })

@app.get("/stub-success")
def stub_success(token: str):
    with conn() as c:
        c.execute("UPDATE paylinks SET status='PAID' WHERE token=?", (token,))
    return RedirectResponse(url=f"/p/{token}", status_code=303)