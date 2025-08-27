# Schemas

Этот каталог содержит все схемы данных (Pydantic модели) для API.

## Структура

- **`parcel.py`** - Схемы для операций с посылками
  - `ParcelTypeResponse` - Ответ с информацией о типе посылки
  - `ParcelRegisterRequest` - Запрос на регистрацию посылки через API
  - `ParcelWebRegisterRequest` - Запрос на регистрацию посылки через веб-форму
  - `ParcelResponse` - Ответ с информацией о посылке

- **`tasks.py`** - Схемы для фоновых задач
  - `PingRequest` - Запрос ping
  - `TaskStatusResponse` - Ответ со статусом задачи

- **`common.py`** - Общие схемы для API
  - `HTTPValidationError` - Схема ошибок валидации HTTP
  - `ValidationError` - Детали ошибки валидации
  - `SuccessResponse` - Общий успешный ответ

- **`__init__.py`** - Удобные импорты для всех схем

## Использование

```python
from schemas import ParcelRegisterRequest, ParcelResponse
# или
from schemas.parcel import ParcelRegisterRequest, ParcelResponse
```

## Принципы

1. Все схемы наследуются от `BaseModel` из Pydantic
2. Используются типы Python 3.10+ (например, `dict | None`)
3. Добавляются описания для полей через `Field(..., description="...")`
4. Схемы группируются по функциональным областям
