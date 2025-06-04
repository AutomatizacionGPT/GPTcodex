# utils/plot_utils.py
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

def crear_figura_equity_drawdown(df, config_cuenta, colores) -> Figure:
    """
    Gráfico de Equity vs Drawdown:
    Extraído de `jota_capital_tracker.py` :contentReference[oaicite:5]{index=5}, sin cambiar nada.
    """
    df = df.copy()
    df['fecha_abreviada'] = df['tiempo_de_entrada'].dt.strftime('%Y-%b-%d')
    fig, ax = plt.subplots(figsize=(12, 6))

    x = df['fecha_abreviada']
    ax.plot(x, df['pnl_acum'], marker='o', linestyle='-', label='PnL Acumulado', color=colores['primario'])
    ax.plot(x, df['equity_peak'], linestyle='--', linewidth=1.5, label='Equity Peak', color=colores['advertencia'])
    ax.fill_between(x, df['equity_peak'], df['pnl_acum'],
                    where=(df['drawdown'] > 0), interpolate=True,
                    color=colores['peligro'], alpha=0.3, label='Drawdown')

    objetivo = config_cuenta.get('OBJETIVO_GANANCIA', 0)
    ax.axhline(y=objetivo, color=colores['exito'], linestyle='--', linewidth=2, label='Objetivo USD')

    umbral = config_cuenta.get('UMBRAL_PAGO', 0)
    ax.axhline(y=umbral, color=colores['advertencia'], linestyle='--', linewidth=2, label='Umbral Pago')

    pago_max = config_cuenta.get('PAGO_MAXIMO', 0)
    ax.axhline(y=pago_max, color=colores['peligro'], linestyle='--', linewidth=2, label='Pago Máximo')

    if len(x) >= 2:
        ax.plot([x.iloc[0], x.iloc[-1]], [0, objetivo],
                linestyle=':', linewidth=2, color=colores['secundario'], label='Tendencia Esperada')

    ax.set_title('📈 Equity y Drawdown', fontsize=14, fontweight='bold')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('USD ($)')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    fig.tight_layout()
    return fig

def crear_histograma_ganancias(df, colores) -> Figure:
    """
    Histograma de ganancias/perdidas por operación.
    Copiado sin cambios de `jota_capital_tracker.py` :contentReference[oaicite:6]{index=6}.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    df['ganancias'].hist(bins=40, ax=ax, color=colores['secundario'], edgecolor='black', alpha=0.7)
    ax.set_title('📊 Distribución de Ganancias/Pérdidas', fontsize=13, fontweight='bold')
    ax.set_xlabel('Resultado por Operación ($)')
    ax.set_ylabel('Frecuencia')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

def crear_grafico_rr(df, colores) -> Figure:
    """
    Gráfico de R:R por operación (r_real).
    Copiado directo de `jota_capital_tracker.py` :contentReference[oaicite:7]{index=7}.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    if 'r_real' in df.columns:
        x = np.arange(len(df))
        ax.plot(x, df['r_real'], marker='x', linestyle='-', color=colores['primario'], alpha=0.7)
        ax.axhline(0, color='black', linewidth=1)

        from matplotlib.lines import Line2D
        legend_elems = [
            Line2D([0], [0], color='black', lw=1, linestyle='-', label='Base 0'),
            Line2D([0], [0], color=colores['advertencia'], lw=1.5, linestyle=':', label='1:1'),
            Line2D([0], [0], color=colores['primario'], lw=1.5, linestyle=':', label='1:2'),
            Line2D([0], [0], color=colores['exito'], lw=2, linestyle='--', label='1:3'),
            Line2D([0], [0], color=colores['peligro'], lw=2, linestyle='--', label='-1R'),
        ]
        ax.legend(handles=legend_elems, loc='upper right', fontsize=9)

        ax.set_title('🎯 Ratio R por Operación', fontsize=13, fontweight='bold')
        ax.set_xlabel('Operación')
        ax.set_ylabel('R (veces riesgo)')
        ax.grid(True, alpha=0.3)
        ax.text(0.5, -0.35, '1:1   |   1:2   |   1:3   |   -1R',
                transform=ax.transAxes, fontsize=10, ha='center', va='top')
    fig.tight_layout()
    return fig

