
# Estrategia ATM “3 Tercios” – RR 1 : 3 (MES Micro E‑mini)

## 1. Concepto general
- **División**: la posición se reparte en **tres contratos** (1 / 1 / 1).
- **Riesgo**: Stop inicial **– \$75** por contrato (≈ 60 ticks / 15 pts).
- **Objetivos de beneficio**:
  | Objetivo | Ganancia | Relación R:R |
  |----------|----------|--------------|
  | 1º | **\$75** (+60 t) | 1 R |
  | 2º | **\$150** (+120 t) | 2 R |
  | 3º | **\$225** (+180 t) | 3 R |

## 2. Parámetros de la plantilla (Tipo = Moneda)

| Campo global | Valor |
|--------------|-------|
| **Cantidad de la orden** | **3 contratos** |
| **Stop loss** | 75 USD |
| **MIT para ganancia** | Activado |

### Objetivo 1
- **Cantidad**: 1 contrato  
- **Ganancias**: 75 USD  
- **Estrategia Stop**: Breakeven (Activador 60 t, Más 4 t)  
- Sin trailing.

### Objetivo 2 y Objetivo 3
- **Cantidad**: 1 contrato cada uno  
- **Ganancias**: 150 USD / 225 USD  
- **Estrategia Stop**:  
  - Breakeven **60 t +4 t**  
  - Auto recorrido (Trailing)  
    | Paso | Activador (ticks) | Offset (ticks) | Stop resultante |
    |------|-------------------|---------------|-----------------|
    | 1 | 90 | 40 | +50 t |
    | 2 | 120 | 56 | +64 t |
    | 3 | 160 | 72 | +88 t |
    | Frecuencia: 1 tick |

## 3. Pasos para configurar en NinjaTrader 8

1. **ChartTrader → ATM Strategy → <Custom>.**
2. *Tipo de parámetro*: **Moneda**.  
3. Introducir **Cantidad de la orden = 3**.  
4. Completar los tres objetivos con los valores anteriores.  
5. En **Estrategia Stop** del Objetivo 2:  
   - Haz clic en **Editar…** y rellena Breakeven + Trailing (ver tabla).  
   - **Guardar como plantilla**: `BE60_4_T90-120-160`.  
6. Selecciona la MISMA plantilla de stop para Objetivo 3.  
7. En Objetivo 1, deja la estrategia vacía o sólo Breakeven 60/4.  
8. Activa **MIT para ganancia**.  
9. Pulsa **Guardar como plantilla…** y nómbrala `ATM_3T_RR1-3`.  
10. Verifica que el cuadro **Qty** de ChartTrader muestre **3** antes de operar.

## 4. Flujo durante la operación

| Fase | Acción automática |
|------|-------------------|
| Entrada | Stop –\$75 por los 3 C. |
| +60 ticks | Cierra 1 C, stop de los 2 C ↗ entrada + 4 t. |
| +90 ticks | Stop ↗ entrada + 50 t. |
| +120 ticks | Cierra 1 C, stop runner ↗ entrada + 64 t y comienza trailing 56 t por detrás. |
| +160 ticks | Stop runner ↗ entrada + 88 t. |
| +180 ticks | Toma de ganancia final (RR 1:3) o salida por trailing. |

## 5. Ajustes finos opcionales
- **Mercado muy volátil**: sube offsets (44/60/80) o activadores (+100/+130/+170).  
- **Mercado lateral**: baja activadores Trail 1/2 (80/110) para proteger antes.  
- **Un solo contrato**: usa una versión simplificada (Stop 75 USD, TP 225 USD, BE 60/4 + trail).

---

*Versión: 2025‑05‑07*  
