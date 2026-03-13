import streamlit as st
import json
import os
import re
import zipfile
import io
import base64
import hmac
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image, ImageEnhance, ImageOps
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
        "step8": "Confirm & Submit",
        "store_name": "Store Name (Google Maps Listing)",
        "phone": "Store Phone Number",
        "category": "Category",
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
        "top_photos": "Top Photos (Storefront / Food / Interior - 3 required)",
        "recommended_top": "Recommended size: 480×480px (processed as square)",
        "recommended_vert": "Recommended size: 540×720px (processed as portrait)",
        "highlights_min": "At least 1 highlight (photo + title + description) required.",
        "menu_min": "At least 1 menu (photo + name) required.",
        "interior_min": "At least 1 interior/exterior photo required.",
        "top_photos_desc": "",
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
        "confirm_title": "Confirm Before Submit",
        "confirm_desc": "Please review the information below. Once submitted, it cannot be modified.",
        "confirm_submit": "Submit",
        "back_edit": "Back to Edit",
        "confirm_and_submit": "Confirm & Submit",
        "back_to_form": "Back to Form",
        "download_zip": "Download ZIP",
        "validation_error": "Please fix the following errors:",
        "required_store": "Store Name is required.",
        "required_phone": "Phone Number is required.",
        "required_email": "Email Address is required.",
        "invalid_email": "Please enter a valid email address.",
        "required_payment": "At least one payment method is required.",
        "required_top3": "All 3 Top Photos are required.",
        "session_expired_photos": "Photo data was lost (session may have expired). Please go back and re-upload all photos.",
        "required_highlights": "At least 1 Highlight (photo, title, description) is required.",
        "required_cert": "At least 1 certification photo is required for the selected Halal level.",
        "invalid_format": "Invalid image format: {name}. Allowed: jpg, png, webp.",
        "file_too_large": "File too large: {name}. Max 10MB.",
        "success": "Submission complete!!",
        "progress_steps": [
            "Basic Info", "Business Info", "Facilities",
            "Photos", "Highlights", "Menu", "Interior", "Submit"
        ],
        "highlight_n": "Highlight {n}",
        "menu_n": "Menu {n}",
        "interior_n": "Interior/Exterior {n}",
        "top_n": "Top Photo {n}",
        "cert_n": "Certification {n}",
        "gs_sending": "Sending... This may take a minute. Please do not close this page.",
        "processing_msg": "Processing. Please wait a moment. Do not close this page.",
        "sending_msg": "Sending. This may take 1–2 minutes. Please do not close this page.",
        "sending_banner": "SENDING...",
        "sending_banner_sub": "This may take 1–2 minutes. Do not close this page.",
        "before_confirm_msg": "Click the button below to proceed to confirmation. Please wait a moment after clicking.",
        "after_confirm_click_msg": "Processing. This may take a moment. Please do not close this page.",
        "before_submit_msg": "Click the button below to submit. Sending may take 1–2 minutes. Do not close this page.",
        "after_submit_click_msg": "Sending. This may take 1–2 minutes. Please do not close this page.",
        "gs_success": "Submission complete!!",
        "gs_error": "Submission failed: {err}. Please try again.",
        "access_code_title": "Access Code",
        "access_code_prompt": "Please enter the access code to use this form.",
        "access_code_input": "Access Code",
        "access_code_submit": "Enter",
        "access_code_error": "Incorrect access code. Please try again.",
        "access_code_ok": "Access granted.",
        "draft_section": "Draft",
        "draft_save": "Save Draft",
        "draft_load": "Load Draft",
        "draft_delete": "Delete",
        "draft_name": "Draft Name",
        "draft_saved": "Draft saved: {name}",
        "draft_loaded": "Draft loaded: {name}",
        "draft_deleted": "Draft deleted: {name}",
        "draft_none": "(No drafts)",
        "draft_select": "Select a draft to load",
        "draft_note": "Photos cannot be saved in drafts. Please re-upload them after loading.",
        "draft_save_desc": "Save your current text and selections so you can continue later. Enter a name (e.g., store name) and click the button. Your draft will be stored on the server.",
        "draft_load_desc": "Select a previously saved draft from the list and click \"Load Draft\" to restore your text and selections. You can continue editing from where you left off.",
        "draft_auto": "Auto-save",
        "draft_auto_on": "Auto-save is ON",
        "manual_link": "Input Manual",
        "session_hint": "Long input sessions may disconnect. Photos are automatically resized for optimal display.",
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
        "step8": "確認・送信",
        "store_name": "店舗名（GoogleMap登録名）",
        "phone": "お店の電話番号",
        "category": "カテゴリー",
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
        "top_photos": "TOP写真（外観 / 料理 / 内観の3枚必須）",
        "recommended_top": "推奨サイズ: 480×480px（加工後は正方形）",
        "recommended_vert": "推奨サイズ: 540×720px（加工後は縦型）",
        "highlights_min": "こだわりは最低1セット（写真＋表題＋説明）必要です。",
        "menu_min": "メニューは最低1つ（写真＋メニュー名）必要です。",
        "interior_min": "内観・外観写真は最低1枚必要です。",
        "top_photos_desc": "",
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
        "confirm_title": "送信前の確認",
        "confirm_desc": "以下の内容をご確認ください。送信後は修正できません。",
        "confirm_submit": "送信する",
        "back_edit": "編集に戻る",
        "confirm_and_submit": "確認して送信",
        "back_to_form": "フォームに戻る",
        "download_zip": "ZIPダウンロード",
        "validation_error": "以下のエラーを修正してください：",
        "required_store": "店舗名は必須です。",
        "required_phone": "電話番号は必須です。",
        "required_email": "メールアドレスは必須です。",
        "invalid_email": "有効なメールアドレスを入力してください。",
        "required_payment": "決済方法を1つ以上選択してください。",
        "required_top3": "TOP写真は3枚すべて必要です。",
        "session_expired_photos": "写真データが失われました（セッション切れの可能性）。編集に戻り、写真を再アップロードしてください。",
        "required_highlights": "こだわりは最低1セット（写真・表題・説明）必要です。",
        "required_cert": "選択されたハラルレベルでは認証写真が1枚以上必要です。",
        "invalid_format": "無効な画像形式: {name}。jpg, png, webp のみ対応。",
        "file_too_large": "ファイルが大きすぎます: {name}。最大10MB。",
        "success": "送信が完了しました！！",
        "progress_steps": [
            "基本情報", "店舗情報", "設備・対応",
            "写真", "こだわり", "メニュー", "内観・外観", "送信"
        ],
        "highlight_n": "こだわり {n}",
        "menu_n": "メニュー {n}",
        "interior_n": "内観・外観 {n}",
        "top_n": "TOP写真 {n}",
        "cert_n": "認証写真 {n}",
        "gs_sending": "送信中です... 1〜2分かかる場合があります。このページを閉じないでください。",
        "processing_msg": "作業中です。少々お待ちください。このページを閉じないでください。",
        "sending_msg": "送信中です。1〜2分かかる場合があります。このページを閉じないでください。",
        "sending_banner": "送信中",
        "sending_banner_sub": "1〜2分かかります。このページを閉じないでください。",
        "before_confirm_msg": "下のボタンをクリックすると確認画面に進みます。クリック後、少々お待ちください。",
        "after_confirm_click_msg": "処理中です。少々お待ちください。このページを閉じないでください。",
        "before_submit_msg": "下のボタンをクリックすると送信が開始されます。1〜2分かかる場合があります。このページを閉じないでください。",
        "after_submit_click_msg": "送信中です。1〜2分かかる場合があります。このページを閉じないでください。",
        "gs_success": "送信が完了しました！！",
        "gs_error": "送信に失敗しました: {err}。もう一度お試しください。",
        "access_code_title": "アクセスコード",
        "access_code_prompt": "このフォームを利用するにはアクセスコードを入力してください。",
        "access_code_input": "アクセスコード",
        "access_code_submit": "入力",
        "access_code_error": "アクセスコードが正しくありません。",
        "access_code_ok": "認証されました。",
        "draft_section": "下書き",
        "draft_save": "下書き保存",
        "draft_load": "下書き読み込み",
        "draft_delete": "削除",
        "draft_name": "下書き名",
        "draft_saved": "下書きを保存しました: {name}",
        "draft_loaded": "下書きを読み込みました: {name}",
        "draft_deleted": "下書きを削除しました: {name}",
        "draft_none": "（下書きなし）",
        "draft_select": "読み込む下書きを選択",
        "draft_note": "写真は下書きに保存されません。読み込み後に再度アップロードしてください。",
        "draft_save_desc": "現在入力中のテキストや選択内容を保存し、後で続きから入力できます。下書き名（例：店舗名）を入力してボタンを押すと、サーバーに保存されます。",
        "draft_load_desc": "過去に保存した下書きを一覧から選び、「下書き読み込み」ボタンを押すと、テキストや選択内容が復元されます。続きから編集を進められます。",
        "draft_auto": "自動保存",
        "draft_auto_on": "自動保存が有効です",
        "manual_link": "入力マニュアル",
        "session_hint": "長時間の入力で画面が切れる場合があります。写真は自動で最適サイズに縮小されます。",
    },
}


