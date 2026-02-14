from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


PROCESSED_DIR = Path("data/processed")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").copy()

    df["y"] = df["unemployment_rate"]
    df["y_l1"] = df["y"].shift(1)

    df["log_upt"] = np.log(df["upt"])
    df["log_upt_l1"] = df["log_upt"].shift(1)

    # YoY log change (approx % change), then lag it to avoid look-ahead
    df["yoy_log_upt"] = df["log_upt"] - df["log_upt"].shift(12)
    df["yoy_log_upt_l1"] = df["yoy_log_upt"].shift(1)

    # Common sample so all models compare apples-to-apples
    return df.dropna(subset=["y", "y_l1", "log_upt_l1", "yoy_log_upt_l1"])


def fit_predict(train: pd.DataFrame, test: pd.DataFrame, x_cols: list[str]) -> float:
    model = LinearRegression()
    model.fit(train[x_cols].values, train["y"].values)
    return float(model.predict(test[x_cols].values)[0])


def expanding_window_backtest(df: pd.DataFrame, initial_train: int = 60) -> pd.DataFrame:
    rows = []

    for t in range(initial_train, len(df)):
        train = df.iloc[:t]
        test = df.iloc[t:t + 1]

        y_true = float(test["y"].iloc[0])

        # Baseline
        y_hat_naive = float(test["y_l1"].iloc[0])

        # AR(1)
        y_hat_ar1 = fit_predict(train, test, x_cols=["y_l1"])

        # ARX (level ridership)
        y_hat_arx_level = fit_predict(train, test, x_cols=["y_l1", "log_upt_l1"])

        # ARX (YoY ridership change)
        y_hat_arx_yoy = fit_predict(train, test, x_cols=["y_l1", "yoy_log_upt_l1"])

        rows.append({
            "date": test["date"].iloc[0],
            "y_true": y_true,
            "y_hat_naive": y_hat_naive,
            "y_hat_ar1": y_hat_ar1,
            "y_hat_arx_level": y_hat_arx_level,
            "y_hat_arx_yoy": y_hat_arx_yoy,
            "err_naive": y_true - y_hat_naive,
            "err_ar1": y_true - y_hat_ar1,
            "err_arx_level": y_true - y_hat_arx_level,
            "err_arx_yoy": y_true - y_hat_arx_yoy,
        })

    return pd.DataFrame(rows)


def summarize_errors(err: np.ndarray) -> dict:
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    return {"mae": mae, "rmse": rmse}


def main() -> None:
    panel_path = PROCESSED_DIR / "panel_monthly.csv"
    df = pd.read_csv(panel_path, parse_dates=["date"])
    df = df.dropna(subset=["unemployment_rate", "upt"])

    df = add_features(df)
    preds = expanding_window_backtest(df, initial_train=60)

    metrics_rows = [
        {"model": "naive_y_l1", **summarize_errors(preds["err_naive"].to_numpy())},
        {"model": "ar1_y_l1", **summarize_errors(preds["err_ar1"].to_numpy())},
        {"model": "arx_y_l1_log_upt_l1", **summarize_errors(preds["err_arx_level"].to_numpy())},
        {"model": "arx_y_l1_yoy_log_upt_l1", **summarize_errors(preds["err_arx_yoy"].to_numpy())},
    ]

    preds.to_csv(RESULTS_DIR / "backtest_predictions.csv", index=False)
    pd.DataFrame(metrics_rows).to_csv(RESULTS_DIR / "backtest_metrics.csv", index=False)

    print("Wrote:")
    print(" - results/backtest_predictions.csv")
    print(" - results/backtest_metrics.csv")


if __name__ == "__main__":
    main()
