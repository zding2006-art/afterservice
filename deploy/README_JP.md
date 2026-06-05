# アフターサービスデータ分析システム
## After-Sales Data Analysis System

**Water X Technologies** 社製のアフターサービス（售后）データ分析システムです。
Excel データをアップロードするだけで、自動的に分析レポートを生成します。

日本語 / 中文 / English の3言語に対応しています。

---

## 📦 ファイル構成

```
deploy/
├── start.sh                  # ワンクリック起動スクリプト（推奨）
├── backend/
│   ├── app.py                # Flask Web サーバー（メイン）
│   ├── analyzer.py           # 分析エンジン
│   ├── db.py                 # データベース管理
│   ├── insights.py           # AI 分析ロジック
│   ├── requirements.txt      # Python 依存パッケージ
│   └── uploads/              # アップロードファイル保存先
├── frontend/
│   ├── index.html            # Web フロントエンド
│   ├── i18n.js               # 多言語対応ファイル
│   └── logo.png              # 会社ロゴ
└── README_JP.md              # このファイル
```

---

## 🚀 デプロイ手順

### Step 1: サーバーを準備する

クラウドサーバー（VPS）を用意します。おすすめ：
- **さくらのVPS** / **ConoHa VPS** / **AWS EC2** / **Alibaba Cloud**

スペック目安：
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 2コア以上
- **RAM**: 2GB 以上
- **ディスク**: 20GB 以上

---

### Step 2: サーバーにログインする

ターミナル（Terminal）を開き、以下のコマンドでサーバーに接続します：

```bash
ssh root@<サーバーのIPアドレス>
```

（例：`ssh root@123.45.67.89`）

---

### Step 3: Python と依存パッケージをインストールする

```bash
# システムアップデート
apt update && apt upgrade -y

# Python と開発ツールをインストール
apt install -y python3 python3-pip python3-venv git curl

# 確認
python3 --version
```

---

### Step 4: プロジェクトをサーバーにアップロードする

#### 方法 A: ZIP ファイルでアップロード（簡単）

1. あなたのPCで `deploy/` フォルダを ZIP に圧縮
2. サーバーにアップロード：

```bash
# サーバー側で受信
mkdir -p /opt/shouhou
cd /opt/shouhou

# ZIP ファイルをアップロード（あなたのPCから）
# scp コマンドを使う場合：
# scp deploy.zip root@<サーバーIP>:/opt/shouhou/

# サーバー側で解凍
unzip deploy.zip -d ./
mv deploy/* ./ && rm -rf deploy deploy.zip
```

#### 方法 B: git clone（開発者向け）

```bash
cd /opt
git clone <リポジトリURL> shouhou
cd shouhou
# deploy フォルダの内容をルートにコピー
```

---

### Step 5: 起動する 🚀

```bash
cd /opt/shouhou
chmod +x start.sh

# デフォルトパスワード（waterx2026）で起動
./start.sh

# または、パスワードを変更して起動
# SHOUHOU_PASSWORD="mypassword" ./start.sh
```

初回起動時に仮想環境と依存パッケージが自動インストールされます。

---

### Step 6: ブラウザでアクセスする

ブラウザを開き、以下の URL にアクセス：

```
http://<サーバーのIPアドレス>:5859
```

例：`http://123.45.67.89:5859`

ログインページが表示されたら、パスワードを入力してください。

| 項目 | デフォルト値 |
|------|-------------|
| ユーザー名 | なし（パスワードのみ） |
| パスワード | `waterx2026` |
| ポート | `5859` |

---

### Step 7: ファイアウォール設定（重要）

サーバーのファイアウォールでポート 5859 を開放してください：

```bash
# UFW の場合
ufw allow 5859/tcp
ufw reload

# Alibaba Cloud / さくら の場合：管理コンソールのセキュリティグループで
# ポート 5859 の受信（Inbound）を許可してください
```

---

## 🌐 ドメイン設定（推奨）

ドメインがある場合、Nginx を使ってリバースプロキシを設定すると
ポート番号なしでアクセスできるようになります。

```bash
apt install -y nginx
```

`/etc/nginx/sites-available/shouhou` を作成：

