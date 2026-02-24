# Halal Store App — User Manual / 使い方マニュアル

---

# English

## Overview

**Halal Store App** is a web application for Halal-certified restaurants to register their store information. It automatically processes and optimizes uploaded photos, saves data to Google Sheets, and stores images in Google Drive.

### Main Features

- **8-step registration form** — Basic info, business details, facilities, photos, highlights, menu, interior photos, and submission
- **Automatic image processing** — Photos are resized, enhanced, and converted to WebP format
- **Bilingual support** — English and 日本語 (Japanese)
- **Draft saving** — Save progress and continue later (text only; photos must be re-uploaded)
- **Access code protection** — Only users with the correct code can access the form
- **Google integration** — Data goes to Google Sheets; images go to Google Drive

---

## For Store Owners (End Users)

### 1. Accessing the App

1. Open the app URL (e.g. `https://your-app.streamlit.app`) in your browser
2. Enter the **access code** provided by the administrator
3. Click **Enter** (or **入力**)
4. If the code is correct, the registration form will appear

### 2. Language Selection

- Use the **Language** buttons at the top-right to switch between **English** and **日本語**
- All form labels and messages will change accordingly

### 3. Step-by-Step Guide

#### Step 1: Basic Information

| Field | Required | Description |
|-------|----------|-------------|
| Store Name (Google Maps Listing) | Yes | Exact name as shown on Google Maps |
| Store Phone Number | Yes | Contact number |
| Category | Yes | e.g. Ramen, Japanese Food, Café |
| Contact Person Name | No | Person responsible for this registration |
| Email Address | Yes | Valid email for correspondence |

#### Step 2: Business Information

| Field | Required | Description |
|-------|----------|-------------|
| Business Hours | No | e.g. "Mon–Sun 11:00–22:00" |
| Regular Holiday | No | e.g. "Tuesdays" |
| Nearest Station | No | e.g. "Shinjuku Station" |

#### Step 3: Facilities & Services

| Field | Required | Description |
|-------|----------|-------------|
| Languages Available | No | Arabic, Chinese, English, Indonesian, Malay, Urdu |
| Wi-Fi | No | Available or Not Available |
| Payment Methods | Yes (≥1) | Cash, Visa, Mastercard, Alipay, etc. |
| Halal Compliance Level | Yes | Fully Halal, Muslim-Friendly, Halal Menu, etc. |
| Preparation Transparency | Yes | Separate kitchen, utensils, dedicated area, etc. |

#### Step 4: Photo Upload

**Top Photos (3 required)** — Storefront, food, or interior  
- Recommended size: **480×480px** (processed as square)  
- Formats: JPG, PNG, WebP (max 10MB each)

**Certification Photos (up to 3)** — Required if "Fully Halal Certified"  
- Recommended size: **540×720px** (portrait)  
- Formats: JPG, PNG, WebP (max 10MB each)

#### Step 5: Highlights (≥1 set required)

Each highlight needs:
- **Photo** — Recommended 540×720px
- **Title** — Short heading
- **Description** — Detailed text

You can add up to 3 highlights.

#### Step 6: Menu Information (≥1 item required)

Each menu item needs:
- **Photo** — Recommended 540×720px
- **Menu Name** — Required
- **Menu Description** — Optional

You can add up to 3 menu items.

#### Step 7: Interior / Exterior Photos (≥1 required)

- Up to 5 photos allowed  
- Recommended size: 540×720px (portrait)

### 4. Draft Feature

- **Save Draft** — Enter a name (e.g. store name) and click to save your text and selections. Photos are **not** saved; you must re-upload them after loading.
- **Load Draft** — Select a saved draft from the list and click **Load Draft** to restore your data.
- **Delete** — Remove a draft you no longer need.

### 5. Submission Flow

1. Fill in all required fields and upload photos
2. Click **Confirm & Submit** (or **確認して送信**)
3. The app validates your input. If there are errors, fix them and try again
4. On success, a **confirmation screen** appears with a summary
5. Click **Submit** (or **送信する**) to send
6. **Wait 1–2 minutes** — Do not close the page
7. On success, you will see "Submission complete!!" — Data cannot be modified after submission

### 6. Image Requirements Summary

| Type | Count | Size | Format |
|------|-------|------|--------|
| Top Photos | 3 | 480×480 (square) | JPG, PNG, WebP |
| Certification | 0–3 | 540×720 (portrait) | JPG, PNG, WebP |
| Highlights | 1–3 | 540×720 | JPG, PNG, WebP |
| Menu | 1–3 | 540×720 | JPG, PNG, WebP |
| Interior | 1–5 | 540×720 | JPG, PNG, WebP |

