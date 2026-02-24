# Render へのデプロイ手順

Streamlit Cloud と異なり、**Fork ボタンや GitHub アイコンが表示されません**。外部のお客様向けにクリーンな画面で提供できます。

---

## 前提条件

- GitHub に halal-store-app のコードがプッシュ済み
- Google Apps Script の Webhook URL が準備済み

---

## Step 1: Render アカウント作成

1. [render.com](https://render.com) にアクセス
2. **「Get Started for Free」** をクリック
3. **「Sign up with GitHub」** で GitHub アカウントと連携

---

## Step 2: 新規 Web Service 作成

1. Render ダッシュボードで **「New +」→「Web Service」** をクリック
2. **「Build and deploy from a Git repository」** を選択
3. **「Connect account」** または **「Configure account」** で GitHub を連携（未連携の場合）
4. リポジトリ一覧から **「halal-store-app」** を選択して **「Connect」**

---

## Step 3: 設定を入力

| 項目 | 入力内容 |
|------|----------|
| **Name** | `halal-store-app`（任意） |
| **Region** | **Singapore**（日本から近い） |
| **Branch** | `main` |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true` |
| **Instance Type** | **Free**（無料） |

---

## Step 4: 環境変数を設定

**「Advanced」** を開き、**「Add Environment Variable」** で以下を追加：

| Key | Value | 必須 |
|-----|-------|------|
| `WEBHOOK_URL` | Google Apps Script の Web App URL | ○ |
| `ACCESS_CODE` | アクセスコード（例：store-owner-2026） | ○ |
| `MANUAL_URL` | 入力マニュアルのURL（Canva/Google Drive等） | 任意 |
| `DRAFT_ENABLED` | `true` で下書き機能を表示 | 任意（未設定=非表示） |

※`MANUAL_URL` は空欄でも動作します。設定するとアプリ上部にリンクが表示されます。  
※`DRAFT_ENABLED` を `true` にすると、下書きの保存・読み込み機能が表示されます。

---

## Step 5: デプロイ実行

1. **「Create Web Service」** をクリック
2. ビルド・デプロイが自動で開始（3〜5分程度）
3. 完了後、**「Your service is live at ○○○.onrender.com」** の URL が表示される

---

## Step 6: 動作確認

1. 表示された URL をブラウザで開く
2. アクセスコードを入力してフォームが表示されるか確認
3. **画面下部に Streamlit / GitHub のアイコンが表示されていない**ことを確認

---

## 注意事項

### 無料プランの制限

- **スリープ**：15分間アクセスがないとスリープ。次回アクセス時に 30秒〜1分かかることがある
- **月750時間**：無料枠の範囲内で利用可能

### スリープ防止（UptimeRobot）

Streamlit Cloud と同様、[UptimeRobot](https://uptimerobot.com) で 5分ごとに URL にアクセスすると、スリープを防げます。

### 下書き・送信データ

- **下書き**：Render の無料プランでは再起動時に消える場合があります
- **送信データ**：Google Sheets / Google Drive に保存されるため問題ありません

---

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| デプロイが失敗する | **Logs** でエラー内容を確認。`requirements.txt` の依存関係を確認 |
| アプリが起動しない | Start Command に `--server.port=$PORT` が含まれているか確認 |
| 環境変数が反映されない | 設定後、**「Manual Deploy」→「Deploy latest commit」** で再デプロイ |