```nginx
server {
    listen 80;
    server_name あなたのドメイン.com;

    location / {
        proxy_pass http://127.0.0.1:5859;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

有効化：

```bash
ln -s /etc/nginx/sites-available/shouhou /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

---

## 🔐 セキュリティ（重要）

本番運用時は以下の設定を推奨します：

1. **パスワード変更**
   ```bash
   export SHOUHOU_PASSWORD="強力なパスワード"
   ```

2. **HTTPS 設定**（Let's Encrypt 無料証明書）
   ```bash
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d あなたのドメイン.com
   ```

3. **セッションシークレット変更**
   ```bash
   export SHOUHOU_SECRET="ランダムな文字列"
   ```

4. **CORS 設定**（ドメインを指定）
   ```bash
   export CORS_ORIGINS="https://あなたのドメイン.com"
   ```

---

## 🔧 環境変数一覧

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `SHOUHOU_PASSWORD` | `waterx2026` | ログインパスワード |
| `SHOUHOU_SECRET` | `shouhou-analyzer-secret-2026` | セッション暗号化キー |
| `PORT` | `5859` | Web サーバーのポート番号 |
| `CORS_ORIGINS` | `http://localhost:5859,...` | 許可するオリジン（カンマ区切り） |

---

## 🛑 停止・再起動

```bash
# 実行中のプロセスを停止（Ctrl+C または）
pkill -f "python3 app.py"

# バックグラウンドで実行したい場合（tmux 使用）
tmux new -s shouhou
./start.sh
# Ctrl+B を押してから D でデタッチ
# 戻る: tmux attach -t shouhou
```

---

## 📝 システム仕様

- **分析対象**: 月次アフターサービスデータ（Excel .xlsx）
- **分析項目**: 13種類の自動分析（費用分析、機種別TOP10、部品分析、クレーム分析など）
- **多言語**: 日本語 / 中文 / English（ブラウザ自動判別）
- **データ保存**: SQLite（`backend/after_sales.db`）
- **データベースのバックアップ**: `after_sales.db` ファイルを定期的にコピーしてください

---

## ❓ よくある質問

**Q: パスワードを忘れた場合**
A: `start.sh` 内の `SHOUHOU_PASSWORD` を編集して再起動してください。

**Q: データベースをリセットしたい**
A: `backend/after_sales.db` を削除して再起動すると初期状態に戻ります。

**Q: サーバーを再起動したらシステムが起動しない**
A: 再度 `./start.sh` を実行してください。常時起動が必要な場合は systemd サービスの設定を推奨します。

**Q: アップロードしたファイルはどこに保存される？**
A: `backend/uploads/` フォルダに保存されます。

**Q: ログインすると「パスワードが間違っています: Failed to fetch」と表示される**
A: これはパスワードが間違っているのではなく、**フロントエンドがバックエンドに接続できない**場合に表示されるエラーです。
以下の順序で確認してください：

1. **サーバーが起動しているか確認**
   ```bash
   ps aux | grep python3
   # または
   curl http://localhost:5859/api/health
   # → {"status": "ok"} と返ってくれば正常
   ```

2. **ポートが開放されているか確認**
   ```bash
   ufw status
   # 5859 が ALLOW になっているか確認
   # なければ: ufw allow 5859/tcp && ufw reload
   ```

3. **Nginx を使っている場合は CORS が不要**（同一オリジン）
   Nginx でリバースプロキシを設定している場合は、
   ブラウザから見て「フロントエンド」と「API」が同じドメインになるため CORS は発生しません。

4. **直接 IP:ポートでアクセスしている場合**
   `http://サーバーIP:5859` でアクセスすれば、Flask が HTML も API も提供するため CORS は発生しません。
   `CORS_ORIGINS` の設定は不要です。

5. **上記で解決しない場合（デバッグ用）**
   ```bash
   CORS_ORIGINS="*" ./start.sh
   ```
   これで全てのオリジンを許可します（本番環境では非推奨）。

---

## 📧 サポート

**Water X Technologies**
- Email: ロダンCEOまでご連絡ください
- システムバージョン: V1.1（多言語対応版）

---

*© 2026 Water X Technologies. All rights reserved.*
*製造業とAIの融合 · Manufacturing × Artificial Intelligence*
