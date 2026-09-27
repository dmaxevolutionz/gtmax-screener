import json
import math
import random
from datetime import datetime

# Mengimpor daftar emiten dari file emiten.py terpisah
try:
    from emiten import EMITEN_DATA
except ImportError:
    EMITEN_DATA = [
        {"ticker": "BBCA", "category": "Bluechip"},
        {"ticker": "BMRI", "category": "Bluechip"}
    ]

# Mengambil list kode ticker saja jika EMITEN_DATA berbentuk list of dict / list
if isinstance(EMITEN_DATA, dict):
    LIST_EMITEN = list(EMITEN_DATA.keys())
elif isinstance(EMITEN_DATA, list) and len(EMITEN_DATA) > 0 and isinstance(EMITEN_DATA[0], dict):
    LIST_EMITEN = [item.get("code") or item.get("ticker") for item in EMITEN_DATA]
else:
    LIST_EMITEN = list(EMITEN_DATA)


def detect_candle_pattern(open_p: float, high_p: float, low_p: float, close_p: float) -> str:
    body = abs(close_p - open_p)
    candle_range = high_p - low_p if high_p != low_p else 1.0
    upper_shade = high_p - max(open_p, close_p)
    lower_shade = min(open_p, close_p) - low_p

    if body <= (0.1 * candle_range):
        return "Doji (Consolidation/Indecision)"
    elif close_p > open_p and lower_shade >= (2 * body) and upper_shade <= (0.2 * body):
        return "Hammer (Bullish Reversal)"
    elif open_p > close_p and upper_shade >= (2 * body) and lower_shade <= (0.2 * body):
        return "Shooting Star (Bearish Reversal)"
    elif close_p > open_p and body >= (0.6 * candle_range):
        return "Bullish Engulfing / Strong Marubozu"
    elif open_p > close_p and body >= (0.6 * candle_range):
        return "Bearish Engulfing / Strong Bearish"
    else:
        return "Standard Candle"


def calculate_support_resistance(high_p: float, low_p: float, close_p: float) -> dict:
    pivot = (high_p + low_p + close_p) / 3.0
    r1 = round((2 * pivot) - low_p)
    s1 = round((2 * pivot) - high_p)
    r2 = round(pivot + (high_p - low_p))
    s2 = round(pivot - (high_p - low_p))

    return {
        "pivot": round(pivot),
        "r1": r1,
        "r2": r2,
        "s1": s1,
        "s2": s2
    }


def calculate_swing_and_power_bar(open_p: float, high_p: float, low_p: float, close_p: float, 
                                   ema20: float, ema50: float, rsi: float, prev_ema20: float = None, prev_ema50: float = None) -> dict:
    score = 0

    # Evaluasi EMA 20
    if close_p >= 1.02 * ema20:
        score += 2
    elif close_p > ema20:
        score += 1
    elif close_p <= 0.98 * ema20:
        score -= 2
    elif close_p < ema20:
        score -= 1

    # Evaluasi EMA 50
    if ema20 > ema50 and close_p > ema50:
        score += 2
    elif ema20 > ema50:
        score += 1
    elif ema20 < ema50 and close_p < ema50:
        score -= 2
    elif ema20 < ema50:
        score -= 1

    # Evaluasi RSI 14
    if rsi >= 65:
        score += 2
    elif 50 <= rsi < 65:
        score += 1
    elif 30 <= rsi <= 40:
        score -= 1
    elif rsi < 30:
        score -= 2

    # Klasifikasi Sinyal
    if score >= 4:
        signal = "STRONG_BULLISH"
    elif score >= 1:
        signal = "BULLISH"
    elif score <= -4:
        signal = "STRONG_BEARISH"
    elif score <= -1:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"

    power_score = min(10, max(1, round((score + 6) / 12 * 10)))

    # Trading Plan
    stop_loss = round(close_p * 0.95)
    take_profit_1 = round(close_p * 1.05)
    take_profit_2 = round(close_p * 1.10)

    # Indikator Status
    p_ema20 = prev_ema20 if prev_ema20 is not None else ema20 * 0.99
    p_ema50 = prev_ema50 if prev_ema50 is not None else ema50
    
    is_golden_cross = (p_ema20 <= p_ema50) and (ema20 > ema50)
    is_bearish_cross = (p_ema20 >= p_ema50) and (ema20 < ema50)
    
    is_overbought = rsi >= 70
    is_oversold = rsi <= 30

    candle_pattern = detect_candle_pattern(open_p, high_p, low_p, close_p)
    sup_res = calculate_support_resistance(high_p, low_p, close_p)

    power_percentage = power_score * 10
    active_boxes = power_score

    if signal in ["STRONG_BULLISH", "BULLISH"]:
        bar_color = "#10B981"
    elif signal in ["STRONG_BEARISH", "BEARISH"]:
        bar_color = "#EF4444"
    else:
        bar_color = "#9CA3AF"

    return {
        "analysis": {
            "close": close_p,
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "ema20": round(ema20, 2),
            "ema50": round(ema50, 2),
            "rsi": round(rsi, 2),
            "score": score,
            "signal": signal,
            "power_score": power_score,
            "trading_plan": {
                "stop_loss": stop_loss,
                "take_profit_1": take_profit_1,
                "take_profit_2": take_profit_2
            },
            "candle_pattern": candle_pattern,
            "support_resistance": sup_res,
            "is_golden_cross": is_golden_cross,
            "is_bearish_cross": is_bearish_cross,
            "is_overbought": is_overbought,
            "is_oversold": is_oversold
        },
        "power_bar": {
            "power_percentage": power_percentage,
            "active_boxes": active_boxes,
            "total_boxes": 10,
            "bar_color": bar_color,
            "is_animated": signal in ["STRONG_BULLISH", "STRONG_BEARISH"]
        }
    }


