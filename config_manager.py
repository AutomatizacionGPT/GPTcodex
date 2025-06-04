# config_manager.py

import os
import json

class ConfigManager:
    """Gestor de plantillas y configuración de empresas."""

    RUTA_PLANTILLAS = os.path.join(os.path.dirname(__file__), "Plantillas")
    RUTA_EMPRESAS = os.path.join(os.path.dirname(__file__), "empresas.json")

    @staticmethod
    def listar_plantillas():
        """Retorna la lista de nombres de archivos JSON en la carpeta Plantillas."""
        if not os.path.isdir(ConfigManager.RUTA_PLANTILLAS):
            os.makedirs(ConfigManager.RUTA_PLANTILLAS, exist_ok=True)
        return [f for f in os.listdir(ConfigManager.RUTA_PLANTILLAS) if f.endswith(".json")]

    @staticmethod
    def cargar_plantilla(nombre_archivo):
        """
        Carga y retorna el contenido de una plantilla JSON.
        nombre_archivo: solo el nombre con extensión (p.ej. "Express50K.json").
        """
        ruta = os.path.join(ConfigManager.RUTA_PLANTILLAS, nombre_archivo)
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def guardar_plantilla(nombre_archivo, data):
        """
        Guarda un diccionario en formato JSON bajo Plantillas/nombre_archivo.
        Si no existe la carpeta, la crea.
        """
        if not os.path.isdir(ConfigManager.RUTA_PLANTILLAS):
            os.makedirs(ConfigManager.RUTA_PLANTILLAS, exist_ok=True)
        ruta = os.path.join(ConfigManager.RUTA_PLANTILLAS, nombre_archivo)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def cargar_empresas():
        """
        Carga empresas.json y retorna su contenido como dict.
        Si no existe, retorna {}.
        """
        try:
            with open(ConfigManager.RUTA_EMPRESAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def guardar_empresas(data):
        """
        Guarda o actualiza el diccionario de empresas en empresas.json.
        data: dict con la información completa a persistir.
        """
        with open(ConfigManager.RUTA_EMPRESAS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
