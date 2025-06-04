# models/contracts.py
class ContratosManager:
    """
    Administra la lista de contratos y sus parámetros (valor por punto, tamaño del tick, valor del tick).
    Exactamente igual a como estaba en el script original.
    """
    MESES_FUTUROS = {
        1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
        7: "JUL", 8: "AGO", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
    }

    CONTRATOS = [
        {"Símbolo": "MES",  "Valor por Punto": 5,  "Tamaño del Tick": 0.25, "Valor del Tick": 1.25},
        {"Símbolo": "MNQ",  "Valor por Punto": 2,  "Tamaño del Tick": 0.25, "Valor del Tick": 0.50},
        {"Símbolo": "MYM",  "Valor por Punto": 0.5,"Tamaño del Tick": 1,    "Valor del Tick": 0.50},
        {"Símbolo": "M2K",  "Valor por Punto": 5,  "Tamaño del Tick": 0.1,  "Valor del Tick": 0.50},
        {"Símbolo": "ES",   "Valor por Punto": 50, "Tamaño del Tick": 0.25, "Valor del Tick": 12.50},
        {"Símbolo": "NQ",   "Valor por Punto": 20, "Tamaño del Tick": 0.25, "Valor del Tick": 5.00},
        {"Símbolo": "YM",   "Valor por Punto": 5,  "Tamaño del Tick": 1,    "Valor del Tick": 5.00},
        {"Símbolo": "RTY",  "Valor por Punto": 50, "Tamaño del Tick": 0.1,  "Valor del Tick": 5.00}
    ]

    @classmethod
    def obtener_parametros_contrato(cls, instrumento):
        simbolo = instrumento.split()[0]
        for contrato in cls.CONTRATOS:
            if contrato["Símbolo"] == simbolo:
                return {
                    'VALOR_PUNTO': contrato["Valor por Punto"],
                    'TAMAÑO_TICK': contrato["Tamaño del Tick"],
                    'VALOR_TICK': contrato["Valor del Tick"]
                }
        return {
            'VALOR_PUNTO': 5.0,
            'TAMAÑO_TICK': 0.25,
            'VALOR_TICK': 1.25
        }
