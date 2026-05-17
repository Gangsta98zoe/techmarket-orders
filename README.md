# TechMarket Orders - Microservicio de Pedidos

**Asignatura:** AUY1104 – Ciclo de vida del Software II  
**Evaluación:** Parcial N°2  
**Caso:** Estrategia de despliegue para el servicio "TechMarket Orders"

---

## Descripción del proyecto

Microservicio REST desarrollado en **Python + FastAPI** para la gestión de pedidos de TechMarket. Implementa una estrategia de despliegue **Blue-Green** mediante un pipeline **GitHub Actions** con integración a servicios **AWS** (ECS, ALB, CodeDeploy).

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions CI/CD                        │
│  Push → Build → Test → Deploy Green → Health Check → Switch LB │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                     ┌──────▼──────┐
                     │  AWS ALB    │  ← Switch atómico Blue/Green
                     └──────┬──────┘
              ┌─────────────┴─────────────┐
       ┌──────▼──────┐           ┌────────▼──────┐
       │  BLUE (prod)│           │ GREEN (nuevo)  │
       │  v1.0.0     │           │  v2.0.0        │
       │  ECS Task   │           │  ECS Task      │
       └─────────────┘           └───────────────┘
```

---

## Estructura del repositorio

```
techmarket-orders/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Build, lint, tests, scan
│       └── blue-green-deploy.yml     # Pipeline CD Blue-Green completo
├── src/
│   ├── main.py                       # FastAPI - endpoints Orders
│   └── requirements.txt
├── tests/
│   └── test_orders.py                # Tests unitarios e integración
├── scripts/
│   ├── deploy-blue-green.sh          # Script de despliegue local
│   └── rollback.sh                   # Rollback instantáneo
├── nginx/
│   └── nginx.conf                    # Load balancer (simula AWS ALB)
├── docs/
│   ├── 01-estrategias-despliegue.md  # IE2.1 - Descripción estrategias
│   ├── 02-analisis-comparativo.md    # IE2.2 - Análisis comparativo
│   └── 03-seleccion-justificada.md   # IE2.3 - Justificación Blue-Green
├── Dockerfile
└── docker-compose.yml                # Stack Blue-Green local completo
```

---

## Inicio rápido

### Prerequisitos
- Docker Desktop instalado y corriendo
- Python 3.11+

### 1. Clonar y ejecutar el stack Blue-Green

```bash
git clone https://github.com/<usuario>/techmarket-orders.git
cd techmarket-orders

# Iniciar ambos entornos (Blue v1.0.0 y Green v2.0.0) + Load Balancer
docker compose up --build -d

# Verificar que ambos entornos están sanos
docker compose ps
```

### 2. Verificar endpoints

```bash
# Producción (Blue - puerto 80 vía LB)
curl http://localhost/health
# → {"status":"healthy","environment":"blue","version":"1.0.0",...}

# Entorno Blue directo
curl http://localhost:8001/health

# Entorno Green directo
curl http://localhost:8002/health
```

### 3. Crear un pedido

```bash
curl -X POST http://localhost/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust-001",
    "items": [
      {"product_id": "laptop-pro", "quantity": 1, "unit_price": 999.99},
      {"product_id": "mouse-usb", "quantity": 2, "unit_price": 29.99}
    ],
    "shipping_address": "Av. Providencia 1234, Santiago"
  }'
```

### 4. Ejecutar despliegue Blue-Green

```bash
# Desplegar nueva versión (simula AWS CodeDeploy)
./scripts/deploy-blue-green.sh 2.0.0

# En caso de fallo: rollback instantáneo
./scripts/rollback.sh
```

### 5. Ejecutar tests

```bash
pip install -r src/requirements.txt
pytest tests/ -v
```

---

## Pipeline CI/CD

### Flujo completo

```
git push main
     │
     ▼
