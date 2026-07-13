from django.http import HttpResponse

MAINTENANCE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bare Bones Soccer — Back Soon</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #08070b;
    color: #fdf5ed;
    font-family: 'Arial', sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 20px;
  }
  .wrap { max-width: 520px; }
  .skull { font-size: 4rem; margin-bottom: 24px; }
  h1 {
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #fdf5ed;
    margin-bottom: 16px;
  }
  p {
    font-size: 1.05rem;
    color: rgba(253,245,237,0.65);
    line-height: 1.7;
    margin-bottom: 12px;
  }
  .accent { color: #00b8e8; font-weight: 700; }
</style>
</head>
<body>
  <div class="wrap">
    <div class="skull">💀⚽</div>
    <h1>We'll Be Right Back</h1>
    <p>The site is currently undergoing maintenance.</p>
    <p>Back up <span class="accent">very soon</span> — thanks for your patience.</p>
    <p style="margin-top:28px; font-size:0.85rem; color:rgba(253,245,237,0.35);">barebonessoccer.com</p>
  </div>
</body>
</html>"""


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return HttpResponse(MAINTENANCE_HTML, status=503)


def maintenance_view(request, *args, **kwargs):
    return HttpResponse(MAINTENANCE_HTML, status=503)