def fetch_stock_data(ticker: str) -> dict:
    """
    Menggenerasikan data teknikal acak untuk SEMUA emiten agar terdistribusi penuh di UI.
    (Jika nantinya terhubung API seperti YFinance, bagian ini tinggal diganti).
    """
    # Menggunakan hash ticker sebagai seed agar nilai konsisten per ticker tetapi bervariasi antar emiten
    random.seed(sum(ord(c) for c in ticker))

    base_price = random.choice([50, 200, 500, 1500, 3000, 5000, 10000])
    variation = random.uniform(-0.05, 0.05)
    close_p = round(base_price * (1 + variation))
    open_p = round(close_p * random.uniform(0.97, 1.03))
    high_p = max(open_p, close_p) + round(base_price * random.uniform(0.01, 0.03))
    low_p = min(open_p, close_p) - round(base_price * random.uniform(0.01, 0.03))

    ema20 = close_p * random.uniform(0.92, 1.08)
    ema50 = close_p * random.uniform(0.88, 1.12)
    rsi = random.uniform(20, 80)

    # Menghasilkan variasi indikator cross secara acak
    prev_ema20 = ema20 * random.choice([0.98, 1.02])
    prev_ema50 = ema50

    return {
        "open": open_p,
        "high": high_p,
        "low": low_p,
        "close": close_p,
        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi,
        "prev_ema20": prev_ema20,
        "prev_ema50": prev_ema50
    }


def run_screener():
    print(f"🔍 Memulai pemindaian untuk {len(LIST_EMITEN)} emiten...")

    output_data = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ihsg": {"status": "BULLISH", "value": 7350.5},
        "all_stocks": [],
        "top_10_entry": [],
        "swing_setup": [],
        "top_10_weakest": [],
        "golden_cross": [],
        "bearish_cross": [],
        "overbought": [],
        "oversold": []
    }

    for ticker in LIST_EMITEN:
        if not ticker:
            continue
            
        stock = fetch_stock_data(ticker)
        
        result = calculate_swing_and_power_bar(
            open_p=stock["open"],
            high_p=stock["high"],
            low_p=stock["low"],
            close_p=stock["close"],
            ema20=stock["ema20"],
            ema50=stock["ema50"],
            rsi=stock["rsi"],
            prev_ema20=stock.get("prev_ema20"),
            prev_ema50=stock.get("prev_ema50")
        )

        stock_entry = {
            "ticker": ticker,
            **result["analysis"],
            "power_bar": result["power_bar"]
        }

        output_data["all_stocks"].append(stock_entry)

        # Pengelompokan Kategori
        if result["analysis"]["signal"] == "STRONG_BULLISH":
            output_data["top_10_entry"].append(stock_entry)
        if result["analysis"]["signal"] in ["STRONG_BULLISH", "BULLISH"]:
            output_data["swing_setup"].append(stock_entry)
        if result["analysis"]["is_golden_cross"]:
            output_data["golden_cross"].append(stock_entry)
        if result["analysis"]["is_bearish_cross"]:
            output_data["bearish_cross"].append(stock_entry)
        if result["analysis"]["is_overbought"]:
            output_data["overbought"].append(stock_entry)
        if result["analysis"]["is_oversold"]:
            output_data["oversold"].append(stock_entry)

    # Mengurutkan 10 Terlemah berdasarkan skor strategi terrendah
    sorted_by_score = sorted(output_data["all_stocks"], key=lambda x: x["score"])
    output_data["top_10_weakest"] = sorted_by_score[:10]

    # Mengurutkan Top 10 Entry terbaik berdasarkan skor tertinggi
    output_data["top_10_entry"] = sorted(output_data["top_10_entry"], key=lambda x: x["score"], reverse=True)[:10]

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print(f"✅ Pemindaian selesai! Berhasil memproses {len(output_data['all_stocks'])} emiten ke 'data.json'.")


if __name__ == "__main__":
    run_screener()
