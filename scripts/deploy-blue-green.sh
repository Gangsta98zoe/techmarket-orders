#!/bin/bash
# =============================================================================
# deploy-blue-green.sh
# Script de despliegue Blue-Green para TechMarket Orders
# Simula el comportamiento de AWS CodeDeploy + ALB
# =============================================================================

set -e

NEW_VERSION="${1:-2.0.0}"
HEALTH_RETRIES=12
HEALTH_INTERVAL=5

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "================================================================"
echo "  TechMarket Orders - Blue-Green Deployment"
echo "  Nueva versión: ${NEW_VERSION}"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"
echo ""

# ── PASO 1: Determinar entorno activo ──────────────────────────────
log_info "PASO 1/6: Detectando entorno activo en producción..."
ACTIVE_ENV=$(curl -s http://localhost/health 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('environment','blue'))" 2>/dev/null || echo "blue")

if [ "$ACTIVE_ENV" = "blue" ]; then
    DEPLOY_ENV="green"
    PROD_ENV="blue"
    DEPLOY_PORT="8002"
    PROD_PORT="8001"
else
    DEPLOY_ENV="blue"
    PROD_ENV="green"
    DEPLOY_PORT="8001"
    PROD_PORT="8002"
fi

log_success "Entorno activo (producción): ${PROD_ENV^^} (puerto ${PROD_PORT})"
log_info    "Desplegando en entorno inactivo: ${DEPLOY_ENV^^} (puerto ${DEPLOY_PORT})"

# ── PASO 2: Build de la nueva imagen ──────────────────────────────
log_info "PASO 2/6: Construyendo imagen Docker versión ${NEW_VERSION}..."
docker build \
    --build-arg APP_VERSION="${NEW_VERSION}" \
    --build-arg ENVIRONMENT="${DEPLOY_ENV}" \
    --tag "techmarket-orders:${NEW_VERSION}" \
    --tag "techmarket-orders:${DEPLOY_ENV}" \
    . 2>&1 | tail -5
log_success "Imagen construida: techmarket-orders:${NEW_VERSION}"

# ── PASO 3: Desplegar en entorno inactivo ─────────────────────────
log_info "PASO 3/6: Iniciando contenedor ${DEPLOY_ENV^^}..."
docker stop "orders-${DEPLOY_ENV}" 2>/dev/null || true
docker rm "orders-${DEPLOY_ENV}" 2>/dev/null || true

docker run -d \
    --name "orders-${DEPLOY_ENV}" \
    --network techmarket-orders-network \
    --env APP_VERSION="${NEW_VERSION}" \
    --env ENVIRONMENT="${DEPLOY_ENV}" \
    --publish "${DEPLOY_PORT}:8000" \
    --label "deployment.version=${NEW_VERSION}" \
    --label "deployment.slot=${DEPLOY_ENV}" \
    "techmarket-orders:${NEW_VERSION}"

log_success "Contenedor ${DEPLOY_ENV^^} iniciado"

# ── PASO 4: Validación de salud ───────────────────────────────────
log_info "PASO 4/6: Validando health del entorno ${DEPLOY_ENV^^}..."
READY=false
for i in $(seq 1 $HEALTH_RETRIES); do
    if curl -sf "http://localhost:${DEPLOY_PORT}/health" > /dev/null 2>&1; then
        READY=true
        break
    fi
    log_warn "  Intento ${i}/${HEALTH_RETRIES}: esperando ${HEALTH_INTERVAL}s..."
    sleep $HEALTH_INTERVAL
done

if [ "$READY" = false ]; then
    log_error "Health check fallido. Iniciando rollback automático..."
    bash "$(dirname "$0")/rollback.sh"
    exit 1
fi

HEALTH_DATA=$(curl -s "http://localhost:${DEPLOY_PORT}/health")
log_success "Health check OK: ${HEALTH_DATA}"

# ── PASO 5: Ejecución de pruebas smoke ────────────────────────────
log_info "PASO 5/6: Ejecutando smoke tests contra ${DEPLOY_ENV^^}..."

# Test 1: Crear una orden de prueba
SMOKE_ORDER=$(curl -s -X POST "http://localhost:${DEPLOY_PORT}/orders" \
    -H "Content-Type: application/json" \
    -d '{
        "customer_id": "smoke-test-001",
        "items": [{"product_id": "test-prod", "quantity": 1, "unit_price": 1.00}],
        "shipping_address": "Smoke Test Address"
    }')

ORDER_ID=$(echo "$SMOKE_ORDER" | python3 -c "import sys,json; print(json.load(sys.stdin)['order_id'])" 2>/dev/null)

if [ -z "$ORDER_ID" ]; then
    log_error "Smoke test FALLIDO: no se pudo crear orden"
    bash "$(dirname "$0")/rollback.sh"
    exit 1
fi

# Test 2: Recuperar la orden creada
curl -sf "http://localhost:${DEPLOY_PORT}/orders/${ORDER_ID}" > /dev/null
log_success "Smoke test PASADO: orden ${ORDER_ID} creada y recuperada exitosamente"

# ── PASO 6: Switch de tráfico (simula ALB target group swap) ──────
log_info "PASO 6/6: Transfiriendo tráfico de ${PROD_ENV^^} → ${DEPLOY_ENV^^}..."

# En AWS real: aws elbv2 modify-listener --listener-arn <ARN> --default-actions ...
# Aquí simulamos actualizando nginx.conf
cat > ./nginx/nginx.conf << NGINX_EOF
events { worker_connections 1024; }

http {
    upstream active_backend {
        server orders-${DEPLOY_ENV}:8000;
    }
    upstream standby_backend {
        server orders-${PROD_ENV}:8000;
    }

    server {
        listen 80;
        location / {
            proxy_pass http://active_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Active-Env "${DEPLOY_ENV}";
        }
        location /standby/ {
            proxy_pass http://standby_backend/;
            proxy_set_header X-Active-Env "${PROD_ENV}";
        }
        location /nginx-health {
            return 200 '{"status":"ok","active_env":"${DEPLOY_ENV}","version":"${NEW_VERSION}"}';
            add_header Content-Type application/json;
        }
    }
}
NGINX_EOF

docker exec orders-lb nginx -s reload 2>/dev/null || true
sleep 2

# Verificación final del tráfico
FINAL_ENV=$(curl -s http://localhost/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('environment','?'))" 2>/dev/null || echo "?")
FINAL_VER=$(curl -s http://localhost/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || echo "?")

echo ""
echo "================================================================"
echo "  DESPLIEGUE COMPLETADO EXITOSAMENTE"
echo "  Entorno activo:  ${DEPLOY_ENV^^}"
echo "  Versión live:    ${FINAL_VER}"
echo "  Entorno standby: ${PROD_ENV^^} (disponible para rollback)"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"
echo ""
log_info "Para rollback inmediato ejecutar: ./scripts/rollback.sh"
