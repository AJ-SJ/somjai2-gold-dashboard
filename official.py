"""Read reference gold and silver prices from their public source pages."""
import re
import threading
import time

import pandas as pd
import requests
import socketio
from bs4 import BeautifulSoup

SOURCE = "https://www.goldtraders.or.th/"
ENDPOINT = "https://www.goldtraders.or.th/api/GoldPrices/Latest?readjson=false"
SILVER_SOURCE = "https://kpt.in.th/silverprice.php"
INTERGOLD_SOURCE = "https://www.intergold.co.th/"


def latest_bullion(session=requests):
    # The association endpoint occasionally answers slowly. Retry once before
    # giving up so a short network hiccup does not blank the whole dashboard.
    last_error = None
    for attempt in range(2):
        try:
            response = session.get(
                ENDPOINT,
                timeout=(5, 20),
                headers={
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0 Somjai2 staff price monitor",
                },
            )
            response.raise_for_status()
            break
        except requests.RequestException as exc:
            last_error = exc
            if attempt == 1:
                raise RuntimeError(
                    "เว็บไซต์สมาคมค้าทองคำตอบกลับช้า หรือเชื่อมต่อไม่ได้ชั่วคราว"
                ) from last_error
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


class IntergoldLiveFeed:
    """Keep one Socket.IO connection open—the same feed used by InterGOLD."""

    def __init__(self):
        self._latest = None
        self._lock = threading.Lock()
        self._ready = threading.Event()
        self._client = socketio.Client(
            reconnection=True,
            reconnection_attempts=0,
            reconnection_delay=1,
            request_timeout=10,
            logger=False,
            engineio_logger=False,
        )

        @self._client.event
        def connect():
            self._client.emit("get_gold_rate_data")

        @self._client.on("updateGoldRateData")
        def update_gold_rate(data):
            if isinstance(data, dict):
                with self._lock:
                    self._latest = dict(data)
                self._ready.set()

        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while True:
            for transports in (["websocket"], ["polling"]):
                try:
                    self._client.connect(
                        "https://ws.intergold.co.th:3000",
                        transports=transports,
                        wait_timeout=12,
                    )
                    self._client.wait()
                except Exception:
                    continue
            time.sleep(2)

    def snapshot(self, timeout=12):
        if not self._ready.wait(timeout):
            raise RuntimeError("ยังไม่ได้รับราคาสดจาก InterGOLD กรุณารอสักครู่")
        with self._lock:
            return dict(self._latest)


def latest_intergold(feed):
    """Return the latest live Socket.IO price board used by InterGOLD."""
    data = feed.snapshot()

    def number(name):
        if name not in data or data[name] is None:
            raise ValueError(f"ไม่พบข้อมูล {name} ในราคาสด InterGOLD")
        return float(data[name])

    rows = [
        {
            "name": "LBMA", "detail": "99.99% (Baht)", "unit": "บาท",
            "buy": number("bidPrice99Lv3"), "sell": number("offerPrice99Lv3"),
            "buy_diff": number("bidPrice99Lv3Diff"), "sell_diff": number("offerPrice99Lv3Diff"),
        },
        {
            "name": "InterGOLD", "detail": "96.5% (Baht)", "unit": "บาท",
            "buy": number("bidPrice96Lv3"), "sell": number("offerPrice96Lv3"),
            "buy_diff": number("bidPrice96Lv3Diff"), "sell_diff": number("offerPrice96Lv3Diff"),
        },
        {
            "name": "สมาคมฯ", "detail": "96.5% (Baht)", "unit": "บาท",
            "buy": number("bidCentralPrice96"), "sell": number("offerCentralPrice96"),
            "buy_diff": number("bidCentralPrice96Diff"), "sell_diff": number("offerCentralPrice96Diff"),
        },
        {
            "name": "Gold Spot", "detail": "USD", "unit": "USD",
            "buy": number("AUXBuy"), "sell": number("AUXSell"),
            "buy_diff": number("AUXBuyDiff"), "sell_diff": number("AUXSellDiff"),
        },
        {
            "name": "ค่าเงินบาท", "detail": "USD/THB", "unit": "บาท/USD",
            "buy": number("usdBuy"), "sell": number("usdSell"),
            "buy_diff": number("usdBuyDiff"), "sell_diff": number("usdSellDiff"),
        },
    ]
    for row in rows:
        if row["buy"] is not None and row["buy"] <= 0:
            raise ValueError("ราคา InterGOLD ไม่สมเหตุสมผล")
        if row["sell"] is not None and row["sell"] <= 0:
            raise ValueError("ราคา InterGOLD ไม่สมเหตุสมผล")

    raw_time = data.get("createDate")
    if not raw_time:
        raise ValueError("ไม่พบเวลาของราคาสด InterGOLD")
    timestamp = pd.Timestamp(raw_time)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("Asia/Bangkok")
    else:
        timestamp = timestamp.tz_convert("Asia/Bangkok")
    return {
        "rows": rows,
        "timestamp": timestamp,
        "source": INTERGOLD_SOURCE,
        "market_open": bool(data.get("statusSystem", True)),
    }
