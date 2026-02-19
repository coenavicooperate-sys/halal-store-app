import streamlit as st
import json
import os
import zipfile
import io
import base64
import hmac
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image, ImageEnhance, ExifTags
from slugify import slugify

# ──────────────────────────────────────────────
# Bilingual labels
# ──────────────────────────────────────────────
LABELS = {
    "en": {
        "app_title": "Halal Restaurant Store Registration",
        "step1": "Step 1: Basic Information",
        "step2": "Step 2: Business Information",
        "step3": "Step 3: Facilities & Services",
        "step4": "Step 4: Photo Upload",
        "step5": "Step 5: Highlights",
        "step6": "Step 6: Menu Information",
        "step7": "Step 7: Interior / Exterior Photos",
        "step8": "Validation & Submit",
        "store_name": "Store Name (Google Maps Listing)",
        "phone": "Phone Number",
        "contact": "Contact Person Name",
        "email": "Email Address",
        "business_hours": "Business Hours (Mon–Sun / Holiday)",
        "regular_holiday": "Regular Holiday",
        "nearest_station": "Nearest Station",
        "languages_available": "Languages Available",
        "wifi": "Wi-Fi",
        "wifi_available": "Available",
        "wifi_not_available": "Not Available",
        "payment_methods": "Payment Methods",
        "halal_level": "Halal Compliance Level",
        "halal_full": "Fully Halal Certified",
        "halal_muslim_friendly": "Muslim-Friendly (No Pork / No Alcohol)",
        "halal_menu": "Halal Menu Available",
        "halal_no_pork": "No Pork / No Alcohol Options",
        "halal_vegan": "Vegan / Vegetarian Options",
        "prep_transparency": "Preparation Transparency",
        "prep_separate_kitchen": "Separate Kitchen",
        "prep_separate_utensils": "Separate Utensils",
        "prep_dedicated_area": "Dedicated Halal Cooking Area",
        "prep_same_kitchen": "Same Kitchen (Carefully Managed)",
        "prep_unknown": "Unknown",
        "top_photos": "Top Photos (Upload 3 images)",
        "top_photos_desc": "Storefront / Food / Interior",
        "cert_photos": "Certification Photos (Up to 3)",
        "cert_required": "At least 1 certification photo is required for Fully/Partially Halal Certified.",
        "highlight_photo": "Highlight Photo",
        "highlight_title": "Title",
        "highlight_desc": "Description",
        "menu_photo": "Menu Photo",
        "menu_name": "Menu Name",
        "menu_desc": "Menu Description",
        "interior_photos": "Interior / Exterior Photos (Up to 5)",
        "submit": "Submit",
        "download_zip": "Download ZIP",
        "validation_error": "Please fix the following errors:",
        "required_store": "Store Name is required.",
        "required_phone": "Phone Number is required.",
        "required_email": "Email Address is required.",
        "required_top3": "All 3 Top Photos are required.",
        "required_highlights": "All 3 Highlights (photo, title, description) are required.",
        "required_cert": "At least 1 certification photo is required for the selected Halal level.",
        "invalid_format": "Invalid image format: {name}. Allowed: jpg, png, webp.",
        "file_too_large": "File too large: {name}. Max 10MB.",
        "success": "Submission successful! Download your ZIP below.",
        "progress_steps": [
            "Basic Info", "Business Info", "Facilities",
            "Photos", "Highlights", "Menu", "Interior", "Submit"
        ],
        "highlight_n": "Highlight {n}",
        "menu_n": "Menu {n}",
        "interior_n": "Interior/Exterior {n}",
        "top_n": "Top Photo {n}",
        "cert_n": "Certification {n}",
        "gs_sending": "Sending to Google Sheets & Drive...",
        "gs_success": "Saved to Google Sheets & Drive!",
        "gs_success_link": "Drive folder: {url}",
        "gs_error": "Google Sheets send failed: {err}  (ZIP is still available below)",
        "access_code_title": "Access Code",
        "access_code_prompt": "Please enter the access code to use this form.",
        "access_code_input": "Access Code",
        "access_code_submit": "Enter",
        "access_code_error": "Incorrect access code. Please try again.",
        "access_code_ok": "Access granted.",
    },
    "ja": {
        "app_title": "ハラル対応レストラン 店舗情報登録",
        "step1": "Step 1：基本情報",
        "step2": "Step 2：店舗情報",
        "step3": "Step 3：設備・対応",
        "step4": "Step 4：写真アップロード",
        "step5": "Step 5：こだわり",
        "step6": "Step 6：メニュー情報",
        "step7": "Step 7：内観・外観写真",
        "step8": "バリデーション・送信",
        "store_name": "店舗名（GoogleMap登録名）",
        "phone": "電話番号",
        "contact": "担当者名",
        "email": "メールアドレス",
        "business_hours": "営業時間（月〜日 / 祝日）",
        "regular_holiday": "定休日",
        "nearest_station": "最寄り駅",
        "languages_available": "対応言語",
        "wifi": "Wi-Fi",
        "wifi_available": "利用可能",
        "wifi_not_available": "利用不可",
        "payment_methods": "決済方法",
        "halal_level": "ハラル対応レベル",
        "halal_full": "完全ハラル認証済み",
        "halal_muslim_friendly": "ムスリムフレンドリー（豚・アルコールなし）",
        "halal_menu": "ハラルメニューあり",
        "halal_no_pork": "豚・アルコールなしメニューあり",
        "halal_vegan": "ヴィーガン / ベジタリアンメニューあり",
        "prep_transparency": "調理配慮レベル",
        "prep_separate_kitchen": "専用キッチン",
        "prep_separate_utensils": "専用調理器具",
        "prep_dedicated_area": "ハラル専用調理エリア",
        "prep_same_kitchen": "同一キッチン（慎重に管理）",
        "prep_unknown": "不明",
        "top_photos": "TOP写真（3枚必須）",
        "top_photos_desc": "外観 / 料理 / 内観",
        "cert_photos": "認証写真（最大3枚）",
        "cert_required": "完全/部分ハラル認証の場合、認証写真が1枚以上必要です。",
        "highlight_photo": "こだわり写真",
        "highlight_title": "表題",
        "highlight_desc": "こだわり説明",
        "menu_photo": "メニュー写真",
        "menu_name": "メニュー名",
        "menu_desc": "メニュー説明",
        "interior_photos": "内観・外観写真（最大5枚）",
        "submit": "送信",
        "download_zip": "ZIPダウンロード",
        "validation_error": "以下のエラーを修正してください：",
        "required_store": "店舗名は必須です。",
        "required_phone": "電話番号は必須です。",
        "required_email": "メールアドレスは必須です。",
        "required_top3": "TOP写真は3枚すべて必要です。",
        "required_highlights": "こだわり3セット（写真・表題・説明）はすべて必要です。",
        "required_cert": "選択されたハラルレベルでは認証写真が1枚以上必要です。",
        "invalid_format": "無効な画像形式: {name}。jpg, png, webp のみ対応。",
        "file_too_large": "ファイルが大きすぎます: {name}。最大10MB。",
        "success": "送信が完了しました！下のボタンからZIPをダウンロードできます。",
        "progress_steps": [
            "基本情報", "店舗情報", "設備・対応",
            "写真", "こだわり", "メニュー", "内観・外観", "送信"
        ],
        "highlight_n": "こだわり {n}",
        "menu_n": "メニュー {n}",
        "interior_n": "内観・外観 {n}",
        "top_n": "TOP写真 {n}",
        "cert_n": "認証写真 {n}",
        "gs_sending": "Google スプレッドシート & Driveに送信中...",
        "gs_success": "Google スプレッドシート & Driveに保存しました！",
        "gs_success_link": "Driveフォルダ: {url}",
        "gs_error": "Google送信に失敗しました: {err}（ZIPは下からダウンロード可能です）",
        "access_code_title": "アクセスコード",
        "access_code_prompt": "このフォームを利用するにはアクセスコードを入力してください。",
        "access_code_input": "アクセスコード",
        "access_code_submit": "入力",
        "access_code_error": "アクセスコードが正しくありません。",
        "access_code_ok": "認証されました。",
    },
}


