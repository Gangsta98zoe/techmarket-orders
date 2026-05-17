#!/bin/bash
# =============================================================================
# rollback.sh
# Rollback instantáneo Blue-Green - revierte el tráfico al entorno anterior
# =============================================================================

set -e

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
echo "  TechMarket Orders - ROLLBACK Blue-Green"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"
echo ""

# Detectar entorno activo
ACTIVE_ENV=$(curl -s http://localhost/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('environment','blue'))" 2>/dev/null || echo "blue")

if [ "$ACTIVE_ENV" = "blue" ]; then
    ROLLBACK_TO="blue"
    log_warn "El tráfico ya está en BLUE. Verificando estado..."
else
    ROLLBACK_TO="blue"
    log_info "Tráfico actual: GREEN → Revertiendo a: BLUE"
fi

# Verificar que el entorno de rollback está healthy
ROLLBACK_PORT=$([ "$ROLLBACK_TO" = "blue" ] && echo "8001" || echo "8002")
if ! curl -sf "http://localhost:${ROLLBACK_PORT}/health" > /dev/null 2>&1; then
    log_error "El entorno de rollback (${ROLLBACK_TO^^}) no está disponible!"
    exit 1
fi

log_info "Redirigiendo tráfico a ${ROLLBACK_TO^^}..."

cat > ./nginx/nginx.conf << NGINX_EOF
events { worker_connections 1024; }

http {
    upstream active_backend {
        server orders-${ROLLBACK_TO}:8000;
    }

    server {
        listen 80;
        location / {
            proxy_pass http://active_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Active-Env "${ROLLBACK_TO}";
        }
        location /nginx-health {
            return 200 '{"status":"ok","active_env":"${ROLLBACK_TO}","rollback":true}';
            add_header Content-Type application/json;
        }
    }
}
NGINX_EOF

docker exec orders-lb nginx -s reload 2>/dev/null || true
sleep 2

ROLLBACK_ENV=$(curl -s http://localhost/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('environment','?'))" 2>/dev/null || echo "?")
ROLLBACK_VER=$(curl -s http://localhost/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || echo "?")

echo ""
echo "================================================================"
echo "  ROLLBACK COMPLETADO"
echo "  Entorno activo:  ${ROLLBACK_ENV^^}"
echo "  Versión live:    ${ROLLBACK_VER}"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"
echo ""
