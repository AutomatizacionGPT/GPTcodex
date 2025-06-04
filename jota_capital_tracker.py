#!/usr/bin/env python3
# jota_capital_tracker.py

# --- Librerías necesarias ---
import os
import json
from config_manager import ConfigManager   # Gestión de plantillas y empresas
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.font import Font
import pandas as pd
import numpy as np
import seaborn as sns
import mplcursors  # Para tooltips interactivos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from datetime import datetime, timedelta
from fpdf import FPDF
from matplotlib.figure import Figure

# --- Importar warnings para manejar mensajes de advertencia ---
import warnings

# --- Configuración de la fuente para matplotlib ---
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# Fuente compatible con emojis (solo para matplotlib)
plt.rcParams['font.family'] = 'Segoe UI Emoji'  # Windows
# plt.rcParams['font.family'] = 'Noto Color Emoji'  # Linux

# --- Configuración de matplotlib para evitar warnings de fuentes ---
warnings.filterwarnings("ignore", message="Glyph.*missing from font")
warnings.filterwarnings("ignore", message="constrained_layout not applied.*")
warnings.filterwarnings("ignore", message=".*?font.*?not found.*?")
warnings.filterwarnings("ignore", message=".*?font.*?not found.*?")
warnings.filterwarnings("ignore", message=".*?font.*?not found.*?")

# --- Constantes del Sistema ---
NOMBRE_REPORTE = "Reporte_Desempeño_JCT.pdf"

