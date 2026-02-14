from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

RESULTS = Path("results")
FIG_DIR = Path("reports/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RESULTS / "backtest_predictions.csv", parse_dates=["date"])

plt.figure()
plt.plot(df["date"], df["y_true"], label="Actual")
plt.plot(df["date"], df["y_hat_naive"], label="Naive (y_{t-1})")
plt.plot(df["date"], df["y_hat_ar1"], label="AR(1)")

plt.xlabel("Date")
plt.ylabel("Unemployment rate")
plt.legend()
plt.tight_layout()
out = FIG_DIR / "unemployment_predictions.png"
plt.savefig(out, dpi=200)
print(f"Saved -> {out}")
