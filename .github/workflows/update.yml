import json
import requests
from datetime import datetime

# 1. Mengimpor daftar emiten dari file emiten.py terpisah
try:
    from emiten import EMITEN_DATA
except ImportError:
    EMITEN_DATA = [
        {"ticker": "BBCA", "category": "Bluechip"},
        {"ticker": "BMRI", "category": "Bluechip"},
        {"ticker": "TPIA", "category": "Petrochemical"},
        {"ticker": "BBRI", "category": "Bluechip"}
    ]

# Ekstrak daftar ticker
if isinstance(EMITEN_DATA, dict):
    LIST_EMITEN = list(EMITEN_DATA.keys())
elif isinstance(EMITEN_DATA, list) and len(EMITEN_DATA) > 0 and isinstance(EMITEN_DATA[0], dict):
    LIST_EMITEN = [item.get("code") or item.get("ticker") for item in EMITEN_DATA]
else:
    LIST_EMITEN = list(EMITEN_DATA)

# URL data JSON dari GitHub Pages Target
EXTERNAL_DATA_URL = "https://cybertechmobile.github.io/sh4ndy-screener/data.json"


def fetch_external_market_data() -> dict:
    """
    Mengambil data JSON dari GitHub Pages dan memetakan harga per ticker.
    """
    print(f"🌐 Mengambil data harga dari {EXTERNAL_DATA_URL}...")
    try:
        response = requests.get(EXTERNAL_DATA_URL, timeout=15)
        if response.status_code == 200:
            data = response.json()
            stocks_list = data.get("all_stocks", [])
            
            # Buat dictionary pemetaan {TICKER: stock_data}
            market_map = {}
            for stock in stocks_list:
                ticker_code = stock.get("ticker", "").strip().upper()
                if ticker_code:
                    market_map[ticker_code] = stock
            
            print(f"✅ Berhasil memuat {len(market_map)} emiten dari GitHub Pages.")
            return market_map
        else:
            print(f"⚠️ Gagal mengambil data. Status Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat koneksi ke GitHub Pages: {e}")
    
    return {}


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
    return {
        "pivot": round(pivot),
        "r1": round((2 * pivot) - low_p),
        "r2": round(pivot + (high_p - low_p)),
        "s1": round((2 * pivot) - high_p),
        "s2": round(pivot - (high_p - low_p))
    }


def calculate_swing_and_power_bar(open_p: float, high_p: float, low_p: float, close_p: float, 
                                   ema20: float, ema50: float, rsi: float) -> dict:
    score = 0
    if close_p >= 1.02 * ema20: score += 2
    elif close_p > ema20: score += 1
    elif close_p <= 0.98 * ema20: score -= 2
    elif close_p < ema20: score -= 1

    if ema20 > ema50 and close_p > ema50: score += 2
    elif ema20 > ema50: score += 1
    elif ema20 < ema50 and close_p < ema50: score -= 2
    elif ema20 < ema50: score -= 1

    if rsi >= 65: score += 2
    elif 50 <= rsi < 65: score += 1
    elif 30 <= rsi <= 40: score -= 1
    elif rsi < 30: score -= 2

    if score >= 4: signal = "STRONG_BULLISH"
    elif score >= 1: signal = "BULLISH"
    elif score <= -4: signal = "STRONG_BEARISH"
    elif score <= -1: signal = "BEARISH"
    else: signal = "NEUTRAL"

    power_score = min(10, max(1, round((score + 6) / 12 * 10)))

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
                "stop_loss": round(close_p * 0.95),
                "take_profit_1": round(close_p * 1.05),
                "take_profit_2": round(close_p * 1.10)
            },
            "candle_pattern": detect_candle_pattern(open_p, high_p, low_p, close_p),
            "support_resistance": calculate_support_resistance(high_p, low_p, close_p)
        },
        "power_bar": {
            "power_percentage": power_score * 10,
            "active_boxes": power_score,
            "total_boxes": 10,
            "bar_color": bar_color,
            "is_animated": signal in ["STRONG_BULLISH", "STRONG_BEARISH"]
        }
    }


def run_screener():
    # 1. Ambil data pasar publik dari GitHub Pages
    external_market = fetch_external_market_data()

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

    # 2. Iterasi seluruh emiten dari emiten.py
    for ticker in LIST_EMITEN:
        if not ticker:
            continue
            
        ticker_clean = ticker.strip().upper()
        
        # Ambil data dari eksternal jika ada
        if ticker_clean in external_market:
            ext_item = external_market[ticker_clean]
            close_p = float(ext_item.get("close", 1000))
            open_p = float(ext_item.get("open", close_p))
            high_p = float(ext_item.get("high", close_p))
            low_p = float(ext_item.get("low", close_p))
            ema20 = float(ext_item.get("ema20", close_p))
            ema50 = float(ext_item.get("ema50", close_p))
            rsi = float(ext_item.get("rsi", 50.0))
        else:
            # Fallback jika ticker baru belum ada di repo eksternal
            close_p, open_p, high_p, low_p = 1000, 1000, 1000, 1000
            ema20, ema50, rsi = 1000.0, 1000.0, 50.0

        # Hitung analisis teknikal dan indikator
        result = calculate_swing_and_power_bar(
            open_p=open_p, high_p=high_p, low_p=low_p,
            close_p=close_p, ema20=ema20, ema50=ema50, rsi=rsi
        )

        stock_entry = {
            "ticker": ticker_clean,
            **result["analysis"],
            "power_bar": result["power_bar"]
        }

        output_data["all_stocks"].append(stock_entry)

        # Pengelompokan Kategori Tab
        if result["analysis"]["signal"] == "STRONG_BULLISH":
            output_data["top_10_entry"].append(stock_entry)
        if result["analysis"]["signal"] in ["STRONG_BULLISH", "BULLISH"]:
            output_data["swing_setup"].append(stock_entry)
        if rsi >= 70:
            output_data["overbought"].append(stock_entry)
        if rsi <= 30:
            output_data["oversold"].append(stock_entry)

    # Sort Top 10
    sorted_by_score = sorted(output_data["all_stocks"], key=lambda x: x["score"])
    output_data["top_10_weakest"] = sorted_by_score[:10]
    output_data["top_10_entry"] = sorted(output_data["top_10_entry"], key=lambda x: x["score"], reverse=True)[:10]

    # Simpan ke data.json lokal
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print(f"✅ Pemindaian Selesai! Berhasil menyinkronkan {len(output_data['all_stocks'])} emiten ke 'data.json'.")


if __name__ == "__main__":
    run_screener()
