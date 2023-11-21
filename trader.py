import json
import random
import os
import argparse
from datetime import datetime


class CurrencyTrader:
    def __init__(self):
        self.load_config()
        self.load_state()

    def load_config(self):
        with open("config.json", "r") as config_file:
            self.config = json.load(config_file)

    def load_state(self):
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
        with open("state.json", "w") as state_file:
            json.dump(self.state, state_file, indent=2)

    def get_current_rate(self):
        return round(random.uniform(
            self.config["rate"] - self.config["delta"],
            self.config["rate"] + self.config["delta"]
        ), 2)

    def execute_command(self, args):
        command = args.command
        if command == "NEXT":
            new_rate = self.get_current_rate()
            self.state["rate"] = new_rate
            self.state["history"].append({"timestamp": str(datetime.now()), "event": "Rate changed", "rate": new_rate})
            self.save_state()
        elif command == "RATE":
            print(self.state["rate"])
        elif command == "BUY ALL":
            self.buy_usd(self.state["balance_uah"])
        elif command.startswith("BUY "):
            amount = float(command.split(" ")[1])
            self.buy_usd(amount)
        elif command == "SELL ALL":
            self.sell_usd(self.state["balance_usd"])
        elif command.startswith("SELL "):
            amount = float(command.split(" ")[1])
            self.sell_usd(amount)
        elif command == "AVAILABLE":
            self.print_available_balances()
        elif command == "RESTART":
            self.restart_game()
        else:
            print("Невідома команда.")

    def buy_usd(self, amount):
        cost = amount / self.state["rate"]
        if cost <= self.state["balance_uah"]:
            self.state["balance_uah"] -= cost
            self.state["balance_usd"] += amount
            self.state["history"].append({"timestamp": str(datetime.now()), "event": "USD bought", "amount": amount})
            self.save_state()
        else:
            print(f"UNAVAILABLE: REQUIRED BALANCE UAH {cost:.2f}, AVAILABLE {self.state['balance_uah']:.2f}")

    def sell_usd(self, amount):
        if amount <= self.state["balance_usd"]:
            income = amount * self.state["rate"]
            self.state["balance_uah"] += income
            self.state["balance_usd"] -= amount
            self.state["history"].append({"timestamp": str(datetime.now()), "event": "USD sold", "amount": amount})
            self.save_state()
        else:
            print(f"UNAVAILABLE: REQUIRED BALANCE USD {amount:.2f}, AVAILABLE {self.state['balance_usd']:.2f}")

    def print_available_balances(self):
        print(f"USD {self.state['balance_usd']:.2f} UAH {self.state['balance_uah']:.2f}")

    def restart_game(self):
        self.state = {
            "rate": self.config["rate"],
            "balance_uah": self.config["initial_balance_uah"],
            "balance_usd": self.config["initial_balance_usd"],
            "history": []
        }
        self.save_state()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Currency trader CLI")
    parser.add_argument("command",
                        choices=["NEXT", "RATE", "BUY", "SELL", "BUY ALL", "SELL ALL", "AVAILABLE", "RESTART"],
                        help="Specify the command to execute.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    trader = CurrencyTrader()
    trader.execute_command(args)
