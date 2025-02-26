# Gym Diary API ドキュメント

## 📌 認証 API

### ✅ 会員登録（メンバー / トレーナー）

- **エンドポイント:** `POST /api/account/register/`
- **リクエスト**

```json
{
  "username": "test_user",
  "name": "テストユーザー",
  "password": "password123",
  "role": "member"
}
```

- **レスポンス**

```json
{
  "id": 1,
  "username": "test_user",
  "name": "テストユーザー"
}
```

- **ステータスコード**
