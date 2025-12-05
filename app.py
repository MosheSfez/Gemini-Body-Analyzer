import os
from io import BytesIO

import streamlit as st
from google import genai
from google.genai import types


# ------------------------
# הגדרות ראשוניות ל-Streamlit
# ------------------------
st.set_page_config(
    page_title="סוכן הניתוח המודיעיני: ניתוח טכניקת אימון",
    layout="centered",
)

# ------------------------
# כותרת ואזהרה
# ------------------------
st.title("סוכן הניתוח המודיעיני: ניתוח טכניקת אימון")
st.caption("⚠️ כלי זה מיועד לניתוח כללי ואינו מחליף ייעוץ מקצועי מאמן אישי מוסמך.")

st.markdown("---")

# ------------------------
# הגדרת מפתח API
# ------------------------
st.sidebar.header("הגדרות Gemini API")

st.sidebar.markdown(
    """
1. קבל מפתח מ־Google AI Studio.  
2. אפשר לבחור:
   - להגדיר משתנה סביבה `GEMINI_API_KEY`, או  
   - להזין כאן את המפתח ידנית.
"""
)

api_key_input = st.sidebar.text_input(
    "Gemini API Key (אופציונלי – אם לא הוגדר כמשתנה סביבה)",
    type="password",
    help="אם לא תזין כאן מפתח, האפליקציה תנסה להשתמש במשתנה הסביבה GEMINI_API_KEY.",
)

# ננסה קודם מהקלט, ואם לא – מהסביבה
effective_api_key = api_key_input or os.getenv("GEMINI_API_KEY", "")

# ------------------------
# UI ראשי: העלאת תמונה ושאלת קונטקסט
# ------------------------
st.subheader("העלה תמונה ושאלת קונטקסט לניתוח")

uploaded_file = st.file_uploader(
    "העלה קובץ תמונה (JPG / PNG)",
    type=["jpg", "jpeg", "png"],
)

context_question = st.text_area(
    "שאלת קונטקסט לניתוח",
    placeholder='לדוגמה: "נתח את טכניקת הדדליפט. האם אני משתמש מספיק ברגליים?"',
    height=100,
)

analyze_button = st.button("נתח טכניקת אימון עם Gemini")


# ------------------------
# פונקציה: יצירת לקוח Gemini
# ------------------------
def get_gemini_client(api_key: str | None = None) -> genai.Client:
    """
    מחזיר אובייקט Client של Gemini.
    אם api_key אינו מוגדר, משתמש ב-GEMINI_API_KEY מהסביבה (אם קיים).
    """
    if api_key:
        return genai.Client(api_key=api_key)
    # אם אין api_key מפורש – נסמוך על משתנה הסביבה GEMINI_API_KEY
    return genai.Client()


# ------------------------
# לוגיקת ניתוח
# ------------------------
def analyze_body_language(
    client: genai.Client,
    image_bytes: bytes,
    mime_type: str,
    question: str,
) -> str:
    """
    שולח בקשה למודל gemini-2.5-flash לניתוח טכניקת כושר מהתמונה.
    מחזיר טקסט Markdown בפורמט של שלושת הסעיפים המבוקשים.
    """

    # נוודא שיש טקסט סביר גם אם המשתמש לא כתב שאלה
    question = question.strip() or "אין שאלת קונטקסט נוספת. נתח את טכניקת התרגיל או היציבה באופן כללי."

    # ********** זהו ה-PROMPT החדש והמקצועי שלך **********
    prompt = f"""
אתה מאמן כושר מוסמך ומומחה לניתוח טכניקת תרגילים ויציבה. עליך לנתח את התמונה שסופקה.
אם התמונה מציגה אדם מבצע תרגיל, התמקד בטכניקה. אם זו תמונת פרופיל כללית, התמקד בניתוח הרכב גוף ויציבה.

החזר תשובה בפורמט Markdown, בעברית, **בדיוק בשלושה סעיפים** עם הכותרות הבאות:

### א. ניתוח טכניקה ודיוק ביצוע
תאר:
- הערך את ביצוע התרגיל (או היציבה הכללית) והצבע על טעויות קריטיות (כגון: גב עגול, ברכיים נופלות פנימה, עומס על מפרק).
- נתח את זוויות המפרקים המרכזיות (ירך, ברך, קרסול).

### ב. הערכת הרכב גוף ופיתוח שרירים
תאר:
- באופן כללי בלבד, נתח אילו קבוצות שרירים נראות דומיננטיות ואילו טעונות שיפור (למשל: יציבה קדמית).
- ציין שהערכה זו אינה מדידה מדויקת אלא רק הערכה ויזואלית כללית.

### ג. 3 המלצות לשיפור מיידי
תן שלוש המלצות ספציפיות, מעשיות וממוקדות:
- המלצה 1: טכניקה (מה לשנות בביצוע).
- המלצה 2: יציבה/פיתוח (תרגיל משלים מומלץ).
- המלצה 3: בטיחות (טיפ למניעת פציעות).

התאם את הניתוח לשאלת הקונטקסט הבאה:
\"\"\"{question}\"\"\"
"""
# ********** סוף ה-PROMPT החדש **********

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    # קריאה למודל
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            image_part,
        ],
    )

    # response.text מחזיר את כל הטקסט המחובר
    return response.text


# ------------------------
# הרצת הניתוח כאשר נלחץ הכפתור
# ------------------------
if analyze_button:
    # בדיקות תקינות בסיסיות
    if not effective_api_key:
        st.error(
            "לא נמצא מפתח API. "
            "יש להזין מפתח ב־sidebar או להגדיר משתנה סביבה GEMINI_API_KEY."
        )
    elif uploaded_file is None:
        st.error("לא הועלתה תמונה. אנא העלה קובץ JPG/PNG.")
    else:
        try:
            # קריאת הבייטים מהקובץ
            image_bytes = uploaded_file.read()
            mime_type = uploaded_file.type or "image/jpeg"

            # הצגת התמונה למשתמש
            st.image(
                image_bytes,
                caption="התמונה שהועלתה לניתוח",
                use_column_width=True,
            )

            # יצירת לקוח Gemini
            client = get_gemini_client(effective_api_key)

            with st.spinner("מריץ ניתוח טכניקת אימון בעזרת Gemini..."):
                analysis_markdown = analyze_body_language(
                    client=client,
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    question=context_question,
                )

            st.markdown("---")
            st.subheader("תוצאות הניתוח (Gemini)")

            # הצגת ה-Markdown שהמודל מחזיר
            st.markdown(analysis_markdown)

        except Exception as e:
            st.error(f"שגיאה במהלך הקריאה ל-Gemini API: {e}")
            st.stop()
