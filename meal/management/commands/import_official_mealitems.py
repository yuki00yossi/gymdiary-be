""" 公式食品データをスプレッドシートからインポートするコマンド

このスクリプトは、Googleスプレッドシートから公式食品データをインポートし、Djangoのデータベースに保存します。
スプレッドシートのデータは、食品ID、食品名、カロリー、たんぱく質、脂質、炭水化物、単位、基準量を含みます。

1. Google Cloud APIの認証情報を取得し、`google_cloud_api_credentials.json`として保存する
2. スプレッドシートのIDとシート名を指定する
3. スプレッドシートからデータを取得し、`MealItem`モデルに保存する
4. 既存のデータは更新し、新しいデータは作成する
5. 結果を表示する
"""

import gspread
import os
from google.oauth2 import service_account
from django.conf import settings
from django.core.management.base import BaseCommand

import pprint

from accounts.models import CustomUser
from meal.models import MealItem


class Command(BaseCommand):
    help = 'スプレッドシートから公式MealItemをインポート（更新 or 作成）'

    def handle(self, *args, **kwargs):
        # --- Google認証設定 ---
        SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'accounts', 'auth', 'google_cloud_api_credentials.json')
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )

        client = gspread.authorize(credentials)
        # --- スプレッドシートのIDとシート名を指定 ---
        SPREADSHEET_ID = '1sy1rOzudorM_bkRVk7TZ-27VF3BMovj96kDQ0-h9YPk'
        SHEET_NAME = '食品マスタ'  # シート名を指定
        # --- スプレッドシートを開く ---
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        # --- データを取得 ---
        data = sheet.get_all_values()
        # --- ヘッダーを取得 ---
        headers = data[0]
        # --- データを辞書形式に変換 ---
        items = []
        for row in data[1:]:
            item = {headers[i]: row[i] for i in range(len(headers))}
            items.append(item)

        updated = 0
        created = 0

        for item in items:
            # --- 公式MealItemを作成 or 更新 ---
            try:
                mealItem = MealItem.objects.get(pk=item['食品ID'])
            except MealItem.DoesNotExist:
                mealItem = None

            def parse_float(value):
                try:
                    return float(value) if value not in ["", None] else None
                except ValueError:
                    return None

            data = {
                "name": item["食品名"],
                "calories": parse_float(item["カロリー"]),
                "protein": parse_float(item["たんぱく質(g)"]),
                "fat": parse_float(item["脂質(g)"]),
                "carbs": parse_float(item["炭水化物(g)"]),
                "unit": item["単位"],
                "base_quantity": item["基準量"],
                "created_by": CustomUser.objects.get(pk=1),
                "is_official": True,

                # 拡張栄養素
                "vitamin_a": parse_float(item["ビタミンA(μg)"]),
                "vitamin_d": parse_float(item["ビタミンD(μg)"]),
                "vitamin_e": parse_float(item["ビタミンE(mg)"]),
                "vitamin_k": parse_float(item["ビタミンK(μg)"]),
                "vitamin_b1": parse_float(item["ビタミンB1(mg)"]),
                "vitamin_b2": parse_float(item["ビタミンB2(mg)"]),
                "niacin": parse_float(item["ナイアシン(mg)"]),
                "vitamin_b6": parse_float(item["ビタミンB6(mg)"]),
                "vitamin_b12": parse_float(item["ビタミンB12(μg)"]),
                "folic_acid": parse_float(item["葉酸(μg)"]),
                "pantothenic_acid": parse_float(item["パントテン酸(mg)"]),
                "biotin": parse_float(item["ビオチン(μg)"]),
                "vitamin_c": parse_float(item["ビタミンC(mg)"]),
                "sodium": parse_float(item["ナトリウム(g)"]),
                "potassium": parse_float(item["カリウム(mg)"]),
                "calcium": parse_float(item["カルシウム(mg)"]),
                "magnesium": parse_float(item["マグネシウム(mg)"]),
                "phosphorus": parse_float(item["リン(mg)"]),
                "iron": parse_float(item["鉄(mg)"]),
                "zinc": parse_float(item["亜鉛(mg)"]),
                "copper": parse_float(item["銅(mg)"]),
                "manganese": parse_float(item["マンガン(mg)"]),
                "iodine": parse_float(item["ヨウ素(μg)"]),
                "selenium": parse_float(item["セレン(μg)"]),
                "chromium": parse_float(item["クロム(μg)"]),
                "molybdenum": parse_float(item["モリブデン(μg)"]),
                "cholesterol": parse_float(item["コレステロール(mg)"]),
                "dietary_fiber": parse_float(item["食物繊維(g)"]),
                "salt_equivalent": parse_float(item["食塩相当量(g)"]),
            }

            if mealItem:
                # 更新
                for key, value in data.items():
                    setattr(mealItem, key, value)
                mealItem.save()
                updated += 1
            else:
                data["id"] = item["食品ID"]
                print(f"Creating new item: {data}")
                # 作成
                MealItem.objects.create(**data)
                created += 1
        print(f"Created {created} items and updated {updated} items.")
        # --- 結果を表示 ---
