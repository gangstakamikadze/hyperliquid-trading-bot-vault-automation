import logging
from typing import List, Tuple
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

# Configure logging for reliability
logging.basicConfig(
    filename="trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class OrderBookWidget:
    def __init__(self, bids_table: QTableWidget, asks_table: QTableWidget):
        """Initialize order book widget with bid/ask tables."""
        self.bids_table = bids_table
        self.asks_table = asks_table
        logging.info("OrderBookWidget initialized")

    def update_order_book(self, symbol: str, order_book: dict):
        """Update bid/ask tables with onchain data."""
        try:
            bids: List[Tuple[float, float]] = order_book.get("bids", [])[:5]
            asks: List[Tuple[float, float]] = order_book.get("asks", [])[:5]
            
            self.bids_table.setRowCount(len(bids))
            for i, (price, size) in enumerate(bids):
                self.bids_table.setItem(i, 0, QTableWidgetItem(f"{price:.2f}"))
                self.bids_table.setItem(i, 1, QTableWidgetItem(f"{size:.4f}"))
            
            self.asks_table.setRowCount(len(asks))
            for i, (price, size) in enumerate(asks):
                self.asks_table.setItem(i, 0, QTableWidgetItem(f"{price:.2f}"))
                self.asks_table.setItem(i, 1, QTableWidgetItem(f"{size:.4f}"))
            
            logging.debug(f"Order book updated for {symbol}")
        except Exception as e:
            logging.error(f"Order book update failed: {e}")

# Example usage (incomplete, for demo only)
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QTableWidget
    app = QApplication([])
    bids_table = QTableWidget()
    bids_table.setColumnCount(2)
    bids_table.setHorizontalHeaderLabels(["Price", "Size"])
    asks_table = QTableWidget()
    asks_table.setColumnCount(2)
    asks_table.setHorizontalHeaderLabels(["Price", "Size"])
    widget = OrderBookWidget(bids_table, asks_table)
    # Mock data
    mock_order_book = {
        "bids": [(50000.0, 1.5), (49950.0, 2.0)],
        "asks": [(50100.0, 1.0), (50150.0, 1.8)],
    }
    widget.update_order_book("BTC-USDC", mock_order_book)
    bids_table.show()
    asks_table.show()
    app.exec_()
