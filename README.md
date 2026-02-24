# Halal Restaurant Store Registration App

ハラル対応レストラン向け 店舗情報登録・画像自動加工Webアプリ

## ローカルでの起動（テスト用）

```bash
pip install -r requirements.txt
```

`.streamlit/secrets.toml.example` を `.streamlit/secrets.toml` にコピーして値を設定：

```bash
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```

```bash
streamlit run app.py
```

---

## 外部公開する方法（Streamlit Community Cloud）

あなたの PC を起動していなくても 24 時間アクセスできるようになります。無料です。

### Step 1: GitHub にリポジトリを作成

1. [GitHub](https://github.com) にログイン
2. 右上の **「+」→「New repository」**
3. Repository name: `halal-store-app`（任意）
4. **Private** を選択（公開したくない場合）
5. 「Create repository」をクリック

### Step 2: コードを GitHub にアップロード

コマンドプロンプトで以下を実行：

```bash
cd C:\Users\siwat\halal-store-app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/halal-store-app.git
git push -u origin main
```

> **重要**: `.gitignore` により `secrets.toml` は Git に含まれません（安全）。

### Step 3: Streamlit Community Cloud にデプロイ

1. [share.streamlit.io](https://share.streamlit.io) にアクセス
2. GitHub アカウントでログイン
3. **「New app」** をクリック
4. 設定：
   - Repository: `あなたのユーザー名/halal-store-app`
   - Branch: `main`
   - Main file path: `app.py`
5. **「Advanced settings」→「Secrets」** を開く
6. 以下を貼り付け（値は実際のものに書き換え）：

```toml
WEBHOOK_URL = "https://script.google.com/macros/s/あなたのスクリプトID/exec"
ACCESS_CODE = "store-owner-2026"

# 入力マニュアルのリンク（任意・設定するとアプリ上部に表示）
MANUAL_URL = "https://github.com/あなたのユーザー名/halal-store-app/blob/main/INPUT_MANUAL.md"
```

7. **「Deploy!」** をクリック

### Step 4: URL を共有

デプロイ完了後、以下のような URL が発行されます：

```
https://あなたのアプリ名.streamlit.app
```

この URL を店舗オーナーにアクセスコードと一緒に共有してください。

---

## セキュリティ対策

### Fork・GitHubアイコンを非表示にする（外部利用者向け）

**Fork ボタンと GitHub アイコン**は、リポジトリが **Public** のときのみ表示されます。外部の方に入力してもらう場合は、**GitHub リポジトリを Private に変更**してください。

1. GitHub でリポジトリを開く
2. **Settings** → **General** → **Danger Zone**
3. **Change repository visibility** → **Make private**

※ Streamlit Community Cloud の無料プランでは、Private リポジトリからデプロイできるアプリは **1つまで** です。

| 対策 | 説明 |
|------|------|
| **アクセスコード保護** | フォーム表示前にコード入力が必要。知らない人はフォームを見ることもできない |
| **Webhook URL 秘匿** | secrets に保存。画面上に一切表示されない |
| **Private リポジトリ** | GitHub を Private にすればコードも非公開 |
| **HTTPS 通信** | Streamlit Cloud は自動で HTTPS。Google Apps Script も HTTPS |
| **.gitignore** | `secrets.toml` は Git に含まれない |
| **タイミング攻撃対策** | アクセスコード照合に `hmac.compare_digest` を使用 |

---

## Google Sheets & Drive 連携セットアップ

### Step 1: Google スプレッドシートを作成

1. [Google Sheets](https://sheets.google.com) で新しいスプレッドシートを作成

### Step 2: Apps Script を設定

1. **拡張機能 → Apps Script** を開く
2. 既存のコードを削除し、`google_apps_script.js` の全内容を貼り付けて保存
3. 関数セレクタで **`setupSheet`** を選択 → **▶ 実行**
4. 初回は権限の承認が必要（「許可」をクリック）

### Step 3: Web App としてデプロイ

1. **デプロイ → 新しいデプロイ**
2. 種類: **ウェブアプリ**
3. 次のユーザーとして実行: **自分** / アクセスできるユーザー: **全員**
4. **デプロイ** → 表示された URL をコピー

### Step 4: Secrets に URL を登録

- ローカル: `.streamlit/secrets.toml` の `WEBHOOK_URL` に貼り付け
- Cloud: Streamlit Cloud の **App Settings → Secrets** に貼り付け

---

## データの流れ

```
店舗オーナーがブラウザでアクセス
    ↓
アクセスコード入力 → 認証OK
    ↓
フォーム入力 → 送信
    ↓
┌─ Google Sheets: 1行追加（店名・電話・メール等）
├─ Google Drive:  フォルダ作成 → data.json + 画像
└─ ブラウザ: ZIP ダウンロード
```

## ファイル構成

```
halal-store-app/
├── app.py                          # メインアプリ
├── google_apps_script.js           # Google側に設置するスクリプト
├── requirements.txt                # 依存パッケージ
├── .gitignore                      # secrets等を除外
├── .streamlit/
│   └── secrets.toml.example        # 設定テンプレート
└── README.md
```
