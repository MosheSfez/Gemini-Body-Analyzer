import os
from io import BytesIO

import streamlit as st
from google import genai
from google.genai import types


# ------------------------
# הגדרות ראשוניות ל-Streamlit (כאן הכותרות השיווקיות)
# ------------------------
st.set_page_config(
    page_title="האמת בעיניים: מנתח שפת הגוף מבוסס AI",
    layout="centered",
)

# ------------------------
# כותרת ואזהרה
# ------------------------
st.title("האמת בעיניים: מנתח שפת הגוף מבוסס AI")
st.caption("⚠️ כלי עזר זה אינו ייעוץ פסיכולוגי או משפטי. מיועד לאבחון תקשורת לא מילולית בלבד.")

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
    placeholder='לדוגמה: "מה הכוונה האמיתית של האדם בתמונה?"',
    height=100,
)

# כאן הכפתור השתנה
analyze_button = st.button("גלה את האמת: הפעל ניתוח AI")


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
# לוגיקת ניתוח (ה-Prompt המשודרג)
# ------------------------
def analyze_body_language(
    client: genai.Client,
    image_bytes: bytes,
    mime_type: str,
    question: str,
) -> str:
    """
    שולח בקשה למודל gemini-2.5-flash לניתוח שפת גוף מהתמונה.
    מחזיר טקסט Markdown בפורמט של שלושת הסעיפים המקצועיים.
    """

    # נוודא שיש טקסט סביר גם אם המשתמש לא כתב שאלה
    question = question.strip() or "אין שאלת קונטקסט נוספת. נתח את שפת הגוף באופן כללי."

    # הנחיות מפורטות למודל כדי שיעמוד בדרישות הפורמט והבטיחות
    prompt = f"""
אתה מומחה בינלאומי למודיעין התנהגותי וניתוח תקשורת לא מילולית. תפקידך הוא לייצר דו"ח אנליטי, מקצועי ומבוסס נתונים על בסיס התמונה ושאלת הקונטקסט שסופקה.

כללי הדו"ח (חובה):
- הפורמט חייב להיות ברור, מנוסח בשפה גבוהה ומקצועית.
- הניתוח חייב להיות מאוזן: הדגש שכל ממצא הוא פרשנות אפשרית בלבד.
- הימנע משיפוטיות.

החזר תשובה בפורמט Markdown, בעברית, **בדיוק בשלושה סעיפים** (כולל כותרות המשנה המדויקות) עם ניתוח מעמיק:

### 1. ציון ביטחון ותקשורת (Confidence & Rapport Score)
**ציון משוער (מ-100) לכוח שפת הגוף:** [הכנס ציון] / 100
תאר:
- ניתוח הבעות פנים, עמידה, מרחב אישי (פרוקסמיקה) ושימוש בידיים.
- פרט כיצד הממדים הלא-מילוליים (Nonverbal Cues) משפיעים על האמינות הנתפסת ועל יכולת יצירת הקשר (Rapport) עם הצד השני.

### 2. זיהוי מיקרו-סימנים ומתחים (Microsignal & Stress Detection)
תאר:
- אילו "דגלים אדומים" (Red Flags) או סימני מצוקה (Comfort/Discomfort Signals) נסתרים ניתן לזהות בפריים (כגון: מתח שרירי, כיווץ סביב העיניים או הפה).
- פרט כיצד מיקרו-סימנים אלו יכולים להעיד על חרדה, הסתייגות או פער בין מה שנאמר למה שמשודר.

### 3. מפת דרכים להתנהגות אסטרטגית (Strategic Behavioral Blueprint)
ספק המלצות אסטרטגיות למשתמש, המבוססות על הניתוח, לשיפור התקשורת העתידית בסיטואציה דומה:
- ציין 3 פעולות מיידיות לשיפור הכריזמה או הפחתת סימני מצוקה.
- המלץ על דרכים להקרין סמכות, ביטחון ושלווה.
- המלצות כלליות ופרקטיות בלבד, שאינן מהוות ייעוץ מקצועי.

התאם את הניתוח לשאלת הקונטקסט הבאה:
\"\"\"{question}\"\"\"
"""

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

            with st.spinner("מריץ ניתוח שפת גוף בעזרת Gemini..."):
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
