"""Internal Streamlit counter dashboard for Somjai2 gold shop staff."""
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

import streamlit as st
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

from official import latest_bullion

SHOP_NAME = "ห้างทองสมใจ 2"
SHOP_TAGLINE = "ทองสวย คุณภาพมั่นใจ บริการด้วยความจริงใจ"
SHOP_PHONE = "034253553"
SHOP_ADDRESS = "24/2-3 ถ.เทศบาล ต.พระปฐมเจดีย์ อ.เมือง จ.นครปฐม 73000"
SHOP_HOURS = "09:00–17:30 น."

WEIGHTS = {"6 สลึง": 1.5, "1 บาท": 1.0, "2 สลึง": .5, "1 สลึง": .25, "ครึ่งสลึง": .125}

st.set_page_config(page_title=f"{SHOP_NAME} | ระบบช่วยงานหน้าร้าน", page_icon="🟡", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp{font-family:'Noto Sans Thai',sans-serif}.stApp{background:#fffaf1;color:#2d241b}
.block-container{max-width:1280px;padding-top:1.2rem;padding-bottom:2rem}#MainMenu,footer,header{visibility:hidden}
.hero{background:linear-gradient(125deg,#24140c 0%,#5b260c 55%,#9b4c0e 100%);border-radius:26px;padding:34px 38px;color:#fff;box-shadow:0 18px 45px rgba(75,34,8,.19);position:relative;overflow:hidden;margin-bottom:22px}
.hero:after{content:'๙๖.๕%';position:absolute;right:34px;top:-18px;font-size:118px;font-weight:800;color:rgba(255,215,116,.10)}
.brand{font-size:2.3rem;font-weight:800;color:#ffd76e;line-height:1.15}.tagline{font-size:1.08rem;color:#fff4d6;margin-top:9px}.hero-note{margin-top:22px;display:inline-block;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:8px 13px;border-radius:99px;color:#fff8e7}
.section-title{font-size:1.55rem;font-weight:800;color:#4d2a12;margin:24px 0 5px}.section-note{color:#77695c;margin-bottom:15px}
.price-wrap{background:#fff;border:1px solid #ead8b8;border-radius:24px;padding:22px;box-shadow:0 10px 30px rgba(90,54,17,.08)}
.price-grid{display:grid;grid-template-columns:1.1fr 1fr 1fr;gap:13px}.product-name{border-radius:17px;background:linear-gradient(135deg,#f5b900,#ffd75a);padding:22px;display:flex;flex-direction:column;justify-content:center;color:#382300}.product-name strong{font-size:1.55rem}.product-name span{font-size:1rem;font-weight:700;margin-top:3px}.quote{border:1px solid #eadfcd;background:#fffdf9;border-radius:17px;padding:17px 20px}.quote-label{font-weight:700;color:#9b6900}.quote-value{font-size:1.85rem;font-weight:800;color:#079b3a;margin-top:3px}.quote-sub{font-size:.84rem;color:#86796e}
.change-up{color:#078c34}.change-down{color:#c43e38}.market-foot{display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap;color:#77695c;font-size:.92rem;margin-top:14px}
.sync-bar{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0}.sync-item{background:#fff;border:1px solid #eadcc5;border-radius:14px;padding:13px 16px}.sync-label{color:#8a7968;font-size:.82rem}.sync-value{color:#4c2d18;font-weight:750;margin-top:2px}.live-dot{display:inline-block;width:9px;height:9px;background:#14a44d;border-radius:50%;margin-right:7px;box-shadow:0 0 0 4px rgba(20,164,77,.12)}
.service-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.service-card,.collection-card{background:#fff;border:1px solid #eadcc5;border-radius:18px;padding:20px;min-height:150px;box-shadow:0 6px 20px rgba(80,48,15,.05)}.service-card h4,.collection-card h4{color:#5d3213;font-size:1.08rem;margin:8px 0}.service-card p,.collection-card p{color:#75695e;line-height:1.65}.service-icon{font-size:1.8rem}
.collection-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.collection-card{background:linear-gradient(145deg,#fff,#fff7e5);min-height:135px}
.weight-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}.weight-card{background:#fff;border:1px solid #e6d2ae;border-radius:20px;padding:19px;box-shadow:0 8px 24px rgba(83,48,14,.06)}.weight-title{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #efe4d2;padding-bottom:12px;margin-bottom:14px}.weight-title strong{font-size:1.25rem;color:#4b2b13}.weight-chip{background:#fff1c8;color:#865a00;padding:4px 10px;border-radius:99px;font-size:.82rem;font-weight:700}.weight-products{display:grid;grid-template-columns:1fr 1fr;gap:12px}.weight-product{background:#fffaf0;border-radius:13px;padding:12px}.weight-product b{color:#6d3b17}.weight-pair{display:flex;justify-content:space-between;gap:8px;margin-top:8px;font-size:.93rem}.weight-pair span{color:#817364}.weight-pair strong{font-variant-numeric:tabular-nums;color:#25362a}
.contact-box{background:linear-gradient(135deg,#fff1ca,#fffaf0);border:1px solid #e7ca88;border-radius:20px;padding:22px;line-height:1.8}.notice{background:#fff4df;border-left:4px solid #e1a414;padding:12px 15px;border-radius:8px;color:#6e5526;margin:12px 0}
.footer{margin-top:36px;background:#2d180d;border-radius:22px;padding:25px;text-align:center;color:#f8e8c9}.footer strong{color:#ffd66d;font-size:1.2rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #eadcc5;border-radius:16px;padding:15px}div[data-testid="stMetricValue"]{color:#4c2d18}.stButton>button,.stFormSubmitButton>button{background:#7d3b12;color:white;border:0;border-radius:10px;font-weight:700}.stButton>button:hover,.stFormSubmitButton>button:hover{background:#a65316;color:white}
@media(max-width:900px){.price-grid{grid-template-columns:1fr}.service-grid{grid-template-columns:repeat(2,1fr)}.collection-grid,.weight-grid{grid-template-columns:1fr}.hero:after{display:none}}@media(max-width:650px){.sync-bar{grid-template-columns:1fr}.weight-products{grid-template-columns:1fr}}@media(max-width:560px){.service-grid,.collection-grid{grid-template-columns:1fr}.hero{padding:25px}.brand{font-size:1.8rem}.quote-value{font-size:1.55rem}}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=10, show_spinner=False)
def official_price():
    return latest_bullion(), datetime.now(ZoneInfo("Asia/Bangkok"))


def money(value):
    value = float(value)
    return f"฿{value:,.0f}" if value.is_integer() else f"฿{value:,.2f}"


def weight_card_html(label, price, bullion_ratio, ornament_ratio=None, chip=None):
    ornament_ratio = bullion_ratio if ornament_ratio is None else ornament_ratio
    chip = chip or f"{bullion_ratio:g} บาททองคำ"
    return f"""
    <article class="weight-card"><div class="weight-title"><strong>{escape(label)}</strong><span class="weight-chip">{escape(chip)}</span></div>
    <div class="weight-products">
      <div class="weight-product"><b>ทองคำแท่ง</b><div class="weight-pair"><span>รับซื้อ</span><strong>{money(price['buy']*bullion_ratio)}</strong></div><div class="weight-pair"><span>ขายออก</span><strong>{money(price['sell']*bullion_ratio)}</strong></div></div>
      <div class="weight-product"><b>ทองรูปพรรณ</b><div class="weight-pair"><span>รับซื้อ</span><strong>{money(price['ornament_buy']*ornament_ratio)}</strong></div><div class="weight-pair"><span>ขายออก*</span><strong>{money(price['ornament_sell']*ornament_ratio)}</strong></div></div>
    </div></article>"""


def weight_cards(price):
    cards = []
    for label, ratio in WEIGHTS.items():
        cards.append(weight_card_html(label, price, ratio))
    cards.append(weight_card_html("1 กรัม", price, 1/15.244, 1/15.16, "คำนวณตามกรัม"))
    st.markdown('<div class="weight-grid">'+''.join(cards)+'</div>', unsafe_allow_html=True)


with st.sidebar:
    st.header("ตั้งค่าหน้าจอพนักงาน")
    refresh_label = st.selectbox("ตรวจราคาสมาคมอัตโนมัติ", ["ทุก 15 วินาที", "ทุก 30 วินาที", "ทุก 1 นาที", "ทุก 5 นาที"], index=1)
    refresh_seconds = {"ทุก 15 วินาที": 15, "ทุก 30 วินาที": 30, "ทุก 1 นาที": 60, "ทุก 5 นาที": 300}[refresh_label]
    st.caption("แนะนำ 30 วินาที หน้าเว็บต้องเปิดอยู่ ระบบจึงตรวจราคาเป็นระยะ")
    if st.button("ตรวจราคาตอนนี้", use_container_width=True):
        official_price.clear()
        st.rerun()

if st_autorefresh is not None:
    st_autorefresh(interval=refresh_seconds*1000, key="association_auto_refresh")
else:
    st.sidebar.warning("ยังไม่ได้ติดตั้งระบบรีเฟรชอัตโนมัติ กด ‘ตรวจราคาตอนนี้’ ได้ หรือรัน pip install -r requirements.txt แล้วเปิดเว็บใหม่")


st.markdown(f"""<section class="hero"><div class="brand">{SHOP_NAME} · ระบบช่วยงานหน้าร้าน</div><div class="tagline">ราคาสมาคม เครื่องคำนวณ และข้อมูลที่พนักงานใช้ประจำ</div><div class="hero-note">สำหรับพนักงานภายในร้าน • ตรวจสอบราคาก่อนยืนยันกับลูกค้าทุกครั้ง</div></section>""", unsafe_allow_html=True)

try:
    price, checked_at = official_price()
except Exception as exc:
    price, checked_at = None, None
    st.error(f"ขณะนี้ยังดึงราคาประกาศสมาคมค้าทองคำไม่ได้ กรุณาตรวจสอบอีกครั้ง: {exc}")

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
    st.markdown('<div class="section-title">ราคาทองวันนี้</div><div class="section-note">ราคาประกาศสมาคมค้าทองคำ ทองคำ 96.5% ต่อ 1 บาททองคำ</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <section class="price-wrap"><div class="price-grid">
      <div class="product-name"><strong>ทองคำแท่ง</strong><span>ความบริสุทธิ์ 96.5%</span></div>
      <div class="quote"><div class="quote-label">รับซื้อ</div><div class="quote-value">{money(price['buy'])}</div><div class="quote-sub">บาทต่อ 1 บาททองคำ</div></div>
      <div class="quote"><div class="quote-label">ขายออก</div><div class="quote-value">{money(price['sell'])}</div><div class="quote-sub">บาทต่อ 1 บาททองคำ</div></div>
      <div class="product-name"><strong>ทองรูปพรรณ</strong><span>ความบริสุทธิ์ 96.5%</span></div>
      <div class="quote"><div class="quote-label">ฐานภาษี / รับซื้อ</div><div class="quote-value">{money(price['ornament_buy'])}</div><div class="quote-sub">ตรวจสภาพและน้ำหนักจริงที่ร้าน</div></div>
      <div class="quote"><div class="quote-label">ขายออก</div><div class="quote-value">{money(price['ornament_sell'])}</div><div class="quote-sub">ยังไม่รวมค่ากำเหน็จของสินค้า</div></div>
    </div><div class="market-foot"><span>ประกาศ {price['timestamp'].strftime('%d/%m/%Y %H:%M น.')} • ครั้งที่ {price['seq'] or 'ไม่ระบุ'}</span><strong class="{change_class}">{change_text}</strong></div></section>
    """, unsafe_allow_html=True)
    st.markdown(f"""<div class="sync-bar">
      <div class="sync-item"><div class="sync-label">สมาคมประกาศล่าสุด</div><div class="sync-value">{price['timestamp'].strftime('%d/%m/%Y %H:%M น.')} · ครั้งที่ {price['seq'] or 'ไม่ระบุ'}</div></div>
      <div class="sync-item"><div class="sync-label">หน้าเว็บตรวจข้อมูลล่าสุด</div><div class="sync-value"><span class="live-dot"></span>{checked_at.strftime('%d/%m/%Y %H:%M:%S น.')}</div></div>
      <div class="sync-item"><div class="sync-label">รอบตรวจอัตโนมัติ</div><div class="sync-value">{escape(refresh_label)} · แจ้งเตือนเมื่อราคาเปลี่ยน</div></div>
    </div>""", unsafe_allow_html=True)
else:
    st.info("ส่วนคำนวณราคาจะเปิดใช้งานเมื่อโหลดประกาศราคาล่าสุดได้")

tabs = st.tabs(["ราคาตามน้ำหนัก", "เครื่องคำนวณหน้าร้าน", "คู่มือบริการ", "ข้อมูลร้าน"])

with tabs[0]:
    st.markdown('<div class="section-title">ราคาแยกตามน้ำหนัก</div>', unsafe_allow_html=True)
    st.caption("คำนวณตามสัดส่วนจากราคาต่อ 1 บาททองคำ ราคาทองรูปพรรณขายจริงอาจมีค่ากำเหน็จเพิ่ม")
    if price:
        weight_cards(price)
        st.caption("* ทองรูปพรรณขายออกเป็นราคาตามสัดส่วนก่อนค่ากำเหน็จ")
        st.markdown("#### คำนวณน้ำหนักที่ไม่ตรงขนาดมาตรฐาน")
        custom_left, custom_right = st.columns([.8, 1.2])
        with custom_left:
            custom_unit = st.radio("หน่วยที่กรอก", ["กรัม", "บาททองคำ"], horizontal=True, key="custom_unit")
            custom_weight = st.number_input(f"กรอกน้ำหนัก ({custom_unit})", min_value=0.01, value=1.0, step=0.01, format="%.2f", key="custom_weight")
            st.caption("ทองคำแท่ง 1 บาท = 15.244 กรัม · ทองรูปพรรณ 1 บาท = 15.16 กรัม")
        if custom_unit == "กรัม":
            bullion_ratio = custom_weight / 15.244
            ornament_ratio = custom_weight / 15.16
            custom_chip = f"{custom_weight:g} กรัม"
        else:
            bullion_ratio = ornament_ratio = custom_weight
            custom_chip = f"{custom_weight:g} บาททองคำ"
        with custom_right:
            st.markdown(weight_card_html("น้ำหนักกำหนดเอง", price, bullion_ratio, ornament_ratio, custom_chip), unsafe_allow_html=True)
    st.markdown('<div class="notice">ราคาบนเว็บไซต์เป็นราคาอ้างอิงก่อนตรวจสินค้า ราคาที่ร้านรับซื้อจริงขึ้นอยู่กับเปอร์เซ็นต์ทอง น้ำหนัก สภาพสินค้า และเงื่อนไขของร้าน</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="section-title">คำนวณราคาทองเบื้องต้น</div>', unsafe_allow_html=True)
    if price:
        left, right = st.columns(2)
        with left:
            product = st.selectbox("ประเภททอง", ["ทองคำแท่ง 96.5%", "ทองรูปพรรณ 96.5%"])
            action = st.radio("ต้องการคำนวณ", ["ซื้อจากร้าน", "ขายคืนให้ร้าน"], horizontal=True)
            weight_choice = st.selectbox("น้ำหนัก", [*WEIGHTS, "กำหนดเอง"])
            baht_weight = st.number_input("น้ำหนักจำนวนบาท", min_value=0.01, value=1.0, step=0.25) if weight_choice == "กำหนดเอง" else WEIGHTS[weight_choice]
            making_fee = st.number_input("ค่ากำเหน็จรวม (บาท)", min_value=0, value=500, step=100, disabled=product.startswith("ทองคำแท่ง") or action.startswith("ขาย"))
        unit = (price["sell"] if action.startswith("ซื้อ") else price["buy"]) if product.startswith("ทองคำแท่ง") else (price["ornament_sell"] if action.startswith("ซื้อ") else price["ornament_buy"])
        estimate = unit * baht_weight + (making_fee if action.startswith("ซื้อ") and product.startswith("ทองรูปพรรณ") else 0)
        with right:
            st.metric("ราคาประเมิน", money(estimate))
            st.write(f"น้ำหนักรวม **{baht_weight:g} บาททองคำ**")
            st.write(f"ราคาอ้างอิงต่อบาท **{money(unit)}**")
            if making_fee and product.startswith("ทองรูปพรรณ") and action.startswith("ซื้อ"):
                st.write(f"รวมค่ากำเหน็จตัวอย่าง **{money(making_fee)}**")
            st.caption("เป็นเพียงการคำนวณเบื้องต้น กรุณาติดต่อร้านเพื่อยืนยันราคาและค่ากำเหน็จ")
        st.divider()
        st.markdown("#### ประเมินวงเงินจำนำเบื้องต้น")
        p1, p2, p3 = st.columns(3)
        pawn_type = p1.selectbox("ประเภท", ["ทองคำแท่ง", "ทองรูปพรรณ"], key="pawn_type")
        pawn_weight = p2.number_input("น้ำหนัก (บาททองคำ)", min_value=0.01, value=1.0, step=0.25)
        pawn_pct = p3.slider("สัดส่วนวงเงิน (%)", 30, 90, 70)
        pawn_base = price["buy"] if pawn_type == "ทองคำแท่ง" else price["ornament_buy"]
        st.metric("วงเงินประมาณการ", money(pawn_base * pawn_weight * pawn_pct / 100))
        st.caption("ไม่ใช่คำเสนอรับจำนำจริง ต้องตรวจทอง บัตรประชาชน และเงื่อนไขตามกฎหมายที่หน้าร้าน")

with tabs[2]:
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

with tabs[3]:
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
        st.write("**ราคาทองรูปพรรณ:** ราคาขายออกในตารางยังไม่รวมค่ากำเหน็จ")
        st.write("**ราคารับซื้อและจำนำ:** ต้องตรวจเปอร์เซ็นต์ น้ำหนัก สภาพ เอกสาร และเงื่อนไขของร้านก่อนยืนยัน")

footer_time = checked_at.strftime('%d/%m/%Y %H:%M:%S น.') if checked_at else "ยังตรวจข้อมูลไม่สำเร็จ"
st.markdown(f"""<footer class="footer"><strong>{SHOP_NAME} · ระบบภายในร้าน</strong><br>ตรวจราคาสมาคมอัตโนมัติเมื่อเปิดหน้านี้ไว้<br><small>หน้าเว็บตรวจข้อมูลล่าสุด {footer_time}</small></footer>""", unsafe_allow_html=True)
