import os
from io import BytesIO

import streamlit as st
from google import genai
from google.genai import types


# ------------------------
# הגדרות ראשוניות ל-Streamlit (כאן הכותרת השתנתה)
# ------------------------
st.set_page_config(
    page_title="האמת בעיניים: מנתח שפת הגוף מבוסס AI",
    layout="centered",
)

# ------------------------
# כותרת ואזהרה (כאן הכותרת השתנתה)
# ------------------------
st.title("האמת בעיניים: מנתח שפת הגוף מבוסס AI")
st.caption("⚠️ כלי עזר זה אינו ייעוץ פסיכולוגי או משפטי. מיועד לאבחון תקשורת לא מילולית בלבד.")
