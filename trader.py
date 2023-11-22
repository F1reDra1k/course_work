import argparse
import json
import random


class Trader:
    def __init__(self, config):
        self.config = config
        self.state = self.load_state()

    def load_state(self):
        try:
            with open('state.json') as state_file:
                state = json.load(state_file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Use default state if file not found or if there's a decoding error
            state = {
                "rate": self.config["rate"],
                "balance_uah": self.config["available_uah"],
                "balance_usd": self.config["available_usd"]
            }

        return state

    def to_dict(self):
        return {
            "rate": self.state["rate"],
            "balance_uah": self.state["balance_uah"],
            "balance_usd": self.state["balance_usd"]
        }

    def save_state(self):
        with open('state.json', 'w') as state_file:
            json.dump(self.to_dict(), state_file, indent=4)

        # Append the current state to the log file
        with open('state_log.txt', 'a') as log_file:
            log_file.write(json.dumps(self.to_dict()) + '\n')

    def generate_new_rate(self):
        current_rate = self.state["rate"]
        delta = self.config["delta"]
        new_rate = round(random.uniform(current_rate - delta, current_rate + delta), 2)
        return new_rate

    def get_balance(self):
        return self.state["balance_uah"], self.state["balance_usd"]

    def display_balance(self):
        balance_uah, balance_usd = self.get_balance()
        print(f"UAH: {balance_uah:.2f}, USD: {balance_usd:.2f}")

    def buy_usd(self, amount):
        required_balance = amount * self.state["rate"]
        if self.state["balance_uah"] >= required_balance:
            self.state["balance_uah"] -= required_balance
            self.state["balance_usd"] += amount
            self.save_state()
            print(f"Successfully bought {amount:.2f} USD.")
        else:
            print(
                f"UNAVAILABLE. REQUIRED BALANCE UAH {required_balance:.2f}, AVAILABLE {self.state['balance_uah']:.2f}")

    def sell_usd(self, amount):
        if self.state["balance_usd"] >= amount:
            self.state["balance_usd"] -= amount
            self.state["balance_uah"] += amount * self.state["rate"]
            self.save_state()
            print(f"Successfully sold {amount:.2f} USD.")
        else:
            print(f"UNAVAILABLE. REQUIRED BALANCE USD {amount:.2f}, AVAILABLE {self.state['balance_usd']:.2f}")

    def buy_all(self):
        max_usd_to_buy = self.state["balance_uah"] / self.state["rate"]
        self.buy_usd(max_usd_to_buy)

    def sell_all(self):
        self.sell_usd(self.state["balance_usd"])

    def next_rate(self):
        new_rate = self.generate_new_rate()
        self.state["rate"] = new_rate
        self.save_state()
        print(f"New rate: {new_rate}")

    def restart(self):
        initial_state = {
            "rate": self.config["rate"],
            "balance_uah": self.config["available_uah"],
            "balance_usd": self.config["available_usd"]
        }
        self.state = initial_state
        self.save_state()


def main():
    with open('config.json') as config_file:
        config = json.load(config_file)

    trader = Trader(config)

    parser = argparse.ArgumentParser(description="Currency Trader")
    parser.add_argument("action",
                        choices=["RATE", "AVAILABLE", "BUY", "SELL", "BUY ALL", "SELL ALL", "NEXT", "RESTART"])
    parser.add_argument("amount", nargs='?', default=None, type=str)

    args = parser.parse_args()

    if args.action == "RATE":
        print(trader.state["rate"])
    elif args.action == "AVAILABLE":
        trader.display_balance()
    elif args.action == "BUY":
        if args.amount is not None:
            if args.amount.lower() == "all":
                trader.buy_all()
            else:
                trader.buy_usd(float(args.amount))
        else:
            print("Please specify the amount to buy.")
    elif args.action == "SELL":
        if args.amount is not None:
            if args.amount.lower() == "all":
                trader.sell_all()
            else:
                trader.sell_usd(float(args.amount))
        else:
            print("Please specify the amount to sell.")
    elif args.action == "NEXT":
        trader.next_rate()
    elif args.action == "RESTART":
        trader.restart()


if __name__ == "__main__":
    main()