def L(key):
    return LABELS[st.session_state.lang].get(key, key)


# ──────────────────────────────────────────────
# Image processing helpers
# ──────────────────────────────────────────────
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_PREVIEW_PIXELS = 1500  # アップロード時に自動縮小（メモリ節約・クラッシュ防止）


class CompressedImageFile:
    """圧縮済み画像のファイル風ラッパー。メモリ使用量を削減。"""

    def __init__(self, buf: io.BytesIO, original_name: str):
        self._buf = buf
        self.name = original_name
        self.size = len(buf.getvalue())

    def seek(self, pos: int = 0):
        self._buf.seek(pos)

    def read(self, size: int = -1):
        return self._buf.read(size)

    def tell(self):
        return self._buf.tell()

    def getvalue(self):
        return self._buf.getvalue()


def compress_uploaded_image(uploaded_file):
    """アップロード画像を自動縮小・圧縮してメモリ節約。失敗時は元のファイルを返す。"""
    if not uploaded_file:
        return None
    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        img = fix_exif_rotation(img)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        w, h = img.size
        if w > MAX_PREVIEW_PIXELS or h > MAX_PREVIEW_PIXELS:
            ratio = min(MAX_PREVIEW_PIXELS / w, MAX_PREVIEW_PIXELS / h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85, optimize=True)
        buf.seek(0)
        name = getattr(uploaded_file, "name", "photo.jpg")
        if not name.lower().endswith((".jpg", ".jpeg")):
            name = name.rsplit(".", 1)[0] + ".jpg" if "." in name else "photo.jpg"
        return CompressedImageFile(buf, name)
    except Exception:
        uploaded_file.seek(0)
        return uploaded_file  # 失敗時は元のファイルをそのまま使用


