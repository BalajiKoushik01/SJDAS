import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QDoubleSpinBox, QGroupBox, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)

from sj_das.core.costing import CostingEngine


class CostingReportDialog(QDialog):
    def __init__(self, color_indices: np.ndarray, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Textile Costing Report")
        self.resize(600, 500)
        self.indices = color_indices
        self.engine = CostingEngine()
        self.init_ui()
        self.calculate()  # Initial calc

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. Inputs
        grp = QGroupBox("Manufacturing Specs")
        glay = QVBoxLayout(grp)

        # Warp Specs
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Warp Denier:"))
        self.spin_warp_den = QDoubleSpinBox()
        self.spin_warp_den.setValue(20.0)  # 20D Silk
        h1.addWidget(self.spin_warp_den)

        h1.addWidget(QLabel("Warp Price (₹/kg):"))
        self.spin_warp_price = QDoubleSpinBox()
        self.spin_warp_price.setRange(0, 100000)
        self.spin_warp_price.setValue(6000.0)
        h1.addWidget(self.spin_warp_price)
        glay.addLayout(h1)

        # Weft Specs (Simplified Average for now)
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Avg Weft Denier:"))
        self.spin_weft_den = QDoubleSpinBox()
        self.spin_weft_den.setValue(40.0)
        h2.addWidget(self.spin_weft_den)

        h2.addWidget(QLabel("Avg Weft Price (₹/kg):"))
        self.spin_weft_price = QDoubleSpinBox()
        self.spin_weft_price.setRange(0, 100000)
        self.spin_weft_price.setValue(4500.0)
        h2.addWidget(self.spin_weft_price)
        glay.addLayout(h2)

        # Dimensions
        h3 = QHBoxLayout()
        self.spin_width = QDoubleSpinBox()
        self.spin_width.setValue(45)  # 45 inches
        h3.addWidget(QLabel("Width (in):"))
        h3.addWidget(self.spin_width)

        self.spin_ppi = QDoubleSpinBox()
        self.spin_ppi.setValue(60)
        h3.addWidget(QLabel("PPI:"))
        h3.addWidget(self.spin_ppi)
        glay.addLayout(h3)

        layout.addWidget(grp)

        # Trigger
        btn_calc = QPushButton("Update Calculation")
        btn_calc.clicked.connect(self.calculate)
        layout.addWidget(btn_calc)

        # 2. Results
        self.result_table = QTableWidget(3, 3)
        self.result_table.setHorizontalHeaderLabels(
            ["Item", "Weight (kg)", "Cost (₹)"])
        layout.addWidget(self.result_table)

        self.lbl_total = QLabel("<h2>Total Saree Cost: ₹0.00</h2>")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_total)

    def calculate(self):
        h, w = self.indices.shape
        # Use Engine
        specs = {
            'width_inches': self.spin_width.value(),
            'ppi': self.spin_ppi.value(),
            'epi': 72,  # Assume standard
            'warp_denier': self.spin_warp_den.value(),
            'weft_denier': self.spin_weft_den.value(),
            'warp_price': self.spin_warp_price.value(),
            'weft_price': self.spin_weft_price.value()
        }

        # Pass dimensions (w=Hooks, h=Picks)
        res = self.engine.calculate_cost(w, h, specs)

        if res.get('success'):
            c = res['consumption']
            cost = res['cost']

            # Update UI
            items = [
                ("Warp Yarn", c['warp_kg'], cost['warp_cost']),
                ("Weft Yarn", c['weft_kg'], cost['weft_cost']),
                ("Total", c['total_kg'], cost['total_cost'])
            ]

            for i, (name, wt, pr) in enumerate(items):
                self.result_table.setItem(i, 0, QTableWidgetItem(name))
                self.result_table.setItem(i, 1, QTableWidgetItem(str(wt)))
                self.result_table.setItem(i, 2, QTableWidgetItem(str(pr)))

            self.lbl_total.setText(
                f"<h2>Total Saree Cost using AI: {cost['total_cost']}</h2>")