**Max file size:** 10MB per image

---

## For Administrators

### Local Setup (Testing)

```bash
pip install -r requirements.txt
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# Edit .streamlit/secrets.toml with your values
streamlit run app.py
```

### Google Sheets & Drive Setup

1. Create a new [Google Spreadsheet](https://sheets.google.com)
2. Go to **Extensions → Apps Script**
3. Delete existing code and paste the contents of `google_apps_script.js`
4. Save, then run **`setupSheet`** once (approve permissions if prompted)
5. **Deploy → New deployment → Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
6. Copy the Web app URL and use it as `WEBHOOK_URL` in secrets

### Secrets Configuration

Create `.streamlit/secrets.toml` (or set in Streamlit Cloud):

```toml
WEBHOOK_URL = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"
ACCESS_CODE = "your-secret-access-code"
```

### Deploying to Streamlit Community Cloud

1. Push the code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. **New app** → Select your repo, branch `main`, main file `app.py`
4. In **Advanced settings → Secrets**, paste the same `secrets.toml` content
5. Deploy and share the app URL with store owners along with the access code

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Incorrect access code" | Verify the code with the administrator |
| "Submission failed" | Check internet connection; try again in 1–2 minutes |
| Photos not uploading | Ensure format is JPG/PNG/WebP and size ≤ 10MB |
| Page closed during submit | Data may not have been saved; re-enter and submit again |
| Draft loaded but photos missing | Photos are not saved in drafts; re-upload them |

---

---

# 日本語

## 概要

**Halal Store App** は、ハラル対応レストランが店舗情報を登録するためのWebアプリです。アップロードした写真を自動で加工し、データはGoogleスプレッドシートに、画像はGoogleドライブに保存されます。

### 主な機能

- **8ステップの登録フォーム** — 基本情報、店舗情報、設備・対応、写真、こだわり、メニュー、内観・外観、送信
- **画像の自動加工** — リサイズ、補正、WebP形式への変換
- **2言語対応** — 英語と日本語
- **下書き保存** — 途中で保存して後から続きを入力可能（テキストのみ。写真は再アップロードが必要）
- **アクセスコード保護** — 正しいコードを知る人のみフォームにアクセス可能
- **Google連携** — データはスプレッドシート、画像はドライブに保存

---

## 店舗オーナー向け（利用者）

### 1. アプリへのアクセス

1. ブラウザでアプリのURL（例：`https://your-app.streamlit.app`）を開く
2. 管理者から受け取った**アクセスコード**を入力
3. **入力**ボタンをクリック
4. コードが正しければ登録フォームが表示されます

### 2. 言語の切り替え

- 画面右上の**Language**ボタンで**English**と**日本語**を切り替えられます
- フォームのラベルやメッセージが選択した言語で表示されます

### 3. ステップ別ガイド

#### Step 1：基本情報

| 項目 | 必須 | 説明 |
|------|------|------|
| 店舗名（GoogleMap登録名） | ○ | Googleマップに表示されている正式な店舗名 |
| お店の電話番号 | ○ | 連絡先電話番号 |
| カテゴリー | ○ | ラーメン、日本料理、カフェなど |
| 担当者名 | - | 登録担当者の名前 |
| メールアドレス | ○ | 連絡用の有効なメールアドレス |

#### Step 2：店舗情報

| 項目 | 必須 | 説明 |
|------|------|------|
| 営業時間 | - | 例：「月〜日 11:00〜22:00」 |
| 定休日 | - | 例：「火曜日」 |
| 最寄り駅 | - | 例：「新宿駅」 |

#### Step 3：設備・対応

| 項目 | 必須 | 説明 |
|------|------|------|
| 対応言語 | - | アラビア語、中国語、英語、インドネシア語、マレー語、ウルドゥー語 |
| Wi-Fi | - | 利用可能 / 利用不可 |
| 決済方法 | ○（1つ以上） | 現金、Visa、Mastercard、Alipayなど |
| ハラル対応レベル | ○ | 完全ハラル認証、ムスリムフレンドリーなど |
| 調理配慮レベル | ○ | 専用キッチン、専用調理器具、専用エリアなど |

#### Step 4：写真アップロード

**TOP写真（3枚必須）** — 外観、料理、内観  
- 推奨サイズ：**480×480px**（加工後は正方形）  
- 形式：JPG、PNG、WebP（各最大10MB）

**認証写真（最大3枚）** — 「完全ハラル認証済み」の場合は必須  
- 推奨サイズ：**540×720px**（縦型）  
- 形式：JPG、PNG、WebP（各最大10MB）

#### Step 5：こだわり（1セット以上必須）

各こだわりには以下が必要です：
- **写真** — 推奨 540×720px
- **表題** — 短い見出し
- **こだわり説明** — 詳細な説明文

最大3セットまで登録できます。

#### Step 6：メニュー情報（1つ以上必須）

各メニューには以下が必要です：
- **写真** — 推奨 540×720px
- **メニュー名** — 必須
- **メニュー説明** — 任意

最大3品目まで登録できます。

#### Step 7：内観・外観写真（1枚以上必須）

- 最大5枚まで  
- 推奨サイズ：540×720px（縦型）

### 4. 下書き機能

- **下書き保存** — 下書き名（例：店舗名）を入力してボタンを押すと、テキストと選択内容を保存します。**写真は保存されません**。読み込み後に再度アップロードしてください。
- **下書き読み込み** — 一覧から保存済みの下書きを選び、**下書き読み込み**をクリックするとデータが復元されます。
- **削除** — 不要な下書きを削除できます。

### 5. 送信の流れ

1. 必須項目をすべて入力し、写真をアップロード
2. **確認して送信**ボタンをクリック
3. アプリが入力内容をチェック。エラーがあれば修正して再度実行
4. 成功すると**確認画面**が表示され、入力内容のサマリーが表示されます
5. **送信する**ボタンをクリックして送信
6. **1〜2分お待ちください** — ページを閉じないでください
7. 成功すると「送信が完了しました！！」と表示されます。送信後は修正できません

### 6. 画像要件まとめ

| 種類 | 枚数 | サイズ | 形式 |
|------|------|--------|------|
| TOP写真 | 3枚 | 480×480（正方形） | JPG、PNG、WebP |
| 認証写真 | 0〜3枚 | 540×720（縦型） | JPG、PNG、WebP |
| こだわり | 1〜3セット | 540×720 | JPG、PNG、WebP |
| メニュー | 1〜3品目 | 540×720 | JPG、PNG、WebP |
| 内観・外観 | 1〜5枚 | 540×720 | JPG、PNG、WebP |

**最大ファイルサイズ：** 1枚あたり10MB

---

## 管理者向け

### ローカルでの起動（テスト用）

```bash
pip install -r requirements.txt
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# .streamlit/secrets.toml を編集して値を設定
streamlit run app.py
```

### Googleスプレッドシート・ドライブの設定

1. [Googleスプレッドシート](https://sheets.google.com)で新規作成
2. **拡張機能 → Apps Script** を開く
3. 既存のコードを削除し、`google_apps_script.js` の内容を貼り付けて保存
4. **`setupSheet`** を1回実行（初回は権限の承認が必要）
5. **デプロイ → 新しいデプロイ → ウェブアプリ**
   - 次のユーザーとして実行：**自分**
   - アクセスできるユーザー：**全員**
6. 表示されたURLをコピーし、secretsの`WEBHOOK_URL`に設定

### シークレットの設定

`.streamlit/secrets.toml` を作成（またはStreamlit Cloudで設定）：

```toml
WEBHOOK_URL = "https://script.google.com/macros/s/あなたのスクリプトID/exec"
ACCESS_CODE = "あなたのアクセスコード"

# 入力マニュアルのリンク（任意・設定するとアプリ上部に表示）
MANUAL_URL = "https://github.com/あなたのユーザー名/halal-store-app/blob/main/INPUT_MANUAL.md"
```

### Streamlit Community Cloud へのデプロイ

1. コードをGitHubリポジトリにプッシュ
2. [share.streamlit.io](https://share.streamlit.io) にアクセスし、GitHubでログイン
3. **New app** → リポジトリ、ブランチ `main`、メインファイル `app.py` を選択
4. **Advanced settings → Secrets** で同じ `secrets.toml` の内容を貼り付け
5. デプロイ後、アプリURLとアクセスコードを店舗オーナーに共有

---

## トラブルシューティング

| 問題 | 対処法 |
|------|--------|
| 「アクセスコードが正しくありません」 | 管理者にコードを確認してください |
| 「送信に失敗しました」 | インターネット接続を確認し、1〜2分後に再試行 |
| 写真がアップロードできない | JPG/PNG/WebP形式で、10MB以下であることを確認 |
| 送信中にページを閉じた | データが保存されていない可能性があります。再度入力して送信してください |
| 下書きを読み込んだが写真がない | 写真は下書きに保存されません。再度アップロードしてください |
