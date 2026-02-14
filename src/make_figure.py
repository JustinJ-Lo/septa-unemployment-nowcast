from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


RESULTS_DIR = Path("results")
FIG_DIR = Path("reports/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

BREAK = pd.Timestamp("2020-03-01")


def main() -> None:
    preds_path = RESULTS_DIR / "backtest_predictions.csv"
    preds = pd.read_csv(preds_path, parse_dates=["date"])

    # ----------------------------
    # Figure 1: Actual vs forecasts
    # ----------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(preds["date"], preds["y_true"], label="Actual")
    plt.plot(preds["date"], preds["y_hat_naive"], label="Naive (y_{t-1})")

    if "y_hat_ar1" in preds.columns:
        plt.plot(preds["date"], preds["y_hat_ar1"], label="AR(1)")

    plt.xlabel("Date")
    plt.ylabel("Unemployment rate")
    plt.legend()
    plt.tight_layout()

    out1 = FIG_DIR / "unemployment_predictions.png"
    plt.savefig(out1, dpi=200)
    plt.close()
    print(f"Saved -> {out1}")

    # ----------------------------
    # Figure 2: Forecast errors over time
    # ----------------------------
    plt.figure(figsize=(12, 6))

    plt.axhline(0, linestyle="--", linewidth=1, alpha=0.6)
    plt.axvline(BREAK, linestyle="--", linewidth=2, alpha=0.7, label="2020-03 breakpoint")

    # Always present
    plt.plot(preds["date"], preds["err_naive"], label="Naive error", alpha=0.8)

    # Optional series (depending on your backtest script)
    if "err_ar1" in preds.columns:
        plt.plot(preds["date"], preds["err_ar1"], label="AR(1) error", alpha=0.8)

    if "err_arx_yoy" in preds.columns:
        plt.plot(preds["date"], preds["err_arx_yoy"], label="ARX-YoY error", alpha=0.8)
    elif "err_arx_level" in preds.columns:
        plt.plot(preds["date"], preds["err_arx_level"], label="ARX-level error", alpha=0.8)

    plt.xlabel("Date")
    plt.ylabel("Forecast error (percentage points)")
    plt.title("Out-of-sample forecast errors over time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out2 = FIG_DIR / "forecast_errors_over_time.png"
    plt.savefig(out2, dpi=200)
    plt.close()
    print(f"Saved -> {out2}")


if __name__ == "__main__":
    main()
