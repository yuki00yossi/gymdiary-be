# Exercise API

エクササイズの取得と管理を行うAPIです。公式エクササイズとユーザーカスタムエクササイズを統合して管理します。

## エンドポイント

### エクササイズ管理（統合版）
- `GET /api/exercises/exercises/` - 部位別エクササイズ一覧取得
- `POST /api/exercises/exercises/` - カスタムエクササイズ作成
- `GET /api/exercises/exercises/{id}/` - エクササイズ詳細取得
- `PUT /api/exercises/exercises/{id}/` - エクササイズ更新（カスタムのみ）
- `PATCH /api/exercises/exercises/{id}/` - エクササイズ部分更新（カスタムのみ）
- `DELETE /api/exercises/exercises/{id}/` - エクササイズ削除（カスタムのみ）

### カテゴリ管理
- `GET /api/exercises/categories/` - エクササイズカテゴリ一覧取得

## 認証

すべてのエンドポイントで認証が必要です。JWTトークンをAuthorizationヘッダーに含めてください。

```
Authorization: Bearer <your_jwt_token>
```

## データ構造

### 部位別エクササイズ一覧取得のレスポンス例

```json
{
  "よく使う": [
    {
      "id": 1,
      "name": "ベンチプレス",
      "description": "バーベルを使った基本的な胸のトレーニング",
      "type": "official"
    },
    {
      "id": 101,
      "name": "マイカスタムエクササイズ",
      "description": "自分で作成したエクササイズ",
      "type": "user"
    }
  ],
  "胸": [
    {
      "id": 101,
      "name": "マイカスタムエクササイズ",
      "description": "自分で作成したエクササイズ",
      "type": "user"
    },
    {
      "id": 1,
      "name": "ベンチプレス",
      "description": "バーベルを使った基本的な胸のトレーニング",
      "type": "official"
    },
    {
      "id": 2,
      "name": "ダンベルプレス",
      "description": "ダンベルを使った胸のトレーニング",
      "type": "official"
    }
  ]
}
```

### カスタムエクササイズ作成・更新のリクエスト例

```json
{
  "name": "マイカスタムエクササイズ",
  "description": "自分で作成したオリジナルエクササイズ",
  "category": 1
}
```

### エクササイズのレスポンス例

```json
{
  "id": 101,
  "name": "マイカスタムエクササイズ",
  "description": "自分で作成したオリジナルエクササイズ",
  "category": 1,
  "category_name": "胸",
  "exercise_type": "user",
  "is_official": false,
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

### カテゴリ一覧のレスポンス例

```json
[
  {"id": 1, "name": "胸"},
  {"id": 2, "name": "背中"},
  {"id": 3, "name": "肩"},
  {"id": 4, "name": "腕"},
  {"id": 5, "name": "脚"},
  {"id": 6, "name": "腹筋"},
  {"id": 7, "name": "有酸素"},
  {"id": 8, "name": "その他"}
]
```

## 特徴

### エクササイズの統合管理
- **公式エクササイズ**: システム提供のマスターデータ（`is_official: true`）
- **カスタムエクササイズ**: ユーザーが作成したオリジナル（`is_official: false`）
- 1つのテーブル、1つのAPIで統合管理

### よく使うエクササイズ
- ユーザーのトレーニング履歴を分析
- 使用頻度の高いエクササイズを上位4つ表示
- 公式・カスタム問わず対象

### ユーザー追加分の優先表示
- 部位別一覧でユーザーが作成したエクササイズを上位に表示
- より使いやすいUXを提供

### エクササイズタイプ
- `official`: システム提供の公式エクササイズ
- `user`: ユーザーが作成したカスタムエクササイズ

## セキュリティ

- すべての操作はログインユーザーのデータのみを対象とします
- 公式エクササイズは参照のみ可能（更新・削除不可）
- カスタムエクササイズは作成者のみが更新・削除可能
- 同じカテゴリに同じ名前のカスタムエクササイズの作成は禁止

## バリデーション

- エクササイズ名は必須です
- カテゴリの指定は必須です
- 同じカテゴリ内でカスタムエクササイズの名前重複は不可
- 公式エクササイズの更新・削除は不可

## エラー例

### 400 Bad Request
```json
{
  "non_field_errors": ["同じカテゴリに同じ名前のエクササイズが既に存在します。"]
}
```

### 403 Forbidden
```json
{
  "detail": "公式エクササイズは更新できません。"
}
```

```json
{
  "detail": "このエクササイズにはアクセスできません。"
}
```

## 使用例

### 部位別エクササイズ取得
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://api.example.com/api/exercises/exercises/"
```

### カスタムエクササイズ作成
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"マイエクササイズ","description":"説明","category":1}' \
     "https://api.example.com/api/exercises/exercises/"
```

### WorkoutやMySetでの使用例

#### Workout作成時
```json
{
  "name": "胸筋トレーニング",
  "date": "2024-01-15",
  "workout_exercises": [
    {
      "exercise": 1,
      "order": 1,
      "workout_exercise_sets": [
        {"order": 1, "weight": 60.0, "reps": 10}
      ]
    }
  ]
}
```

#### MySet作成時
```json
{
  "name": "胸筋セット",
  "exercises": [
    {
      "exercise": 1,
      "order": 1,
      "sets": [
        {"order": 1, "weight": 60.0, "reps": 10}
      ]
    }
  ]
}
```

## マイグレーション

統合されたExerciseモデルへの移行手順：

1. マイグレーション実行
2. カテゴリと公式エクササイズの初期データ投入
3. 既存データの移行（必要に応じて）

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata exercise_categories exercises
```