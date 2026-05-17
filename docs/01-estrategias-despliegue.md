# IE2.1 – Descripción de Estrategias de Despliegue

## Contexto Ágil

En entornos ágiles, el software se entrega de forma iterativa e incremental. El despliegue es parte del ciclo de entrega continua (CI/CD), y su estrategia determina cómo se actualiza el sistema productivo sin comprometer la experiencia del usuario. A continuación se describen las cuatro estrategias principales.

---

## 1. All-in-Once (Big Bang)

### Propósito
Reemplazar la versión completa del sistema en un único evento de despliegue. Toda la infraestructura se actualiza simultáneamente.

### Mecanismo de actualización
1. Se detiene el servicio o se pone en modo mantenimiento.
2. Se despliega la nueva versión en todos los servidores/contenedores.
3. Se reinicia el servicio con la nueva versión.
4. Si hay errores, se debe revertir manualmente a la versión anterior.

### Contexto ágil
- **Uso**: Adecuada solo en etapas tempranas del ciclo o en proyectos de bajo tráfico donde el downtime es aceptable.
- **Limitación**: Contradice los principios ágiles de entregas frecuentes con bajo riesgo. Un fallo afecta al 100% de los usuarios.
- **Relación CD**: Es el enfoque más simple, pero el más riesgoso en integración continua porque cada merge puede provocar una interrupción total.

---

## 2. Rolling Update (Actualización gradual)

### Propósito
Reemplazar instancias antiguas de forma progresiva, asegurando que siempre exista al menos una instancia activa mientras se actualiza el resto.

### Mecanismo de actualización
1. El orquestador (Kubernetes, ECS) selecciona un subconjunto de instancias.
2. Las instancias seleccionadas se detienen y se reemplazan con la nueva versión.
3. El proceso se repite hasta que todas las instancias ejecuten la nueva versión.
4. El rollback implica revertir el proceso en sentido inverso.

### Contexto ágil
- **Uso**: Común en equipos que hacen despliegues frecuentes con alta disponibilidad requerida.
- **Ventaja ágil**: Permite actualizar sin downtime manteniendo parte del sistema en producción.
- **Riesgo**: Durante la transición coexisten dos versiones, lo que puede causar inconsistencias si hay cambios de esquema de datos o API.
- **En Kubernetes**: Controlado por `maxUnavailable` y `maxSurge` en el deployment.

---

## 3. Canary Deployment (Despliegue Canario)

### Propósito
Liberar una nueva versión a un pequeño porcentaje del tráfico real para validar su comportamiento antes de un despliegue masivo.

### Mecanismo de actualización
1. Se mantiene la versión estable sirviendo el 90–95% del tráfico.
2. La nueva versión recibe un porcentaje reducido (5–10%) de usuarios reales.
3. Se monitorean métricas (tasa de errores, latencia, comportamiento).
4. Si las métricas son satisfactorias, se aumenta el porcentaje gradualmente hasta el 100%.
5. Si se detectan anomalías, el rollback es inmediato reduciendo el tráfico a 0%.

### Contexto ágil
- **Uso**: Ideal para equipos con alta frecuencia de releases que necesitan validación con datos reales.
- **Feedback rápido**: Detecta errores en producción afectando solo a un subconjunto de usuarios.
- **Herramientas**: AWS CodeDeploy con canary, Kubernetes con Argo Rollouts, feature flags.
- **Complejidad**: Requiere sistema de ruteo de tráfico sofisticado y observabilidad avanzada.

---

## 4. Blue-Green Deployment

### Propósito
Mantener dos entornos de producción idénticos (Blue = actual, Green = nuevo) y cambiar el tráfico de forma instantánea una vez validada la nueva versión.

### Mecanismo de actualización
1. **Blue** es el entorno activo de producción.
2. **Green** es el entorno inactivo donde se despliega la nueva versión.
3. Se valida Green completamente (tests, smoke tests, health checks).
4. Se redirige el tráfico de Blue → Green cambiando el apuntador del Load Balancer (AWS ALB, nginx).
5. Blue permanece en standby como respaldo. El rollback es instantáneo (reapuntar el LB).

### Contexto ágil
- **Uso**: Microservicios críticos con SLA estrictos donde el downtime es inaceptable.
- **Reducción de riesgo**: El rollback se realiza en segundos sin redeployment.
- **Feedback rápido**: La validación en Green antes del switch permite detectar fallos sin impactar usuarios.
- **Automatización**: El pipeline CI/CD controla completamente el switch mediante APIs del Load Balancer.
- **En AWS**: Implementado con Elastic Load Balancer + ECS/EKS o CodeDeploy Blue/Green.

---

## Resumen visual de mecanismos

| Estrategia    | ¿Hay downtime? | Coexistencia de versiones | Control de rollback |
|---------------|:--------------:|:-------------------------:|:-------------------:|
| All-in-Once   | Sí             | No                        | Manual / Lento      |
| Rolling Update| No (parcial)   | Sí (temporal)             | Automático / Lento  |
| Canary        | No             | Sí (permanente)           | Automático / Rápido |
| Blue-Green    | No             | No (switch atómico)       | Automático / Instantáneo |
