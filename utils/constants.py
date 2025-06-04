# Definiciones globales
ACCOUNT_SIZES = {
    '5K': 5000,
    '10K': 10000,
    '15K': 15000,
    '25K': 25000,
    '50K': 50000,
    '100K': 100000,
    '150K': 150000,
    '200K': 200000,
    '300K': 300000,
    '500K': 500000,
    '600K': 600000
}

ACCOUNT_TYPES = [
    "Mini",
    "Live",
    "Micro",
    "Full",
    "Static",
    "Express",
    "Premium",
    "Estandar",
    "Challenge",
    "Prop Firm", 
    "Personal", 
    "Compartida"
]

texto_ayuda = """
📘 GUÍA DE USO – Jota Capital Tracker

📌 1. Reglas de Evaluación:
- 🛡️ Stop Loss (pips): Define cuántos pips estás dispuesto a perder por operación.
- 🎯 Take Profit (pips): Define tu ganancia objetivo por trade.
- 💥 Pérdida Diaria Máxima: Límite de pérdida permitido en un solo día.
- 🔻 Pérdida Semanal Máxima: Igual pero a nivel semanal.
- 📆 Días de Operación Mínimos: Requisito de consistencia.
- 🛑 Stop Loss Obligatorio: Todas las operaciones deben tener SL asignado.
- 📌 Consistencia (%): Evalúa cuán estable es tu rendimiento promedio diario.

📊 2. Interpretación de Gráficos:
- "Evolución de Ganancias y Drawdown": Muestra tu curva de capital y zonas de riesgo.
- "Win Rate por Hora": Colores verdes = rendimiento positivo por hora. Rojo = negativo.
- "MAE vs MFE": Muestra cuánto dejó ir el trade en contra (MAE) y a favor (MFE).
- "Drawdown por Fecha": Indica cuántos USD estuviste por debajo del punto más alto.
- "Distribución de Ganancias por Trade": Gráfico de campana que te muestra la varianza de tus resultados.

📄 3. Columnas del archivo CSV:
- numero_de_trade: ID de cada operación.
- instrumento: Activo operado (ej. ES, NQ, CL...).
- cuenta: ID de la cuenta.
- estrategia: Nombre del enfoque usado.
- mercado_pos: Long o Short.
- cant: Tamaño del contrato.
- precio_de_entrada: Precio al que se ejecutó la entrada.
- precio_de_salida: Precio de salida.
- tiempo_de_entrada: Timestamp de entrada.
- tiempo_de_salida: Timestamp de salida.
- ganancias: Resultado de la operación ($).
- mae: Máxima pérdida durante la operación.
- mfe: Máxima ganancia durante la operación.
- con_ganancia_neto: Ganancia acumulada hasta ese trade.


| Emoji | Significado                              | Uso sugerido / Actual                       |
| ----- | ---------------------------------------- | ------------------------------------------- |
| 🏦    | Tamaño de cuenta                         | Parámetro: capital base de evaluación       |
| 🎯    | Objetivo de ganancia                     | Parámetro: target monetario o porcentual    |
| 💥    | Pérdida diaria máxima                    | Regla crítica (riesgo)                      |
| 🔻    | Pérdida semanal máxima                   | Regla crítica (riesgo)                      |
| 📉    | Pérdidas consecutivas                    | Regla de consistencia / riesgo emocional    |
| 📈    | Ganancia diaria máxima                   | Límite de rendimiento (antimanipulación)    |
| 📆    | Mínimo de días operados                  | Constancia operativa                        |
| 🛑    | Stop Loss obligatorio                    | Cumplimiento técnico por política           |
| 🛡️    | Tamaño del SL en pips                    | Gestión de riesgo específica                |
| 🤑    | Retiro máximo permitido                  | Regla de retiro o premio                    |
| 📤    | Umbral de pago                           | Nivel mínimo antes de retiro                |
| ⚠️    | Alerta visual intermedia                 | Estado: cerca de romper regla               |
| ❌    | Regla violada                            | Estado: crítico o fallido                   |
| ✅    | Regla cumplida correctamente             | Estado: válido o aprobado                   |
| ⚙️    | Valor por defecto usado                  | Advertencia visual (usuario no definió)     |
| 🕒    | Horario de inicio de operación           | Regla de tiempo                             |
| 🕔    | Horario de cierre de operación           | Regla de tiempo                             |
| 📌    | Consistencia operativa                   | Evaluación de estabilidad o progresión      |
| 📊    | Multiplicador de contratos               | Control de exposición                       |
| 📂    | Botón: cargar plantilla o archivo        | UI: explorador de archivos                  |
| 🔍    | Botón: analizar operaciones              | UI: acción de análisis                      |
| 📜    | Evaluar reglas / plantilla cargada       | UI: validación o verificación de estructura |
| 🚀    | Botón de acción principal (ej. ejecutar) | UI: lanzar proceso principal                |
| 🔒    | Elemento bloqueado o de protección       | (opcional para reglas inalterables)         |
| 📘    | Pestaña de ayuda                         | UI: sección informativa                     |
| 📊    | Gráfico de análisis                      | UI: visualización de datos                  |
| 📈    | Gráfico de rendimiento                   | UI: visualización de resultados             |
| 📉    | Gráfico de riesgo                        | UI: visualización de riesgo                 |
| 📅    | Selector de fecha                        | UI: entrada de datos                        |
| 📤    | Botón de exportar                        | UI: acción de exportación                   |
| 📅    | Selector de fecha                        | UI: entrada de datos                        |
| 📊    | Gráfico de análisis                      | UI: visualización de datos                  |

"""