def crear_grafico_win_rate_por_hora(df, colores) -> Figure:
    """
    Win Rate (%) por hora de operación.
    Sacado de `jota_capital_tracker.py` :contentReference[oaicite:8]{index=8}, sección Timing.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    if 'hora_operacion' in df.columns and 'resultado' in df.columns:
        df_hora = df.groupby('hora_operacion')['resultado'].mean() * 100
        df_hora = df_hora.sort_index()
        ax.bar(df_hora.index, df_hora.values, color=colores['acento'], alpha=0.7, edgecolor='black')
        ax.set_title('⏱️ Win Rate por Hora', fontsize=13, fontweight='bold')
        ax.set_xlabel('Hora (HH:MM)')
        ax.set_ylabel('Win Rate (%)')
        ax.set_xticklabels(df_hora.index, rotation=45, ha='right')
        ax.grid(True, axis='y', alpha=0.3)
    fig.tight_layout()
    return fig

def crear_grafico_mae_vs_mfe(df, colores) -> Figure:
    """
    Dispersión MAE vs MFE.
    Copiado de `jota_capital_tracker.py` :contentReference[oaicite:9]{index=9}.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    if 'mae' in df.columns and 'mfe' in df.columns:
        ax.scatter(df['mae'], df['mfe'], color=colores['secundario'], alpha=0.6)
        ax.set_title('📉 MAE vs MFE', fontsize=13, fontweight='bold')
        ax.set_xlabel('MAE (máxima pérdida)')
        ax.set_ylabel('MFE (máxima ganancia)')
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

def crear_grafico_duracion(df, colores) -> Figure:
    """
    Histograma de duración de operaciones (en minutos).
    Extraído de la sección “Duración de Operaciones” en el script original.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    if 'duracion_minutos' in df.columns:
        duraciones = df['duracion_minutos']
        bins = [0, 5, 15, 30, 60, 120, 240, 480, 1440]
        etiquetas = ['0-5m', '5-15m', '15-30m', '30m-1h', '1-2h', '2-4h', '4-8h', '8h+']
        conteos = np.histogram(duraciones, bins=bins)[0]
        ax.bar(etiquetas, conteos, color=colores['primario'], alpha=0.7)
        ax.set_title('⏳ Duración de Operaciones', fontsize=13, fontweight='bold')
        ax.set_xlabel('Duración')
        ax.set_ylabel('Cantidad')
        ax.grid(True, axis='y', alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    fig.tight_layout()
    return fig

def crear_grafico_drawdown_diario(df, colores) -> Figure:
    """
    Drawdown acumulado por fecha.
    Copiado de `jota_capital_tracker.py` :contentReference[oaicite:10]{index=10}.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    if 'fecha' in df.columns and 'ganancias' in df.columns:
        df2 = df.copy()
        pnl_diario = df2.groupby('fecha')['ganancias'].sum().cumsum()
        drawdown = pnl_diario.cummax() - pnl_diario
        ax.plot(drawdown.index, drawdown.values, color=colores['peligro'], linewidth=2)
        ax.set_title('📉 Drawdown Diario', fontsize=13, fontweight='bold')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Drawdown ($)')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    fig.tight_layout()
    return fig

def crear_graficos_timing(df, colores) -> list:
    """
    Retorna [fig_win_rate, fig_mae_mfe, fig_duracion].
    Textualmente igual que el bloque “Gráficos Avanzados” original.
    """
    figs = []
    figs.append(crear_grafico_win_rate_por_hora(df, colores))
    figs.append(crear_grafico_mae_vs_mfe(df, colores))
    figs.append(crear_grafico_duracion(df, colores))
    return figs