import threading
# --- Hilo con capacidad de detenerse (sin cambios) ---
class StoppableThread(threading.Thread):
    """Thread con capacidad de detenerse."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

# --- Funciones de procesamiento de datos y gráficos importadas ---
from template_editor import TemplateEditor
from utils.data_utils import cargar_datos_csv, procesar_datos, validar_numerico, validar_fecha
from utils.plot_utils import (
    crear_figura_equity_drawdown,
    crear_histograma_ganancias,
    crear_grafico_rr,
    crear_graficos_timing,
    crear_grafico_drawdown_diario
)
from utils.report_utils import exportar_reporte_pdf
from models.trade_model import TradeModel
from models.contracts import ContratosManager
from utils.constants import texto_ayuda

# --- Variables globales de reglas y parámetros (tal cual estaban) ---
REGLAS_TRADING = {
    'PERDIDA_DIARIA_MAX': 0.05,      # 5% pérdida diaria máxima
    'PERDIDA_SEMANAL_MAX': 0.10,     # 10% pérdida semanal máxima
    'PERDIDAS_CONSECUTIVAS_MAX': 7,  # 7 días perdidos consecutivos máximo
    'DIAS_OPERANDO_MIN': 5,          # Mínimo 5 días operando
    'GANANCIA_DIARIA_MAX_PORC': 0.70,# 70% de ganancia máxima diaria
    'MULTIPLICADOR_CONTRATOS_MAX': 3.0  # 3 veces el tamaño permitido
}

NOMBRES_REGLAS_DEFECTO = {
    'PERDIDA_DIARIA_MAX':        'Pérdida Diaria Máxima (%)',
    'PERDIDA_SEMANAL_MAX':       'Pérdida Semanal Máxima (%)',
    'PERDIDAS_CONSECUTIVAS_MAX': 'Máx. Días Perdidos Consecutivos',
    'DIAS_OPERANDO_MIN':         'Mínimo de Días Operando',
    'GANANCIA_DIARIA_MAX_PORC':  'Ganancia Diaria Máxima (%)',
    'MULTIPLICADOR_CONTRATOS_MAX':'Multiplicador de Contratos Máximo'
}

PARAMETROS_OPERATIVOS = {
    'VALOR_PUNTO': 5.0,
    'TAMAÑO_TICK': 0.25,
    'VALOR_TICK': 1.25,
    'STOP_LOSS_TICKS': 60,
    'TAKE_PROFIT_TICKS': 180
}

# --- Clase principal de la aplicación (GUI + orquestación) ---
class JotaCapitalTracker:
    def __init__(self, nombre_empresa=None):
        # Variables de estado internas
        self.df = None
        self.metricas = {}
        self.threads = []  # Initialize threads as an empty list
        self.parametros_operativos = PARAMETROS_OPERATIVOS.copy()
        self.fecha_inicio = None
        self.cuenta_seleccionada = None
        self.plantillas_cuentas = {}
        self.config_cuenta = {}

        self.nombre_empresa = nombre_empresa or "Jota Capital Tracker"
        self.nombre_archivo_csv = None

        
        # Colores corporativos (sin modificación)
        self.colores = {
            'fondo': '#f5f5f5',
            'primario': '#1e3a8a',
            'secundario': '#6b7280',
            'acento': '#ef4444',
            'exito': '#10b981',
            'advertencia': '#f59e0b',
            'peligro': '#dc2626',
            'texto': '#111827',
            'claro': '#ffffff',
            'oscuro': '#1f2937'
        }
        self.raiz = tk.Tk()
        self.var_cuenta_analisis = tk.StringVar()
        self.var_cuenta = tk.StringVar()  # Define var_cuenta as a StringVar
        self.var_fecha = tk.StringVar()
        self.var_estado = tk.StringVar(value="Listo para comenzar.")
        self.var_estado.set(f"Bienvenido a {self.nombre_empresa} - Cargando plantillas...")


        # Cargar plantillas existentes
        for tpl_file in ConfigManager.listar_plantillas():
            if not tpl_file.endswith('.json'):
                continue
            name = os.path.splitext(tpl_file)[0]
            data = ConfigManager.cargar_plantilla(tpl_file)
            reglas = data.get('reglas', {})
            self.plantillas_cuentas[name] = {
                'TAMAÑO_CUENTA': data.get('size', 0),
                'OBJETIVO_GANANCIA': reglas.get('objetivo_usd', 0),
                'OBJETIVO_PORC':    reglas.get('objetivo_ganancia_pct', 0),
                'DRAWDOWN_MAX':     reglas.get('drawdown_usd', 0),
                'DRAWDOWN_MAX_PORC':reglas.get('drawdown_maximo_pct', 0),
                'UMBRAL_PAGO':      reglas.get('umbral_pago', 0),
                'PAGO_MAXIMO':      reglas.get('pago_maximo', 0),
                'DIAS_PRUEBA':      reglas.get('dias_prueba', reglas.get('dias_minimos_operados', 0)),
                'REGLAS': {
                    key.upper(): {'nombre': key.replace('_', ' ').capitalize(), 'valor': value}
                    for key, value in reglas.items()
                }
            }

        # Inicializar interfaz
        self.configurar_interfaz()

    def configurar_interfaz(self):
        """Construye la ventana principal y sus pestañas (sin cambios en estilos)."""
        # Ya existe una única raíz creada en __init__ (self.raiz); no volvemos a instanciarla.
        self.raiz.title(f"Jota Capital Tracker - {self.nombre_empresa}")
        self.raiz.geometry("1280x850")
        self.raiz.configure(bg=self.colores['fondo'])

        # Estilos ttk idénticos a los originales
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('TNotebook', background=self.colores['fondo'])
        estilo.configure('TFrame', background=self.colores['fondo'])
        estilo.configure('TLabel', background=self.colores['fondo'], font=('Segoe UI', 10))
        estilo.configure('Titulo.TLabel', font=('Segoe UI', 14, 'bold'), foreground=self.colores['primario'])
        estilo.configure('TButton', font=('Segoe UI', 10), foreground='white')
        estilo.configure('Exito.TButton', background=self.colores['exito'], foreground='white')
        estilo.configure('Peligro.TButton', background=self.colores['peligro'], foreground='white')

        # Notebook principal
        self.notebook = ttk.Notebook(self.raiz)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pestaña 1: Configuración de Cuenta
        self.marco_config = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.marco_config, text="🔧 Configuración de Cuenta")
        self.construir_pestaña_config()

        # Pestaña 2: Análisis de Operaciones
        self.marco_analisis = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.marco_analisis, text="📈 Análisis de Operaciones")
        self.construir_pestaña_analisis()

        # Pestaña 3: Progreso de Retiros (sin contenido, tal como estaba)
        self.marco_retiros = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.marco_retiros, text="💰 Progreso Retiros")
        ttk.Label(self.marco_retiros, text="(Aquí irá el flujo de progreso de retiros)", font=('Segoe UI', 12)).pack()

        # Pestaña 4: Ayuda (idéntica al original)
        pestaña_ayuda = ttk.Frame(self.notebook)
        self.notebook.add(pestaña_ayuda, text="📘 Ayuda")
        texto = tk.Text(pestaña_ayuda, wrap='word', font=('Segoe UI Emoji', 10))
        texto.insert(tk.END, self._texto_ayuda_completo())
        texto.config(state='disabled')
        texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Barra de estado (idéntica)
        barra = ttk.Label(self.raiz, textvariable=self.var_estado, relief=tk.SUNKEN, anchor=tk.W)
        barra.pack(side=tk.BOTTOM, fill=tk.X)

        self.raiz.protocol("WM_DELETE_WINDOW", self.al_cerrar)

    def _texto_ayuda_completo(self) -> str:
        """
        Texto largo de ayuda, importado desde constants.py.
        """
        return texto_ayuda

    # -----------------------
    #     Pestaña Config
    # -----------------------
    def construir_pestaña_config(self):
        """Construye la interfaz de configuración de cuenta, idéntica al script original :contentReference[oaicite:18]{index=18}."""
        marco_cuenta = ttk.LabelFrame(self.marco_config, text="Plantilla de Cuenta", padding=15)
        marco_cuenta.pack(fill=tk.X, pady=10)

        ttk.Label(marco_cuenta, text="Archivo de Plantilla:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_cuenta = ttk.Entry(marco_cuenta, textvariable=self.var_cuenta_analisis, width=40, state='readonly')
        self.entry_cuenta.grid(row=0, column=1, padx=5, pady=5)

        btn_cargar = ttk.Button(marco_cuenta, text="📂 Cargar Plantilla", command=self.cargar_plantilla_desde_archivo)
        btn_cargar.grid(row=0, column=2, padx=5)

        marco_parametros = ttk.LabelFrame(self.marco_config, text="Parámetros de la Cuenta", padding=15)
        marco_parametros.pack(fill=tk.BOTH, expand=True, pady=10)

        # Crear un marco para los parámetros
        self.entradas_parametros = {}
        definiciones_parametros = [
            ('TAMAÑO_CUENTA', '🏦 Tamaño de Cuenta ($)', 0, 0, 2),  # Añadido columnspan=2 para ocupar toda la fila
            ('OBJETIVO_GANANCIA', '🎯 Objetivo de Ganancia ($)', 1, 0),
            ('OBJETIVO_PORC', '🎯 Objetivo de Ganancia (%)', 1, 2),
            ('DRAWDOWN_MAX', '💥 Drawdown Máximo ($)', 2, 0),
            ('DRAWDOWN_MAX_PORC', '💣 Drawdown Máximo (%)', 2, 2),
            ('UMBRAL_PAGO', '📤 Umbral de Pago ($)', 3, 0),
            ('PAGO_MAXIMO', '🤑 Retiro Máximo ($)', 3, 2),
            ('DIAS_PRUEBA', '📅 Días de Prueba', 4, 0),
            ('TIPO_DRAWDOWN', '💫 Tipo de Drawdown', 4, 2)
        ]

        # Título principal para la primera fila
        ttk.Label(marco_parametros, 
             text="🏦 Tamaño de Cuenta ($)",  
             font=("Segoe UI", 14, "bold"),
             anchor="center").grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        # Entrada para el tamaño de cuenta con estilo especial
        var = tk.StringVar()
        var.set(str(self.config_cuenta.get('TAMAÑO_CUENTA', '')))
        entrada = ttk.Entry(marco_parametros, 
                  textvariable=var, 
                  width=30,  # Mayor ancho
                  font=("Segoe UI", 12),  # Fuente más grande
                  justify="center",
                  state='readonly')
        entrada.grid(row=0, column=2, columnspan=2, pady=5, padx=10, sticky="ew")
        self.entradas_parametros['TAMAÑO_CUENTA'] = var

        # Resto de parámetros
        for param, etiqueta, fila, columna in definiciones_parametros[1:]:  # Empezar desde el segundo elemento
            ttk.Label(marco_parametros, text=etiqueta).grid(row=fila, column=columna, sticky=tk.W, padx=5, pady=5)
            var = tk.StringVar()
            var.set(str(self.config_cuenta.get(param, '')))
            entrada = ttk.Entry(marco_parametros, textvariable=var, width=15, state='readonly')
            entrada.grid(row=fila, column=columna + 1, sticky=tk.W, padx=5, pady=5)
            self.entradas_parametros[param] = var


        self.marco_estado_reglas = ttk.LabelFrame(self.marco_config, text="Estado de Reglas de la Plantilla", padding=15)
        self.marco_estado_reglas.pack(fill=tk.BOTH, expand=True, pady=10)
        ttk.Label(self.marco_estado_reglas, text="Analice operaciones para ver estado real.").pack()


    def cargar_plantilla_desde_archivo(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar plantilla de cuenta",
            filetypes=[("Archivos JSON", "*.json")]
        )
        
        if not ruta_archivo:
            return

        try:
            data = ConfigManager.cargar_plantilla(os.path.basename(ruta_archivo))

            reglas_crudas = data.get('reglas', {})

            # Si no hay reglas, usar las reglas estándar
            self.reglas_por_defecto = []


            # Adaptar formato de reglas a estructura extendida
            def adaptar_regla(clave, nombre_legible, valor_defecto):
                valor_crudo = reglas_crudas.get(clave, valor_defecto)

                # Si ya viene estructurado
                if isinstance(valor_crudo, dict) and 'valor' in valor_crudo:
                    valor = valor_crudo['valor']
                else:
                    valor = valor_crudo

                # Convertir el tipo adecuadamente
                if isinstance(valor, str):
                    valor = valor.strip()
                    if valor.lower() in ['true', 'false']:
                        valor = valor.lower() == 'true'
                    else:
                        try:
                            valor = int(valor) if valor.isdigit() else float(valor)
                        except ValueError:
                            pass  # mantener como string si no se puede convertir
                    
                # Detectar si vino por defecto
                reglas = {}
                self.reglas_por_defecto = []

                for clave, (nombre_legible, valor_defecto) in REGLAS_ESTANDARD.items():
                    valor_crudo = reglas_crudas.get(clave, valor_defecto)

                    if isinstance(valor_crudo, dict) and 'valor' in valor_crudo:
                        valor = valor_crudo['valor']
                    else:
                        valor = valor_crudo

                    # Convertir tipo
                    if isinstance(valor, str):
                        valor = valor.strip()
                        if valor.lower() in ['true', 'false']:
                            valor = valor.lower() == 'true'
                        else:
                            try:
                                valor = int(valor) if valor.isdigit() else float(valor)
                            except ValueError:
                                pass

                    # Detectar si vino por defecto
                    if clave not in reglas_crudas:
                        self.reglas_por_defecto.append(clave)

                    reglas[clave] = {
                        'nombre': nombre_legible,
                        'valor': valor
                    }


            # Reglas estándar esperadas con nombre legible (y ahora con emojis) y valor por defecto
            REGLAS_ESTANDARD = {
                'RATIO_SL_PIPS': ('🛡️ Stop Loss (pips)', 10),
                'RATIO_TP_PIPS': ('🎯 Take Profit (pips)', 15),
                'HORARIO_INICIO': ('🕒 Horario de Inicio', '08:00'),
                'HORARIO_FIN': ('🕔 Horario de Cierre', '16:00'),
                'STOP_LOSS_OBLIGATORIO': ('🛑 Stop Loss Obligatorio', False),
                'PERDIDA_DIARIA_MAX': ('💥 Pérdida Diaria Máxima (%)', 5),
                'PERDIDA_SEMANAL_MAX': ('🔻 Pérdida Semanal Máxima (%)', 10),
                'PERDIDAS_CONSECUTIVAS_MAX': ('📉 Pérdidas Consecutivas Máx.', 7),
                'DIAS_OPERANDO_MIN': ('📆 Mínimo de Días Operando', 5),
                'GANANCIA_DIARIA_MAX_PORC': ('📈 Ganancia Diaria Máx. (%)', 70),
                'MULTIPLICADOR_CONTRATOS_MAX': ('📊 Multiplicador de Contratos', 3),
                'CONSISTENCIA': ('📌 Porcentaje de Consistencia (%)', 50),
            }

            # Inyectar claves huérfanas al bloque de reglas
            mapa_claves = {
                'porcentaje_consistencia': 'CONSISTENCIA',
                'ganancia_diaria_maxima': 'GANANCIA_DIARIA_MAX_PORC',
                'dias_minimos_operados': 'DIAS_OPERANDO_MIN',
                'perdidas_consecutivas_maxima': 'PERDIDAS_CONSECUTIVAS_MAX',
                'perdida_diaria_maxima': 'PERDIDA_DIARIA_MAX',
                'perdida_semanal_maxima': 'PERDIDA_SEMANAL_MAX',
                'contratos_maximos': 'MULTIPLICADOR_CONTRATOS_MAX',
                'ratio_tp_pips': 'RATIO_TP_PIPS',
                'ratio_sl_pips': 'RATIO_SL_PIPS',
                'uso_stop_loss_obligatorio': 'STOP_LOSS_OBLIGATORIO',
            }

            # Horarios especiales
            if 'horario_operacion' in reglas_crudas:
                if 'inicio' in reglas_crudas['horario_operacion']:
                    reglas_crudas['HORARIO_INICIO'] = reglas_crudas['horario_operacion']['inicio']
                if 'fin' in reglas_crudas['horario_operacion']:
                    reglas_crudas['HORARIO_FIN'] = reglas_crudas['horario_operacion']['fin']

            for clave_origen, clave_destino in mapa_claves.items():
                if clave_origen in reglas_crudas and clave_destino not in reglas_crudas:
                    reglas_crudas[clave_destino] = reglas_crudas[clave_origen]
                    del reglas_crudas[clave_origen]


            # Reconstruir todas las reglas garantizadas
            reglas = {}
            for clave, (nombre_legible, valor_defecto) in REGLAS_ESTANDARD.items():
                valor = reglas_crudas.get(clave, valor_defecto)
                if isinstance(valor, dict) and 'valor' in valor:
                    reglas[clave] = valor
                else:
                    reglas[clave] = {'nombre': nombre_legible, 'valor': valor}

            self.config_cuenta = {
                'TAMAÑO_CUENTA': data.get('size', 0),
                'OBJETIVO_GANANCIA': reglas_crudas.get('objetivo_usd', 0),
                'OBJETIVO_PORC': reglas_crudas.get('objetivo_ganancia_pct', 0),
                'DRAWDOWN_MAX': reglas_crudas.get('drawdown_usd', 0),
                'DRAWDOWN_MAX_PORC': reglas_crudas.get('drawdown_maximo_pct', 0),
                'UMBRAL_PAGO': reglas_crudas.get('umbral_pago', 0),
                'PAGO_MAXIMO': reglas_crudas.get('pago_maximo', 0),
                'DIAS_PRUEBA': reglas_crudas.get('dias_prueba', reglas_crudas.get('dias_minimos_operados', 0)),
                'TIPO_DRAWDOWN': reglas_crudas.get('tipo_drawdown', 'Diario'),
                'REGLAS': reglas
            }

            # Guardar la plantilla en memoria
            if self.reglas_por_defecto:
                reglas_nombres = [reglas[clave]['nombre'] for clave in self.reglas_por_defecto]
                lista_nombres = "\n- ".join(reglas_nombres)
                messagebox.showwarning(
                    "Valores por defecto usados",
                    f"Las siguientes reglas no estaban definidas en la plantilla y se usaron con valores por defecto:\n\n- {lista_nombres}\n\nPuedes revisar o actualizar la plantilla si es necesario."
                )
            # Fin de la advertencia
            
            self.cuenta_seleccionada = os.path.basename(ruta_archivo)
            self.var_cuenta.set(self.cuenta_seleccionada)

            for param, var in self.entradas_parametros.items():
                var.set(str(self.config_cuenta.get(param, '')))

            self.var_estado.set(f"Plantilla cargada: {self.cuenta_seleccionada}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la plantilla: {str(e)}")
            self.var_estado.set("Error al cargar plantilla")



    # ----------------------------
    #    Pestaña Análisis Oper.
    # ----------------------------
    def construir_pestaña_analisis(self):
        marco = self.marco_analisis

        # Controles superiores (igual que en original :contentReference[oaicite:20]{index=20})
        control = ttk.Frame(marco, padding=10)
        control.pack(fill=tk.X)

        btn_cargar = ttk.Button(control, text="📂 Cargar Operaciones", command=self.cargar_datos_operaciones)
        btn_cargar.pack(side=tk.LEFT, padx=5)

        btn_verificar = ttk.Button(control, text="✅ Verificar CSV", command=self.verificar_archivo_csv)
        btn_verificar.pack(side=tk.LEFT, padx=5)

        btn_analizar = ttk.Button(control, text="📊 Analizar Operaciones", command=self.analizar_operaciones)
        btn_analizar.pack(side=tk.LEFT, padx=5)

        btn_exportar = ttk.Button(control, text="📝 Exportar a PDF", command=self.exportar_reporte_pdf, style='Exito.TButton')
        btn_exportar.pack(side=tk.LEFT, padx=5)

        ttk.Label(control, text="Cuenta:").pack(side=tk.LEFT, padx=(20, 5))
        self.var_cuenta_analisis = tk.StringVar()
        self.combo_cuenta_analisis = ttk.Combobox(control, textvariable=self.var_cuenta_analisis, state='readonly', width=25)
        self.combo_cuenta_analisis.pack(side=tk.LEFT)

        ttk.Label(control, text="Fecha Inicio:").pack(side=tk.LEFT, padx=(20, 5))
        self.var_fecha.set(datetime.today().strftime('%Y-%m-%d'))
        ttk.Entry(control, textvariable=self.var_fecha, width=12).pack(side=tk.LEFT)

        # Encabezado dinámico
        encabezado = ttk.Frame(marco, padding=5)
        encabezado.pack(fill=tk.X)
        self.label_enc_empresa = ttk.Label(encabezado, text="", style='Titulo.TLabel')
        self.label_enc_empresa.pack()
        self.label_enc_detalle = ttk.Label(encabezado, text="", font=("Segoe UI", 11))
        self.label_enc_detalle.pack()

        # Sub-notebook para resultados
        self.subtabs = ttk.Notebook(marco)
        self.subtabs.pack(fill=tk.BOTH, expand=True)

        self.tab_resumen = ttk.Frame(self.subtabs)
        self.tab_metrica = ttk.Frame(self.subtabs)
        self.tab_timing = ttk.Frame(self.subtabs)

        self.subtabs.add(self.tab_resumen, text="📈 Gráficos Resumen")
        self.subtabs.add(self.tab_metrica, text="📊 Métricas y R:R")
        self.subtabs.add(self.tab_timing, text="⏱️ Tiempo y Distribución")

    def verificar_archivo_csv(self):
        """
        Verifica la integridad de un CSV antes de cargarlo (idéntico al original :contentReference[oaicite:21]{index=21}).
        """
        ruta = filedialog.askopenfilename(
            filetypes=[('Archivos CSV', '*.csv'), ('Todos', '*.*')],
            title="Seleccionar archivo para verificar"
        )
        if not ruta:
            return
        try:
            with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                muestra = f.read(2048)
            delim = csv.Sniffer().sniff(muestra, delimiters=",;").delimiter
            df = pd.read_csv(ruta, sep=delim, encoding='latin1', engine='python')
            df = df.loc[:, ~df.columns.str.match(r'^Unnamed')]
            df = cargar_datos_csv(ruta)
            df = procesar_datos(df, self.config_cuenta)

            faltantes = [c for c in ['cuenta', 'ganancias', 'precio_de_entrada', 'precio_de_salida', 'mercado_pos'] if c not in df.columns]
            if faltantes:
                messagebox.showerror("Error", f"Columnas faltantes: {', '.join(faltantes)}")
                return

            errores = []
            for col in ['ganancias', 'precio_de_entrada', 'precio_de_salida']:
                cnt = df[col].apply(lambda x: validar_numerico(x)).sum()
                if cnt:
                    errores.append(f"{col}: {cnt} errores de conversión")
            for col in ['tiempo_de_entrada', 'tiempo_de_salida']:
                if col in df.columns:
                    cnt = df[col].apply(lambda x: validar_fecha(x)).sum()
                    if cnt:
                        errores.append(f"{col}: {cnt} errores de fecha")
            if errores:
                messagebox.showwarning("Advertencia", "Inconsistencias:\n\n" + "\n".join(errores))
            else:
                messagebox.showinfo("Éxito", "El archivo es válido y puede cargarse.")
        except Exception as e:
            messagebox.showerror("Error", f"Error verificando archivo:\n{e}")

    def cargar_datos_operaciones(self):
        """
        Carga y procesa el CSV, idéntico al bloque original :contentReference[oaicite:22]{index=22}.
        """
        ruta = filedialog.askopenfilename(filetypes=[('CSV', '*.csv'), ('Todos', '*.*')])
        if not ruta:
            return
        try:
            self.var_estado.set("Cargando datos…")
            if self.raiz:
                self.raiz.update()

            df_crudo = cargar_datos_csv(ruta)
            df_proc = procesar_datos(df_crudo, self.config_cuenta)
            self.df = df_proc.copy()
            self.nombre_archivo_csv = os.path.basename(ruta)

            if 'cuenta' in self.df.columns:
                cuentas = sorted(self.df['cuenta'].dropna().unique())
                self.combo_cuenta_analisis.config(values=cuentas)
                if cuentas:
                    self.var_cuenta_analisis.set(cuentas[0])

            if 'tiempo_de_entrada' in self.df.columns and not self.df['tiempo_de_entrada'].isnull().all():
                fecha_min = self.df['tiempo_de_entrada'].min().date()
                self.var_fecha.set(fecha_min.strftime('%Y-%m-%d'))
            else:
                self.var_fecha.set(datetime.now().strftime('%Y-%m-%d'))

            self.var_estado.set(f"Cargado {self.nombre_archivo_csv}: {len(self.df)} operaciones.")
            self.notebook.select(1)
        except Exception as e:
            self.var_estado.set(f"Error cargando datos: {e}")
            self.df = None

    def analizar_operaciones(self):
        """
        Filtra por cuenta, calcula métricas, genera gráficos y despliega estado de reglas, tal como en el original :contentReference[oaicite:23]{index=23}.
        """
        if self.df is None:
            messagebox.showwarning("Advertencia", "No se han cargado datos.")
            return
        cuenta = self.var_cuenta_analisis.get()
        if not cuenta:
            messagebox.showwarning("Advertencia", "Seleccione una cuenta.")
            return
        try:
            if 'tiempo_de_entrada' in self.df.columns:
                self.fecha_inicio = self.df['tiempo_de_entrada'].min().date()
                self.var_fecha.set(self.fecha_inicio.strftime('%Y-%m-%d'))
            else:
                self.fecha_inicio = datetime.now().date()

            df_cuenta = self.df[self.df['cuenta'] == cuenta].copy()
            if df_cuenta.empty:
                messagebox.showwarning("Advertencia", f"No hay operaciones para {cuenta}.")
                return

            self.metricas = TradeModel.calcular_metricas(df_cuenta, self.fecha_inicio, self.config_cuenta)

            # Limpiar sub-pestañas
            for tab in [self.tab_resumen, self.tab_metrica, self.tab_timing]:
                for w in tab.winfo_children():
                    w.destroy()

            self._actualizar_encabezado()

            # Gráficos Resumen
            fig1 = crear_figura_equity_drawdown(df_cuenta, self.config_cuenta, self.colores)
            fig2 = crear_grafico_drawdown_diario(df_cuenta, self.colores)
            self._embeder_figura(self.tab_resumen, fig1)
            self._embeder_figura(self.tab_resumen, fig2)

            # Gráficos Métricas
            fig3 = crear_histograma_ganancias(df_cuenta, self.colores)
            fig4 = crear_grafico_rr(df_cuenta, self.colores)
            self._embeder_figura(self.tab_metrica, fig3)
            self._embeder_figura(self.tab_metrica, fig4)

            # Gráficos Timing
            figs_timing = crear_graficos_timing(df_cuenta, self.colores)
            for f in figs_timing:
                self._embeder_figura(self.tab_timing, f)

            self.var_estado.set(f"Análisis listo: {self.metricas['progress_to_target']:.1f}% al objetivo.")
            self._mostrar_estado_reglas(df_cuenta)
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar:\n{e}")

    def _embeder_figura(self, marco, figura):
        """Crea y empaqueta FigureCanvasTkAgg para la figura dada."""
        canvas = tk.Canvas(marco, bg=self.colores['claro'])
        canvas.pack(fill=tk.BOTH, expand=True)
        fc = FigureCanvasTkAgg(figura, master=marco)
        fc.draw()
        fc.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _actualizar_encabezado(self):
        """Actualiza el encabezado de la pestaña Análisis (idéntico al original)."""
        self.label_enc_empresa.config(text=f"📊 Análisis de Desempeño - {self.nombre_empresa}")
        cuenta = self.var_cuenta_analisis.get()
        fecha = self.var_fecha.get()
        self.label_enc_detalle.config(text=f"Cuenta: {cuenta} | Inicio: {fecha}")

    def _mostrar_estado_reglas(self, df_cuenta):
        """
        Despliega el estado de cada regla (fatal/crítico/importante/operativa) en la pestaña Configuración,
        tal cual estaba en el original :contentReference[oaicite:24]{index=24}.
        """
        for w in self.marco_estado.winfo_children():
            w.destroy()

        reglas = self.config_cuenta.get('REGLAS', {})
        if not reglas:
            ttk.Label(self.marco_estado, text="⚠️ No hay reglas definidas.").pack(pady=20)
            return

        categorias = {
            'fatal':     ttk.LabelFrame(self.marco_estado, text="💀 Reglas Fatales", padding=10),
            'critico':   ttk.LabelFrame(self.marco_estado, text="🚨 Reglas Críticas", padding=10),
            'importante':ttk.LabelFrame(self.marco_estado, text="⚠️ Reglas Importantes", padding=10),
            'operativa': ttk.LabelFrame(self.marco_estado, text="📊 Reglas Operativas", padding=10)
        }
        for cat in categorias.values():
            cat.pack(fill=tk.X, padx=10, pady=5)

        reglas_por_categoria = {
            'fatal':     ['TRAILING_DRAWDOWN', 'LIMITE_CONTRATOS', 'OVERNIGHT_POSITIONS'],
            'critico':   ['PERDIDA_DIARIA_MAX', 'PERDIDA_SEMANAL_MAX', 'PERDIDAS_CONSECUTIVAS_MAX'],
            'importante':['STOP_LOSS_OBLIGATORIO', 'RATIO_SL_PIPS', 'RATIO_TP_PIPS', 'HORARIO_INICIO', 'HORARIO_FIN'],
            'operativa': ['DIAS_OPERANDO_MIN', 'GANANCIA_DIARIA_MAX_PORC', 'MULTIPLICADOR_CONTRATOS_MAX', 'CONSISTENCIA']
        }

        for categoria, claves in reglas_por_categoria.items():
            marco_cat = categorias[categoria]
            for clave in claves:
                if clave not in reglas:
                    reglas[clave] = {'nombre': clave, 'valor': 0}

                nombre_leg = reglas[clave].get('nombre', clave)
                limite = reglas[clave].get('valor', 0)
                try:
                    valor_real = self._calcular_valor_real(clave, df_cuenta) if not df_cuenta.empty else None
                except:
                    valor_real = None

                estado_ok = True
                mensaje = ""
                if valor_real is not None:
                    if categoria == 'fatal':
                        if clave == 'TRAILING_DRAWDOWN':
                            balance_min = self.config_cuenta['TAMAÑO_CUENTA'] - limite
                            if df_cuenta['pnl_acum'].min() < balance_min:
                                estado_ok = False
                                mensaje = f"Balance bajo mínimo: {df_cuenta['pnl_acum'].min():.2f}"
                        elif clave == 'LIMITE_CONTRATOS':
                            max_c = df_cuenta['parametros_operativos'].apply(lambda x: x['VALOR_PUNTO']).sum()
                            if max_c > limite:
                                estado_ok = False
                                mensaje = f"Exceso contratos totales: {max_c}"
                        elif clave == 'OVERNIGHT_POSITIONS':
                            conteo = df_cuenta[df_cuenta['hora_operacion'] < '09:30'].shape[0]
                            if conteo > 0:
                                estado_ok = False
                                mensaje = f"Posiciones Overnight: {conteo}"
                    elif categoria == 'critico':
                        if valor_real > limite:
                            estado_ok = False
                            mensaje = f"Excedido: {valor_real}"
                    elif categoria == 'importante':
                        if clave in ['STOP_LOSS_OBLIGATORIO', 'RATIO_SL_PIPS', 'RATIO_TP_PIPS']:
                            if valor_real > 0:
                                estado_ok = False
                                mensaje = f"{valor_real} violaciones"
                        elif clave in ['HORARIO_INICIO', 'HORARIO_FIN']:
                            if valor_real > 0:
                                estado_ok = False
                                mensaje = f"{valor_real} ops fuera de horario"
                    elif categoria == 'operativa':
                        if clave == 'DIAS_OPERANDO_MIN':
                            if valor_real < limite:
                                estado_ok = False
                                mensaje = f"{valor_real}/{limite} días"
                        elif valor_real > limite:
                            estado_ok = False
                            mensaje = f"{valor_real} > {limite}"

                marco_linea = ttk.Frame(marco_cat)
                marco_linea.pack(fill=tk.X, pady=2)
                color = self.colores['exito'] if estado_ok else self.colores['peligro']
                icono = "✅" if estado_ok else "❌"
                texto = f"{icono} {nombre_leg}"
                if valor_real is not None:
                    texto += f": {valor_real}"
                texto += f" (Límite: {limite})"
                lbl = ttk.Label(marco_linea, text=texto, foreground=color)
                lbl.pack(side=tk.LEFT)
                if mensaje:
                    ttk.Label(marco_linea, text=f"⚠️ {mensaje}", foreground=self.colores['peligro']).pack(side=tk.LEFT, padx=(10,0))

    def _calcular_valor_real(self, clave, df):
        """
        Calcula el valor real de la regla `clave` basándose en el DataFrame de operaciones.
        Copiado textualmente de `jota_capital_tracker.py` :contentReference[oaicite:25]{index=25}.
        """
        try:
            if clave == 'PERDIDA_DIARIA_MAX':
                diario = df.groupby(df['tiempo_de_entrada'].dt.date)['ganancias'].sum()
                return abs(diario.min()) if not diario.empty else 0
            if clave == 'PERDIDA_SEMANAL_MAX':
                semanal = df.resample('W', on='tiempo_de_entrada')['ganancias'].sum()
                return abs(semanal.min()) if not semanal.empty else 0
            if clave == 'PERDIDAS_CONSECUTIVAS_MAX':
                return df['loss_streak'].max() if 'loss_streak' in df.columns else 0
            if clave == 'GANANCIA_DIARIA_MAX_PORC':
                diario = df.groupby(df['tiempo_de_entrada'].dt.date)['ganancias'].sum()
                base = self.config_cuenta.get('TAMAÑO_CUENTA', 1)
                return (diario.max() / base) * 100 if not diario.empty and base else 0
            if clave == 'CONSISTENCIA':
                wins_dia = df.groupby(df['tiempo_de_entrada'].dt.date)['resultado'].mean() * 100
                return wins_dia.mean() if not wins_dia.empty else 0
            if clave == 'STOP_LOSS_OBLIGATORIO':
                return self.metricas.get('sl_violations', 0)
            if clave == 'DIAS_OPERANDO_MIN':
                return df['tiempo_de_entrada'].dt.date.nunique() if 'tiempo_de_entrada' in df.columns else 0
            if clave == 'RATIO_SL_PIPS':
                if 'sl_deviation' in df.columns:
                    return int((df['sl_deviation'] > 0.25).sum())
            if clave == 'RATIO_TP_PIPS':
                if 'tp_deviation' in df.columns:
                    return int((df['tp_deviation'] > 0.25).sum())
            if clave in ('HORARIO_INICIO', 'HORARIO_FIN'):
                return int(self.metricas.get('fuera_horario_count', 0))
            if clave == 'MULTIPLICADOR_CONTRATOS_MAX':
                return df['parametros_operativos'].apply(lambda x: x['VALOR_PUNTO']).max() if 'parametros_operativos' in df.columns else 0
            if clave == 'TRAILING_DRAWDOWN':
                return df['pnl_acum'].min() if 'pnl_acum' in df.columns else 0
            if clave == 'LIMITE_CONTRATOS':
                return df['parametros_operativos'].apply(lambda x: x['VALOR_PUNTO']).sum() if 'parametros_operativos' in df.columns else 0
            if clave == 'OVERNIGHT_POSITIONS':
                if 'hora_operacion' in df.columns:
                    return int((df['hora_operacion'] < '09:30').sum())
                return 0
        except Exception:
            return 0
        return 0

    def exportar_reporte_pdf(self):
        """
        Llamado al botón “Exportar a PDF”. Invoca `utils/report_utils.exportar_reporte_pdf`.
        """
        cuenta = self.var_cuenta_analisis.get()
        if not cuenta:
            messagebox.showwarning("Advertencia", "Seleccione una cuenta antes de exportar.")
            return
        exportar_reporte_pdf(
            self.metricas,
            self.config_cuenta,
            self.nombre_empresa,
            cuenta,
            self.fecha_inicio,
            self.raiz
        )

    def al_cerrar(self):
        """
        Al cerrar la ventana principal:
          - Detiene hilos
          - Cierra figuras de matplotlib
          - Destruye la ventana (idéntico al original :contentReference[oaicite:26]{index=26}).
        """
        try:
            if hasattr(self, 'threads'):
                for t in self.threads:
                    t.stop()
            plt.close('all')
            self.raiz.quit()
            self.raiz.destroy()
        except Exception as e:
            print(f"Error durante el cierre: {e}")
        finally:
            os._exit(0)

if __name__ == "__main__":
    app = None
    try:
        app = JotaCapitalTracker()
        app.raiz.mainloop()
    except KeyboardInterrupt:
        print("Interrupción por teclado, cerrando…")
        if app:
            app.al_cerrar()
    except Exception as e:
        print(f"Error inesperado: {e}")
        if app:
            app.al_cerrar()
    finally:
        print("Aplicación cerrada correctamente.")
