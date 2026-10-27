# Гончаренко Артём, лабораторная работа 2 — вариант 5

Обработка и сжатие изображений. Три взаимосвязанных метода:

1. **Нелинейные фильтры на основе порядковых статистик** — медианный, min, max и обобщённый процентильный (rank) фильтр.
2. **Построение и эквализация гистограммы** — CDF-эквализация для grayscale, per-channel RGB и HSV V-only.
3. **Линейное контрастирование** — устойчивое растяжение с процентильным отсечением выбросов.

Всё реализовано на **NumPy с нуля** (без `cv2.medianBlur` / `cv2.equalizeHist` в рабочем коде) и **провалидировано против OpenCV** в unit-тестах.

---

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate          # linux
# .venv\Scripts\activate           # windows

pip install -r requirements.txt

streamlit run app.py