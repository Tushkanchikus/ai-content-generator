import json
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)


def handler(event, context):
    logging.info(f"Event: {event}")

    try:
        # ----- 1. ЧИТАЕМ ВХОДНЫЕ ДАННЫЕ -----
        # Вариант A: вызов через API Gateway → тело в event["body"]
        # Вариант B: тест "Без шаблона" → данные сразу в event
        if "body" in event:
            body = event["body"]
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
        else:
            data = event

        prompt = data.get("prompt", "").strip()

        if not prompt:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Нет промпта"})
            }

        # ----- 2. ЧИТАЕМ API_KEY ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ -----
        api_key = os.environ.get("API_KEY")
        if not api_key:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Нет API_KEY в переменных окружения"})
            }

        # ----- 3. НАСТРОЙКИ YANDEXGPT -----
        # ВАЖНО: здесь ДОЛЖЕН быть ID твоего каталога (folder_id),
        # например: "b1g0s609h0b48ira8rgm"
        folder_id = "b1g4ouc3vjd4nc6k0f7a"

        # Лёгкая модель YandexGPT
        model_uri = f"gpt://{folder_id}/yandexgpt-lite"

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

        headers = {
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "modelUri": model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 500
            },
            "messages": [
                {
                    "role": "user",
                    "text": f"Создай текст по теме: {prompt}"
                }
            ]
        }

        # ----- 4. ВЫЗОВ МОДЕЛИ -----
        resp = requests.post(url, headers=headers, json=payload, timeout=30)

        # Если ошибка 4xx/5xx — вернём ПОЛНЫЙ ответ от API, чтобы видеть причину
        if resp.status_code != 200:
            logging.error(f"LLM error {resp.status_code}: {resp.text}")
            return {
                "statusCode": resp.status_code,
                "headers": {"Content-Type": "application/json"},
                "body": resp.text
            }

        data_resp = resp.json()
        result = data_resp["result"]["alternatives"][0]["message"]["text"]

        # ----- 5. УСПЕШНЫЙ ОТВЕТ -----
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"result": result.strip()})
        }

    except Exception as e:
        logging.error(f"Error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
