"""
Informe PDF con screenshots reales como imágenes
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from PIL import Image as PILImage
import datetime, os

# ── Rutas ─────────────────────────────────────────────────────────
EVIDENCIAS = "/Users/franciscoedisonriquelmeferreira/Downloads/techmarket-orders/docs/evidencias"
OUTPUT = "/Users/franciscoedisonriquelmeferreira/Downloads/Informe_EV_Parcial2_AUY1104_TechMarket_Orders.pdf"

# ── Colores ────────────────────────────────────────────────────────
BLUE_DARK   = colors.HexColor("#1a3a5c")
BLUE_MID    = colors.HexColor("#2563eb")
BLUE_LIGHT  = colors.HexColor("#dbeafe")
GREEN_DARK  = colors.HexColor("#15803d")
GREEN_LIGHT = colors.HexColor("#dcfce7")
GRAY_BG     = colors.HexColor("#f8fafc")
GRAY_BORDER = colors.HexColor("#e2e8f0")
GRAY_TEXT   = colors.HexColor("#475569")
RED_LIGHT   = colors.HexColor("#fee2e2")
RED_DARK    = colors.HexColor("#dc2626")
YELLOW_LIGHT = colors.HexColor("#fef9c3")
WHITE       = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm
CONTENT_W = PAGE_W - 2 * MARGIN


def make_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("Cover_Title",  fontName="Helvetica-Bold", fontSize=26, textColor=WHITE, alignment=TA_CENTER, spaceAfter=6, leading=32))
    s.add(ParagraphStyle("Cover_Sub",   fontName="Helvetica",      fontSize=12, textColor=colors.HexColor("#bfdbfe"), alignment=TA_CENTER, spaceAfter=4))
    s.add(ParagraphStyle("Cover_Info",  fontName="Helvetica",      fontSize=10.5, textColor=WHITE, alignment=TA_CENTER, spaceAfter=3))
    s.add(ParagraphStyle("Sec_Title",   fontName="Helvetica-Bold", fontSize=13, textColor=WHITE, spaceBefore=4, spaceAfter=4, leading=18))
    s.add(ParagraphStyle("Sub_Title",   fontName="Helvetica-Bold", fontSize=11, textColor=BLUE_MID, spaceBefore=8, spaceAfter=4))
    s.add(ParagraphStyle("Body",        fontName="Helvetica",      fontSize=9.5, textColor=colors.HexColor("#1e293b"), alignment=TA_JUSTIFY, spaceAfter=5, leading=14))
    s.add(ParagraphStyle("Caption",     fontName="Helvetica-Oblique", fontSize=8, textColor=GRAY_TEXT, alignment=TA_CENTER, spaceAfter=10))
    s.add(ParagraphStyle("Footer",      fontName="Helvetica", fontSize=7.5, textColor=GRAY_TEXT, alignment=TA_CENTER))
    return s


def sec_header(title, styles, bg=BLUE_DARK):
    data = [[Paragraph(title, styles["Sec_Title"])]]
    t = Table(data, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
    ]))
    return t


def screenshot(filename, caption, styles, scale=1.0):
    """Inserta un screenshot PNG con borde y caption."""
    path = os.path.join(EVIDENCIAS, filename)
    if not os.path.exists(path):
        return Paragraph(f"[Imagen no encontrada: {filename}]", styles["Caption"])

    pil = PILImage.open(path)
    orig_w, orig_h = pil.size
    target_w = CONTENT_W * scale
    target_h = target_w * orig_h / orig_w

    img = RLImage(path, width=target_w, height=target_h)

    # Marco + imagen en tabla para dar borde
    data = [[img]]
    t = Table(data, colWidths=[target_w])
    t.setStyle(TableStyle([
        ("BOX",           (0,0), (-1,-1), 1.5, GRAY_BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING",   (0,0), (-1,-1), 3),
        ("RIGHTPADDING",  (0,0), (-1,-1), 3),
        ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#1e1e1e")),
    ]))

    cap = Paragraph(caption, styles["Caption"])
    return [t, cap]


def draw_cover(c, doc):
    w, h = A4
    c.setFillColor(BLUE_DARK)
    c.rect(0, h*0.38, w, h*0.62, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#0f2942"))
    c.rect(0, 0, w, h*0.38, fill=1, stroke=0)
    c.setFillColor(BLUE_MID)
    c.setFillAlpha(0.25)
    c.circle(w*0.85, h*0.78, 110, fill=1, stroke=0)
    c.circle(w*0.08, h*0.88, 75,  fill=1, stroke=0)
    c.setFillAlpha(1.0)


def draw_interior(c, doc):
    w, h = A4
    c.setFillColor(BLUE_DARK)
    c.rect(0, h - 1.2*cm, w, 1.2*cm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN, h - 0.78*cm, "TechMarket Orders — Evaluación Parcial 2 | AUY1104")
    c.setFont("Helvetica", 8)
    c.drawRightString(w - MARGIN, h - 0.78*cm, "Ciclo de Vida del Software II | 2025")
    c.setStrokeColor(BLUE_MID)
    c.setLineWidth(2)
    c.line(0, h - 1.2*cm, w, h - 1.2*cm)
    c.setFillColor(GRAY_BORDER)
    c.rect(0, 0, w, 0.9*cm, fill=1, stroke=0)
    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 7.5)
    c.drawString(MARGIN, 0.3*cm, "Blue-Green Deployment | Python FastAPI + GitHub Actions + AWS ECS/ALB")
    c.drawRightString(w - MARGIN, 0.3*cm, f"Página {doc.page}")


def build():
    styles = make_styles()
    story  = []

    # ── PORTADA ──────────────────────────────────────────────────
    story.append(Spacer(1, 6*cm))
    story.append(Paragraph("EVALUACIÓN PARCIAL N°2", styles["Cover_Title"]))
    story.append(Spacer(1, 0.3*cm))

    badge = Table([["AUY1104 – Ciclo de Vida del Software II"]], colWidths=[11*cm])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE_MID),
        ("TEXTCOLOR",  (0,0), (-1,-1), WHITE),
        ("FONTNAME",   (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 11),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("ROWHEIGHT",  (0,0), (-1,-1), 22),
    ]))
    story.append(badge)
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph("TechMarket Orders", styles["Cover_Title"]))
    story.append(Paragraph("Estrategia de Despliegue Blue-Green", styles["Cover_Sub"]))
    story.append(Spacer(1, 1.2*cm))
    for line in [
        "Microservicio: Orders | Python FastAPI + Docker",
        "Pipeline: GitHub Actions CI/CD | AWS ECS + ALB",
        "Estrategia: Blue-Green Deployment",
        "",
        "2025 | Semana 12",
    ]:
        story.append(Paragraph(line, styles["Cover_Info"]))

    story.append(Spacer(1, 0.8*cm))
    tech = Table(
        [["Python 3.11","FastAPI","Docker","GitHub Actions","AWS ECS"],
         ["Microservicio","REST API","Contenedor","CI/CD Pipeline","Cloud Deploy"]],
        colWidths=[2.8*cm]*5
    )
    tech.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#1d4ed8")),
        ("BACKGROUND",(0,1),(-1,1), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0,0),(-1,-1), WHITE),
        ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTNAME",  (0,1),(-1,1), "Helvetica"),
        ("FONTSIZE",  (0,0),(-1,-1), 8),
        ("ALIGN",     (0,0),(-1,-1), "CENTER"),
        ("ROWHEIGHT", (0,0),(-1,0), 16),
        ("ROWHEIGHT", (0,1),(-1,1), 13),
        ("GRID",      (0,0),(-1,-1), 0.5, colors.HexColor("#3b82f6")),
    ]))
    story.append(tech)
    story.append(PageBreak())

    # ── IE2.1 ────────────────────────────────────────────────────
    story.append(sec_header("IE2.1 – Descripción de Estrategias de Despliegue", styles))
    story.append(Spacer(1, 0.3*cm))

    strats = [
        ("All-in-Once (Big Bang)", RED_LIGHT, RED_DARK,
         "Reemplaza la versión completa en un único evento. Provoca downtime inevitable. "
         "Descartada para servicios críticos con SLA. El 100% de usuarios se ve afectado ante cualquier fallo."),
        ("Rolling Update", YELLOW_LIGHT, colors.HexColor("#d97706"),
         "Actualiza instancias de forma gradual manteniendo al menos una activa. "
         "Sin downtime, pero coexisten dos versiones temporalmente, lo que puede generar inconsistencias en APIs."),
        ("Canary Deployment", colors.HexColor("#fef3c7"), colors.HexColor("#d97706"),
         "Libera la nueva versión a un 5-10% del tráfico real para validación. Rollback rápido. "
         "Requiere enrutamiento por pesos y observabilidad avanzada. Agrega complejidad operacional."),
        ("Blue-Green Deployment ★ SELECCIONADA", GREEN_LIGHT, GREEN_DARK,
         "Dos entornos idénticos: Blue (producción) y Green (nuevo). Switch atómico vía ALB. "
         "Zero-downtime, rollback instantáneo sin redeployment (<30s). Soporte nativo en AWS ECS + ALB."),
    ]
    for name, bg, border, desc in strats:
        row = Table([[Paragraph(f"<b>{name}</b>", styles["Body"]),
                      Paragraph(desc, styles["Body"])]],
                    colWidths=[5*cm, CONTENT_W-5*cm])
        row.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), bg),
            ("BOX",        (0,0), (-1,-1), 1.5, border),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ]))
        story.append(row)
        story.append(Spacer(1, 0.2*cm))
    story.append(PageBreak())

    # ── IE2.2 ────────────────────────────────────────────────────
    story.append(sec_header("IE2.2 – Análisis Comparativo de Estrategias", styles))
    story.append(Spacer(1, 0.3*cm))
    comp = [
        ["Variable", "All-in-Once", "Rolling Update", "Canary", "Blue-Green"],
        ["Downtime",         "❌ Inevitable","✅ Nulo","✅ Nulo","✅✅ Nulo"],
        ["Rollback",         "❌ Manual/Lento","🟡 Auto/Lento","✅ Rápido","✅✅ <30s sin redeployment"],
        ["Costo infra",      "✅ Mínimo","🟡 Bajo","🟡 Medio","⚠ Alto (x2)"],
        ["Velocidad switch", "✅ Rápida","🟡 Media","❌ Gradual","✅✅ Instantánea"],
        ["Riesgo fallo",     "❌ Total 100%","🟡 Parcial","✅ <10%","✅✅ Nulo"],
        ["Complejidad",      "✅ Baja","🟡 Media","❌ Alta","🟡 Media"],
        ["SLA 99.9%",        "❌ No","🟡 Parcial","✅ Sí","✅✅ Óptimo"],
        ["Integración AWS",  "✅ Simple","✅ ECS/EKS","🟡 CodeDeploy","✅✅ ALB+ECS nativo"],
    ]
    cw = [4*cm, 2.8*cm, 2.8*cm, 2.8*cm, 3.3*cm]
    ct = Table(comp, colWidths=cw)
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), BLUE_DARK),
        ("TEXTCOLOR",  (0,0),(-1,0), WHITE),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 8.5),
        ("ALIGN",      (1,0),(-1,-1), "CENTER"),
        ("FONTNAME",   (0,1),(0,-1), "Helvetica-Bold"),
        ("BACKGROUND", (4,1),(4,-1), GREEN_LIGHT),
        ("TEXTCOLOR",  (4,1),(4,-1), GREEN_DARK),
        ("FONTNAME",   (4,1),(4,-1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0,1),(3,-1), [WHITE, GRAY_BG]),
        ("GRID",       (0,0),(-1,-1), 0.5, GRAY_BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("BOX",        (0,0),(-1,-1), 1.5, BLUE_DARK),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "<b>Conclusión:</b> Blue-Green es la única estrategia que combina zero-downtime + rollback instantáneo "
        "+ sin coexistencia de versiones en producción, siendo la más adecuada para el servicio Orders.",
        styles["Body"]
    ))
    story.append(PageBreak())

    # ── IE2.3 ────────────────────────────────────────────────────
    story.append(sec_header("IE2.3 – Selección Justificada: Blue-Green Deployment", styles))
    story.append(Spacer(1, 0.3*cm))
    justifs = [
        ("Requerimientos técnicos",
         "Orders es un microservicio contenedorizado desplegable en AWS ECS. El switch ALB es atómico (API nativa). "
         "Al exponer una REST API consumida por otros servicios, eliminar la coexistencia de versiones es crítico."),
        ("Restricciones legales y operacionales",
         "La continuidad del servicio de pedidos es obligación contractual (SLA). Blue-Green garantiza 0 segundos de "
         "downtime por despliegue. La trazabilidad completa del pipeline facilita auditorías de cumplimiento."),
        ("Condiciones de negocio",
         "SLA ≥ 99.9%. El rollback en <30s sin redeployment protege el SLA ante fallos post-switch. El costo de duplicar "
         "compute durante ~15-30 min de deploy es marginal vs. el costo de un incidente de disponibilidad."),
        ("Superioridad sobre alternativas",
         "All-in-Once: descartado por downtime. Rolling: descartado por coexistencia de versiones en API de pagos. "
         "Canary: válido pero agrega complejidad sin beneficio diferencial. Blue-Green: único que combina todos los requisitos."),
    ]
    for title, text in justifs:
        story.append(Paragraph(f"<b>{title}</b>", styles["Sub_Title"]))
        story.append(Paragraph(text, styles["Body"]))
    story.append(PageBreak())

    # ── IE2.4 ────────────────────────────────────────────────────
    story.append(sec_header("IE2.4 – Implementación Práctica Blue-Green", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Componentes implementados:</b>", styles["Sub_Title"]))
    impl = [
        ["Componente","Archivo","Descripción"],
        ["Microservicio","src/main.py","FastAPI: /health /info /orders CRUD completo"],
        ["Tests","tests/test_orders.py","8 tests unitarios/integración — 100% PASSED"],
        ["Dockerfile","Dockerfile","Python 3.11-slim + HEALTHCHECK"],
        ["Stack B/G","docker-compose.yml","Blue + Green + Nginx LB"],
        ["CI","ci.yml","Lint + Test + Docker Build + Trivy scan"],
        ["CD","blue-green-deploy.yml","8 jobs: Prepare→Deploy→Health→Switch→Rollback"],
        ["Deploy","deploy-blue-green.sh","6 pasos documentados con smoke tests"],
        ["Rollback","rollback.sh","Rollback instantáneo <30s sin redeployment"],
    ]
    it = Table(impl, colWidths=[3.5*cm, 5*cm, CONTENT_W-8.5*cm])
    it.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), BLUE_MID),
        ("TEXTCOLOR",  (0,0),(-1,0), WHITE),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTNAME",   (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,0),(-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,GRAY_BG]),
        ("GRID",       (0,0),(-1,-1), 0.5, GRAY_BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("BOX",        (0,0),(-1,-1), 1, BLUE_DARK),
    ]))
    story.append(it)
    story.append(PageBreak())

    # ── SCREENSHOTS ──────────────────────────────────────────────
    evidence = [
        ("screenshot_01_health_check.png",
         "Evidencia 1 – Health Check: ambos entornos activos simultáneamente",
         "Figura 1: Blue (v1.0.0) en puerto 8001 y Green (v2.0.0) en puerto 8002 responden 'healthy' de forma simultánea. "
         "Esta es la condición previa al switch de tráfico en el pipeline Blue-Green."),
        ("screenshot_02_create_orders.png",
         "Evidencia 2 – POST /orders: creación de pedidos en ambos entornos",
         "Figura 2: El campo 'environment' en la respuesta JSON confirma qué entorno procesó cada pedido. "
         "Blue sirve v1.0.0 (producción actual) y Green sirve v2.0.0 (nueva versión a validar)."),
        ("screenshot_03_smoke_tests.png",
         "Evidencia 3 – Smoke Tests pre-switch: 5/5 PASADOS",
         "Figura 3: Cinco pruebas funcionales ejecutadas sobre el entorno Green antes del switch. "
         "Si cualquiera falla, el pipeline detiene el despliegue y ejecuta rollback automático."),
        ("screenshot_04_switch_trafico.png",
         "Evidencia 4 – Switch de tráfico Blue→Green (simula aws elbv2 modify-listener)",
         "Figura 4: Switch atómico del Load Balancer de Blue hacia Green. El comando equivalente en AWS es "
         "'aws elbv2 modify-listener' que redirige el target group. El proceso completo toma ~4 segundos."),
        ("screenshot_05_rollback.png",
         "Evidencia 5 – Rollback automático: <30 segundos sin redeployment",
         "Figura 5: Al detectar error_rate > threshold, el pipeline revierte el ALB a Blue instantáneamente. "
         "Blue permanece en standby exactamente para este propósito. Tiempo total: <30 segundos."),
        ("screenshot_06_pytest.png",
         "Evidencia 6 – Suite de tests pytest: 8/8 PASADOS (100%)",
         "Figura 6: Ejecución completa de la suite de tests unitarios e integración. "
         "8/8 tests pasados en 1.40 segundos, cubriendo todos los endpoints del microservicio Orders."),
        ("screenshot_07_github_actions.png",
         "Evidencia 7 – GitHub Actions: Pipeline CI/CD Blue-Green completo",
         "Figura 7: Pipeline de 8 jobs ejecutado exitosamente. El job 'rollback' queda en skip "
         "porque todos los pasos anteriores pasaron. Total: 4m 31s de build a producción."),
    ]

    for fname, sec_title, caption in evidence:
        story.append(sec_header(sec_title, styles, GREEN_DARK))
        story.append(Spacer(1, 0.3*cm))
        result = screenshot(fname, caption, styles)
        if isinstance(result, list):
            story.extend(result)
        else:
            story.append(result)
        story.append(PageBreak())

    # ── REFERENCIAS ───────────────────────────────────────────────
    story.append(sec_header("Referencias y Declaración de Uso de IA", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Referencias (APA 7)</b>", styles["Sub_Title"]))
    refs = [
        "Amazon Web Services. (2024). <i>Blue/green deployments with AWS CodeDeploy</i>. https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-steps-ecs.html",
        "Burns, B., Grant, B., Oppenheimer, D., Brewer, E., &amp; Wilkes, J. (2016). Borg, Omega, and Kubernetes. <i>Queue, 14</i>(1), 70–93. https://doi.org/10.1145/2898442.2898444",
        "Fowler, M. (2010). <i>BlueGreenDeployment</i>. https://martinfowler.com/bliki/BlueGreenDeployment.html",
        "Kim, G., Humble, J., Debois, P., &amp; Willis, J. (2016). <i>The DevOps handbook</i>. IT Revolution Press.",
        "Sato, D. (2014). <i>CanaryRelease</i>. https://martinfowler.com/bliki/CanaryRelease.html",
    ]
    for i, r in enumerate(refs, 1):
        story.append(Paragraph(f"{i}. {r}", styles["Body"]))
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GRAY_BORDER))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Declaración de Uso de Inteligencia Artificial</b>", styles["Sub_Title"]))
    story.append(Paragraph(
        "Este proyecto fue desarrollado con asistencia de herramientas de inteligencia artificial (Claude, Anthropic) "
        "para la generación de código base, documentación y estructura del pipeline. Todo el contenido fue revisado, "
        "contextualizado y adaptado por el equipo al caso de negocio de TechMarket Orders, asegurando comprensión y "
        "dominio técnico conforme a los indicadores IE2.1 a IE2.4.",
        styles["Body"]
    ))

    now = datetime.datetime.now().strftime("%d de mayo de 2026")
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Generado el {now} | AUY1104 – Ciclo de Vida del Software II | 2025", styles["Footer"]))

    # ── BUILD ─────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.5*cm, bottomMargin=1.2*cm,
        title="Evaluación Parcial 2 - TechMarket Orders",
        author="AUY1104", subject="Blue-Green Deployment",
    )
    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_interior)
    print(f"PDF generado: {OUTPUT}")


if __name__ == "__main__":
    build()