┌─────────────┐    ┌──────────────┐    ┌────────────────────┐
│  CI - Build │───▶│   CI - Test  │───▶│   CI - Docker Build│
│  Lint/Flake8│    │  pytest + cov│    │  + Trivy scan      │
└─────────────┘    └──────────────┘    └─────────┬──────────┘
                                                  │
                                                  ▼
                                       ┌──────────────────────┐
                                       │  CD - Preparación    │
                                       │  Detectar env activo │
                                       └──────────┬───────────┘
                                                  │
                                                  ▼
                                       ┌──────────────────────┐
                                       │  Deploy en inactivo  │
                                       │  (Green/Blue ECS)    │
                                       └──────────┬───────────┘
                                                  │
                                                  ▼
                                       ┌──────────────────────┐
                                       │  Health Check x10    │
                                       │  + Smoke Tests       │
                                       └──────────┬───────────┘
                                                  │
                              ┌───────────────────┴──────────────┐
                              │ ¿Healthy?                        │
                         YES  ▼                         NO       ▼
                    ┌──────────────────┐        ┌───────────────────────┐
                    │  Switch LB ALB   │        │  Rollback Automático  │
                    │  Blue → Green    │        │  + Crear Issue GitHub │
                    └──────────────────┘        └───────────────────────┘
```

### Jobs del pipeline

| Job | Descripción | Herramienta |
|-----|-------------|-------------|
| `lint` | Verificación de calidad con Black, isort, flake8 | GitHub Actions |
| `test` | Tests unitarios con cobertura | pytest + codecov |
| `build` | Build imagen Docker + escaneo Trivy | docker/build-push-action@v5 |
| `prepare` | Detecta entorno activo/inactivo | Script bash |
| `deploy-inactive` | Despliega en entorno standby | AWS ECS / Docker |
| `health-check` | Valida salud + smoke tests (10 reintentos) | curl + pytest |
| `traffic-switch` | Redirige tráfico ALB | AWS CLI / nginx |
| `rollback` | Revierte automáticamente si falla | AWS CLI / nginx |

---

## Documentación académica

- [IE2.1 – Descripción de estrategias](docs/01-estrategias-despliegue.md)
- [IE2.2 – Análisis comparativo](docs/02-analisis-comparativo.md)
- [IE2.3 – Selección justificada (Blue-Green)](docs/03-seleccion-justificada.md)

---

## Contribución a continuidad operativa y agilidad

### Continuidad operativa
- **Zero downtime**: El switch ALB es atómico; ningún request queda sin respuesta.
- **Rollback < 30s**: El entorno anterior permanece en standby. Revertir es reapuntar el LB.
- **Aislamiento de versiones**: No existe coexistencia de versiones en producción. Cada entorno sirve una versión exacta.
- **Resiliencia**: Health checks automatizados impiden que una versión defectuosa llegue a producción.

### Agilidad del equipo
- **Ciclos cortos**: Un `git push` desencadena todo el pipeline sin intervención manual.
- **Automatización completa**: Build → Test → Deploy → Validate → Switch en un flujo sin pasos manuales.
- **Menor riesgo por release**: Cada cambio puede revertirse instantáneamente, lo que incentiva releases frecuentes.
- **Feedback rápido**: Si el health check falla, el equipo recibe un issue automático con contexto del fallo.

---

## Declaración de uso de IA

Este proyecto fue desarrollado con asistencia de herramientas de inteligencia artificial (Claude, Anthropic) para la generación de código base, documentación y estructura del pipeline. Todo el contenido fue revisado, contextualizado y adaptado por el equipo al caso de negocio específico de TechMarket.

---

## Referencias (formato APA 7)

Amazon Web Services. (2024). *Blue/green deployments with AWS CodeDeploy*. AWS Documentation. https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-steps-ecs.html

Burns, B., Grant, B., Oppenheimer, D., Brewer, E., & Wilkes, J. (2016). Borg, Omega, and Kubernetes. *Queue, 14*(1), 70–93. https://doi.org/10.1145/2898442.2898444

Fowler, M. (2010, March 1). *BlueGreenDeployment*. Martin Fowler's Bliki. https://martinfowler.com/bliki/BlueGreenDeployment.html

Kim, G., Humble, J., Debois, P., & Willis, J. (2016). *The DevOps handbook: How to create world-class agility, reliability, and security in technology organizations*. IT Revolution Press.

Sato, D. (2014, June 25). *CanaryRelease*. Martin Fowler's Bliki. https://martinfowler.com/bliki/CanaryRelease.html
