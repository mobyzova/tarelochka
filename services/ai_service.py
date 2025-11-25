import requests
import re

class AIService:
    def __init__(self):
        self.api_key = "cpk_403ff693ca1748f1be9bcbf2b488b098.7e9c19dc143a522984c231cce23c424c.xHkl5G3a6wl8pzoK7r43wzUTsuNkICAA"
        self.api_url = "https://llm.chutes.ai/v1/chat/completions"

    def get_recommendations(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-ai/DeepSeek-R1",
            "messages": [
                {
                    "role": "system",
                    "content": """Ты опытный диетолог и нутрициолог с научным подходом. Анализируй рацион пользователя с учетом:

АНАЛИТИЧЕСКИЙ ПОДХОД:
1. Детальный анализ текущего рациона относительно целей пользователя
2. Оценка баланса макронутриентов и микроэлементов
3. Анализ соответствия индивидуальным нормам потребления
4. Учет диетических ограничений и медицинских показаний
5. Научно обоснованные рекомендации

СТРУКТУРА ОТВЕТА:
ВВЕДЕНИЕ: Краткий общий анализ ситуации
АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ: Детальный разбор потребления
БАЛАНС ПИТАТЕЛЬНЫХ ВЕЩЕСТВ: Оценка макронутриентов
СООТВЕТСТВИЕ ЦЕЛЯМ: Анализ прогресса к целям
КОНКРЕТНЫЕ РЕКОМЕНДАЦИИ: Практические советы
ПЛАН ДЕЙСТВИЙ: Конкретные шаги для улучшения

ТРЕБОВАНИЯ К ФОРМАТУ:
- Используй только обычный текст с абзацами
- Не используй смайлики, эмодзи или markdown-разметку
- Будь максимально конкретен и аналитичен
- Приводи числовые данные и проценты
- Обосновывай рекомендации научными фактами
- Учитывай индивидуальные особенности профиля
- Давай измеримые и выполнимые рекомендации
- Отвечай на русском языке грамотно и профессионально
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 3000,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, json=data, headers=headers, timeout=360)
            response.raise_for_status()

            result = response.json()
            response_text = result['choices'][0]['message']['content']

            return self.clean_response(response_text)

        except requests.exceptions.Timeout:
            return "Сервер не ответил за отведенное время. Возможно, сервер перегружен. Рекомендуется повторить запрос через несколько минут."

        except requests.exceptions.ConnectionError:
            return "Ошибка подключения к серверу. Проверьте интернет-соединение и правильность URL."

        except Exception as e:
            return f"Ошибка API: {str(e)}. Проверьте API ключ и доступность сервиса."

    def clean_response(self, text):
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'`(.*?)`', r'\1', text)

        text = re.sub(r'[^\w\s,.:;!?()\-–—%+=\\/@$#&*\[\]{}|<>]', '', text)

        text = re.sub(r'^\s*[-*•]\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '• ', text, flags=re.MULTILINE)

        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)

        return text.strip()

    def check_api_status(self):
        if not self.api_key or self.api_key == "your_chutes_api_key_here":
            return False

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            test_data = {
                "model": "deepseek-ai/DeepSeek-R1",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }

            response = requests.post(self.api_url, json=test_data, headers=headers, timeout=10)
            return response.status_code == 200

        except:
            return False