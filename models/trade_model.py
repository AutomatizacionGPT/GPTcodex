# models/trade_model.py
import numpy as np
import pandas as pd
from datetime import datetime

class TradeModel:
    """
    Cálculo de métricas avanzadas a partir de un DataFrame ya procesado.
    Extraído íntegro de `jota_capital_tracker.py` :contentReference[oaicite:14]{index=14}.
    """

    @staticmethod
    def calcular_metricas(df, fecha_inicio, config_cuenta) -> dict:
        fecha_hoy = datetime.now().date()
        dias_transcurridos = (fecha_hoy - fecha_inicio).days + 1
        dias_restantes = max(0, config_cuenta['DIAS_PRUEBA'] - dias_transcurridos)

        pnl_actual = df['ganancias'].sum()
        objetivo = config_cuenta.get('OBJETIVO_GANANCIA', 0)
        progreso = (pnl_actual / objetivo) * 100 if objetivo else 0

        pnl_acumulado = df['ganancias'].cumsum()
        max_drawdown = (pnl_acumulado.cummax() - pnl_acumulado).max()

        df['resultado'] = np.where(df['ganancias'] > 0, 1, 0)
        wins = int(df['resultado'].sum())
        losses = int(len(df) - wins)
        win_rate = (wins / len(df)) * 100 if len(df) > 0 else 0

        valor_tick = df['parametros_operativos'].iloc[0]['VALOR_TICK'] if 'parametros_operativos' in df.columns else 1
        avg_win_ticks = df[df['ganancias'] > 0]['ganancias'].mean() / valor_tick if wins > 0 else 0
        avg_loss_ticks = df[df['ganancias'] < 0]['ganancias'].mean() / valor_tick if losses > 0 else 0
        avg_rr = abs(avg_win_ticks / avg_loss_ticks) if avg_loss_ticks != 0 else 0

        gross_profit = df[df['ganancias'] > 0]['ganancias'].sum()
        gross_loss = abs(df[df['ganancias'] < 0]['ganancias'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else 0

        expectancy = (
            (win_rate * avg_win_ticks) + ((100 - win_rate) * avg_loss_ticks)
        ) / 100 if (wins + losses) > 0 else 0

        daily_loss_ok = "OK"
        if 'tiempo_de_entrada' in df.columns:
            df['fecha'] = df['tiempo_de_entrada'].dt.date
            df_diario = df.groupby('fecha')['ganancias'].sum()
            if any(df_diario < -config_cuenta['DRAWDOWN_MAX']):
                daily_loss_ok = "EXCEDIDO"

        avg_mae = df['mae'].mean() if 'mae' in df.columns else 0
        avg_mfe = df['mfe'].mean() if 'mfe' in df.columns else 0
        avg_etd = df['etd'].mean() if 'etd' in df.columns else 0

        daily_wins = df.groupby(df['tiempo_de_entrada'].dt.date)['resultado'].mean() * 100 if 'tiempo_de_entrada' in df.columns else pd.Series(dtype=float)
        avg_daily_consistency = daily_wins.mean() if not daily_wins.empty else 0

        df['loss_streak'] = (df['resultado'] == 0).astype(int).groupby(df['resultado'].eq(1).cumsum()).cumsum()
        max_loss_streak = int(df['loss_streak'].max()) if 'loss_streak' in df.columns else 0

        horario_inicio = config_cuenta['REGLAS']['HORARIO_INICIO']['valor']
        horario_fin = config_cuenta['REGLAS']['HORARIO_FIN']['valor']
        df['fuera_horario'] = ~df['hora_operacion'].between(horario_inicio, horario_fin)
        fuera_horario_count = int(df['fuera_horario'].sum()) if 'fuera_horario' in df.columns else 0

        sl_violations = 0
        if config_cuenta['REGLAS']['STOP_LOSS_OBLIGATORIO']['valor'] and 'mae' in df.columns:
            sl_ticks = config_cuenta['REGLAS']['RATIO_SL_PIPS']['valor']
            sl_usd = df['parametros_operativos'].apply(lambda x: sl_ticks * x['VALOR_TICK'])
            sl_violations = int((df['mae'].abs() > sl_usd).sum())

        return {
            'current_pnl': pnl_actual,
            'progress_to_target': progreso,
            'days_elapsed': dias_transcurridos,
            'days_remaining': dias_restantes,
            'max_drawdown': max_drawdown,
            'total_trades': len(df),
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_win_ticks': avg_win_ticks,
            'avg_loss_ticks': avg_loss_ticks,
            'avg_rr': avg_rr,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'daily_loss_status': daily_loss_ok,
            'avg_mae': avg_mae,
            'avg_mfe': avg_mfe,
            'avg_etd': avg_etd,
            'avg_daily_consistency': avg_daily_consistency,
            'max_loss_streak': max_loss_streak,
            'fuera_horario_count': fuera_horario_count,
            'sl_violations': sl_violations
        }
