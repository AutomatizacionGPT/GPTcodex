
# Estrategia ATM “3 Tercios” – RR 1 : 3 (Versión 50 %)

*Valores reducidos al **50 %** del plan original para operar con menor riesgo y objetivos más cortos.*

## 1. Concepto general (50 %)
- **Contratos**: 3 (1 / 1 / 1).
- **Stop inicial**: **– $ 37,50** por contrato (≈ 30 ticks / 7,5 pts).
- **Objetivos de beneficio**:

| Objetivo | Ganancia | Relación R:R |
|----------|----------|--------------|
| 1º | **$ 37,50** (+30 t) | 1 R |
| 2º | **$ 75** (+60 t) | 2 R |
| 3º | **$ 112,50** (+90 t) | 3 R |

## 2. Parámetros de la plantilla (Moneda)

| Campo global | Valor |
|--------------|-------|
| **Cantidad de la orden** | **3 contratos** |
| **Stop loss** | 37,50 USD |
| **MIT para ganancia** | Activado |

### Objetivo 1
- **Cantidad**: 1 contrato  
- **Ganancias**: 37,50 USD  
- **Estrategia Stop**: Breakeven (Activador 30 t, Más **2 t**)  
- Sin trailing.

### Objetivo 2 y 3
- **Cantidad**: 1 contrato cada uno  
- **Ganancias**: 75 USD / 112,50 USD  
- **Estrategia Stop** (en ticks):

| Parámetro | Valor |
|-----------|-------|
| Breakeven: Activador | 30 |
| Breakeven: Más | 2 |
| **Trailing pasos:** | |
| Paso 1: Activador | **45** |
| Paso 1: Offset | **20** |
| Paso 2: Activador | **60** |
| Paso 2: Offset | **28** |
| Paso 3: Activador | **80** |
| Paso 3: Offset | **36** |
| Frecuencia | 1 tick |

## 3. Pasos de configuración en NinjaTrader 8
1. **ChartTrader → ATM Strategy → <Custom>.**  
2. *Tipo parámetro*: **Moneda**.  
3. **Cantidad de la orden = 3**.  
4. Completa cada fila según las tablas anteriores.  
5. En Objetivo 2, crea la Stop Strategy con los valores 50 % (Breakeven 30/2 + trail 45/20, 60/28, 80/36).  
   - **Guardar como** `BE30_2_T45_60_80`.  
6. Selecciona la misma Stop Strategy para Objetivo 3.  
7. Guarda la ATM como `ATM_3T_RR1-3_half`.  

## 4. Flujo esperado

| Fase | Acción automática |
|------|-------------------|
| Entrada | Stop –$37,5 por 3 C. |
| +30 ticks | Cierra 1 C, stop 2 C ↗ entrada + 2 t. |
| +45 ticks | Stop ↗ entrada + 25 t. |
| +60 ticks | Cierra 1 C, stop runner ↗ entrada + 32 t (trail 28 t). |
| +80 ticks | Stop runner ↗ entrada + 44 t. |
| +90 ticks | Toma de ganancia final (RR 1:3) o salida por trailing. |

---

*Versión reducida al 50 % — 2025‑05‑08*
