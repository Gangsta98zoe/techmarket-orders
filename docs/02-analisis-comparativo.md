# IE2.2 – Análisis Comparativo de Estrategias de Despliegue

## Variables de análisis

Se evalúan las cuatro estrategias considerando las variables críticas para un servicio de e-commerce como **TechMarket Orders**.

---

## 1. Uptime / Disponibilidad del servicio

### All-in-Once
Provoca **downtime inevitable** durante el reemplazo. Toda la flota se detiene simultáneamente. En un servicio de pedidos, esto implica pérdida de transacciones durante el mantenimiento. En escenarios de alta carga (Black Friday, campañas), el riesgo es crítico.

### Rolling Update
**Sin downtime**, pero durante la actualización coexisten dos versiones. Si una instancia falla a mitad del proceso, el servicio puede quedar parcialmente degradado. El tiempo de transición depende del número de instancias y del `maxUnavailable` configurado.

### Canary
**Sin downtime**. Solo un porcentaje pequeño de usuarios puede experimentar errores si la versión canario tiene fallos. El 90–95% del tráfico permanece estable en la versión anterior. Esto garantiza alta disponibilidad incluso ante errores en la nueva versión.

### Blue-Green
**Sin downtime**. El switch es atómico: en el momento del cutover, el 100% del tráfico migra instantáneamente al nuevo entorno ya validado. No existe período de coexistencia en producción. El uptime es prácticamente del 100%.

---

## 2. Impacto y facilidad de rollback

### All-in-Once
Rollback **manual y lento**. Requiere redeploy completo de la versión anterior. En entornos sin automatización, puede tardar horas. El impacto en el usuario es total durante ese período.

### Rolling Update
Rollback **automático pero progresivo**. Kubernetes puede revertir pods gradualmente, pero al igual que el despliegue, el proceso toma tiempo. Durante el rollback, ambas versiones coexisten nuevamente.

### Canary
Rollback **rápido** (segundos). Reducir el tráfico canario a 0% efectivamente elimina la versión problemática. Sin embargo, los usuarios que ya fueron dirigidos al canario pueden haber experimentado errores.

### Blue-Green
Rollback **instantáneo** (< 30 segundos). El entorno anterior (Blue) permanece intacto y en standby. Basta con reapuntar el Load Balancer para revertir. No requiere redeployment. Este es el mecanismo de rollback más rápido y confiable.

---

## 3. Costo operativo e infraestructura

### All-in-Once
**Costo mínimo**. No requiere infraestructura adicional. Solo un entorno. Sin embargo, el costo oculto son las pérdidas por downtime y la remediación de incidentes.

### Rolling Update
**Costo bajo-medio**. Requiere capacidad adicional temporal (`maxSurge`) para nuevas instancias durante la actualización. En ECS/Kubernetes el orquestador gestiona esto automáticamente.

### Canary
**Costo medio**. Requiere infraestructura para enrutar tráfico diferenciado (pesos en ALB, Istio, Argo Rollouts). La complejidad operacional incrementa el costo de mantenimiento del pipeline.

### Blue-Green
**Costo alto**. Requiere **duplicar** la infraestructura: dos entornos idénticos ejecutándose simultáneamente. En AWS ECS, esto implica dos task definitions, dos target groups, y potencialmente el doble de compute. Sin embargo, el entorno standby puede escalar a 0 entre despliegues para reducir costos.

---

## 4. Velocidad de despliegue y propagación del cambio

### All-in-Once
**Rápida** en tiempo de despliegue (todo a la vez), pero lenta en recuperación ante fallos.

### Rolling Update
**Media**. El tiempo de propagación es lineal al número de instancias. Con 10 pods y `maxUnavailable=2`, el proceso toma varios ciclos de healthcheck.

### Canary
**Lenta por diseño**. La propagación es deliberadamente gradual (5% → 25% → 50% → 100%), lo que puede tardar horas o días según la estrategia de incremento definida.

### Blue-Green
**Muy rápida en el switch**. La preparación toma tiempo (build + deploy en Green), pero el switch de tráfico es instantáneo. Una vez validado Green, el cambio al 100% del tráfico es inmediato.

---

## Tabla Comparativa: Ventajas y Desventajas

| Variable               | All-in-Once        | Rolling Update        | Canary               | Blue-Green              |
|------------------------|--------------------|-----------------------|----------------------|-------------------------|
| **Downtime**           | ❌ Siempre         | ✅ Nulo               | ✅ Nulo              | ✅ Nulo                 |
| **Rollback**           | ❌ Lento/Manual    | 🟡 Automático/Lento   | ✅ Rápido            | ✅✅ Instantáneo        |
| **Costo infra**        | ✅ Mínimo          | 🟡 Bajo-Medio         | 🟡 Medio             | ❌ Alto (x2 infra)      |
| **Velocidad switch**   | ✅ Rápida          | 🟡 Media              | ❌ Lenta (gradual)   | ✅ Instantánea          |
| **Riesgo ante fallo**  | ❌ Total (100%)    | 🟡 Parcial            | ✅ Mínimo (< 10%)    | ✅ Nulo (validación previa) |
| **Complejidad**        | ✅ Baja            | 🟡 Media              | ❌ Alta              | 🟡 Media                |
| **Coexistencia versiones** | ✅ No          | ❌ Temporal           | ❌ Permanente        | ✅ No (switch atómico)  |
| **Apto para SLA crítico** | ❌ No           | 🟡 Parcialmente       | ✅ Sí                | ✅✅ Sí (óptimo)        |
| **Rollback con datos** | ❌ Complejo        | 🟡 Complejo           | 🟡 Complejo          | 🟡 Complejo (mismo para todos) |
| **Integración AWS**    | ✅ Simple          | ✅ ECS/EKS nativo     | 🟡 CodeDeploy Canary | ✅ CodeDeploy/ALB nativo |

### Escenarios reales asociados

- **Picos de tráfico** (Black Friday): Blue-Green y Canary son las únicas que garantizan zero-downtime. All-in-Once es inviable.
- **Despliegue crítico** (cambio de esquema de pagos): Blue-Green permite validar la nueva versión completamente antes del switch.
- **Alta carga con rollback rápido**: Blue-Green es superior; el rollback toma segundos sin re-despliegue.
- **Frecuencia de cambios** (múltiples releases/día): Rolling Update es eficiente, pero Canary y Blue-Green son más seguras.
