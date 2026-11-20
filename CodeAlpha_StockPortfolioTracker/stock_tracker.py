import csv
from pathlib import Path


STOCK_PRICES = {
    "AAPL": 180.00,
    "TSLA": 250.00,
    "MSFT": 420.00,
    "GOOGL": 175.00,
    "AMZN": 185.00,
}


def get_output_filename(extension: str) -> Path | None:
    filename = input(
        f"Enter output filename (default: portfolio.{extension}): "
    ).strip()
    path = Path(filename or f"portfolio.{extension}").expanduser()

    if path.suffix.lower() != f".{extension}":
        print(f"Filename must have a .{extension} extension.")
        return None
    if path.name in {".", ".."} or not path.name:
        print("Please enter a valid filename.")
        return None

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Could not create the output folder: {error}")
        return None
    return path


def collect_holdings() -> list[tuple[str, int, float, float]]:
    holdings: list[tuple[str, int, float, float]] = []

    print("Available stocks:")
    print(", ".join(f"{symbol} (${price:.2f})" for symbol, price in STOCK_PRICES.items()))
    print("Enter 'done' when you have finished adding stocks.\n")

    while True:
        symbol = input("Enter stock symbol: ").strip().upper()
        if symbol == "DONE":
            break
        if symbol not in STOCK_PRICES:
            print("Unknown stock symbol. Please choose one from the available stocks.\n")
            continue

        quantity_text = input(f"Enter quantity of {symbol}: ").strip()
        try:
            quantity = int(quantity_text)
        except ValueError:
            print("Quantity must be a whole number.\n")
            continue

        if quantity <= 0:
            print("Quantity must be greater than zero.\n")
            continue

        price = STOCK_PRICES[symbol]
        holdings.append((symbol, quantity, price, quantity * price))
        print(f"Added {quantity} share(s) of {symbol}.\n")

    return holdings


def display_portfolio(holdings: list[tuple[str, int, float, float]]) -> None:
    if not holdings:
        print("\nNo stocks were added.")
        return

    total = sum(value for _, _, _, value in holdings)
    print("\nPortfolio summary")
    print("-" * 52)
    print(f"{'Symbol':<10}{'Quantity':>10}{'Price':>14}{'Value':>14}")
    print("-" * 52)
    for symbol, quantity, price, value in holdings:
        print(f"{symbol:<10}{quantity:>10}{price:>13.2f}{value:>14.2f}")
    print("-" * 52)
    print(f"{'Total investment:':<34}${total:>16.2f}")


def save_as_text(holdings: list[tuple[str, int, float, float]], filename: str) -> None:
    total = sum(value for _, _, _, value in holdings)
    with Path(filename).open("w", encoding="utf-8") as file:
        file.write("Stock Portfolio Summary\n")
        file.write("=======================\n")
        for symbol, quantity, price, value in holdings:
            file.write(
                f"{symbol}: {quantity} share(s) at ${price:.2f} = ${value:.2f}\n"
            )
        file.write(f"\nTotal investment: ${total:.2f}\n")


def save_as_csv(holdings: list[tuple[str, int, float, float]], filename: str) -> None:
    with Path(filename).open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Symbol", "Quantity", "Price", "Value"])
        writer.writerows(
            (symbol, quantity, f"{price:.2f}", f"{value:.2f}")
            for symbol, quantity, price, value in holdings
        )
        writer.writerow([])
        writer.writerow(["Total investment", "", "", f"{sum(value for _, _, _, value in holdings):.2f}"])


def main() -> None:
    print("Stock Portfolio Tracker")
    print("=======================\n")
    holdings = collect_holdings()
    display_portfolio(holdings)

    if not holdings:
        return

    export_choice = input(
        "\nSave the result? Enter 'txt', 'csv', or press Enter to skip: "
    ).strip().lower()
    if export_choice not in {"txt", "csv"}:
        if export_choice:
            print("Invalid export choice. Please choose 'txt' or 'csv'.")
        return

    filename = get_output_filename(export_choice)
    if filename is None:
        return

    try:
        if export_choice == "txt":
            save_as_text(holdings, str(filename))
        else:
            save_as_csv(holdings, str(filename))
    except OSError as error:
        print(f"Could not save the portfolio: {error}")
        return
    print(f"Portfolio saved to {filename}.")


if __name__ == "__main__":
    main()