def maybe_compress(file, cache_key: str):
    """圧縮可能なら圧縮版を返す。キャッシュで再圧縮を避け、サクサク動作。"""
    if not file:
        for k in [cache_key, f"{cache_key}_src"]:
            st.session_state.pop(k, None)
        return None
    # 同一ファイルならキャッシュを使用（毎回のrerunで再圧縮しない）
    src_id = f"{cache_key}_src"
    if src_id in st.session_state and st.session_state[src_id] == id(file):
        return st.session_state.get(cache_key, file)
    result = compress_uploaded_image(file)
    st.session_state[cache_key] = result
    st.session_state[src_id] = id(file)
    return result


def fix_exif_rotation(img: Image.Image) -> Image.Image:
    """Fix orientation for smartphone photos using EXIF metadata."""
    try:
        return ImageOps.exif_transpose(img)
    except Exception:
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
    img = center_crop_to_ratio(img, 540, 720)
    img = img.resize((540, 720), Image.LANCZOS)
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


def display_image_with_orientation(uploaded_file):
    """Display uploaded image with correct EXIF orientation (for mobile photos)."""
    if not uploaded_file:
        return
    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        img = fix_exif_rotation(img)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        st.image(img, use_container_width=True)
        uploaded_file.seek(0)
    except Exception:
        st.image(uploaded_file, use_container_width=True)
        uploaded_file.seek(0)


def is_valid_email(email: str) -> bool:
    """Check if string is a valid email format."""
    if not email or not email.strip():
        return False
    # RFC 5322 simplified: local@domain.tld
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


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
# Draft save / load helpers
# ──────────────────────────────────────────────
DRAFTS_DIR = Path("drafts")

