# resources/i18n.py
# Интернационализация для презентационного слоя
# Маппинг типов посылок с английского на русский
PARCEL_TYPE_TRANSLATIONS = {
    "Documents": "Документы",
    "Electronics": "Электроника", 
    "Clothing": "Одежда",
    "Books": "Книги",
    "Other": "Прочее"
}

def translate_parcel_type(english_name: str) -> str:
    return PARCEL_TYPE_TRANSLATIONS.get(english_name, english_name)
