# Workout API

トレーニングセッションの取得、作成、更新、削除を行うAPIです。

## エンドポイント

- `GET /api/workouts/` - トレーニングセッション一覧取得
- `POST /api/workouts/` - トレーニングセッション作成
- `GET /api/workouts/{id}/` - トレーニングセッション詳細取得
- `PUT /api/workouts/{id}/` - トレーニングセッション更新
- `PATCH /api/workouts/{id}/` - トレーニングセッション部分更新
- `DELETE /api/workouts/{id}/` - トレーニングセッション削除

## 認証

すべてのエンドポイントで認証が必要です。JWTトークンをAuthorizationヘッダーに含めてください。

```
Authorization: Bearer <your_jwt_token>
```

## クエリパラメータ（一覧取得時）

- `date`: 特定の日付のセッションを取得（YYYY-MM-DD形式）
- `date_from`: 開始日（YYYY-MM-DD形式）
- `date_to`: 終了日（YYYY-MM-DD形式）

例：
```
GET /api/workouts/?date=2024-01-15
GET /api/workouts/?date_from=2024-01-01&date_to=2024-01-31
```

## データ構造

### トレーニングセッション作成・更新のリクエスト例

```json
{
  "name": "胸筋トレーニング",
  "date": "2024-01-15",
  "memo": "今日は調子が良かった",
  "workout_exercises": [
    {
      "name": "ベンチプレス",
      "order": 1,
      "workout_exercise_sets": [
        {
          "order": 1,
          "weight": 60.0,
          "reps": 10,
          "memo": "ウォームアップセット"
        },
        {
          "order": 2,
          "weight": 70.0,
          "reps": 8
        },
        {
          "order": 3,
          "weight": 75.0,
          "reps": 6
        }
      ]
    },
    {
      "name": "インクラインダンベルプレス",
      "order": 2,
      "workout_exercise_sets": [
        {
          "order": 1,
          "weight": 20.0,
          "reps": 12
        },
        {
          "order": 2,
          "weight": 22.5,
          "reps": 10
        },
        {
          "order": 3,
          "weight": 25.0,
          "reps": 8
        }
      ]
    },
    {
      "name": "ランニング",
      "order": 3,
      "workout_exercise_sets": [
        {
          "order": 1,
          "distance": 5.0,
          "distance_unit": "km",
          "duration": 1800,
          "duration_unit": "sec",
          "fat_burn": 300.0,
          "memo": "クールダウン"
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
  "date": "2024-01-15",
  "memo": "今日は調子が良かった",
  "workout_exercises": [
    {
      "name": "ベンチプレス",
      "order": 1,
      "workout_exercise_sets": [
        {
          "order": 1,
          "weight": 60.0,
          "reps": 10,
          "distance": null,
          "distance_unit": null,
          "duration": null,
          "duration_unit": null,
          "fat_burn": null,
          "memo": "ウォームアップセット"
        },
        {
          "order": 2,
          "weight": 70.0,
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
          "weight": 75.0,
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
      "workout_exercise_sets": [
        {
          "order": 1,
          "weight": 20.0,
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
          "weight": 22.5,
          "reps": 10,
          "distance": null,
          "distance_unit": null,
          "duration": null,
          "duration_unit": null,
          "fat_burn": null,
          "memo": null
        },
        {
          "order": 3,
          "weight": 25.0,
          "reps": 8,
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
      "workout_exercise_sets": [
        {
          "order": 1,
          "weight": null,
          "reps": null,
          "distance": 5.0,
          "distance_unit": "km",
          "duration": 1800,
          "duration_unit": "sec",
          "fat_burn": 300.0,
          "memo": "クールダウン"
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
- 他のユーザーのトレーニングセッションにはアクセスできません
- 同じ日に同じ名前のトレーニングセッションの作成は禁止されています

## バリデーション

- セッション名は必須です
- トレーニング日は必須です
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
  "non_field_errors": ["同じ日に同じ名前のトレーニングセッションが既に存在します。"]
}
```

### 403 Forbidden
```json
{
  "detail": "このトレーニングセッションにはアクセスできません。"
}
```

### 404 Not Found
```json
{
  "detail": "見つかりませんでした。"
}
```

## 使用例

### 今日のトレーニング記録を取得
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://api.example.com/api/workouts/?date=2024-01-15"
```

### 月間のトレーニング記録を取得
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://api.example.com/api/workouts/?date_from=2024-01-01&date_to=2024-01-31"
```

### 新しいトレーニングセッションを作成
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"胸筋トレーニング","date":"2024-01-15","workout_exercises":[...]}' \
     "https://api.example.com/api/workouts/"
```