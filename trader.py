import json
import random
import os
from datetime import datetime

class CurrencyTrader:
    def __init__(self):
        # Ініціалізація класу - завантаження конфігурації та стану системи
        self.load_config()
        self.load_state()

    def load_config(self):
        # Завантаження конфігурації з файлу config.json
        with open("config.json", "r") as config_file:
            self.config = json.load(config_file)

    def load_state(self):
        # Завантаження стану системи з файлу state.json або створення нового, якщо файлу не існує
        if os.path.exists("state.json"):
            with open("state.json", "r") as state_file:
                self.state = json.load(state_file)
        else:
            self.state = {
                "rate": self.config["rate"],
                "balance_uah": self.config["initial_balance_uah"],
                "balance_usd": self.config["initial_balance_usd"],
                "history": []
            }
            self.save_state()

    def save_state(self):
        # Збереження стану системи у файл state.json
        with open("state.json", "w") as state_file:
            json.dump(self.state, state_file, indent=2)

    def get_current_rate(self):
        # Генерація випадкового курсу валют
        return round(random.uniform(
            self.config["rate"] - self.config["delta"],
            self.config["rate"] + self.config["delta"]
        ), 2)

    def execute_command(self, command):
        # Виконання команд користувача
        if command == "NEXT":
            new_rate = self.get_current_rate()
            self.state["rate"] = new_rate
            self.state["history"].append({"timestamp": str(datetime.now()), "event": "Rate changed", "rate": new_rate})
            self.save_state()
        elif command == "RATE":
            print(self.state["rate"])
        # Додавання інших команд (BUY, SELL, AVAILABLE, RESTART і т. д.)

if __name__ == "__main__":
    # Створення екземпляру класу та виконання команд користувача
    trader = CurrencyTrader()
    command = input("Введіть команду: ")
    trader.execute_command(command)
