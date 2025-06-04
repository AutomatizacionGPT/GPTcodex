# utils/data_utils.py
import pandas as pd
import numpy as np
import string

def validar_numerico(x):
    """Verificar si un valor se puede convertir a float. Retorna 0 si OK, 1 si error."""
    try:
        s = str(x).replace('$', '').replace(' ', '').replace('%', '').replace(',', '.')
        float(s)
        return 0
    except:
        return 1

def validar_fecha(x):
    """Verificar si un valor se puede convertir a fecha. Retorna 0 si OK o vacío, 1 si error."""
    try:
        if pd.isna(x) or x == '':
            return 0
        pd.to_datetime(x, errors='coerce')
        return 0
    except:
        return 1

def limpiar_numerico(x):
    """
    Convierte cadenas a float, eliminando símbolos de moneda y separadores.
    Devuelve 0.0 si no es convertible.
    """
    if pd.isna(x) or x == '':
        return 0.0
    x_str = str(x).strip()
    # Quitar símbolos comunes de moneda
    for simb in ['$', '€', '£', '¥', 'R$', 'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'NZD', 'MXN', 'COP', 'CLP', 'PEN', 'ARS', 'BRL']:
        x_str = x_str.replace(simb, '')
    x_str = x_str.replace('%', '').replace(' ', '').rstrip(',')
    x_str = x_str.replace(',', '.')
    partes = x_str.split('.')
    if len(partes) > 2:
        x_str = ''.join(partes[:-1]) + '.' + partes[-1]
    elif len(partes) == 2 and partes[1] == '':
        x_str = partes[0]
    try:
        return float(x_str)
    except (ValueError, TypeError):
        return 0.0

def parsear_fecha_hora(x):
    """
    Intenta convertir múltiples formatos de fecha/hora a pd.Timestamp.
    Retorna pd.NaT si no es convertible.
    """
    if pd.isna(x) or x == '':
        return pd.NaT
    s = str(x).strip().replace('Â', '').replace('\u00a0', ' ').replace('\xa0', ' ')
    for am in ['a m', 'am', 'a.m.', 'A M', 'AM', 'A.M.']:
        s = s.replace(am, 'AM')
    for pm in ['p m', 'pm', 'p.m.', 'P M', 'PM', 'P.M.']:
        s = s.replace(pm, 'PM')

    formatos = [
        '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S',
        '%m/%d/%Y %H:%M:%S', '%m-%d-%Y %H:%M:%S',
        '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %I:%M:%S %p', '%d-%m-%Y %I:%M:%S %p',
        '%m/%d/%Y %I:%M:%S %p', '%m-%d-%Y %I:%M:%S %p',
        '%d/%m/%Y %H:%M', '%d-%m-%Y %H:%M',
        '%m/%d/%Y %H:%M', '%m-%d-%Y %H:%M',
        '%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M',
        '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d'
    ]
    for fmt in formatos:
        try:
            resultado = pd.to_datetime(s, format=fmt, errors='coerce')
            if not pd.isna(resultado):
                return resultado
        except:
            continue
    try:
        resultado = pd.to_datetime(s, dayfirst=True, errors='coerce')
        if resultado.year < 1900 or resultado.year > 2100:
            return pd.NaT
        return resultado
    except:
        return pd.NaT

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza nombres de columnas a minúsculas, sin espacios, sin tildes,
    sin puntuación final y con mapeo corto tal como hacía el script original.
    """
    df = df.copy()
    nuevas = []
    for col in df.columns:
        col2 = col.strip().lower()
        col2 = col2.replace(' ', '_')
        for a, b in [('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ñ', 'n')]:
            col2 = col2.replace(a, b)
        col2 = col2.rstrip(string.punctuation)
        col2 = col2.replace('número_de_trade', 'numero_trade')
        col2 = col2.replace('mercado_pos.', 'mercado_pos')
        nuevas.append(col2)
    df.columns = nuevas
    return df

def cargar_datos_csv(ruta_archivo: str) -> pd.DataFrame:
    """
    Carga un CSV usando delimitador ';' fijo (tal como en el original),
    elimina columnas 'Unnamed', maneja miles y decimales latinos.
    """
    df = pd.read_csv(
        ruta_archivo,
        sep=';',
        encoding='utf-8',
        decimal=',',
        thousands='.',
        engine='python',
        on_bad_lines='skip'
    )
    df = df.loc[:, ~df.columns.str.match(r'^Unnamed')]
    df.columns = df.columns.str.strip()
    return df

def procesar_datos(df: pd.DataFrame, config_cuenta: dict) -> pd.DataFrame:
    """
    Aplica todo el flujo de normalización/limpieza y cálculo de métricas intermedias.
    Extraído textualmente de `jota_capital_tracker.py` :contentReference[oaicite:3]{index=3}, sin cambiar nada.
    """
    df = normalizar_columnas(df)

    requeridas = ['cuenta', 'ganancias', 'precio_de_entrada', 'precio_de_salida', 'mercado_pos']
    faltantes = [c for c in requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas requeridas faltantes: {', '.join(faltantes)}")

    for col in ['precio_de_entrada', 'precio_de_salida', 'ganancias', 'mae', 'mfe', 'etd']:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_numerico)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    for col in ['tiempo_de_entrada', 'tiempo_de_salida']:
        if col in df.columns:
            df[col] = df[col].map(parsear_fecha_hora)
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df = df[~df[col].isna()]

    if df.empty:
        raise ValueError("No hay datos válidos después del procesamiento de fechas.")
    df = df.sort_values('tiempo_de_entrada').reset_index(drop=True)

    if 'tiempo_de_entrada' in df.columns and 'tiempo_de_salida' in df.columns:
        df['duracion_minutos'] = (df['tiempo_de_salida'] - df['tiempo_de_entrada']).dt.total_seconds() / 60
        df['duracion_minutos'] = df['duracion_minutos'].fillna(0).clip(lower=0)

    if 'instrumento' in df.columns:
        from models.contracts import ContratosManager
        df['parametros_operativos'] = df['instrumento'].apply(
            lambda x: ContratosManager.obtener_parametros_contrato(x)
        )
        df['ticks'] = df.apply(
            lambda row: (row['precio_de_salida'] - row['precio_de_entrada'])
                        / row['parametros_operativos']['TAMAÑO_TICK'], axis=1
        )
        df['valor_ticks'] = df['ticks'] * df['parametros_operativos'].apply(lambda x: x['VALOR_TICK'])
        df['puntos'] = df['ticks'] * df['parametros_operativos'].apply(lambda x: x['TAMAÑO_TICK'])

    df['ticks_magnitud'] = df['ticks'].abs()
    df['pnl_neto'] = df['ganancias'].apply(lambda x: -abs(x) if x < 0 else x)
    df['pnl_acum'] = df['pnl_neto'].cumsum()
    df['equity_peak'] = df['pnl_acum'].cummax()
    df['drawdown'] = (df['equity_peak'] - df['pnl_acum']).abs()

    if 'REGLAS' in config_cuenta:
        sl_ticks = config_cuenta['REGLAS']['RATIO_SL_PIPS']['valor']
        tp_ticks = config_cuenta['REGLAS']['RATIO_TP_PIPS']['valor']
        df['sl_planeado_usd'] = df['parametros_operativos'].apply(lambda x: sl_ticks * x['VALOR_TICK'])
        df['r_real'] = df['pnl_neto'] / df['sl_planeado_usd']
        df['tp_planeado_usd'] = df['parametros_operativos'].apply(lambda x: tp_ticks * x['VALOR_TICK'])
        df['sl_deviation'] = np.where(
            df['pnl_neto'] < 0,
            abs(df['pnl_neto']) / df['sl_planeado_usd'] - 1,
            0
        )
        df['tp_deviation'] = np.where(
            df['pnl_neto'] > 0,
            df['pnl_neto'] / df['tp_planeado_usd'] - 1,
            0
        )

    if 'mfe' in df.columns and 'ganancias' in df.columns:
        df['etd'] = np.where(df['mfe'] > 0, df['mfe'] - df['ganancias'], 0)

    if 'tiempo_de_entrada' in df.columns:
        df['hora_operacion'] = df['tiempo_de_entrada'].dt.strftime('%H:%M')
        df['fecha'] = df['tiempo_de_entrada'].dt.date

    df['resultado'] = np.where(df['ganancias'] > 0, 1, 0)
    df['loss_streak'] = (df['resultado'] == 0).astype(int).groupby(
        df['resultado'].eq(1).cumsum()
    ).cumsum()

    return df
