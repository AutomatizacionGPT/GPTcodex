# 🧠 AGENTS.md – Codex Tracker Agent

## 📌 Nombre del Agente
**CodexTracker**

---

## 🎯 Objetivo General
Analizar en tiempo real y bajo demanda el cumplimiento de las reglas de una cuenta de fondeo en función de las operaciones ejecutadas y los parámetros establecidos en la plantilla del evaluador.

---

## 🧩 Funciones del Agente

1. **Leer datos de entrada**
   - `plantilla.json`: reglas de la cuenta de fondeo.
   - `trades.csv`: historial de operaciones.

2. **Analizar cumplimiento**
   - Drawdown en tiempo real.
   - Verificar días operados, lotes máximos y objetivo.
   - Validar reglas críticas.

3. **Generar alertas**
   - Visuales y de texto en caso de incumplimiento.
   - Recomendaciones preventivas.

4. **Informar gráficamente**
   - PnL acumulado, días operados, drawdown, R:R, etc.
   - Tabla dinámica de reglas cumplidas/incumplidas.

5. **Persistencia**
   - Guardar estado de cuenta y cambios evaluados.

---

## 🧾 Entradas esperadas
- `trades.csv` con operaciones reales.
- `plantilla.json` con reglas activas.
- Configuración de usuario (zona horaria, empresa, idioma).

---

## 📤 Salidas esperadas
- Reporte visual/GUI o por consola.
- Gráficos y tablas.
- Log de recomendaciones.

---

## 🔐 Restricciones
- No opera en mercados en vivo.
- No modifica archivos sin autorización.
- Requiere revisión humana final.

