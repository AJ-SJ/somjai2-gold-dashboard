"""Internal Streamlit counter dashboard for Somjai2 gold shop staff."""
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

import streamlit as st
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

from official import latest_bullion, latest_silver

SHOP_NAME = "ห้างทองสมใจ 2"
SHOP_TAGLINE = "ทองสวย คุณภาพมั่นใจ บริการด้วยความจริงใจ"
SHOP_PHONE = "034253553"
SHOP_ADDRESS = "24/2-3 ถ.เทศบาล ต.พระปฐมเจดีย์ อ.เมือง จ.นครปฐม 73000"
SHOP_HOURS = "09:00–17:30 น."

RETAIL_SIZES = [
    {"label": "1 บาท", "grams": 15.244, "bullion_ratio": 1.0, "ornament_ratio": 1.0, "making_fee": 1000, "block_fee": 600},
    {"label": "2 สลึง", "grams": 15.244 / 2, "bullion_ratio": .5, "ornament_ratio": .5, "making_fee": 900, "block_fee": 500},
    {"label": "1 สลึง", "grams": 15.244 / 4, "bullion_ratio": .25, "ornament_ratio": .25, "making_fee": 800, "block_fee": 500},
    {"label": "ครึ่งสลึง", "grams": 15.244 / 8, "bullion_ratio": .125, "ornament_ratio": .125, "making_fee": 700, "block_fee": 500},
    {"label": "1 กรัม", "grams": 1.0, "bullion_ratio": 1 / 15.244, "ornament_ratio": 1 / 15.16, "making_fee": 700, "block_fee": 500},
    {"label": "0.6 กรัม", "grams": 0.6, "bullion_ratio": 0.6 / 15.244, "ornament_ratio": 0.6 / 15.16, "making_fee": 500, "block_fee": 500},
    {"label": "0.5 กรัม", "grams": 0.5, "bullion_ratio": 0.5 / 15.244, "ornament_ratio": 0.5 / 15.16, "making_fee": 500, "block_fee": 500},
    {"label": "0.3 กรัม", "grams": 0.3, "bullion_ratio": 0.3 / 15.244, "ornament_ratio": 0.3 / 15.16, "making_fee": 500, "block_fee": 500},
    {"label": "0.2 กรัม", "grams": 0.2, "bullion_ratio": 0.2 / 15.244, "ornament_ratio": 0.2 / 15.16, "making_fee": 500, "block_fee": 500},
    {"label": "0.1 กรัม", "grams": 0.1, "bullion_ratio": 0.1 / 15.244, "ornament_ratio": 0.1 / 15.16, "making_fee": 400, "block_fee": 500},
]
RETAIL_SIZE_BY_LABEL = {item["label"]: item for item in RETAIL_SIZES}

OLD_GOLD_TYPES = {
    "โปร่งเล็ก (ต่ำกว่า 2 บาท)": 3.10,
    "โปร่งใหญ่ 2 บาทขึ้นไป": 2.70,
    "โปร่งใหญ่ 5 บาทขึ้นไป": 2.55,
    "โปร่งใหญ่ 10 บาทขึ้นไป": 2.48,
    "ตันเล็ก (ต่ำกว่า 2 บาท)": 1.70,
    "ตันใหญ่ (2 บาทขึ้นไป)": 1.50,
    "งานเครื่องเล็ก": 1.70,
    "งานเครื่องใหญ่": 1.50,
    "แหวนโปร่งเล็ก (ต่ำกว่า 2 สลึง)": 3.00,
    "แหวนโปร่งใหญ่ (2 สลึงขึ้นไป)": 2.70,
    "แหวนตัน / มังกรฉลุ": 1.00,
    "แหวนปลอกมีด": 0.75,
    "ตะขอ": 0.65,
}
OLD_GOLD_COMPARISON_PERCENT = 5.0
GOLD_PER_GRAM_FACTOR = 0.0656