DRAFT_TEXT_KEYS = [
    "store_name", "phone", "contact_name", "email",
    "business_hours", "regular_holiday", "nearest_station",
    "highlight_title_0", "highlight_title_1", "highlight_title_2",
    "highlight_desc_0", "highlight_desc_1", "highlight_desc_2",
    "menu_name_0", "menu_name_1", "menu_name_2",
    "menu_desc_0", "menu_desc_1", "menu_desc_2",
]
DRAFT_MULTI_KEYS = ["languages", "payments"]
DRAFT_RADIO_KEYS = ["wifi_radio", "halal_level_radio", "prep_transparency_radio"]
DRAFT_SELECT_KEYS = ["category"]

# Category options (alphabetical order)
CATEGORY_OPTIONS = [
    "Asian Food",
    "Café",
    "Japanese Food",
    "Meat Dishes",
    "Middle Eastern Food",
    "Other Foods",
    "Ramen",
    "Vegan/Vegetarian Cuisine",
    "Wagyu Beef",
]


def _drafts_list() -> list[str]:
    if not DRAFTS_DIR.exists():
        return []
    names = sorted(
        [f.stem for f in DRAFTS_DIR.glob("*.json")],
        key=lambda n: DRAFTS_DIR.joinpath(f"{n}.json").stat().st_mtime,
        reverse=True,
    )
    return names


def _save_draft(name: str):
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    payload: dict = {}
    for k in DRAFT_TEXT_KEYS:
        payload[k] = st.session_state.get(k, "")
    for k in DRAFT_MULTI_KEYS:
        payload[k] = st.session_state.get(k, [])
    for k in DRAFT_RADIO_KEYS:
        payload[k] = st.session_state.get(k, None)
    for k in DRAFT_SELECT_KEYS:
        payload[k] = st.session_state.get(k, None)
    payload["lang"] = st.session_state.get("lang", "en")
    safe_name = slugify(name, allow_unicode=True) or "draft"
    path = DRAFTS_DIR / f"{safe_name}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return safe_name


def _load_draft(name: str) -> dict | None:
    path = DRAFTS_DIR / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _delete_draft(name: str):
    path = DRAFTS_DIR / f"{name}.json"
    if path.exists():
        path.unlink()


def _apply_draft(draft: dict):
    """Write draft values into session_state so widgets pick them up."""
    for k in DRAFT_TEXT_KEYS:
        if k in draft:
            st.session_state[k] = draft[k]
    for k in DRAFT_MULTI_KEYS:
        if k in draft:
            st.session_state[k] = draft[k]
    for k in DRAFT_RADIO_KEYS:
        if k in draft:
            st.session_state[k] = draft[k]
    for k in DRAFT_SELECT_KEYS:
        if k in draft:
            st.session_state[k] = draft[k]
    if "lang" in draft:
        st.session_state.lang = draft["lang"]


# ──────────────────────────────────────────────
# Main App
# ──────────────────────────────────────────────
st.set_page_config(page_title="Halal Store Registration", layout="wide")

