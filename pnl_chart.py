import logging
from typing import List
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# Configure logging for transparency
logging.basicConfig(
    filename="trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class PnLChartWidget(QWidget):
    def __init__(self):
        """Initialize the PnL chart widget."""
        super().__init__()
        self.pnl_history: List[float] = []
        self.time_history: List[float] = []
        self.init_ui()
        logging.info("PnLChartWidget initialized")

    def init_ui(self):
        """Set up the chart UI with Matplotlib."""
        layout = QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        logging.debug("PnL chart UI setup complete")

    def update_chart(self, new_pnl: float, new_time: float):
        """Update the PnL chart with new data."""
        try:
            self.pnl_history.append(new_pnl)
            self.time_history.append(new_time)
            if len(self.pnl_history) > 100:  # Limit history
                self.pnl_history.pop(0)
                self.time_history.pop(0)
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(self.time_history, self.pnl_history, "b-", label="PnL")
            ax.set_title("Portfolio PnL Over Time")
            ax.set_xlabel("Time")
            ax.set_ylabel("PnL (USD)")
            ax.legend()
            self.canvas.draw()
            logging.debug(f"PnL chart updated with value ${new_pnl:.2f}")
        except Exception as e:
            logging.error(f"PnL chart update failed: {e}")

# Example usage (incomplete, for demo only)
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import time
    app = QApplication([])
    widget = PnLChartWidget()
    # Mock data
    widget.update_chart(10000.0, time.time())
    widget.update_chart(10200.0, time.time() + 5)
    widget.show()
    app.exec_()