st.set_page_config(
    page_title=f"{SHOP_NAME} | ระบบช่วยงานหน้าร้าน",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp{font-family:'Noto Sans Thai',sans-serif}.stApp{background:#fffaf1;color:#2d241b;overflow-x:hidden}
.block-container{width:100%;max-width:1280px;padding:1.2rem 2rem 2rem}#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{overflow-x:hidden}
.hero{background:linear-gradient(125deg,#24140c 0%,#5b260c 55%,#9b4c0e 100%);border-radius:26px;padding:34px 38px;color:#fff;box-shadow:0 18px 45px rgba(75,34,8,.19);position:relative;overflow:hidden;margin-bottom:22px}
.hero:after{content:'๙๖.๕%';position:absolute;right:34px;top:-18px;font-size:118px;font-weight:800;color:rgba(255,215,116,.10)}
.brand{font-size:2.3rem;font-weight:800;color:#ffd76e;line-height:1.15}.tagline{font-size:1.08rem;color:#fff4d6;margin-top:9px}.hero-note{margin-top:22px;display:inline-block;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:8px 13px;border-radius:99px;color:#fff8e7}
.section-title{font-size:1.55rem;font-weight:800;color:#4d2a12;margin:24px 0 5px}.section-note{color:#77695c;margin-bottom:15px}
.price-wrap{background:#fff;border:1px solid #ead8b8;border-radius:24px;padding:22px;box-shadow:0 10px 30px rgba(90,54,17,.08)}
.price-grid{display:grid;grid-template-columns:1.1fr repeat(3,1fr);gap:13px}.product-name{border-radius:17px;background:linear-gradient(135deg,#f5b900,#ffd75a);padding:22px;display:flex;flex-direction:column;justify-content:center;color:#382300}.product-name strong{font-size:1.55rem}.product-name span{font-size:1rem;font-weight:700;margin-top:3px}.quote{border:1px solid #eadfcd;background:#fffdf9;border-radius:17px;padding:17px 20px}.quote-label{font-weight:700;color:#9b6900}.quote-value{font-size:1.85rem;font-weight:800;color:#079b3a;margin-top:3px}.quote-sub{font-size:.84rem;color:#86796e}.scb-quote{background:linear-gradient(145deg,#fff8df,#fff);border:2px solid #e3b83f}.scb-quote .quote-label{color:#7b5200}.grid-placeholder{visibility:hidden}
.change-up{color:#078c34}.change-down{color:#c43e38}.market-foot{display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap;color:#77695c;font-size:.92rem;margin-top:14px}
.sync-bar{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0}.sync-item{background:#fff;border:1px solid #eadcc5;border-radius:14px;padding:13px 16px}.sync-label{color:#8a7968;font-size:.82rem}.sync-value{color:#4c2d18;font-weight:750;margin-top:2px}.live-dot{display:inline-block;width:9px;height:9px;background:#14a44d;border-radius:50%;margin-right:7px;box-shadow:0 0 0 4px rgba(20,164,77,.12)}
.service-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.service-card,.collection-card{background:#fff;border:1px solid #eadcc5;border-radius:18px;padding:20px;min-height:150px;box-shadow:0 6px 20px rgba(80,48,15,.05)}.service-card h4,.collection-card h4{color:#5d3213;font-size:1.08rem;margin:8px 0}.service-card p,.collection-card p{color:#75695e;line-height:1.65}.service-icon{font-size:1.8rem}
.collection-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.collection-card{background:linear-gradient(145deg,#fff,#fff7e5);min-height:135px}
.weight-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}.weight-card{background:#fff;border:1px solid #e6d2ae;border-radius:20px;padding:19px;box-shadow:0 8px 24px rgba(83,48,14,.06)}.weight-title{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #efe4d2;padding-bottom:12px;margin-bottom:14px}.weight-title strong{font-size:1.25rem;color:#4b2b13}.weight-chip{background:#fff1c8;color:#865a00;padding:4px 10px;border-radius:99px;font-size:.82rem;font-weight:700}.weight-products{display:grid;grid-template-columns:1fr 1fr;gap:12px}.weight-product{background:#fffaf0;border-radius:13px;padding:12px}.weight-product b{color:#6d3b17}.weight-pair{display:flex;justify-content:space-between;gap:8px;margin-top:8px;font-size:.93rem}.weight-pair span{color:#817364}.weight-pair strong{font-variant-numeric:tabular-nums;color:#25362a}
.contact-box{background:linear-gradient(135deg,#fff1ca,#fffaf0);border:1px solid #e7ca88;border-radius:20px;padding:22px;line-height:1.8}.notice{background:#fff4df;border-left:4px solid #e1a414;padding:12px 15px;border-radius:8px;color:#6e5526;margin:12px 0}
.old-table-wrap{width:100%;border:1px solid #e4c98f;border-radius:16px;overflow:hidden;background:#fff;box-shadow:0 8px 24px rgba(83,48,14,.06)}
.old-table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:1.05rem}.old-table th{background:linear-gradient(135deg,#5b260c,#9b4c0e);color:#fff7e4;padding:16px 12px;text-align:right;line-height:1.35;font-size:1.08rem}.old-table th:first-child{text-align:left;width:27%}.old-table td{padding:15px 12px;border-bottom:1px solid #f0e1c8;text-align:right;vertical-align:middle;line-height:1.45;word-break:break-word;font-variant-numeric:tabular-nums}.old-table td:first-child{text-align:left;font-weight:750;color:#563116}.old-table tbody tr:nth-child(even){background:#fff8ea}.old-table tbody tr:hover{background:#fff0c9}.old-table tbody tr:last-child td{border-bottom:0}.deduct-badge{display:inline-block;background:#fff0bd;color:#815500;border-radius:99px;padding:5px 9px;font-weight:800}.price-cell{color:#087b34;font-weight:850;font-size:1.08rem}.diff-plus{color:#087b34;font-weight:750}.diff-minus{color:#bd3833;font-weight:750}
.old-summary-grid{display:grid;grid-template-columns:.72fr 1.28fr;gap:14px;margin:8px 0 14px}.old-summary-card{background:#fff;border:2px solid #e6d2ae;border-radius:20px;padding:20px 22px;box-shadow:0 8px 22px rgba(83,48,14,.07)}.old-summary-label{color:#826c58;font-size:1rem;font-weight:700}.old-summary-value{color:#4d2a12;font-size:2.2rem;font-weight:850;line-height:1.15;margin-top:6px}.old-summary-card.highlight{background:linear-gradient(135deg,#fff8df,#fff);border-color:#e2b84e}.old-summary-card.highlight .old-summary-value{color:#078c34;font-size:2.55rem}.old-formula{color:#746657;font-size:.9rem;margin-top:8px}
div[data-testid="stNumberInput"] input{background:#fff!important;font-size:1.45rem!important;font-weight:800!important;min-height:60px!important;color:#2d241b!important}div[data-testid="stNumberInput"] button{min-height:60px!important;min-width:48px!important}
div[data-baseweb="tab-list"] button[data-baseweb="tab"]{color:#3d2a1d!important;font-size:1.02rem!important;font-weight:750!important;opacity:1!important}div[data-baseweb="tab-list"] button[data-baseweb="tab"] p,div[data-baseweb="tab-list"] button[data-baseweb="tab"] span{color:inherit!important;-webkit-text-fill-color:currentColor!important;opacity:1!important}div[data-baseweb="tab-list"] button[data-baseweb="tab"][aria-selected="true"]{color:#ff4b4b!important;border-bottom-color:#ff4b4b!important}div[data-baseweb="tab-list"] button[data-baseweb="tab"][aria-selected="false"]{color:#3d2a1d!important}div[data-baseweb="tab-highlight"]{background-color:#ff4b4b!important}
.silver-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}.silver-card{background:linear-gradient(145deg,#fff,#f3f4f6);border:1px solid #d8dce2;border-radius:16px;padding:15px}.silver-label{font-size:.82rem;color:#737983}.silver-value{font-size:1.25rem;font-weight:800;color:#39414b;margin-top:4px}.silver-sub{font-size:.76rem;color:#8a9098;margin-top:3px}.silver-source{margin-top:12px;color:#77695c;font-size:.86rem}.silver-source a{color:#8a5a00;font-weight:700}
.footer{margin-top:36px;background:#2d180d;border-radius:22px;padding:25px;text-align:center;color:#f8e8c9}.footer strong{color:#ffd66d;font-size:1.2rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #eadcc5;border-radius:16px;padding:15px}div[data-testid="stMetricValue"]{color:#4c2d18}.stButton>button,.stFormSubmitButton>button{background:#7d3b12;color:white;border:0;border-radius:10px;font-weight:700}.stButton>button:hover,.stFormSubmitButton>button:hover{background:#a65316;color:white}
/* Tablet: keep every section visible and remove fixed desktop assumptions. */
@media(max-width:1024px){
  .block-container{max-width:100%;padding:1rem 1.15rem 1.8rem}
  .price-grid{grid-template-columns:1fr 1fr}.price-grid .product-name{grid-column:1/-1}
  .grid-placeholder{display:none}
  .service-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .collection-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .weight-grid{grid-template-columns:1fr}
  .sync-bar{grid-template-columns:1fr}
  .silver-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .old-summary-grid{grid-template-columns:1fr 1.25fr}
  .hero:after{display:none}
  [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:1rem!important}
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{min-width:280px!important;flex:1 1 320px!important;width:auto!important}
}
/* Phone: one readable column. Nothing is hidden; cards stack vertically. */
@media(max-width:640px){
  .block-container{padding:.75rem .75rem 1.5rem}
  .hero{padding:22px 18px;border-radius:18px;margin-bottom:14px}
  .brand{font-size:1.55rem}.tagline{font-size:.92rem}.hero-note{font-size:.82rem;margin-top:15px;border-radius:14px}
  .section-title{font-size:1.3rem;margin-top:19px}.section-note{font-size:.9rem}
  .price-wrap{padding:12px;border-radius:17px}.price-grid{grid-template-columns:1fr;gap:9px}.price-grid .product-name{grid-column:auto}
  .product-name{padding:16px}.product-name strong{font-size:1.3rem}.quote{padding:14px 16px}.quote-value{font-size:1.5rem}
  .service-grid,.collection-grid,.weight-grid,.weight-products{grid-template-columns:1fr}
  .silver-grid{grid-template-columns:1fr}
  .old-summary-grid{grid-template-columns:1fr}.old-summary-value{font-size:1.8rem}.old-summary-card.highlight .old-summary-value{font-size:2.1rem}
  .service-card,.collection-card{min-height:0;padding:16px}.weight-card{padding:14px}.weight-title{align-items:flex-start;gap:8px}
  .weight-pair{font-size:.9rem}.weight-pair strong{white-space:nowrap}
  .market-foot{display:block}.market-foot strong{display:block;margin-top:6px}
  [data-testid="stHorizontalBlock"]{display:block!important}
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{display:block!important;width:100%!important;min-width:0!important;margin-bottom:.75rem}
  [data-baseweb="tab-list"]{display:flex!important;flex-wrap:wrap!important;white-space:normal!important;gap:.15rem}
  [data-baseweb="tab"]{flex:0 0 auto;padding:.45rem .65rem}
  [data-testid="stSidebar"]{max-width:min(88vw,340px)}
  [data-testid="stRadio"] label,[data-testid="stRadio"] p{color:#2d241b!important;opacity:1!important}
  .old-table{font-size:.76rem}.old-table th{font-size:.76rem}.old-table th,.old-table td{padding:9px 4px}.old-table th:first-child{width:25%}.deduct-badge{padding:3px 4px}.price-cell{font-size:.78rem}
  .footer{padding:20px 14px;border-radius:16px}
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=10, show_spinner=False)
def official_price():
    return latest_bullion(), datetime.now(ZoneInfo("Asia/Bangkok"))


@st.cache_data(ttl=30, show_spinner=False)
def silver_price():
    return latest_silver(), datetime.now(ZoneInfo("Asia/Bangkok"))


def money(value):
    value = float(value)
    return f"฿{value:,.0f}" if value.is_integer() else f"฿{value:,.2f}"


def weight_card_html(label, price, bullion_ratio, ornament_ratio=None, chip=None, making_fee=0, block_fee=0, weight_grams=None):
    ornament_ratio = bullion_ratio if ornament_ratio is None else ornament_ratio
    weight_grams = ornament_ratio * 15.244 if weight_grams is None else weight_grams
    chip = chip or f"{bullion_ratio:g} บาททองคำ"
    bullion_sell = price["sell"] * bullion_ratio + block_fee
    ornament_sell = price["sell"] * ornament_ratio + making_fee
    scb_price = price["buy"] * (1 - OLD_GOLD_COMPARISON_PERCENT / 100)
    ornament_buy = scb_price * GOLD_PER_GRAM_FACTOR * weight_grams
    return f"""
    <article class="weight-card"><div class="weight-title"><strong>{escape(label)}</strong><span class="weight-chip">{escape(chip)}</span></div>
    <div class="weight-products">
      <div class="weight-product"><b>ทองคำแท่ง</b><div class="weight-pair"><span>รับซื้อ</span><strong>{money(price['buy']*bullion_ratio)}</strong></div><div class="weight-pair"><span>ขายหน้าร้าน</span><strong>{money(bullion_sell)}</strong></div><div class="quote-sub">รวมค่า Block {money(block_fee)}</div></div>
      <div class="weight-product"><b>ทองรูปพรรณ</b><div class="weight-pair"><span>รับซื้อ</span><strong>{money(ornament_buy)}</strong></div><div class="weight-pair"><span>ขายหน้าร้าน</span><strong>{money(ornament_sell)}</strong></div><div class="quote-sub">รับซื้อจากราคาสคบ. × 0.0656 × {weight_grams:g} กรัม</div><div class="quote-sub">รวมค่ากำเหน็จ {money(making_fee)}</div></div>
    </div></article>"""


def weight_cards(price):
    cards = [
        weight_card_html(
            item["label"],
            price,
            item["bullion_ratio"],
            item["ornament_ratio"],
            "ราคาหน้าร้าน",
            item["making_fee"],
            item["block_fee"],
            item["grams"],
        )
        for item in RETAIL_SIZES
    ]
    st.markdown('<div class="weight-grid">'+''.join(cards)+'</div>', unsafe_allow_html=True)


with st.expander("ตั้งค่าการอัปเดตราคา", expanded=False):
    refresh_col, action_col = st.columns([1.2, .8])
    with refresh_col:
        refresh_label = st.selectbox(
            "ตรวจราคาสมาคมอัตโนมัติ",
            ["ทุก 15 วินาที", "ทุก 30 วินาที", "ทุก 1 นาที", "ทุก 5 นาที"],
            index=1,
        )
        st.caption("แนะนำ 30 วินาที หน้าเว็บต้องเปิดอยู่ ระบบจึงตรวจราคาเป็นระยะ")
    with action_col:
        st.write("ตรวจสอบทันทีโดยไม่ต้องรอรอบถัดไป")
        if st.button("ตรวจราคาตอนนี้", use_container_width=True):
            official_price.clear()
            silver_price.clear()
            st.rerun()

refresh_seconds = {"ทุก 15 วินาที": 15, "ทุก 30 วินาที": 30, "ทุก 1 นาที": 60, "ทุก 5 นาที": 300}[refresh_label]

if st_autorefresh is not None:
    st_autorefresh(interval=refresh_seconds*1000, key="association_auto_refresh")
else:
    st.warning("ยังไม่ได้ติดตั้งระบบรีเฟรชอัตโนมัติ กด ‘ตรวจราคาตอนนี้’ ได้ หรือรัน pip install -r requirements.txt แล้วเปิดเว็บใหม่")


st.markdown(f"""<section class="hero"><div class="brand">{SHOP_NAME} · ระบบช่วยงานหน้าร้าน</div><div class="tagline">ราคาสมาคม เครื่องคำนวณ และข้อมูลที่พนักงานใช้ประจำ</div><div class="hero-note">สำหรับพนักงานภายในร้าน • ตรวจสอบราคาก่อนยืนยันกับลูกค้าทุกครั้ง</div></section>""", unsafe_allow_html=True)

try:
    price, checked_at = official_price()
    st.session_state["last_good_official_price"] = price
    st.session_state["last_good_official_checked_at"] = checked_at
    using_saved_price = False
except Exception as exc:
    price = st.session_state.get("last_good_official_price")
    checked_at = st.session_state.get("last_good_official_checked_at")
    using_saved_price = price is not None and checked_at is not None
    if using_saved_price:
        st.warning(
            "เว็บสมาคมตอบกลับช้าชั่วคราว — ขณะนี้กำลังแสดงราคาสมาคมครั้งล่าสุด"
            f"ที่ดึงสำเร็จเมื่อ {checked_at.strftime('%d/%m/%Y %H:%M:%S น.')} "
            "ระบบจะลองใหม่อัตโนมัติในรอบถัดไป"
        )
    else:
        st.error(
            "ขณะนี้ยังดึงราคาประกาศสมาคมค้าทองคำไม่ได้ "
            "ระบบจะลองใหม่อัตโนมัติในรอบถัดไป หรือกด ‘ตรวจราคาตอนนี้’"
        )

if price:
    fingerprint = (price["buy"], price["sell"], price["ornament_buy"], price["ornament_sell"], price["seq"])
    previous_fingerprint = st.session_state.get("official_fingerprint")
    if previous_fingerprint is not None and previous_fingerprint != fingerprint:
        st.toast(f"ราคาสมาคมเปลี่ยนแล้ว · ครั้งที่ {price['seq'] or 'ไม่ระบุ'}", icon="🔔")
        st.session_state["price_changed_at"] = checked_at
    st.session_state["official_fingerprint"] = fingerprint
    st.session_state.setdefault("price_changed_at", checked_at)
    change = float(price.get("change", 0))
    change_class = "change-up" if change >= 0 else "change-down"
    change_text = f"{'▲' if change > 0 else '▼' if change < 0 else '—'} {change:+,.0f} บาท จากประกาศสุดท้ายวันก่อน"
    saved_note = " · กำลังแสดงราคาล่าสุดที่บันทึกไว้" if using_saved_price else ""
    st.markdown(f'<div class="section-title">ราคาทองวันนี้</div><div class="section-note">ราคาประกาศสมาคมค้าทองคำ ทองคำ 96.5% ต่อ 1 บาททองคำ{saved_note}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <section class="price-wrap"><div class="price-grid">
      <div class="product-name"><strong>ทองคำแท่ง</strong><span>ความบริสุทธิ์ 96.5%</span></div>
      <div class="quote"><div class="quote-label">รับซื้อ</div><div class="quote-value">{money(price['buy'])}</div><div class="quote-sub">บาทต่อ 1 บาททองคำ</div></div>
      <div class="quote"><div class="quote-label">ขายออก</div><div class="quote-value">{money(price['sell'])}</div><div class="quote-sub">บาทต่อ 1 บาททองคำ</div></div>
      <div class="grid-placeholder" aria-hidden="true"></div>
      <div class="product-name"><strong>ทองรูปพรรณ</strong><span>ความบริสุทธิ์ 96.5%</span></div>
      <div class="quote"><div class="quote-label">ฐานภาษี / รับซื้อ</div><div class="quote-value">{money(price['ornament_buy'])}</div><div class="quote-sub">ตรวจสภาพและน้ำหนักจริงที่ร้าน</div></div>
      <div class="quote"><div class="quote-label">ขายออก</div><div class="quote-value">{money(price['ornament_sell'])}</div><div class="quote-sub">ยังไม่รวมค่ากำเหน็จของสินค้า</div></div>
      <div class="quote scb-quote"><div class="quote-label">ราคาสคบ.</div><div class="quote-value">{money(price['buy']*(1-OLD_GOLD_COMPARISON_PERCENT/100))}</div><div class="quote-sub">ราคารับซื้อทองคำแท่ง − 5%</div></div>
    </div><div class="market-foot"><span>ประกาศ {price['timestamp'].strftime('%d/%m/%Y %H:%M น.')} • ครั้งที่ {price['seq'] or 'ไม่ระบุ'}</span><strong class="{change_class}">{change_text}</strong></div></section>
    """, unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("#### คำนวณราคารับซื้อทองเก่าแบบรวดเร็ว")
        quick_input, quick_result = st.columns([1, 1])
        with quick_input:
            quick_old_gold_grams = st.number_input(
                "กรอกน้ำหนักทองเก่า (กรัม)",
                min_value=0.01,
                value=1.00,
                step=0.01,
                format="%.2f",
                key="quick_old_gold_grams",
            )
        quick_scb_price = price["buy"] * (1 - OLD_GOLD_COMPARISON_PERCENT / 100)
        quick_old_gold_price = quick_scb_price * 0.0656 * quick_old_gold_grams
        with quick_result:
            st.markdown(
                '<div class="old-summary-card highlight">'
                '<div class="old-summary-label">ราคารับซื้อทองเก่าหน้าร้าน</div>'
                f'<div class="old-summary-value">{money(quick_old_gold_price)}</div>'
                f'<div class="old-summary-sub">น้ำหนัก {quick_old_gold_grams:,.2f} กรัม</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        st.caption("สูตร: ราคาสคบ. × 0.0656 × น้ำหนักกรัม · กรุณาตรวจเปอร์เซ็นต์ทองและน้ำหนักจริงก่อนยืนยันราคา")

    st.markdown(f"""<div class="sync-bar">
      <div class="sync-item"><div class="sync-label">สมาคมประกาศล่าสุด</div><div class="sync-value">{price['timestamp'].strftime('%d/%m/%Y %H:%M น.')} · ครั้งที่ {price['seq'] or 'ไม่ระบุ'}</div></div>
      <div class="sync-item"><div class="sync-label">หน้าเว็บตรวจข้อมูลล่าสุด</div><div class="sync-value"><span class="live-dot"></span>{checked_at.strftime('%d/%m/%Y %H:%M:%S น.')}</div></div>
      <div class="sync-item"><div class="sync-label">รอบตรวจอัตโนมัติ</div><div class="sync-value">{escape(refresh_label)} · แจ้งเตือนเมื่อราคาเปลี่ยน</div></div>
    </div>""", unsafe_allow_html=True)
else:
    st.info("ส่วนคำนวณราคาจะเปิดใช้งานเมื่อโหลดประกาศราคาล่าสุดได้")

tabs = st.tabs(["ราคาตามน้ำหนัก", "ต้นทุนรับซื้อทองเก่า", "ราคาเงิน", "คู่มือบริการ", "ข้อมูลร้าน"])

with tabs[0]:
    st.markdown('<div class="section-title">ราคาแยกตามน้ำหนัก</div>', unsafe_allow_html=True)
    st.caption("ราคาขายหน้าร้านรวมค่ากำเหน็จทองรูปพรรณและค่า Block ทองคำแท่งตามขนาดแล้ว")
    if price:
        weight_cards(price)
        st.caption("สูตรรับซื้อทองรูปพรรณ: ราคาสคบ. × 0.0656 × น้ำหนักกรัม · ราคาขายใช้ราคาทองตามน้ำหนักบวกค่ากำเหน็จหรือค่า Block")
        st.markdown("#### คำนวณน้ำหนักที่ไม่ตรงขนาดมาตรฐาน")
        custom_left, custom_right = st.columns([.8, 1.2])
        with custom_left:
            custom_unit = st.radio("หน่วยที่กรอก", ["กรัม", "บาททองคำ"], horizontal=True, key="custom_unit")
            custom_weight = st.number_input(f"กรอกน้ำหนัก ({custom_unit})", min_value=0.01, value=1.0, step=0.01, format="%.2f", key="custom_weight")
            custom_making_fee = st.number_input("ค่ากำเหน็จทองรูปพรรณ (บาท)", min_value=0, value=700, step=100, key="custom_making_fee")
            custom_block_fee = st.number_input("ค่า Block ทองคำแท่ง (บาท)", min_value=0, value=500, step=100, key="custom_block_fee")
            st.caption("สูตรน้ำหนักรับซื้อ 1 บาททองคำ = 15.244 กรัม")
        if custom_unit == "กรัม":
            bullion_ratio = custom_weight / 15.244
            ornament_ratio = custom_weight / 15.16
            custom_weight_grams = custom_weight
            custom_chip = f"{custom_weight:g} กรัม"
        else:
            bullion_ratio = ornament_ratio = custom_weight
            custom_weight_grams = custom_weight * 15.244
            custom_chip = f"{custom_weight:g} บาททองคำ"
        with custom_right:
            st.markdown(weight_card_html("น้ำหนักกำหนดเอง", price, bullion_ratio, ornament_ratio, custom_chip, custom_making_fee, custom_block_fee, custom_weight_grams), unsafe_allow_html=True)
    st.markdown('<div class="notice">ราคาบนเว็บไซต์เป็นราคาอ้างอิงก่อนตรวจสินค้า ราคาที่ร้านรับซื้อจริงขึ้นอยู่กับเปอร์เซ็นต์ทอง น้ำหนัก สภาพสินค้า และเงื่อนไขของร้าน</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="section-title">คำนวณต้นทุนรับซื้อทองเก่า</div>', unsafe_allow_html=True)
    st.caption("กรอกน้ำหนักเป็นกรัม ระบบจะแสดงราคาหน้าร้านทันทีและคำนวณครบทุกประเภทงาน")
    if price:
        input_col, result_col = st.columns([0.8, 1.2])
        with input_col:
            old_weight_grams = st.number_input(
                "กรอกน้ำหนักทองเก่า (กรัม)",
                min_value=0.01,
                value=1.90,
                step=0.01,
                format="%.2f",
                key="old_gold_grams_direct_v3",
            )
            additional_deduction = st.number_input(
                "หักเพิ่มจากราคาร้านส่งต่อชิ้น (บาท)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
                key="old_gold_extra_deduction_all_types",
            )
            st.caption("กรอกตัวเลขน้ำหนักจากเครื่องชั่งได้โดยตรง เช่น 1.90 กรัม")

        price_per_gram_before_five_percent = price["buy"] * GOLD_PER_GRAM_FACTOR
        storefront_per_gram = price_per_gram_before_five_percent * (1 - OLD_GOLD_COMPARISON_PERCENT / 100)
        official_base_total = price_per_gram_before_five_percent * old_weight_grams
        comparison_cost = official_base_total * (1 - OLD_GOLD_COMPARISON_PERCENT / 100)

        with result_col:
            st.markdown(
                '<div class="old-summary-grid">'
                f'<div class="old-summary-card"><div class="old-summary-label">น้ำหนักที่กรอก</div><div class="old-summary-value">{old_weight_grams:,.2f} กรัม</div></div>'
                f'<div class="old-summary-card highlight"><div class="old-summary-label">ราคาหน้าร้าน หัก 5%</div><div class="old-summary-value">{money(comparison_cost)}</div><div class="old-formula">{money(price["buy"])} × 0.0656 × {old_weight_grams:,.2f} กรัม − 5%</div></div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.write(f"ราคาหน้าร้านต่อกรัม **{money(storefront_per_gram)}**")

        old_gold_rows = []
        for item_type, deduction in OLD_GOLD_TYPES.items():
            after_percent = official_base_total * (1 - deduction / 100)
            wholesale_price = max(0.0, after_percent - additional_deduction)
            storefront_price = comparison_cost
            old_gold_rows.append({
                "ประเภทงาน": item_type,
                "หัก (%)": deduction,
                "ราคาร้านส่ง": wholesale_price,
                "ราคาหน้าร้าน": storefront_price,
                "ราคาต่อกรัม": storefront_per_gram,
                "ส่วนต่าง": wholesale_price - storefront_price,
            })

        st.markdown("#### ราคารับซื้อทุกประเภทงาน")
        table_rows = []
        for row in old_gold_rows:
            difference = row["ส่วนต่าง"]
            difference_class = "diff-plus" if difference >= 0 else "diff-minus"
            difference_text = f"{'+' if difference >= 0 else '−'}{money(abs(difference))}"
            table_rows.append(
                "<tr>"
                f"<td>{escape(row['ประเภทงาน'])}</td>"
                f"<td><span class=\"deduct-badge\">{row['หัก (%)']:.2f}%</span></td>"
                f"<td>{money(row['ราคาร้านส่ง'])}</td>"
                f"<td class=\"price-cell\">{money(row['ราคาหน้าร้าน'])}</td>"
                f"<td class=\"price-cell\">{money(row['ราคาต่อกรัม'])}</td>"
                f"<td class=\"{difference_class}\">{difference_text}</td>"
                "</tr>"
            )
        table_html = (
            '<div class="old-table-wrap"><table class="old-table">'
            '<thead><tr><th>ประเภทงาน</th><th>หัก</th>'
            '<th>ราคาร้านส่ง</th><th>ราคาหน้าร้าน</th><th>ราคาต่อกรัม</th><th>ส่วนต่าง</th>'
            f"</tr></thead><tbody>{''.join(table_rows)}</tbody></table></div>"
        )
        st.markdown(table_html, unsafe_allow_html=True)
        st.caption("ราคาต่อกรัม = ราคารับซื้อทองคำแท่ง × 0.0656 แล้วหัก 5%")

        st.markdown(
            '<div class="notice">ผลลัพธ์เป็นเครื่องมือช่วยคำนวณภายในร้าน ต้องตรวจเปอร์เซ็นต์ทอง น้ำหนักสุทธิ หิน ตะขอ รอยเชื่อม สภาพสินค้า และยืนยันราคาก่อนจ่ายเงินจริง</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("เครื่องคำนวณจะเปิดเมื่อโหลดราคารับซื้อทองคำแท่งล่าสุดได้")

with tabs[2]:
    st.markdown('<div class="section-title">ราคาเงินวันนี้</div><div class="section-note">ราคาอ้างอิงจากห้างกำปั่นทอง KPT · ราคาขายออกยังไม่รวมภาษีมูลค่าเพิ่ม</div>', unsafe_allow_html=True)
    try:
        silver, silver_checked_at = silver_price()
        st.markdown(
            '<section class="price-wrap"><div class="silver-grid">'
            f'<div class="silver-card"><div class="silver-label">ขายออก</div><div class="silver-value">{money(silver["sell_per_baht"])}</div><div class="silver-sub">บาท/บาท</div></div>'
            f'<div class="silver-card"><div class="silver-label">รับซื้อ</div><div class="silver-value">{money(silver["buy_per_baht"])}</div><div class="silver-sub">บาท/บาท</div></div>'
            f'<div class="silver-card"><div class="silver-label">ขายออก</div><div class="silver-value">{money(silver["sell_per_kg"])}</div><div class="silver-sub">บาท/กิโลกรัม</div></div>'
            f'<div class="silver-card"><div class="silver-label">รับซื้อ</div><div class="silver-value">{money(silver["buy_per_kg"])}</div><div class="silver-sub">บาท/กิโลกรัม</div></div>'
            f'<div class="silver-card"><div class="silver-label">รับซื้อคืนเงินรูปพรรณ</div><div class="silver-value">{money(silver["ornament_buy_per_gram"])}</div><div class="silver-sub">บาท/กรัม</div></div>'
            '</div>'
            f'<div class="silver-source">KPT ประกาศ {escape(silver["updated_text"])} · หน้าเว็บตรวจล่าสุด {silver_checked_at.strftime("%d/%m/%Y %H:%M:%S น.")} · <a href="{escape(silver["source"])}" target="_blank">เปิดหน้าอ้างอิง KPT</a></div></section>',
            unsafe_allow_html=True,
        )
    except Exception as exc:
        st.warning(f"ขณะนี้ยังดึงราคาเงินจาก KPT ไม่ได้: {exc}")
        st.link_button("เปิดหน้าอ้างอิงราคาเงิน KPT", "https://kpt.in.th/silverprice.php")

with tabs[3]:
    st.markdown('<div class="section-title">คู่มือช่วยพนักงานแนะนำสินค้า</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="collection-grid">
      <div class="collection-card"><div class="service-icon">◈</div><h4>สร้อยคอและสร้อยข้อมือ</h4><p>มีหลายลาย หลายน้ำหนัก พร้อมช่วยเลือกให้เหมาะกับงบประมาณ</p></div>
      <div class="collection-card"><div class="service-icon">◇</div><h4>แหวนและของขวัญ</h4><p>แหวนทอง ของขวัญวันเกิด ของรับขวัญ และของมงคลสำหรับโอกาสพิเศษ</p></div>
      <div class="collection-card"><div class="service-icon">✦</div><h4>งานสั่งทำพิเศษ</h4><p>ปรึกษาแบบ ขนาด น้ำหนัก และงบประมาณก่อนเริ่มงานทุกครั้ง</p></div>
    </div><div class="section-title">บริการของร้าน</div>
    <div class="service-grid">
      <div class="service-card"><div class="service-icon">฿</div><h4>ซื้อและขายทอง</h4><p>แจ้งราคาอย่างชัดเจน ชั่งน้ำหนักต่อหน้าลูกค้า และออกหลักฐานรายการ</p></div>
      <div class="service-card"><div class="service-icon">✧</div><h4>ทำความสะอาดและซ่อม</h4><p>ตรวจสภาพ ขัดล้าง เปลี่ยนตะขอ ปรับขนาด และประเมินค่าบริการก่อนซ่อม</p></div>
      <div class="service-card"><div class="service-icon">◎</div><h4>ตรวจเปอร์เซ็นต์ทอง</h4><p>ตรวจสอบเบื้องต้นก่อนรับซื้อ พร้อมอธิบายผลและน้ำหนักสุทธิให้ลูกค้า</p></div>
      <div class="service-card"><div class="service-icon">▣</div><h4>ประเมินวงเงิน</h4><p>ประเมินเบื้องต้นจากราคารับซื้อ น้ำหนัก คุณภาพ และเงื่อนไขของร้าน</p></div>
    </div>""", unsafe_allow_html=True)

with tabs[4]:
    st.markdown('<div class="section-title">ข้อมูลร้านและขั้นตอนก่อนยืนยันราคา</div>', unsafe_allow_html=True)
    info, checklist = st.columns([.85, 1.15])
    with info:
        st.markdown(f"""<div class="contact-box"><strong>{SHOP_NAME}</strong><br>โทร: {SHOP_PHONE}<br>ที่อยู่: {SHOP_ADDRESS}<br>เวลาเปิดร้าน: {SHOP_HOURS}<br><br>ตรวจสอบราคาสมาคมและเลขครั้งประกาศก่อนยืนยันราคากับลูกค้าทุกครั้ง</div>""", unsafe_allow_html=True)
    with checklist:
        st.markdown("#### เช็กลิสต์รับซื้อทอง")
        st.checkbox("ตรวจบัตรประชาชนและข้อมูลผู้ขาย", key="check_id")
        st.checkbox("ชั่งน้ำหนักและตรวจเปอร์เซ็นต์ทอง", key="check_weight")
        st.checkbox("ตรวจราคาสมาคมและเลขครั้งประกาศล่าสุด", key="check_price")
        st.checkbox("แจ้งน้ำหนักสุทธิ รายการหัก และราคาก่อนยืนยัน", key="check_confirm")
        st.caption("เช็กลิสต์เป็นตัวช่วยบนหน้าจอและจะเริ่มใหม่เมื่อ session สิ้นสุด ไม่ใช่หลักฐานธุรกรรม")
    with st.expander("หลักการใช้ราคาบนหน้าจอ"):
        st.write("**ราคาสมาคม:** ใช้เป็นราคาอ้างอิง และตรวจเวลา/ครั้งที่ประกาศทุกครั้ง")
        st.write("**ราคาทองรูปพรรณ:** ราคาขายหน้าร้านในตารางน้ำหนักรวมค่ากำเหน็จตามขนาดแล้ว")
        st.write("**ราคารับซื้อและจำนำ:** ต้องตรวจเปอร์เซ็นต์ น้ำหนัก สภาพ เอกสาร และเงื่อนไขของร้านก่อนยืนยัน")

footer_time = checked_at.strftime('%d/%m/%Y %H:%M:%S น.') if checked_at else "ยังตรวจข้อมูลไม่สำเร็จ"
st.markdown(f"""<footer class="footer"><strong>{SHOP_NAME} · ระบบภายในร้าน</strong><br>ตรวจราคาสมาคมอัตโนมัติเมื่อเปิดหน้านี้ไว้<br><small>หน้าเว็บตรวจข้อมูลล่าสุด {footer_time}</small></footer>""", unsafe_allow_html=True)
