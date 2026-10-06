"""Read reference gold and silver prices from their public source pages."""
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

SOURCE = "https://www.goldtraders.or.th/"
ENDPOINT = "https://www.goldtraders.or.th/api/GoldPrices/Latest?readjson=false"
SILVER_SOURCE = "https://kpt.in.th/silverprice.php"


def latest_bullion(session=requests):
    response = session.get(ENDPOINT,timeout=10)
    response.raise_for_status()
    record = response.json()
    buy = float(record["bL_BuyPrice"])
    sell = float(record["bL_SellPrice"])
    ornament_buy = float(record["oM965_BuyPrice"])
    ornament_sell = float(record["oM965_SellPrice"])
    if not (0 < buy <= sell < 1_000_000):
        raise ValueError("ประกาศทองคำแท่งมีราคาที่ไม่สมเหตุสมผล")
    if not (0 < ornament_buy <= ornament_sell < 1_000_000):
        raise ValueError("ประกาศทองรูปพรรณมีราคาที่ไม่สมเหตุสมผล")
    timestamp = pd.Timestamp(record["asTime"])
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("Asia/Bangkok")
    else:
        timestamp = timestamp.tz_convert("Asia/Bangkok")
    if timestamp > pd.Timestamp.now(tz="Asia/Bangkok") + pd.Timedelta(minutes=10):
        raise ValueError("เวลาประกาศจากสมาคมอยู่ในอนาคต")
    return dict(buy=buy,sell=sell,ornament_buy=ornament_buy,
                ornament_sell=ornament_sell,timestamp=timestamp,seq=record.get("seq"),
                change=float(record.get("priceChangeFromPrevDayLast") or 0))


def latest_silver(session=requests):
    """Return the silver prices displayed by KPT without estimating values."""
    response = session.get(
        SILVER_SOURCE,
        timeout=12,
        headers={"User-Agent": "Mozilla/5.0 Somjai2 staff price monitor"},
    )
    response.raise_for_status()
    text = BeautifulSoup(response.text, "html.parser").get_text(" ", strip=True)

    def find_number(pattern, label):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            raise ValueError(f"ไม่พบ{label}ในหน้าอ้างอิงราคาเงิน")
        return float(match.group(1).replace(",", ""))

    updated_match = re.search(
        r"ประจำวันที่\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s*เวลา\s*(\d{1,2}:\d{2})\s*น\.?",
        text,
        flags=re.IGNORECASE,
    )
    updated_text = (
        f"{updated_match.group(1)} {updated_match.group(2)} น."
        if updated_match else "ไม่พบเวลาประกาศ"
    )
    sell_per_baht = find_number(
        r"ราคาขายออก\s+([\d,]+(?:\.\d+)?)\s+[\d,]+(?:\.\d+)?", "ราคาขายออก"
    )
    sell_per_kg = find_number(
        r"ราคาขายออก\s+[\d,]+(?:\.\d+)?\s+([\d,]+(?:\.\d+)?)",
        "ราคาขายออกต่อกิโลกรัม",
    )
    buy_per_baht = find_number(
        r"ราคารับซื้อ\s+([\d,]+(?:\.\d+)?)\s+[\d,]+(?:\.\d+)?", "ราคารับซื้อ"
    )
    buy_per_kg = find_number(
        r"ราคารับซื้อ\s+[\d,]+(?:\.\d+)?\s+([\d,]+(?:\.\d+)?)",
        "ราคารับซื้อต่อกิโลกรัม",
    )
    ornament_buy_per_gram = find_number(
        r"ราคารับซื้อคืนเงินรูปพรรณ\s*:?\s*กรัมละ\s*([\d,]+(?:\.\d+)?)",
        "ราคารับซื้อคืนเงินรูปพรรณต่อกรัม",
    )
    if not (
        0 < buy_per_baht <= sell_per_baht < 100_000
        and 0 < buy_per_kg <= sell_per_kg < 10_000_000
        and 0 < ornament_buy_per_gram < 100_000
    ):
        raise ValueError("ราคาเงินจากหน้าอ้างอิงไม่สมเหตุสมผล")
    return {
        "sell_per_baht": sell_per_baht,
        "sell_per_kg": sell_per_kg,
        "buy_per_baht": buy_per_baht,
        "buy_per_kg": buy_per_kg,
        "ornament_buy_per_gram": ornament_buy_per_gram,
        "updated_text": updated_text,
        "source": SILVER_SOURCE,
    }
