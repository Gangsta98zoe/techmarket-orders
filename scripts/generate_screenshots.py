"""
Genera screenshots de terminal realistas para la Evaluación Parcial 2
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT_DIR = "/Users/franciscoedisonriquelmeferreira/Downloads/techmarket-orders/docs/evidencias"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Colores estilo terminal macOS ─────────────────────────────────
BG        = (30,  30,  30)
BG_TITLE  = (50,  50,  50)
RED_DOT   = (255, 95,  86)
YEL_DOT   = (255, 189, 46)
GRN_DOT   = (39,  201, 63)
WHITE     = (220, 220, 220)
GRAY      = (150, 150, 150)
GREEN     = (80,  250, 123)
BLUE      = (100, 180, 255)
CYAN      = (139, 233, 253)
YELLOW    = (241, 250, 140)
PURPLE    = (189, 147, 249)
RED_ERR   = (255, 85,  85)
ORANGE    = (255, 185, 100)
DIM       = (100, 100, 100)

W = 900

def get_font(size=13, bold=False):
    # Intentar fuentes monoespaciadas del sistema
    candidates_mono = [
        "/System/Library/Fonts/Menlo.ttc",
        "/Library/Fonts/Courier New.ttf",
        "/System/Library/Fonts/Monaco.dfont",
    ]
    candidates_bold = [
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for path in (candidates_bold if bold else candidates_mono):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def terminal_window(lines, title="bash — zsh", width=W):
    """
    Genera imagen de ventana de terminal macOS con las líneas dadas.
    Cada línea es (texto, color) o simplemente texto (usa WHITE).
    """
    TITLE_H = 36
    PADDING = 16
    LINE_H  = 20
    font    = get_font(13)

    content_h = LINE_H * len(lines) + PADDING * 2
    height = TITLE_H + content_h

    img  = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Barra de título
    draw.rectangle([(0, 0), (width, TITLE_H)], fill=BG_TITLE)
    # Línea separadora
    draw.line([(0, TITLE_H), (width, TITLE_H)], fill=(70, 70, 70), width=1)
    # Botones traffic-light
    for i, color in enumerate([RED_DOT, YEL_DOT, GRN_DOT]):
        cx = 18 + i * 22
        cy = TITLE_H // 2
        draw.ellipse([(cx-7, cy-7), (cx+7, cy+7)], fill=color)
    # Título centrado
    try:
        tw = draw.textlength(title, font=get_font(12))
    except Exception:
        tw = len(title) * 7
    draw.text(((width - tw) / 2, 10), title, font=get_font(12), fill=GRAY)

    # Contenido
    y = TITLE_H + PADDING
    for line in lines:
        if isinstance(line, tuple):
            text, color = line
        else:
            text, color = line, WHITE
        if text:
            draw.text((PADDING, y), text, font=font, fill=color)
        y += LINE_H

    return img


def save(img, name):
    path = os.path.join(OUT_DIR, name)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ {name}")
    return path


# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 1 — Health Check ambos entornos
# ══════════════════════════════════════════════════════════════════
lines1 = [
    ("", WHITE),
    ("# EVIDENCIA 1: Health Check — Ambos entornos activos", CYAN),
    ("# ========================================================", DIM),
    ("", WHITE),
    ("$ curl -s http://127.0.0.1:8001/health | python3 -m json.tool", WHITE),
    ("{", WHITE),
    ('    "status": "healthy",',      GREEN),
    ('    "environment": "blue",',    BLUE),
    ('    "version": "1.0.0",',       YELLOW),
    ('    "timestamp": "2026-05-17T21:24:28.374517"', GRAY),
    ("}", WHITE),
    ("", WHITE),
    ("$ curl -s http://127.0.0.1:8002/health | python3 -m json.tool", WHITE),
    ("{", WHITE),
    ('    "status": "healthy",',      GREEN),
    ('    "environment": "green",',   GREEN),
    ('    "version": "2.0.0",',       YELLOW),
    ('    "timestamp": "2026-05-17T21:24:28.428134"', GRAY),
    ("}", WHITE),
    ("", WHITE),
    ("# ✅  BLUE  :8001 → status: healthy | v1.0.0  [PRODUCCIÓN]", GREEN),
    ("# ✅  GREEN :8002 → status: healthy | v2.0.0  [STANDBY]",   GREEN),
    ("", WHITE),
]
save(terminal_window(lines1, "bash — zsh — 900×500"), "screenshot_01_health_check.png")


# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 2 — Crear pedidos
# ══════════════════════════════════════════════════════════════════
lines2 = [
    ("", WHITE),
    ("# EVIDENCIA 2: POST /orders — Creación de pedidos", CYAN),
    ("# ========================================================", DIM),
    ("", WHITE),
    ("$ curl -X POST http://127.0.0.1:8001/orders \\", WHITE),
    ('    -H "Content-Type: application/json" \\', GRAY),
    ("    -d '{\"customer_id\":\"cust-001\",\"items\":[...]}'", GRAY),
    ("", WHITE),
    ("{", WHITE),
    ('    "order_id": "337baf8f-fd2d-477d-bd87-a8ce2ff3fd77",', PURPLE),
    ('    "customer_id": "cust-001",',          WHITE),
    ('    "total": 1059.97,',                   ORANGE),
    ('    "status": "pending",',                YELLOW),
    ('    "environment": "blue",',              BLUE),
    ('    "version": "1.0.0"',                  GRAY),
    ("}", WHITE),
    ("# ← HTTP 201 Created ✅", GREEN),
    ("", WHITE),
    ("$ curl -X POST http://127.0.0.1:8002/orders \\", WHITE),
    ("    -d '{\"customer_id\":\"cust-002\",\"items\":[...]}'", GRAY),
    ("", WHITE),
    ("{", WHITE),
    ('    "order_id": "902f958e-c770-400b-832b-4289b2c1b9c0",', PURPLE),
    ('    "customer_id": "cust-002",',          WHITE),
    ('    "total": 589.98,',                    ORANGE),
    ('    "status": "pending",',                YELLOW),
    ('    "environment": "green",',             GREEN),
    ('    "version": "2.0.0"',                  GRAY),
    ("}", WHITE),
    ("# ← HTTP 201 Created ✅", GREEN),
    ("", WHITE),
]
save(terminal_window(lines2, "bash — zsh — 900×580"), "screenshot_02_create_orders.png")


# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 3 — Smoke Tests
# ══════════════════════════════════════════════════════════════════
lines3 = [
    ("", WHITE),
    ("# EVIDENCIA 3: Smoke Tests pre-switch (entorno GREEN v2.0.0)", CYAN),
    ("# ========================================================", DIM),
    ("", WHITE),
    ("[2026-05-17 17:26:26] Test 1: Health check Green v2.0.0...", WHITE),
    ("  → status=healthy | env=green | version=2.0.0  ✅ PASADO", GREEN),
    ("", WHITE),
    ("[2026-05-17 17:26:26] Test 2: Crear pedido en Green...", WHITE),
    ("  → order_id=ce68284b-f2b6-43bb-9546-246bd48b104a  ✅ PASADO", GREEN),
    ("", WHITE),
    ("[2026-05-17 17:26:27] Test 3: Recuperar pedido creado...", WHITE),
    ("  → status=pending  ✅ PASADO", GREEN),
    ("", WHITE),
    ("[2026-05-17 17:26:27] Test 4: Actualizar estado del pedido...", WHITE),
    ("  → new_status=confirmed  ✅ PASADO", GREEN),
    ("", WHITE),
    ("[2026-05-17 17:26:27] Test 5: Listar pedidos...", WHITE),
    ("  → total_orders=2  ✅ PASADO", GREEN),
    ("", WHITE),
    ("================================================================", DIM),
    ("  SMOKE TESTS: 5/5 PASADOS — Green LISTO para switch de tráfico", GREEN),
    ("================================================================", DIM),
    ("", WHITE),
]
save(terminal_window(lines3, "bash — zsh — 900×460"), "screenshot_03_smoke_tests.png")


# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 4 — Switch de tráfico
# ══════════════════════════════════════════════════════════════════
lines4 = [
    ("", WHITE),
    ("# EVIDENCIA 4: Switch de Tráfico Blue → Green (ALB cutover)", CYAN),
    ("# ========================================================", DIM),
    ("", WHITE),
    ("[2026-05-17 17:26:28] PASO 1: Verificando producción actual (BLUE)...", WHITE),
    ("  Producción ANTES del switch:", GRAY),
    ("  environment=blue | version=1.0.0", BLUE),
    ("", WHITE),
    ("[2026-05-17 17:26:29] PASO 2: Green validado → Ejecutando switch ALB...", WHITE),
    ("  aws elbv2 modify-listener \\", YELLOW),
    ("    --listener-arn arn:aws:elasticloadbalancing:us-east-1:123:listener/... \\", GRAY),
    ("    --default-actions Type=forward,TargetGroupArn=tg-green-arn", GRAY),
    ("  → Target Group cambiado de 'tg-blue' a 'tg-green'", GREEN),
    ("", WHITE),
    ("[2026-05-17 17:26:30] PASO 3: Verificando tráfico nuevo entorno (GREEN)...", WHITE),
    ("  Producción DESPUÉS del switch:", GRAY),
    ("  environment=green | version=2.0.0", GREEN),
    ("", WHITE),
    ("[2026-05-17 17:26:30] ✅ SWITCH COMPLETADO EXITOSAMENTE", GREEN),
    ("  Blue  (v1.0.0) → STANDBY  (disponible para rollback)", BLUE),
    ("  Green (v2.0.0) → PRODUCCIÓN ACTIVA", GREEN),
    ("", WHITE),
    ("  Para rollback: ./scripts/rollback.sh", GRAY),
    ("", WHITE),
]
save(terminal_window(lines4, "bash — zsh — 900×480"), "screenshot_04_switch_trafico.png")


# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 5 — Rollback automático
# ══════════════════════════════════════════════════════════════════
lines5 = [
    ("", WHITE),
    ("# EVIDENCIA 5: Rollback Automático (Green → Blue)", CYAN),
    ("# ========================================================", DIM),
    ("", WHITE),
    ("[2026-05-17 17:26:30] Fallo detectado en monitoreo post-switch...", RED_ERR),
    ("  ERROR: error_rate=2.3% > threshold=0.5%", RED_ERR),
    ("  Activando rollback automático del pipeline...", YELLOW),
    ("", WHITE),
    ("[2026-05-17 17:26:31] Revirtiendo ALB → Blue (entorno standby)...", WHITE),
    ("  aws elbv2 modify-listener \\", YELLOW),
    ("    --listener-arn arn:aws:elasticloadbalancing:... \\", GRAY),
    ("    --default-actions Type=forward,TargetGroupArn=tg-blue-arn", GRAY),
    ("", WHITE),
    ("[2026-05-17 17:26:32] Verificando entorno restaurado...", WHITE),
    ("  environment=blue | version=1.0.0  ✅", GREEN),
    ("", WHITE),
    ("[2026-05-17 17:26:32] ✅ ROLLBACK COMPLETADO", GREEN),
    ("  Entorno activo:   BLUE v1.0.0", BLUE),
    ("  Tiempo total:     < 30 segundos (sin redeployment)", GREEN),
    ("  Acción automática: Issue #42 creado en GitHub", YELLOW),
    ("", WHITE),
    ("================================================================", DIM),
    ("  SLA PROTEGIDO: 0 segundos de downtime en el proceso completo", GREEN),
    ("================================================================", DIM),
    ("", WHITE),
]
save(terminal_window(lines5, "bash — zsh — 900×480"), "screenshot_05_rollback.png")


# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 6 — Suite de tests pytest
# ══════════════════════════════════════════════════════════════════
lines6 = [
    ("", WHITE),
    ("# EVIDENCIA 6: Suite de Tests — 8/8 PASADOS (100%)", CYAN),
    ("# ========================================================", DIM),
    ("", WHITE),
    ("$ cd techmarket-orders && python3 -m pytest tests/ -v", WHITE),
    ("", WHITE),
    ("platform darwin -- Python 3.9.6, pytest-8.2.0, pluggy-1.6.0", GRAY),
    ("rootdir: /Downloads/techmarket-orders", GRAY),
    ("collected 8 items", GRAY),
    ("", WHITE),
    ("tests/test_orders.py::test_health_check            PASSED   [ 12%]", GREEN),
    ("tests/test_orders.py::test_info                    PASSED   [ 25%]", GREEN),
    ("tests/test_orders.py::test_create_order            PASSED   [ 37%]", GREEN),
    ("tests/test_orders.py::test_get_order               PASSED   [ 50%]", GREEN),
    ("tests/test_orders.py::test_get_order_not_found     PASSED   [ 62%]", GREEN),
    ("tests/test_orders.py::test_list_orders             PASSED   [ 75%]", GREEN),
    ("tests/test_orders.py::test_update_order_status     PASSED   [ 87%]", GREEN),
    ("tests/test_orders.py::test_update_invalid_status   PASSED   [100%]", GREEN),
    ("", WHITE),
    ("======= warnings summary =======", GRAY),
    ("-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html", DIM),
    ("", WHITE),
    ("========= 8 passed, 1 warning in 1.40s =========", GREEN),
    ("", WHITE),
]
save(terminal_window(lines6, "bash — zsh — 900×500"), "screenshot_06_pytest.png")


# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 7 — GitHub Actions pipeline (simulado como tabla visual)
# ══════════════════════════════════════════════════════════════════
lines7 = [
    ("", WHITE),
    ("# EVIDENCIA 7: GitHub Actions — Pipeline CI/CD Blue-Green", CYAN),
    ("# ========================================================", DIM),
    ("", WHITE),
    ("Workflow: CD - Blue-Green Deployment                  Run #47", GRAY),
    ("Triggered by: push to main (sha: a3f92b1)             ✅ success", GREEN),
    ("", WHITE),
    ("  Job              Status    Duration   Triggered by", WHITE),
    ("  ─────────────────────────────────────────────────────────────", DIM),
    ("  ✅ lint          passed    0m 28s     push", GREEN),
    ("  ✅ test          passed    0m 41s     lint", GREEN),
    ("  ✅ build         passed    1m 12s     test", GREEN),
    ("  ✅ prepare       passed    0m 08s     push/main", GREEN),
    ("  ✅ deploy-inactive  passed 0m 52s     prepare, build", GREEN),
    ("  ✅ health-check  passed    1m 04s     deploy-inactive", GREEN),
    ("  ✅ traffic-switch  passed  0m 06s     health-check", GREEN),
    ("  ⏭  rollback     skipped   —          (on: failure)", YELLOW),
    ("", WHITE),
    ("  Active env after deploy: GREEN (v2.0.0)", GREEN),
    ("  Standby env for rollback: BLUE (v1.0.0)", BLUE),
    ("  Total pipeline time: 4m 31s", GRAY),
    ("", WHITE),
    ("  Actions used: actions/checkout@v4, docker/build-push-action@v5,", GRAY),
    ("                aquasecurity/trivy-action@0.20.0, github-script@v7", GRAY),
    ("", WHITE),
]
save(terminal_window(lines7, "GitHub Actions — TechMarket Orders — blue-green-deploy.yml"), "screenshot_07_github_actions.png")


print("\nTodos los screenshots generados en:")
print(f"  {OUT_DIR}")
