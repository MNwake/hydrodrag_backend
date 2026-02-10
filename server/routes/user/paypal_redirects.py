"""
PayPal redirect landing pages.

After the user approves or cancels payment on PayPal, they are redirected to
these URLs. We serve simple HTML that tells them to return to the HydroDrags app
and (for return) tap "I've completed payment".
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/paypal", tags=["PayPal redirects"])


_RETURN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Payment approved – HydroDrags</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; box-sizing: border-box; background: #f5f5f5; }
    .card { background: #fff; padding: 2rem; border-radius: 12px; max-width: 360px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    h1 { margin: 0 0 0.5rem; font-size: 1.25rem; color: #1a1a1a; }
    p { margin: 0; color: #555; line-height: 1.5; }
    .icon { font-size: 48px; margin-bottom: 0.5rem; }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">✓</div>
    <h1>Payment approved</h1>
    <p>Return to the HydroDrags app and tap <strong>“I've completed payment”</strong> to finish your registration.</p>
  </div>
</body>
</html>
"""

_CANCEL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Payment cancelled – HydroDrags</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; box-sizing: border-box; background: #f5f5f5; }
    .card { background: #fff; padding: 2rem; border-radius: 12px; max-width: 360px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    h1 { margin: 0 0 0.5rem; font-size: 1.25rem; color: #1a1a1a; }
    p { margin: 0; color: #555; line-height: 1.5; }
    .icon { font-size: 48px; margin-bottom: 0.5rem; }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">✕</div>
    <h1>Payment cancelled</h1>
    <p>You can return to the HydroDrags app to try again or change your order.</p>
  </div>
</body>
</html>
"""
_SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Payment approved – HydroDrags</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      margin: 0;
      padding: 2rem;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background: #f5f5f5;
    }
    .card {
      background: #fff;
      padding: 2rem;
      border-radius: 14px;
      max-width: 380px;
      text-align: center;
      box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }
    .icon {
      font-size: 48px;
      margin-bottom: 0.75rem;
    }
    h1 {
      margin: 0 0 0.5rem;
      font-size: 1.4rem;
      color: #111;
    }
    p {
      margin: 0.5rem 0;
      color: #555;
      line-height: 1.5;
    }
    .btn {
      display: inline-block;
      margin-top: 1.25rem;
      padding: 0.75rem 1.25rem;
      border-radius: 10px;
      background: #0b74ff;
      color: #fff;
      font-weight: 600;
      text-decoration: none;
    }
    .order {
      margin-top: 0.75rem;
      font-size: 0.85rem;
      color: #888;
      word-break: break-all;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">✅</div>
    <h1>Payment approved</h1>

    <p>Your payment was approved by PayPal.</p>
    <p>To finish, return to the HydroDrags app and complete the purchase.</p>

    <a
      class="btn"
      href="hydrodrags://paypal/complete?order_id={{ORDER_ID}}"
    >
      Return to HydroDrags
    </a>

    <div class="order">
      Order ID:<br>{{ORDER_ID}}
    </div>
  </div>
</body>
</html>
"""

@router.get("/return", response_class=HTMLResponse)
async def paypal_return():
    """Landing page after user approves payment on PayPal."""
    return HTMLResponse(content=_RETURN_HTML)


@router.get("/cancel", response_class=HTMLResponse)
async def paypal_cancel():
    """Landing page after user cancels payment on PayPal."""
    return HTMLResponse(content=_CANCEL_HTML)

@router.get("/success", response_class=HTMLResponse)
async def paypal_return(token: str | None = None):
    return HTMLResponse(
        content=_SUCCESS_HTML.replace("{{ORDER_ID}}", token or "")
    )
