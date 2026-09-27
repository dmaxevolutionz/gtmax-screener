import json
import math
# Mengimpor daftar emiten dari file emiten.py terpisah
from emiten import EMITEN_DATA

# Mengambil list kode ticker saja jika EMITEN_DATA berbentuk list of dict / list
if isinstance(EMITEN_DATA, dict):
    LIST_EMITEN = list(EMITEN_DATA.keys())
elif isinstance(EMITEN_DATA, list) and len(EMITEN_DATA) > 0 and isinstance(EMITEN_DATA[0], dict):
    LIST_EMITEN = [item.get("code") or item.get("ticker") for item in EMITEN_DATA]
else:
    LIST_EMITEN = list(EMITEN_DATA)


def detect_candle_pattern(open_p: float, high_p: float, low_p: float, close_p: float) -> str:
    """
    Kalkulasi pola candlestick mandiri (bebas/tidak terikat strategi swing).
    """
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
    """
    Kalkulasi Support & Resistance Visual berbasis Pivot Point (Mandiri).
    """
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
    """
    1. Algoritma Strategi Swing & Trading Plan (SL / TP)
    2. Kalkulasi Sinyal & Power Score (Skala 1-10)
    3. Logika Visual Power Bar
    4. Indikator Tambahan: Golden Cross, Bearish Cross, Overbought, Oversold
    """
    # -------------------------------------------------------------
    # A. KALKULASI SKOR STRATEGI SWING (EMA20, EMA50, RSI14)
    # -------------------------------------------------------------
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

    # -------------------------------------------------------------
    # B. KLASIFIKASI SINYAL & POWER SCORE (1 - 10)
    # -------------------------------------------------------------
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

    power_score = min(10, max(1, round((score + 5) / 10 * 10)))

    # -------------------------------------------------------------
    # C. TRADING PLAN (Stop Loss & Take Profit)
    # -------------------------------------------------------------
    stop_loss = round(close_p * 0.95)
    take_profit_1 = round(close_p * 1.05)
    take_profit_2 = round(close_p * 1.10)

    # -------------------------------------------------------------
    # D. INDIKATOR CROSSING & RSI STATUS
    # -------------------------------------------------------------
    # Simulasi/Cek Golden Cross & Bearish Cross
    p_ema20 = prev_ema20 if prev_ema20 is not None else ema20 * 0.99
    p_ema50 = prev_ema50 if prev_ema50 is not None else ema50
    
    is_golden_cross = (p_ema20 <= p_ema50) and (ema20 > ema50)
    is_bearish_cross = (p_ema20 >= p_ema50) and (ema20 < ema50)
    
    is_overbought = rsi >= 70
    is_oversold = rsi <= 30

    # -------------------------------------------------------------
    # E. KALKULASI MANDIRI: CANDLE PATTERN & SUPPORT RESISTANCE
    # -------------------------------------------------------------
    candle_pattern = detect_candle_pattern(open_p, high_p, low_p, close_p)
    sup_res = calculate_support_resistance(high_p, low_p, close_p)

    # -------------------------------------------------------------
    # F. KONTROL VISUAL POWER BAR
    # -------------------------------------------------------------
    power_percentage = power_score * 10
    active_boxes = power_score

    if signal in ["STRONG_BULLISH", "BULLISH"]:
        bar_color = "#10B981"  # Hijau
    elif signal in ["STRONG_BEARISH", "BEARISH"]:
        bar_color = "#EF4444"  # Merah
    else:
        bar_color = "#9CA3AF"  # Abu-abu

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
    Database simulasi harga emiten.
    """
    sample_database = {
        "BBCA": {"open": 10100, "high": 10300, "low": 10050, "close": 10250, "ema20": 9900, "ema50": 9600, "rsi": 68, "prev_ema20": 9590, "prev_ema50": 9600},
        "BMRI": {"open": 7000, "high": 7150, "low": 6950, "close": 7100, "ema20": 6900, "ema50": 6800, "rsi": 58},
        "BBRI": {"open": 5100, "high": 5250, "low": 5050, "close": 5200, "ema20": 5100, "ema50": 5000, "rsi": 72}, # Overbought
        "TLKM": {"open": 2850, "high": 2880, "low": 2780, "close": 2800, "ema20": 2950, "ema50": 3100, "rsi": 26}, # Oversold & Bearish
        "ASII": {"open": 5000, "high": 5050, "low": 4950, "close": 5000, "ema20": 5010, "ema50": 5000, "rsi": 49},
        "GOTO": {"open": 62, "high": 66, "low": 61, "close": 65, "ema20": 62, "ema50": 60, "rsi": 66},
        "ADRO": {"open": 3600, "high": 3750, "low": 3580, "close": 3720, "ema20": 3500, "ema50": 3510, "rsi": 64, "prev_ema20": 3505, "prev_ema50": 3510}, # Golden Cross
        "UNVR": {"open": 2400, "high": 2420, "low": 2300, "close": 2320, "ema20": 2390, "ema50": 2380, "rsi": 29, "prev_ema20": 2385, "prev_ema50": 2380}, # Bearish Cross & Oversold
        "AMMN": {"open": 9800, "high": 10200, "low": 9750, "close": 10150, "ema20": 9500, "ema50": 9100, "rsi": 75}, # Overbought
        "BREN": {"open": 6800, "high": 7100, "low": 6750, "close": 7050, "ema20": 6600, "ema50": 6300, "rsi": 71}  # Overbought
    }
    
    return sample_database.get(ticker, {
        "open": 1000, "high": 1020, "low": 980, "close": 1000, 
        "ema20": 1000, "ema50": 1000, "rsi": 50
    })


def run_screener():
    """
    Memproses seluruh data emiten dan menyimpan kualifikasi ke data.json
    """
    print(f"🔍 Memulai pemindaian untuk {len(LIST_EMITEN)} emiten...")

    output_data = {
        "updated_at": "2026-09-27 22:00:00",
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

    print("✅ Pemindaian selesai! Hasil disimpan di 'data.json'.")


if __name__ == "__main__":
    run_screener()