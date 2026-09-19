"""Read the latest 96.5% bullion and ornament announcement from the association."""
import pandas as pd
import requests

SOURCE = "https://www.goldtraders.or.th/"
ENDPOINT = "https://www.goldtraders.or.th/api/GoldPrices/Latest?readjson=false"


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
