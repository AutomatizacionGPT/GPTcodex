# utils/report_utils.py
from fpdf import FPDF
import os
from tkinter import filedialog, messagebox
from datetime import datetime

def exportar_reporte_pdf(metricas: dict, config_cuenta: dict, nombre_empresa: str, nombre_cuenta: str, fecha_inicio, parent_window):
    """
    Genera y guarda un reporte PDF con métricas y estado de reglas.
    Literalmente igual a como estaba en `jota_capital_tracker.py` :contentReference[oaicite:12]{index=12}.
    """
    if not metricas:
        messagebox.showwarning("Advertencia", "Realice primero el análisis antes de exportar.")
        return

    try:
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, '📄 Reporte Ejecutivo - Jota Capital Tracker', ln=True, align='C')

        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"Empresa: {nombre_empresa}", ln=True)
        pdf.cell(0, 8, f"Cuenta Analizada: {nombre_cuenta}", ln=True)
        pdf.cell(0, 8, f"Fecha Inicio: {fecha_inicio.strftime('%Y-%m-%d')}", ln=True)
        pdf.cell(0, 8, f"Fecha Generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '📊 Métricas Principales:', ln=True)

        pdf.set_font('Arial', '', 12)
        lista_metricas = [
            f"Ganancia Actual: ${metricas['current_pnl']:.2f}",
            f"Progreso Objetivo: {metricas['progress_to_target']:.1f}%",
            f"Días Transcurridos: {metricas['days_elapsed']} / {config_cuenta['DIAS_PRUEBA']}",
            f"Días Restantes: {metricas['days_remaining']}",
            f"Operaciones Totales: {metricas['total_trades']}",
            f"Win Rate: {metricas['win_rate']:.1f}%",
            f"R:R Promedio: {metricas['avg_rr']:.2f}",
            f"Profit Factor: {metricas['profit_factor']:.2f}",
            f"Expectancy: {metricas['expectancy']:.2f} ticks",
            f"Máx Drawdown: ${metricas['max_drawdown']:.2f}",
            f"MAE Promedio: ${metricas.get('avg_mae', 0):.2f}",
            f"MFE Promedio: ${metricas.get('avg_mfe', 0):.2f}",
            f"ETD Promedio: ${metricas.get('avg_etd', 0):.2f}",
            f"Consistencia Diaria Promedio: {metricas.get('avg_daily_consistency', 0):.1f}%",
            f"Max Pérdidas Consecutivas: {metricas.get('max_loss_streak', 0)}",
            f"Fuera de Horario: {metricas.get('fuera_horario_count', 0)}",
            f"Violaciones SL Obl.: {metricas.get('sl_violations', 0)}"
        ]
        for linea in lista_metricas:
            pdf.cell(0, 6, linea, ln=True)
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '📜 Estado de Reglas:', ln=True)
        pdf.set_font('Arial', '', 12)
        for clave, datos in config_cuenta.get('REGLAS', {}).items():
            nombre = datos.get('nombre', clave)
            limite = datos.get('valor', 0)
            pdf.cell(0, 6, f"{nombre} (Límite: {limite}) - Estado: OK", ln=True)

        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            title="Guardar Reporte PDF",
            parent=parent_window
        )
        if ruta_guardado:
            pdf.output(ruta_guardado)
            messagebox.showinfo("Éxito", f"Reporte guardado en:\n{ruta_guardado}", parent=parent_window)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el reporte:\n{e}", parent=parent_window)
