# configurator.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QDoubleSpinBox, QSpinBox,
    QListWidget, QListWidgetItem, QGroupBox, QMessageBox, QTimeEdit,
    QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, QTime, QObject, QEvent
import typing
import sys
import os
import json
from config_manager import ConfigManager

# Clase para manejar la configuración de empresas y plantillas
from constants import ACCOUNT_SIZES, ACCOUNT_TYPES

class Configurator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠 Constructor de Plantillas")
        self.resize(600, 700)
        self.current_template = None
        self.init_ui()
        self._load_initial_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Empresa
        empresa_layout = QHBoxLayout()
        empresa_label = QLabel("Empresa:")
        self.empresa_combo = QComboBox()
        self.empresa_combo.setEditable(True)
        self.empresa_combo.setToolTip("Nombre de la empresa o firma de trading")
        empresa_layout.addWidget(empresa_label)
        empresa_layout.addWidget(self.empresa_combo)
        layout.addLayout(empresa_layout)

        # Tamaño de cuenta
        size_layout = QHBoxLayout()
        size_label = QLabel("Tamaño de cuenta (USD):")
        self.size_combo = QComboBox()
        for name, value in ACCOUNT_SIZES.items():
            self.size_combo.addItem(f"{name} (${value})", value)
        self.size_combo.setToolTip("Capital total de la cuenta")
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        layout.addLayout(size_layout)

        # Tipo de cuenta
        type_layout = QHBoxLayout()
        type_label = QLabel("Tipo de cuenta:")
        self.type_list = QListWidget()
        self.type_list.addItems(ACCOUNT_TYPES)
        self.type_list.setSelectionMode(QListWidget.SingleSelection)
        self.type_list.setToolTip("Selecciona un tipo de cuenta")
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_list)
        layout.addLayout(type_layout)

        # Reglas
        rules_group = QGroupBox("Reglas de Trading")
        rules_layout = QVBoxLayout()
        rules_layout.setSpacing(10)

        # Objetivo porcentaje
        self.objetivo_spin = QDoubleSpinBox()
        self.objetivo_spin.setSuffix(" %")
        self.objetivo_spin.setRange(0, 100)
        self.objetivo_spin.setToolTip("Porcentaje de ganancia objetivo")
        self.objetivo_spin.setValue(6.0)
        rules_layout.addWidget(QLabel("Objetivo (%) :"))
        rules_layout.addWidget(self.objetivo_spin)

        # Objetivo USD
        self.objetivo_usd_spin = QDoubleSpinBox()
        self.objetivo_usd_spin.setPrefix("$")
        self.objetivo_usd_spin.setRange(0, 1000000)
        self.objetivo_usd_spin.setToolTip("Ganancia objetivo en dólares")
        self.objetivo_usd_spin.setValue(3000.0)
        rules_layout.addWidget(QLabel("Objetivo USD :"))
        rules_layout.addWidget(self.objetivo_usd_spin)

        # Drawdown %
        self.drawdown_spin = QDoubleSpinBox()
        self.drawdown_spin.setSuffix(" %")
        self.drawdown_spin.setRange(0, 100)
        self.drawdown_spin.setToolTip("Máximo drawdown permitido en porcentaje")
        self.drawdown_spin.setValue(5.0)
        rules_layout.addWidget(QLabel("Drawdown (%) :"))
        rules_layout.addWidget(self.drawdown_spin)

        # Drawdown USD
        self.drawdown_usd_spin = QDoubleSpinBox()
        self.drawdown_usd_spin.setPrefix("$")
        self.drawdown_usd_spin.setRange(0, 100000)
        self.drawdown_usd_spin.setToolTip("Máximo drawdown permitido en USD")
        self.drawdown_usd_spin.setValue(2500.0)
        rules_layout.addWidget(QLabel("Drawdown USD :"))
        rules_layout.addWidget(self.drawdown_usd_spin)

        # Umbral de pago
        self.umbral_pago_spin = QDoubleSpinBox()
        self.umbral_pago_spin.setPrefix("$")
        self.umbral_pago_spin.setRange(0, 100000)
        self.umbral_pago_spin.setToolTip("Umbral mínimo para solicitar retiro")
        self.umbral_pago_spin.setValue(1600.0)
        rules_layout.addWidget(QLabel("Umbral de Pago :"))
        rules_layout.addWidget(self.umbral_pago_spin)

        # Pago máximo
        self.pago_maximo_spin = QDoubleSpinBox()
        self.pago_maximo_spin.setPrefix("$")
        self.pago_maximo_spin.setRange(0, 50000)
        self.pago_maximo_spin.setToolTip("Máximo que se puede retirar")
        self.pago_maximo_spin.setValue(1000.0)
        rules_layout.addWidget(QLabel("Pago Máximo :"))
        rules_layout.addWidget(self.pago_maximo_spin)

        # Pérdida diaria máxima
        self.perdida_diaria_spin = QDoubleSpinBox()
        self.perdida_diaria_spin.setSuffix(" %")
        self.perdida_diaria_spin.setRange(0, 100)
        self.perdida_diaria_spin.setToolTip("Pérdida diaria máxima permitida")
        self.perdida_diaria_spin.setValue(1.0)
        rules_layout.addWidget(QLabel("Pérdida Diaria (%) :"))
        rules_layout.addWidget(self.perdida_diaria_spin)

        # Pérdida semanal máxima
        self.perdida_semanal_spin = QDoubleSpinBox()
        self.perdida_semanal_spin.setSuffix(" %")
        self.perdida_semanal_spin.setRange(0, 100)
        self.perdida_semanal_spin.setToolTip("Pérdida semanal máxima permitida")
        self.perdida_semanal_spin.setValue(3.0)
        rules_layout.addWidget(QLabel("Pérdida Semanal (%) :"))
        rules_layout.addWidget(self.perdida_semanal_spin)

        # Ganancia diaria máxima
        self.ganancia_diaria_spin = QDoubleSpinBox()
        self.ganancia_diaria_spin.setSuffix(" %")
        self.ganancia_diaria_spin.setRange(0, 100)
        self.ganancia_diaria_spin.setToolTip("Ganancia diaria máxima permitida")
        self.ganancia_diaria_spin.setValue(2.0)
        rules_layout.addWidget(QLabel("Ganancia Diaria (%) :"))
        rules_layout.addWidget(self.ganancia_diaria_spin)

        # Días mínimos operados
        self.dias_minimos_spin = QSpinBox()
        self.dias_minimos_spin.setSuffix(" días")
        self.dias_minimos_spin.setRange(1, 90)
        self.dias_minimos_spin.setToolTip("Días mínimos necesarios para evaluación")
        self.dias_minimos_spin.setValue(5)
        rules_layout.addWidget(QLabel("Días Mínimos Operados :"))
        rules_layout.addWidget(self.dias_minimos_spin)

        # Días de prueba
        self.dias_prueba_spin = QSpinBox()
        self.dias_prueba_spin.setSuffix(" días")
        self.dias_prueba_spin.setRange(1, 365)
        self.dias_prueba_spin.setToolTip("Duración del periodo de prueba")
        self.dias_prueba_spin.setValue(60)
        rules_layout.addWidget(QLabel("Días de Prueba :"))
        rules_layout.addWidget(self.dias_prueba_spin)

        # Porcentaje de consistencia
        self.consistencia_spin = QDoubleSpinBox()
        self.consistencia_spin.setSuffix(" %")
        self.consistencia_spin.setRange(0, 100)
        self.consistencia_spin.setToolTip("Porcentaje de consistencia requerida")
        self.consistencia_spin.setValue(30.0)
        rules_layout.addWidget(QLabel("Consistencia (%) :"))
        rules_layout.addWidget(self.consistencia_spin)

        # Contratos máximos
        self.contratos_maximos_spin = QSpinBox()
        self.contratos_maximos_spin.setSuffix(" contratos")
        self.contratos_maximos_spin.setRange(1, 10)
        self.contratos_maximos_spin.setToolTip("Máximo número de contratos permitidos")
        self.contratos_maximos_spin.setValue(3)
        rules_layout.addWidget(QLabel("Contratos Máximos :"))
        rules_layout.addWidget(self.contratos_maximos_spin)

        # Horario operativo
        horario_layout = QHBoxLayout()
        self.horario_inicio = QTimeEdit()
        self.horario_inicio.setToolTip("Hora de inicio permitida para operar")
        self.horario_inicio.setTime(QTime(8, 30))
        self.horario_fin = QTimeEdit()
        self.horario_fin.setToolTip("Hora final permitida para operar")
        self.horario_fin.setTime(QTime(15, 55))
        horario_layout.addWidget(QLabel("Horario Inicio:"))
        horario_layout.addWidget(self.horario_inicio)
        horario_layout.addWidget(QLabel("Horario Fin:"))
        horario_layout.addWidget(self.horario_fin)
        rules_layout.addLayout(horario_layout)

        # Stop Loss obligatorio
        self.stop_loss_check = QCheckBox("Uso de Stop Loss obligatorio")
        self.stop_loss_check.setToolTip("Requerir uso de stop loss en cada operación")
        rules_layout.addWidget(self.stop_loss_check)

        # Ratio TP/SL
        ratio_box = QGroupBox("Ratio Riesgo/Recompensa")
        ratio_layout = QHBoxLayout()
        ratio_layout.setSpacing(8)

        self.tp_spin = QDoubleSpinBox()
        self.tp_spin.setSuffix(" pips")
        self.tp_spin.setRange(0, 1000)
        self.tp_spin.setValue(45)
        self.tp_spin.setToolTip("Take Profit en pips")

        self.sl_spin = QDoubleSpinBox()
        self.sl_spin.setSuffix(" pips")
        self.sl_spin.setRange(0, 500)
        self.sl_spin.setValue(15)
        self.sl_spin.setToolTip("Stop Loss en pips")

        ratio_info = QPushButton("ℹ️")
        ratio_info.setFixedSize(25, 25)
        ratio_info.setToolTip("El ratio muestra cuánto se gana por cada unidad de riesgo")

        ratio_layout.addWidget(QLabel("TP:"))
        ratio_layout.addWidget(self.tp_spin)
        ratio_layout.addWidget(QLabel(":"))
        ratio_layout.addWidget(QLabel("SL:"))
        ratio_layout.addWidget(self.sl_spin)
        ratio_layout.addWidget(ratio_info)
        ratio_box.setLayout(ratio_layout)
        rules_layout.addWidget(ratio_box)

        # Otras reglas
        extra_rules_layout = QVBoxLayout()
        self.regla_5_check = QCheckBox("Regla 5% de cuenta")
        self.regla_5_check.setToolTip("Permitir arriesgar hasta 5% del capital")
        self.safety_net_check = QCheckBox("Safety Net")
        self.safety_net_check.setToolTip("Activar red de seguridad")
        extra_rules_layout.addWidget(self.regla_5_check)
        extra_rules_layout.addWidget(self.safety_net_check)
        extra_rules_layout.addStretch()
        rules_layout.addLayout(extra_rules_layout)

        layout.addWidget(rules_group)

        # Botones
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Guardar Plantilla")
        self.save_btn.clicked.connect(self._validate_all)
        self.save_btn.setEnabled(False)
        cancel_btn = QPushButton("✖ Cancelar")
        cancel_btn.clicked.connect(lambda: (self.close(), None)[1])
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _load_initial_data(self):
        empresas = ConfigManager.cargar_empresas()
        self.empresa_combo.addItems(empresas)

    def _validate_all(self) -> None:
        nombre_empresa = self.empresa_combo.currentText().strip()
        if not nombre_empresa:
            return
        if not self.type_list.selectedItems():
            return
        self.save_btn.setEnabled(True)

    def eventFilter(self, a0: typing.Optional['QObject'], a1: typing.Optional['QEvent']) -> bool:
        self._validate_all()
        return super().eventFilter(a0, a1)

    def _on_save(self):
        if not self.save_btn.isEnabled():
            QMessageBox.warning(self, "Error", "Verifica la configuración: campos requeridos o inconsistentes.")
            return

        try:
            selected_type_items = self.type_list.selectedItems()
            if not selected_type_items:
                raise ValueError("No se seleccionó un tipo de cuenta válido.")

            config = {
                "empresa": self.empresa_combo.currentText().strip(),
                "size": self.size_combo.currentData(),
                "types": [item.text() for item in selected_type_items],
                "reglas": {
                    "objetivo_ganancia_pct": self.objetivo_spin.value(),
                    "objetivo_usd": self.objetivo_usd_spin.value(),
                    "drawdown_maximo_pct": self.drawdown_spin.value(),
                    "drawdown_usd": self.drawdown_usd_spin.value(),
                    "umbral_pago": self.umbral_pago_spin.value(),
                    "pago_maximo": self.pago_maximo_spin.value(),
                    "perdida_diaria_maxima": self.perdida_diaria_spin.value(),
                    "perdida_semanal_maxima": self.perdida_semanal_spin.value(),
                    "ganancia_diaria_maxima": self.ganancia_diaria_spin.value(),
                    "dias_minimos_operados": self.dias_minimos_spin.value(),
                    "dias_prueba": self.dias_prueba_spin.value(),
                    "porcentaje_consistencia": self.consistencia_spin.value(),
                    "contratos_maximos": self.contratos_maximos_spin.value(),
                    "horario_operacion": {
                        "inicio": self.horario_inicio.time().toString("HH:mm"),
                        "fin": self.horario_fin.time().toString("HH:mm")
                    },
                    "uso_stop_loss_obligatorio": self.stop_loss_check.isChecked(),
                    "ratio_tp_pips": self.tp_spin.value(),
                    "ratio_sl_pips": self.sl_spin.value(),
                    "regla_5_por_ciento": self.regla_5_check.isChecked(),
                    "regla_safety_net": self.safety_net_check.isChecked()
                }
            }

            tp = self.tp_spin.value()
            sl = self.sl_spin.value()
            ratio = tp / sl if sl > 0 else float('inf')

            filename = f"{config['empresa']}_{int(config['size'])}.json"
            ConfigManager.guardar_plantilla(filename, config)
            QMessageBox.information(
                self, "Éxito",
                f"Plantilla guardada como {filename}\nRatio R/R: {ratio:.2f}:1"
            )
            self.close()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la plantilla: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Configurator()
    window.show()
    sys.exit(app.exec_())