# IE2.3 – Selección Justificada de Estrategia: Blue-Green

## Estrategia seleccionada: **Blue-Green Deployment**

---

## Análisis de requerimientos del microservicio Orders

### Requerimientos técnicos
- **Microarquitectura**: Orders es un microservicio independiente, contenedorizado con Docker, lo que facilita mantener dos entornos idénticos (Blue y Green) sin dependencias cruzadas.
- **Entorno cloud (AWS)**: AWS soporta nativamente Blue-Green mediante ALB (Application Load Balancer) + ECS o CodeDeploy. El switch de target groups es una operación atómica con API nativa.
- **API expuesta**: Al exponer una API REST consumida por otros servicios, los cambios de versión deben ser transparentes. Blue-Green garantiza que no exista coexistencia de versiones en producción.
- **Tolerancia a fallas**: Si la nueva versión falla smoke tests, el entorno Blue permanece inalterado. No hay degradación parcial.

### Restricciones legales y operacionales
- **Continuidad del servicio**: Procesar pedidos en línea es una función de negocio crítica. Cualquier downtime implica pérdida directa de ingresos y potenciales sanciones por incumplimiento de SLA. Blue-Green elimina el downtime en los despliegues.
- **Trazabilidad**: Cada despliegue es un evento documentado: qué versión, cuándo, quién. El pipeline registra cada paso con logs y artefactos.
- **Respaldo de datos**: Al no migrar datos durante el switch (solo se redirige el tráfico), el riesgo de corrupción o pérdida de datos es mínimo comparado con All-in-Once.

### Condiciones de negocio
- **SLA**: TechMarket requiere disponibilidad ≥ 99.9% (menos de 8.7 horas de downtime al año). Con Blue-Green, los despliegues no contribuyen al downtime. Con All-in-Once o Rolling Update, cada despliegue consume minutos del SLA.
- **Tráfico esperado**: Servicio de pedidos con picos en horarios comerciales. El switch instantáneo de Blue-Green evita que usuarios activos experimenten errores mid-session.
- **Ventanas de mantenimiento**: Blue-Green elimina la necesidad de ventanas de mantenimiento programadas para despliegues.
- **Costos**: El costo de duplicar infraestructura (~2x compute durante el despliegue, escalable a costo mínimo en standby) es significativamente menor que el costo de un incidente de disponibilidad en producción.

---

## Por qué Blue-Green es superior a las alternativas en este caso

| Criterio | All-in-Once | Rolling | Canary | **Blue-Green** |
|----------|:-----------:|:-------:|:------:|:--------------:|
| SLA 99.9% | ❌ | 🟡 | ✅ | ✅✅ |
| Rollback < 1 min | ❌ | ❌ | ✅ | ✅✅ |
| Sin versiones mixtas en prod | ✅ | ❌ | ❌ | ✅✅ |
| Apto para AWS ECS/ALB | ✅ | ✅ | 🟡 | ✅✅ |
| Riesgo en despliegue de pagos | ❌ Alto | 🟡 Medio | 🟡 Bajo | ✅ Mínimo |

**All-in-Once** queda descartado por el downtime inevitable, incompatible con el SLA.  
**Rolling Update** queda descartado porque durante la actualización coexisten dos versiones del API de orders, lo que puede generar inconsistencias en el estado de los pedidos.  
**Canary** es válido pero agrega complejidad significativa (enrutamiento por peso, observabilidad avanzada) sin un beneficio diferencial para este caso, donde el entorno puede ser completamente validado antes del go-live.  
**Blue-Green** ofrece el mejor equilibrio: validación completa previa al switch, rollback instantáneo, y soporte nativo en AWS, alineándose perfectamente con los requisitos técnicos, legales y de negocio de TechMarket Orders.
