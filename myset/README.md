# MySet API

マイセットの取得、作成、更新、削除を行うAPIです。

## エンドポイント

- `GET /api/mysets/` - マイセット一覧取得
- `POST /api/mysets/` - マイセット作成
- `GET /api/mysets/{id}/` - マイセット詳細取得
- `PUT /api/mysets/{id}/` - マイセット更新
- `PATCH /api/mysets/{id}/` - マイセット部分更新
- `DELETE /api/mysets/{id}/` - マイセット削除

## 認証

すべてのエンドポイントで認証が必要です。JWTトークンをAuthorizationヘッダーに含めてください。

```
Authorization: Bearer <your_jwt_token>
```

## データ構造

### マイセット作成・更新のリクエスト例

```json
{
  "name": "胸筋トレーニング",
  "description": "胸筋を重点的に鍛えるメニュー",
  "exercises": [
    {
      "name": "ベンチプレス",
      "order": 1,
      "sets": [
        {
          "order": 1,
          "weight": 60.0,
          "reps": 10
        },
        {
          "order": 2,
          "weight": 65.0,
          "reps": 8
        },
        {
          "order": 3,
          "weight": 70.0,
          "reps": 6
        }
      ]
    },
    {
      "name": "インクラインダンベルプレス",
      "order": 2,
      "sets": [
        {
          "order": 1,
          "weight": 22.5,
          "reps": 12
        },
        {
          "order": 2,
          "weight": 25.0,
          "reps": 10
        }
      ]
    },
    {
      "name": "ランニング",
      "order": 3,
      "sets": [
        {
          "order": 1,
          "distance": 5.0,
          "distance_unit": "km",
          "duration": 1800,
          "duration_unit": "sec",
          "fat_burn": 300.0,
          "memo": "ウォームアップとして"
        }
      ]
    }
  ]
}
```

### レスポンス例

```json
{
  "id": 1,
  "name": "胸筋トレーニング",
  "description": "胸筋を重点的に鍛えるメニュー",
  "exercises": [
    {
      "name": "ベンチプレス",
      "order": 1,
      "sets": [
        {
          "order": 1,
          "weight": 60.0,
          "reps": 10,
          "distance": null,
          "distance_unit": null,
          "duration": null,
          "duration_unit": null,
          "fat_burn": null,
          "memo": null
        },
        {
          "order": 2,
          "weight": 65.0,
          "reps": 8,
          "distance": null,
          "distance_unit": null,
          "duration": null,
          "duration_unit": null,
          "fat_burn": null,
          "memo": null
        },
        {
          "order": 3,
          "weight": 70.0,
          "reps": 6,
          "distance": null,
          "distance_unit": null,
          "duration": null,
          "duration_unit": null,
          "fat_burn": null,
          "memo": null
        }
      ]
    },
    {
      "name": "インクラインダンベルプレス",
      "order": 2,
      "sets": [
        {
          "order": 1,
          "weight": 22.5,
          "reps": 12,
          "distance": null,
          "distance_unit": null,
          "duration": null,
          "duration_unit": null,
          "fat_burn": null,
          "memo": null
        },
        {
          "order": 2,
          "weight": 25.0,
          "reps": 10,
          "distance": null,
          "distance_unit": null,
          "duration": null,
          "duration_unit": null,
          "fat_burn": null,
          "memo": null
        }
      ]
    },
    {
      "name": "ランニング",
      "order": 3,
      "sets": [
        {
          "order": 1,
          "weight": null,
          "reps": null,
          "distance": 5.0,
          "distance_unit": "km",
          "duration": 1800,
          "duration_unit": "sec",
          "fat_burn": 300.0,
          "memo": "ウォームアップとして"
        }
      ]
    }
  ],
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

## セキュリティ

- すべての操作はログインユーザーのデータのみを対象とします
- 他のユーザーのマイセットにはアクセスできません
- 同じ名前のマイセットの作成は禁止されています

## バリデーション

- セット名は必須です
- 少なくとも1つの種目を含む必要があります
- 種目の順番とセットの順番は1以上で重複不可です
- 重量、回数、距離、時間、脂肪燃焼は0以上の値である必要があります

## エラー例

### 401 Unauthorized
```json
{
  "detail": "認証情報が提供されていません。"
}
```

### 400 Bad Request
```json
{
  "name": ["同じ名前のマイセットが既に存在します。"]
}
```

### 403 Forbidden
```json
{
  "detail": "このマイセットにはアクセスできません。"
}
```

### 404 Not Found
```json
{
  "detail": "見つかりませんでした。"
}
```