# template_editor.py
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config_manager import ConfigManager

# --- Reglas estándar tal como estaban definidas en el script original ---
REGLAS_ESTANDARD = {
    'RATIO_SL_PIPS':     ('🛡️ Stop Loss (pips)',            10),
    'RATIO_TP_PIPS':     ('🎯 Take Profit (pips)',         15),
    'HORARIO_INICIO':    ('🕒 Horario de Inicio',       '08:00'),
    'HORARIO_FIN':       ('🕔 Horario de Cierre',       '16:00'),
    'STOP_LOSS_OBLIGATORIO': ('🛑 Stop Loss Obligatorio', False),
    'PERDIDA_DIARIA_MAX':     ('💥 Pérdida Diaria Máxima (%)', 5),
    'PERDIDA_SEMANAL_MAX':    ('🔻 Pérdida Semanal Máxima (%)', 10),
    'PERDIDAS_CONSECUTIVAS_MAX':('📉 Pérdidas Consecutivas Máx.', 7),
    'DIAS_OPERANDO_MIN':      ('📆 Mínimo de Días Operando',      5),
    'GANANCIA_DIARIA_MAX_PORC':('📈 Ganancia Diaria Máx. (%)', 70),
    'MULTIPLICADOR_CONTRATOS_MAX':('📊 Multiplicador de Contratos', 3),
    'CONSISTENCIA':           ('📌 Porcentaje de Consistencia (%)', 50),
}

# --- Mapeo de claves usadas en JSON de plantillas al estándar interno ---
MAPA_CLAVES = {
    'porcentaje_consistencia':     'CONSISTENCIA',
    'ganancia_diaria_maxima':      'GANANCIA_DIARIA_MAX_PORC',
    'dias_minimos_operados':       'DIAS_OPERANDO_MIN',
    'perdidas_consecutivas_maxima':'PERDIDAS_CONSECUTIVAS_MAX',
    'perdida_diaria_maxima':       'PERDIDA_DIARIA_MAX',
    'perdida_semanal_maxima':      'PERDIDA_SEMANAL_MAX',
    'contratos_maximos':           'MULTIPLICADOR_CONTRATOS_MAX',
    'ratio_tp_pips':               'RATIO_TP_PIPS',
    'ratio_sl_pips':               'RATIO_SL_PIPS',
    'uso_stop_loss_obligatorio':   'STOP_LOSS_OBLIGATORIO',
}

class TemplateEditor(tk.Toplevel):
    """
    Ventana para crear/editar plantillas de cuenta. 
    Extraída literalmente de `jota_capital_tracker.py` :contentReference[oaicite:1]{index=1}, parte de carga y adaptación de reglas.
    """

    def __init__(self, parent, nombre_plantilla=None):
        super().__init__(parent)
        self.parent = parent
        self.title("Editor de Plantilla de Cuenta")
        self.geometry("650x550")
        self.resizable(False, False)

        self.nombre_plantilla = nombre_plantilla  # Ej. "MiPlantilla.json"
        self.plantilla_data = {}
        self.reglas_por_defecto = []

        # Si hay un nombre de plantilla, cargar su contenido
        if self.nombre_plantilla:
            data = ConfigManager.cargar_plantilla(self.nombre_plantilla)
            self.plantilla_data = data if isinstance(data, dict) else {}

        # Título y botón de guardar (sin cambiar diseño)
        ttk.Label(self, text=f"Editar Plantilla: {self.nombre_plantilla or 'Nueva Plantilla'}",
                  font=("Segoe UI", 12, "bold")).pack(pady=15)
        ttk.Button(self, text="Guardar Plantilla", command=self._guardar_plantilla).pack(pady=10)

        # Explicación estática (sin tocar)
        ttk.Label(self, wraplength=600, justify=tk.LEFT,
                  text="• La plantilla debe contener un bloque 'reglas' con claves y valores.\n"
                       "• Al guardar, se completarán las reglas faltantes con valores por defecto.\n"
                       "• Si falta alguna clave en el JSON original, se asigna el valor DEFAULT."
                 ).pack(padx=20, pady=(0, 20))

    def _adaptar_reglas(self, reglas_crudas):
        """
        Reestructura el bloque 'reglas' para:
          1) Migrar claves antiguas (MAPA_CLAVES) a su forma interna estándar.
          2) Asegurarse de que todas las claves de REGLAS_ESTANDARD existan.
          3) Detectar cuáles se completaron con default (para notificar).
        """
        # Migrar claves antiguas
        for origen, destino in MAPA_CLAVES.items():
            if origen in reglas_crudas and destino not in reglas_crudas:
                reglas_crudas[destino] = reglas_crudas.pop(origen)

        # Extraer y transformar horarios anidados
        if 'horario_operacion' in reglas_crudas:
            ho = reglas_crudas['horario_operacion']
            if 'inicio' in ho:
                reglas_crudas['HORARIO_INICIO'] = ho['inicio']
            if 'fin' in ho:
                reglas_crudas['HORARIO_FIN'] = ho['fin']
            del reglas_crudas['horario_operacion']

        reglas_final = {}
        self.reglas_por_defecto = []
        for clave, (nombre_legible, valor_defecto) in REGLAS_ESTANDARD.items():
            valor_crudo = reglas_crudas.get(clave, valor_defecto)
            # Si ya viene como dict {'valor': ...}, extraer ese valor
            if isinstance(valor_crudo, dict) and 'valor' in valor_crudo:
                valor = valor_crudo['valor']
            else:
                valor = valor_crudo

            # Si vino como string, intentar convertir a numérico o booleano
            if isinstance(valor, str):
                v = valor.strip()
                if v.lower() in ['true', 'false']:
                    valor = (v.lower() == 'true')
                else:
                    try:
                        valor = int(v) if v.isdigit() else float(v)
                    except ValueError:
                        pass  # mantener string si no se convierte

            # Detectar si se completó con default
            if clave not in reglas_crudas:
                self.reglas_por_defecto.append(clave)

            reglas_final[clave] = {'nombre': nombre_legible, 'valor': valor}

        return reglas_final

    def _guardar_plantilla(self):
        """
        Recolecta `self.plantilla_data['reglas']`, las adapta con _adaptar_reglas
        y guarda el JSON resultante en 'Plantillas/nombre_plantilla'. 
        Sin cambios en lógica ni estilos de mensaje.
        """
        data = self.plantilla_data.copy()
        reglas_crudas = data.get('reglas', {})
        reglas_adaptadas = self._adaptar_reglas(reglas_crudas)

        salida = {
            'size': data.get('size', 0),
            'reglas': reglas_adaptadas
        }

        if not self.nombre_plantilla:
            ts = int(datetime.now().timestamp())
            self.nombre_plantilla = f"Plantilla_{ts}.json"

        ConfigManager.guardar_plantilla(self.nombre_plantilla, salida)

        if self.reglas_por_defecto:
            nombres = [reglas_adaptadas[c]['nombre'] for c in self.reglas_por_defecto]
            lista = "\n- ".join(nombres)
            messagebox.showwarning(
                "Valores por defecto usados",
                f"Las siguientes reglas se completaron con valores por defecto:\n\n- {lista}"
            )

        messagebox.showinfo("Éxito", f"Plantilla guardada:\n{self.nombre_plantilla}")
        self.destroy()