def L(key):
    return LABELS[st.session_state.lang].get(key, key)


# ──────────────────────────────────────────────
# Image processing helpers
# ──────────────────────────────────────────────
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def fix_exif_rotation(img: Image.Image) -> Image.Image:
    try:
        exif = img._getexif()
        if exif is None:
            return img
        orientation_key = None
        for k, v in ExifTags.TAGS.items():
            if v == "Orientation":
                orientation_key = k
                break
        if orientation_key is None or orientation_key not in exif:
            return img
        orientation = exif[orientation_key]
        rotations = {
            3: Image.Transpose.ROTATE_180,
            6: Image.Transpose.ROTATE_270,
            8: Image.Transpose.ROTATE_90,
        }
        if orientation in rotations:
            img = img.transpose(rotations[orientation])
    except Exception:
        pass
    return img


def enhance_image(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    return img


def center_crop_square(img: Image.Image) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def center_crop_to_ratio(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    w, h = img.size
    target_ratio = target_w / target_h
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img


def process_image_common(img: Image.Image) -> Image.Image:
    img = fix_exif_rotation(img)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img = enhance_image(img)
    return img


def image_to_webp_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=80, optimize=True)
    return buf.getvalue()


def process_top_photo(uploaded_file) -> Image.Image:
    img = Image.open(uploaded_file)
    img = process_image_common(img)
    img = center_crop_square(img)
    img = img.resize((480, 480), Image.LANCZOS)
    return img


def process_cert_photo(uploaded_file) -> Image.Image:
    img = Image.open(uploaded_file)
    img = process_image_common(img)
    max_side = 1600
    w, h = img.size
    if max(w, h) > max_side:
        ratio = max_side / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    return img


def process_highlight_photo(uploaded_file) -> Image.Image:
    img = Image.open(uploaded_file)
    img = process_image_common(img)
    img = center_crop_to_ratio(img, 540, 720)
    img = img.resize((540, 720), Image.LANCZOS)
    return img


def process_menu_photo(uploaded_file) -> Image.Image:
    img = Image.open(uploaded_file)
    img = process_image_common(img)
    img = center_crop_to_ratio(img, 540, 720)
    img = img.resize((540, 720), Image.LANCZOS)
    return img


def process_interior_photo(uploaded_file) -> Image.Image:
    img = Image.open(uploaded_file)
    img = process_image_common(img)
    img = center_crop_to_ratio(img, 540, 720)
    img = img.resize((540, 720), Image.LANCZOS)
    return img


def generate_thumbnail(images_480: list[Image.Image]) -> Image.Image:
    thumbs = [img.resize((128, 128), Image.LANCZOS) for img in images_480]
    combined = Image.new("RGB", (384, 128))
    for i, thumb in enumerate(thumbs):
        combined.paste(thumb, (i * 128, 0))
    return combined


def validate_upload(file) -> list[str]:
    errors = []
    if file is None:
        return errors
    ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
    if ext not in ALLOWED_EXTENSIONS:
        errors.append(L("invalid_format").format(name=file.name))
    if file.size > MAX_FILE_SIZE:
        errors.append(L("file_too_large").format(name=file.name))
    return errors


# ──────────────────────────────────────────────
# Secrets helpers
# ──────────────────────────────────────────────
def get_secret(key: str, default: str = "") -> str:
    """Read from Streamlit secrets (cloud) or fallback to env var / empty."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.environ.get(key, default)


def check_access_code(input_code: str) -> bool:
    correct = get_secret("ACCESS_CODE", "")
    if not correct:
        return True
    return hmac.compare_digest(input_code, correct)


# ──────────────────────────────────────────────
# Google Sheets webhook helpers
# ──────────────────────────────────────────────
def send_to_google(webhook_url: str, data_json: dict, processed_images: list[dict]) -> dict:
    """POST data + base64 images to the Google Apps Script webhook.

    processed_images: [{"filename": "xxx.webp", "data": "<base64>"}]
    Returns the JSON response from the webhook.
    """
    payload = {
        "json_data": data_json,
        "images": processed_images,
    }
    resp = requests.post(
        webhook_url,
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


# ──────────────────────────────────────────────
# Main App
# ──────────────────────────────────────────────
st.set_page_config(page_title="Halal Store Registration", layout="wide")

if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Language toggle (top-right)
lang_col1, lang_col2 = st.columns([8, 2])
with lang_col2:
    st.markdown("🌐 **Language**")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("English", use_container_width=True,
                      type="primary" if st.session_state.lang == "en" else "secondary"):
            st.session_state.lang = "en"
    with c2:
        if st.button("日本語", use_container_width=True,
                      type="primary" if st.session_state.lang == "ja" else "secondary"):
            st.session_state.lang = "ja"

st.title(L("app_title"))

# ──────────────────────────────────────────────
# Access code gate
# ──────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

access_code_secret = get_secret("ACCESS_CODE", "")

if access_code_secret and not st.session_state.authenticated:
    st.markdown(f"### {L('access_code_title')}")
    st.info(L("access_code_prompt"))
    code_input = st.text_input(L("access_code_input"), type="password", key="access_code_field")
    if st.button(L("access_code_submit"), type="primary"):
        if check_access_code(code_input):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error(L("access_code_error"))
    st.stop()

# Read webhook URL from secrets (invisible to end users)
webhook_url = get_secret("WEBHOOK_URL", "")

# ──────────────────────────────────────────────
# Progress bar
# ──────────────────────────────────────────────
steps = L("progress_steps")
progress_html = "<div style='display:flex;gap:4px;margin-bottom:24px;'>"
for i, step_label in enumerate(steps):
    color = "#1f77b4" if i == 0 else "#ddd"
    progress_html += (
        f"<div style='flex:1;text-align:center;padding:8px 4px;"
        f"background:{color};color:{'#fff' if i == 0 else '#333'};"
        f"border-radius:6px;font-size:13px;font-weight:600;'>"
        f"Step {i+1}<br><span style='font-weight:400;font-size:11px;'>{step_label}</span></div>"
    )
progress_html += "</div>"
st.markdown(progress_html, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Step 1: Basic Information
# ──────────────────────────────────────────────
st.header(L("step1"))
store_name = st.text_input(L("store_name"), key="store_name")
phone = st.text_input(L("phone"), key="phone")
contact_name = st.text_input(L("contact"), key="contact_name")
email = st.text_input(L("email"), key="email")

st.divider()

# ──────────────────────────────────────────────
# Step 2: Business Information
# ──────────────────────────────────────────────
st.header(L("step2"))
business_hours = st.text_area(L("business_hours"), key="business_hours")
regular_holiday = st.text_input(L("regular_holiday"), key="regular_holiday")
nearest_station = st.text_input(L("nearest_station"), key="nearest_station")

st.divider()

# ──────────────────────────────────────────────
# Step 3: Facilities & Services
# ──────────────────────────────────────────────
st.header(L("step3"))

language_options = ["English", "Malay", "Indonesian", "French", "Chinese", "Korean", "Other"]
languages = st.multiselect(L("languages_available"), language_options, key="languages")

wifi_options = [L("wifi_available"), L("wifi_not_available")]
wifi = st.radio(L("wifi"), wifi_options, key="wifi_radio", horizontal=True)

payment_options = ["Cash", "Visa", "Mastercard", "JCB", "American Express"]
payment_methods = st.multiselect(L("payment_methods"), payment_options, key="payments")

halal_options = [
    L("halal_full"),
    L("halal_muslim_friendly"),
    L("halal_menu"),
    L("halal_no_pork"),
    L("halal_vegan"),
]
halal_level = st.radio(L("halal_level"), halal_options, key="halal_level_radio")

prep_options = [
    L("prep_separate_kitchen"),
    L("prep_separate_utensils"),
    L("prep_dedicated_area"),
    L("prep_same_kitchen"),
    L("prep_unknown"),
]
prep_transparency = st.radio(L("prep_transparency"), prep_options, key="prep_transparency_radio")

st.divider()

# ──────────────────────────────────────────────
# Step 4: Photo Upload
# ──────────────────────────────────────────────
st.header(L("step4"))

st.subheader(L("top_photos"))
st.caption(L("top_photos_desc"))
top_cols = st.columns(3)
top_photos = []
for i in range(3):
    with top_cols[i]:
        f = st.file_uploader(
            L("top_n").format(n=i + 1),
            type=["jpg", "jpeg", "png", "webp"],
            key=f"top_photo_{i}",
        )
        top_photos.append(f)
        if f:
            st.image(f, use_container_width=True)

st.subheader(L("cert_photos"))
if halal_level == L("halal_full"):
    st.info(L("cert_required"))
cert_photos = []
cert_cols = st.columns(3)
for i in range(3):
    with cert_cols[i]:
        f = st.file_uploader(
            L("cert_n").format(n=i + 1),
            type=["jpg", "jpeg", "png", "webp"],
            key=f"cert_photo_{i}",
        )
        cert_photos.append(f)
        if f:
            st.image(f, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────
# Step 5: Highlights
# ──────────────────────────────────────────────
st.header(L("step5"))
highlight_cols = st.columns(3)
highlights = []
for i in range(3):
    with highlight_cols[i]:
        st.markdown(f"**{L('highlight_n').format(n=i+1)}**")
        h_photo = st.file_uploader(
            L("highlight_photo"),
            type=["jpg", "jpeg", "png", "webp"],
            key=f"highlight_photo_{i}",
        )
        if h_photo:
            st.image(h_photo, use_container_width=True)
        h_title = st.text_input(L("highlight_title"), key=f"highlight_title_{i}")
        h_desc = st.text_area(L("highlight_desc"), key=f"highlight_desc_{i}")
        highlights.append({"photo": h_photo, "title": h_title, "description": h_desc})

st.divider()

# ──────────────────────────────────────────────
# Step 6: Menu Information
# ──────────────────────────────────────────────
st.header(L("step6"))
menu_cols = st.columns(3)
menus = []
for i in range(3):
    with menu_cols[i]:
        st.markdown(f"**{L('menu_n').format(n=i+1)}**")
        m_photo = st.file_uploader(
            L("menu_photo"),
            type=["jpg", "jpeg", "png", "webp"],
            key=f"menu_photo_{i}",
        )
        if m_photo:
            st.image(m_photo, use_container_width=True)
        m_name = st.text_input(L("menu_name"), key=f"menu_name_{i}")
        m_desc = st.text_area(L("menu_desc"), key=f"menu_desc_{i}")
        menus.append({"photo": m_photo, "name": m_name, "description": m_desc})

st.divider()

# ──────────────────────────────────────────────
# Step 7: Interior / Exterior Photos
# ──────────────────────────────────────────────
st.header(L("step7"))
interior_photos = []
int_cols = st.columns(5)
for i in range(5):
    with int_cols[i]:
        f = st.file_uploader(
            L("interior_n").format(n=i + 1),
            type=["jpg", "jpeg", "png", "webp"],
            key=f"interior_photo_{i}",
        )
        interior_photos.append(f)
        if f:
            st.image(f, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────
# Step 8: Validation & Submit
# ──────────────────────────────────────────────
st.header(L("step8"))

if st.button(L("submit"), type="primary", use_container_width=True):
    errors = []

    if not store_name.strip():
        errors.append(L("required_store"))
    if not phone.strip():
        errors.append(L("required_phone"))
    if not email.strip():
        errors.append(L("required_email"))

    if not all(top_photos):
        errors.append(L("required_top3"))

    for h in highlights:
        if not h["photo"] or not h["title"].strip() or not h["description"].strip():
            errors.append(L("required_highlights"))
            break

    if halal_level == L("halal_full"):
        if not any(cert_photos):
            errors.append(L("required_cert"))

    all_files = (
        [f for f in top_photos if f]
        + [f for f in cert_photos if f]
        + [h["photo"] for h in highlights if h["photo"]]
        + [m["photo"] for m in menus if m["photo"]]
        + [f for f in interior_photos if f]
    )
    for f in all_files:
        errors.extend(validate_upload(f))

    if errors:
        st.error(L("validation_error"))
        for e in errors:
            st.warning(e)
    else:
        store_slug = slugify(store_name, allow_unicode=False) or "store"
        zip_buffer = io.BytesIO()
        image_manifest = []

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # --- TOP photos ---
            processed_tops = []
            for i, f in enumerate(top_photos):
                f.seek(0)
                img = process_top_photo(f)
                processed_tops.append(img)
                fname = f"{store_slug}_top_{i+1}.webp"
                zf.writestr(f"{store_slug}/images/{fname}", image_to_webp_bytes(img))
                image_manifest.append({"type": "top", "file": fname})

            # Thumbnail
            thumb = generate_thumbnail(processed_tops)
            thumb_name = f"{store_slug}_thumb.webp"
            zf.writestr(f"{store_slug}/images/{thumb_name}", image_to_webp_bytes(thumb))
            image_manifest.append({"type": "thumbnail", "file": thumb_name})

            # --- Certification photos ---
            for i, f in enumerate(cert_photos):
                if f:
                    f.seek(0)
                    img = process_cert_photo(f)
                    fname = f"{store_slug}_cert_{i+1}.webp"
                    zf.writestr(f"{store_slug}/images/{fname}", image_to_webp_bytes(img))
                    image_manifest.append({"type": "certification", "file": fname})

            # --- Highlights ---
            commitment_data = []
            for i, h in enumerate(highlights):
                h["photo"].seek(0)
                img = process_highlight_photo(h["photo"])
                fname = f"{store_slug}_commitment_{i+1}.webp"
                zf.writestr(f"{store_slug}/images/{fname}", image_to_webp_bytes(img))
                image_manifest.append({"type": "commitment", "file": fname})
                commitment_data.append({
                    "title": h["title"],
                    "description": h["description"],
                    "image": fname,
                })

            # --- Menus ---
            menu_data = []
            for i, m in enumerate(menus):
                if m["photo"] and m["name"].strip():
                    m["photo"].seek(0)
                    img = process_menu_photo(m["photo"])
                    fname = f"{store_slug}_menu_{i+1}.webp"
                    zf.writestr(f"{store_slug}/images/{fname}", image_to_webp_bytes(img))
                    image_manifest.append({"type": "menu", "file": fname})
                    menu_data.append({
                        "name": m["name"],
                        "description": m["description"],
                        "image": fname,
                    })

            # --- Interior photos ---
            for i, f in enumerate(interior_photos):
                if f:
                    f.seek(0)
                    img = process_interior_photo(f)
                    fname = f"{store_slug}_interior_{i+1}.webp"
                    zf.writestr(f"{store_slug}/images/{fname}", image_to_webp_bytes(img))
                    image_manifest.append({"type": "interior", "file": fname})

            # --- Halal level key mapping ---
            halal_key_map = {
                L("halal_full"): "fully_halal_certified",
                L("halal_muslim_friendly"): "muslim_friendly",
                L("halal_menu"): "halal_menu_available",
                L("halal_no_pork"): "no_pork_no_alcohol",
                L("halal_vegan"): "vegan_vegetarian",
            }
            prep_key_map = {
                L("prep_separate_kitchen"): "separate_kitchen",
                L("prep_separate_utensils"): "separate_utensils",
                L("prep_dedicated_area"): "dedicated_halal_cooking_area",
                L("prep_same_kitchen"): "same_kitchen_carefully_managed",
                L("prep_unknown"): "unknown",
            }
            wifi_val = wifi == L("wifi_available")

            # --- data.json ---
            data = {
                "store_name": store_name,
                "phone": phone,
                "contact_name": contact_name,
                "email": email,
                "business_hours": business_hours,
                "regular_holiday": regular_holiday,
                "nearest_station": nearest_station,
                "languages": languages,
                "wifi": wifi_val,
                "payment_methods": payment_methods,
                "halal_level": halal_key_map.get(halal_level, halal_level),
                "preparation_transparency": prep_key_map.get(prep_transparency, prep_transparency),
                "commitments": commitment_data,
                "menus": menu_data,
                "images": image_manifest,
                "display_language": st.session_state.lang,
            }
            json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            zf.writestr(f"{store_slug}/data.json", json_bytes)

        # Collect processed images as base64 for Google upload
        gs_images = []
        zip_buffer.seek(0)
        with zipfile.ZipFile(zip_buffer, "r") as zf_read:
            for entry in zf_read.namelist():
                if entry.endswith(".webp"):
                    img_bytes = zf_read.read(entry)
                    fname = entry.rsplit("/", 1)[-1]
                    gs_images.append({
                        "filename": fname,
                        "data": base64.b64encode(img_bytes).decode("ascii"),
                    })

        # Save to submissions/ folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        submission_dir = os.path.join("submissions", f"{timestamp}_{store_slug}")
        os.makedirs(os.path.join(submission_dir, "images"), exist_ok=True)

        zip_buffer.seek(0)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            zf.extractall(submission_dir)

        zip_buffer.seek(0)

        # --- Send to Google Sheets & Drive ---
        active_url = webhook_url.strip()
        if active_url:
            with st.spinner(L("gs_sending")):
                try:
                    gs_resp = send_to_google(active_url, data, gs_images)
                    if gs_resp.get("status") == "success":
                        st.success(L("gs_success"))
                        folder_url = gs_resp.get("folder_url", "")
                        if folder_url:
                            st.markdown(L("gs_success_link").format(url=folder_url))
                    else:
                        st.warning(L("gs_error").format(
                            err=gs_resp.get("message", "Unknown error")))
                except Exception as exc:
                    st.warning(L("gs_error").format(err=str(exc)[:200]))

        st.success(L("success"))
        st.download_button(
            label=L("download_zip"),
            data=zip_buffer,
            file_name=f"{store_slug}.zip",
            mime="application/zip",
            use_container_width=True,
        )