# 外部利用者向け：Streamlit・GitHubアイコン、フッター等を非表示
st.markdown(
    """
    <style>
    /* フッター全体を非表示 */
    footer {visibility: hidden !important; display: none !important;}
    /* メニュー・ツールバー */
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    /* Streamlit Cloud のフッターアイコン（Streamlit・GitHub） */
    a[href*="streamlit.io"] {display: none !important;}
    a[href*="github.com"] {display: none !important;}
    /* viewerBadge 系（Streamlit Cloud のバッジ） */
    .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_,
    .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK,
    [class*="viewerBadge"],
    [class*="stBottom"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

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

# Manual link (ログイン後のみ表示)
manual_url = get_secret("MANUAL_URL", "")
if manual_url and manual_url.strip():
    st.markdown(f'📖 [{L("manual_link")}]({manual_url.strip()})')

# Read webhook URL from secrets (invisible to end users)
webhook_url = get_secret("WEBHOOK_URL", "")

# ──────────────────────────────────────────────
# 送信結果表示（スマホで見やすいようページ上部に表示）
# ──────────────────────────────────────────────
if "_submission_result" in st.session_state:
    result = st.session_state["_submission_result"]
    msg = st.session_state.get("_submission_message", "")
    if result == "success":
        st.toast(L("gs_success"), icon="✅")
        st.success(L("gs_success"))
        st.balloons()
        st.info("送信後は修正できません。" if st.session_state.lang == "ja" else "Submitted data cannot be modified.")
    else:
        st.toast(msg or L("gs_error").format(err="Unknown error"), icon="❌")
        st.error(msg if msg else L("gs_error").format(err="Unknown error"))
        if st.button(L("back_to_form"), type="primary", use_container_width=True):
            for k in ["_submission_result", "_submission_message"]:
                st.session_state.pop(k, None)
            st.rerun()
    st.stop()

# ──────────────────────────────────────────────
# 送信処理中：目立つバナーを最上部に表示（ボタン押下後すぐ表示）
# ──────────────────────────────────────────────
if st.session_state.get("do_submit", False):
    st.markdown(
        f"""
        <div style="text-align:center; padding:32px 20px; margin:0 0 24px 0; background:linear-gradient(135deg,#1565c0,#0d47a1);
        border-radius:12px; color:#fff; box-shadow:0 4px 20px rgba(0,0,0,0.2);">
        <div style="font-size:28px; font-weight:bold; margin-bottom:8px;">⏳ {L('sending_banner')}</div>
        <div style="font-size:16px; opacity:0.95;">{L('sending_banner_sub')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if not st.session_state.get("do_submit", False):
    st.caption("💡 " + L("session_hint"))
    # ──────────────────────────────────────────────
    # Draft（長時間入力対策：こまめに保存を推奨）
    # ──────────────────────────────────────────────
    draft_enabled = get_secret("DRAFT_ENABLED", "").lower() in ("true", "1", "yes")
    if draft_enabled:
        with st.expander(f"📋 {L('draft_section')}（{L('draft_save')} / {L('draft_load')}）", expanded=False):
            note_text = L("draft_note")
            st.markdown(
                f"<div style='font-size:14px; color:#b71c1c; margin:8px 0; padding:10px; "
                f"background:#ffebee; border-radius:6px;'>⚠️ {note_text}</div>",
                unsafe_allow_html=True,
            )
            draft_name_input = st.text_input(
                L("draft_name"),
                value=st.session_state.get("store_name", ""),
                key="draft_name_input",
            )
            col_save, col_load = st.columns(2)
            with col_save:
                if st.button(L("draft_save"), use_container_width=True, type="primary"):
                    if draft_name_input.strip():
                        saved = _save_draft(draft_name_input.strip())
                        st.success(L("draft_saved").format(name=saved))
                    else:
                        st.warning(L("required_store"))
            with col_load:
                drafts = _drafts_list()
                if drafts:
                    chosen = st.selectbox(L("draft_select"), drafts, key="draft_choice", label_visibility="collapsed")
                    load_col, del_col = st.columns(2)
                    with load_col:
                        if st.button(L("draft_load"), use_container_width=True):
                            draft = _load_draft(chosen)
                            if draft:
                                _apply_draft(draft)
                                st.rerun()
                    with del_col:
                        if st.button(L("draft_delete"), use_container_width=True):
                            _delete_draft(chosen)
                            st.rerun()
                else:
                    st.info(L("draft_none"))

    # ──────────────────────────────────────────────
    # Step 1: Basic Information
    # ──────────────────────────────────────────────
    st.header(L("step1"))
    store_name = st.text_input(L("store_name"), key="store_name")
    phone = st.text_input(L("phone"), key="phone")
    category = st.selectbox(
        L("category"),
        options=CATEGORY_OPTIONS,
        key="category",
    )
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

    # 日本に来るムスリム観光客に多い言語（6つ）
    language_options = ["Arabic", "Chinese", "English", "Indonesian", "Malay", "Urdu"]
    languages = st.multiselect(L("languages_available"), language_options, key="languages")

    wifi_options = [L("wifi_available"), L("wifi_not_available")]
    wifi = st.radio(L("wifi"), wifi_options, key="wifi_radio", horizontal=True)

    # 観光客向け（Suica/PASMO等の国内決済は除外）
    payment_options = [
        "Cash", "Visa", "Mastercard", "JCB", "American Express",
        "Alipay", "WeChat Pay", "UnionPay", "Apple Pay", "Google Pay", "Other",
    ]
    st.caption(L("required_payment"))
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
    st.markdown(f"**📐 {L('recommended_top')}**")
    top_cols = st.columns(3)
    top_photos = []
    for i in range(3):
        with top_cols[i]:
            f = st.file_uploader(
                L("top_n").format(n=i + 1),
                type=["jpg", "jpeg", "png", "webp"],
                key=f"top_photo_{i}",
            )
            f = maybe_compress(f, f"comp_top_{i}")
            top_photos.append(f)
            if f:
                display_image_with_orientation(f)

    st.subheader(L("cert_photos"))
    st.markdown(f"**📐 {L('recommended_vert')}**")
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
            f = maybe_compress(f, f"comp_cert_{i}")
            cert_photos.append(f)
            if f:
                display_image_with_orientation(f)

    st.divider()

    # ──────────────────────────────────────────────
    # Step 5: Highlights
    # ──────────────────────────────────────────────
    st.header(L("step5"))
    st.caption(L("highlights_min"))
    st.markdown(f"**📐 {L('recommended_vert')}**")
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
            h_photo = maybe_compress(h_photo, f"comp_hl_{i}")
            if h_photo:
                display_image_with_orientation(h_photo)
            h_title = st.text_input(L("highlight_title"), key=f"highlight_title_{i}")
            h_desc = st.text_area(L("highlight_desc"), key=f"highlight_desc_{i}")
            highlights.append({"photo": h_photo, "title": h_title, "description": h_desc})

    st.divider()

    # ──────────────────────────────────────────────
    # Step 6: Menu Information
    # ──────────────────────────────────────────────
    st.header(L("step6"))
    st.caption(L("menu_min"))
    st.markdown(f"**📐 {L('recommended_vert')}**")
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
            m_photo = maybe_compress(m_photo, f"comp_menu_{i}")
            if m_photo:
                display_image_with_orientation(m_photo)
            m_name = st.text_input(L("menu_name"), key=f"menu_name_{i}")
            m_desc = st.text_area(L("menu_desc"), key=f"menu_desc_{i}")
            menus.append({"photo": m_photo, "name": m_name, "description": m_desc})

    st.divider()

    # ──────────────────────────────────────────────
    # Step 7: Interior / Exterior Photos
    # ──────────────────────────────────────────────
    st.header(L("step7"))
    st.caption(L("interior_min"))
    st.markdown(f"**📐 {L('recommended_vert')}**")
    interior_photos = []
    int_cols = st.columns(5)
    for i in range(5):
        with int_cols[i]:
            f = st.file_uploader(
                L("interior_n").format(n=i + 1),
                type=["jpg", "jpeg", "png", "webp"],
                key=f"interior_photo_{i}",
            )
            f = maybe_compress(f, f"comp_int_{i}")
            interior_photos.append(f)
            if f:
                display_image_with_orientation(f)

    st.divider()

# ──────────────────────────────────────────────
# Step 8: Confirm & Submit
# ──────────────────────────────────────────────
st.header(L("step8"))

# 確認モード・送信フラグの初期化
if "confirm_mode" not in st.session_state:
    st.session_state.confirm_mode = False
if "do_submit" not in st.session_state:
    st.session_state.do_submit = False

# 編集に戻る
if st.session_state.confirm_mode and st.button(L("back_edit"), use_container_width=True):
    st.session_state.confirm_mode = False
    st.session_state.do_submit = False
    st.rerun()

# 確認画面表示（confirm_mode かつ do_submit でないとき）
if st.session_state.confirm_mode and not st.session_state.do_submit:
    st.subheader(L("confirm_title"))
    st.info(L("confirm_desc"))

    data = st.session_state.get("_submit_data", {})
    summary_title = (data.get("store_name", "") or ("Store" if st.session_state.lang == "en" else "店舗"))
    with st.expander(f"📋 {summary_title} - Summary", expanded=True):
        st.write("**" + L("store_name") + ":**", data.get("store_name", ""))
        st.write("**" + L("phone") + ":**", data.get("phone", ""))
        st.write("**" + L("category") + ":**", data.get("category", ""))
        st.write("**" + L("email") + ":**", data.get("email", ""))
        st.write("**" + L("business_hours") + ":**", data.get("business_hours", "") or "-")
        st.write("**" + L("halal_level") + ":**", data.get("halal_level_display", ""))
        n_hl = sum(1 for h in data.get("highlights", []) if h.get("photo") and h.get("title") and h.get("description"))
        n_menu = sum(1 for m in data.get("menus", []) if m.get("photo") and m.get("name"))
        n_int = sum(1 for f in data.get("interior_photos", []) if f)
        st.write("**" + L("step5") + ":**", n_hl, "sets" if st.session_state.lang == "en" else "セット")
        st.write("**" + L("step6") + ":**", n_menu, "items" if st.session_state.lang == "en" else "件")
        st.write("**" + L("step7") + ":**", n_int, "photos" if st.session_state.lang == "en" else "枚")

    st.info("⏳ " + L("before_submit_msg"))
    submit_clicked = st.button(L("confirm_submit"), type="primary", use_container_width=True)
    if submit_clicked:
        # 送信ボタン押下後すぐに送信フラグを立ててrerun → 次フレームで送信中バナーを表示してから送信開始
        st.session_state.do_submit = True
        st.rerun()
    st.markdown(
        f"<div style='font-size:15px; color:#1565c0; margin-top:12px; padding:14px; "
        f"background:#e3f2fd; border-radius:8px; border-left:6px solid #1565c0;'>"
        f"⏳ {L('after_submit_click_msg')}</div>",
        unsafe_allow_html=True,
    )

    st.stop()

# 実際の送信処理（do_submit が True のとき）
if st.session_state.do_submit:
    data = st.session_state.get("_submit_data", {})
    if data:
        try:
            with st.status(L("sending_msg"), state="running", expanded=True):
                store_name = data.get("store_name", "")
                phone = data.get("phone", "")
                category = data.get("category", "")
                contact_name = data.get("contact_name", "")
                email = data.get("email", "")
                business_hours = data.get("business_hours", "")
                regular_holiday = data.get("regular_holiday", "")
                nearest_station = data.get("nearest_station", "")
                languages = data.get("languages", [])
                wifi = data.get("wifi", "")
                payment_methods = data.get("payment_methods", [])
                halal_level = data.get("halal_level", "")
                prep_transparency = data.get("prep_transparency", "")
                top_photos = data.get("top_photos") or []
                cert_photos = data.get("cert_photos") or []
                highlights = data.get("highlights") or []
                menus = data.get("menus") or []
                interior_photos = data.get("interior_photos") or []

                # 必須データのチェック（セッション切れ等でファイルが無効化された場合）
                if not top_photos or len(top_photos) < 3:
                    raise ValueError(L("session_expired_photos"))

                # 送信処理（既存ロジック）
                store_slug = slugify(store_name, allow_unicode=False) or "store"
            zip_buffer = io.BytesIO()
            image_manifest = []

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                processed_tops = []
                for i, f in enumerate(top_photos):
                    f.seek(0)
                    img = process_top_photo(f)
                    processed_tops.append(img)
                    fname = f"{store_slug}_top_{i+1}.webp"
                    zf.writestr(f"{store_slug}/images/{fname}", image_to_webp_bytes(img))
                    image_manifest.append({"type": "top", "file": fname})

                thumb = generate_thumbnail(processed_tops)
                thumb_name = f"{store_slug}_thumb.webp"
                zf.writestr(f"{store_slug}/images/{thumb_name}", image_to_webp_bytes(thumb))
                image_manifest.append({"type": "thumbnail", "file": thumb_name})

                for i, f in enumerate(cert_photos):
                    if f:
                        f.seek(0)
                        img = process_cert_photo(f)
                        fname = f"{store_slug}_cert_{i+1}.webp"
                        zf.writestr(f"{store_slug}/images/{fname}", image_to_webp_bytes(img))
                        image_manifest.append({"type": "certification", "file": fname})

                commitment_data = []
                for i, h in enumerate(highlights):
                    if h["photo"] and h["title"].strip() and h["description"].strip():
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

                for i, f in enumerate(interior_photos):
                    if f:
                        f.seek(0)
                        img = process_interior_photo(f)
                        fname = f"{store_slug}_interior_{i+1}.webp"
                        zf.writestr(f"{store_slug}/images/{fname}", image_to_webp_bytes(img))
                        image_manifest.append({"type": "interior", "file": fname})

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

                data_json = {
                    "store_name": store_name,
                    "phone": phone,
                    "category": category,
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
                json_bytes = json.dumps(data_json, ensure_ascii=False, indent=2).encode("utf-8")
                zf.writestr(f"{store_slug}/data.json", json_bytes)

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

            # ローカル保存（Streamlit Cloud等では書き込み不可のためスキップ）
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                submission_dir = os.path.join("submissions", f"{timestamp}_{store_slug}")
                os.makedirs(os.path.join(submission_dir, "images"), exist_ok=True)
                zip_buffer.seek(0)
                with zipfile.ZipFile(zip_buffer, "r") as zf:
                    zf.extractall(submission_dir)
                zip_buffer.seek(0)
            except OSError:
                pass  # クラウド環境ではスキップ

            active_url = webhook_url.strip()
            if active_url:
                try:
                    gs_resp = send_to_google(active_url, data_json, gs_images)
                    if gs_resp.get("status") == "success":
                        st.session_state["_submission_result"] = "success"
                    else:
                        st.session_state["_submission_result"] = "error"
                        st.session_state["_submission_message"] = L("gs_error").format(
                            err=gs_resp.get("message", "Unknown error"))
                except Exception as exc:
                    st.session_state["_submission_result"] = "error"
                    st.session_state["_submission_message"] = L("gs_error").format(err=str(exc)[:200])
            else:
                st.session_state["_submission_result"] = "success"

        except Exception as exc:
            err_msg = str(exc)[:300] if exc else "Unknown error"
            st.session_state["_submission_result"] = "error"
            st.session_state["_submission_message"] = L("gs_error").format(err=err_msg)
        finally:
            st.session_state.confirm_mode = False
            st.session_state.do_submit = False
            if "_submit_data" in st.session_state:
                del st.session_state["_submit_data"]
        st.rerun()
    st.stop()

# 確認前メッセージ & 確認ボタン（通常フロー）
st.info("📋 " + L("before_confirm_msg"))
confirm_clicked = st.button(L("confirm_and_submit"), type="primary", use_container_width=True)
if confirm_clicked:
    st.markdown(
        f"<div style='font-size:14px; color:#1565c0; margin-top:8px; padding:10px; "
        f"background:#e3f2fd; border-radius:6px; border-left:4px solid #1565c0;'>"
        f"⏳ {L('after_confirm_click_msg')}</div>",
        unsafe_allow_html=True,
    )
    errors = []

    if not store_name.strip():
        errors.append(L("required_store"))
    if not phone.strip():
        errors.append(L("required_phone"))
    if not email.strip():
        errors.append(L("required_email"))
    elif not is_valid_email(email):
        errors.append(L("invalid_email"))

    if not payment_methods:
        errors.append(L("required_payment"))

    if not all(top_photos):
        errors.append(L("required_top3"))

    # Highlights: 最低1セット（写真+タイトル+説明）
    complete_highlights = [h for h in highlights if h["photo"] and h["title"].strip() and h["description"].strip()]
    if not complete_highlights:
        errors.append(L("required_highlights"))

    # Menu: 最低1つ（写真+名前）
    complete_menus = [m for m in menus if m["photo"] and m["name"].strip()]
    if not complete_menus:
        errors.append(L("menu_min"))

    # Interior: 最低1枚
    if not any(interior_photos):
        errors.append(L("interior_min"))

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
        # 確認モードへ：データを保存して確認画面表示
        with st.spinner(L("processing_msg")):
            st.session_state["_submit_data"] = {
                "store_name": store_name,
                "phone": phone,
                "category": category,
                "contact_name": contact_name,
                "email": email,
                "business_hours": business_hours,
                "regular_holiday": regular_holiday,
                "nearest_station": nearest_station,
                "languages": languages,
                "wifi": wifi,
                "payment_methods": payment_methods,
                "halal_level": halal_level,
                "halal_level_display": halal_level,
                "prep_transparency": prep_transparency,
                "top_photos": top_photos,
                "cert_photos": cert_photos,
                "highlights": highlights,
                "menus": menus,
                "interior_photos": interior_photos,
            }
            st.session_state.confirm_mode = True
            st.rerun()
