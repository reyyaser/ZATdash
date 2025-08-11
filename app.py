
# app.py
# -*- coding: utf-8 -*-
import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="متابعة بروسس العملاء", page_icon="📊", layout="wide")
st.title("📊 داش بورد متابعة بروسس العملاء")
st.caption("إدارة العملاء الجدد والمستمرين + متابعة الخدمة والفواتير")

DATA_FILE = "clients.csv"

PROCESS_COLUMNS_NEW = [
    "العرض الفني",
    "العرض المالي",
    "COI Form",
    "CA Form",
    "عقد وورد",
    "EL Form",
    "عقد PDF (توقيع المدير)",
    "إرسال للعميل",
]

PROCESS_COLUMNS_EXISTING = [
    "COI Form",
    "CA Form",
    "عقد وورد",
    "EL Form",
    "عقد PDF (توقيع المدير)",
    "إرسال للعميل",
]

ALL_COLUMNS = [
    "اسم العميل",
    "نوع العميل",
    *PROCESS_COLUMNS_NEW,
    "حالة الخدمة",
    "فاتورة أولى (50%)",
    "فاتورة ثانية (50%)",
    "ملاحظات",
]

CLIENT_TYPES = ["جديد", "مستمر"]
SERVICE_STATUS = ["لم تبدأ", "قيد التنفيذ", "مكتملة"]
DONE_STATUS = ["تم", "لم يتم"]

def create_template_df():
    rows = [
        {
            "اسم العميل": "شركة ABC",
            "نوع العميل": "جديد",
            "العرض الفني": "تم",
            "العرض المالي": "تم",
            "COI Form": "تم",
            "CA Form": "تم",
            "عقد وورد": "تم",
            "EL Form": "تم",
            "عقد PDF (توقيع المدير)": "تم",
            "إرسال للعميل": "تم",
            "حالة الخدمة": "قيد التنفيذ",
            "فاتورة أولى (50%)": "تم",
            "فاتورة ثانية (50%)": "لم يتم",
            "ملاحظات": "—",
        },
        {
            "اسم العميل": "شركة XYZ",
            "نوع العميل": "مستمر",
            "العرض الفني": "",
            "العرض المالي": "",
            "COI Form": "تم",
            "CA Form": "تم",
            "عقد وورد": "تم",
            "EL Form": "تم",
            "عقد PDF (توقيع المدير)": "لم يتم",
            "إرسال للعميل": "لم يتم",
            "حالة الخدمة": "لم تبدأ",
            "فاتورة أولى (50%)": "لم يتم",
            "فاتورة ثانية (50%)": "لم يتم",
            "ملاحظات": "—",
        },
        {
            "اسم العميل": "شركة DEF",
            "نوع العميل": "جديد",
            "العرض الفني": "تم",
            "العرض المالي": "تم",
            "COI Form": "تم",
            "CA Form": "تم",
            "عقد وورد": "تم",
            "EL Form": "لم يتم",
            "عقد PDF (توقيع المدير)": "لم يتم",
            "إرسال للعميل": "لم يتم",
            "حالة الخدمة": "لم تبدأ",
            "فاتورة أولى (50%)": "لم يتم",
            "فاتورة ثانية (50%)": "لم يتم",
            "ملاحظات": "—",
        },
    ]
    return pd.DataFrame(rows, columns=ALL_COLUMNS)

def ensure_df(df):
    for col in ALL_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    if "نوع العميل" in df.columns:
        df.loc[~df["نوع العميل"].isin(CLIENT_TYPES), "نوع العميل"] = "جديد"
    if "حالة الخدمة" in df.columns:
        df.loc[~df["حالة الخدمة"].isin(SERVICE_STATUS), "حالة الخدمة"] = "لم تبدأ"
    for c in PROCESS_COLUMNS_NEW + ["COI Form", "CA Form", "عقد وورد", "EL Form", "عقد PDF (توقيع المدير)", "إرسال للعميل", "فاتورة أولى (50%)", "فاتورة ثانية (50%)", "العرض الفني", "العرض المالي"]:
        if c in df.columns:
            df[c] = df[c].where(df[c].isin(DONE_STATUS), df[c])
            df.loc[~df[c].isin(DONE_STATUS), c] = df[c].replace("", "لم يتم")
    return df.fillna("")

def compute_progress(row):
    steps = PROCESS_COLUMNS_EXISTING if row.get("نوع العميل") == "مستمر" else PROCESS_COLUMNS_NEW
    done = sum(1 for s in steps if str(row.get(s, "لم يتم")).strip() == "تم")
    total = len(steps) + 1
    if row.get("حالة الخدمة") == "مكتملة":
        done += 1
    return (done / total) * 100 if total > 0 else 0.0

if not os.path.exists(DATA_FILE):
    df0 = create_template_df()
    df0.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

@st.cache_data
def load_data(path):
    return pd.read_csv(path, encoding="utf-8-sig")

df = ensure_df(load_data(DATA_FILE))
df["نسبة التقدم"] = df.apply(compute_progress, axis=1).round(0)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("إجمالي العملاء", len(df))
with c2:
    st.metric("الجدد", int((df["نوع العميل"] == "جديد").sum()))
with c3:
    st.metric("المستمرين", int((df["نوع العميل"] == "مستمر").sum()))
with c4:
    st.metric("متوسط التقدم %", float(df["نسبة التقدم"].mean() if len(df) > 0 else 0))

st.divider()

with st.expander("🔎 فلاتر"):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        f_type = st.multiselect("نوع العميل", CLIENT_TYPES, default=CLIENT_TYPES)
    with fc2:
        f_service = st.multiselect("حالة الخدمة", SERVICE_STATUS, default=SERVICE_STATUS)
    with fc3:
        f_invoice = st.multiselect("المدفوعات", DONE_STATUS, default=DONE_STATUS)

mask = (
    df["نوع العميل"].isin(f_type) &
    df["حالة الخدمة"].isin(f_service) &
    (df["فاتورة أولى (50%)"].isin(f_invoice) | df["فاتورة ثانية (50%)"].isin(f_invoice))
)
filtered = df[mask].copy()

st.subheader("📋 جدول العملاء (قابل للتحرير)")
edit_config = {
    "نوع العميل": st.column_config.SelectboxColumn(options=CLIENT_TYPES),
    "حالة الخدمة": st.column_config.SelectboxColumn(options=SERVICE_STATUS),
    "ملاحظات": st.column_config.TextColumn(),
}
for c in PROCESS_COLUMNS_NEW + ["COI Form","CA Form","عقد وورد","EL Form","عقد PDF (توقيع المدير)","إرسال للعميل","فاتورة أولى (50%)","فاتورة ثانية (50%)","العرض الفني","العرض المالي"]:
    if c in df.columns:
        edit_config[c] = st.column_config.SelectboxColumn(options=DONE_STATUS)

edited = st.data_editor(
    filtered,
    num_rows="dynamic",
    use_container_width=True,
    column_config=edit_config,
    hide_index=True,
    key="data_editor",
)

if st.button("💾 حفظ التعديلات إلى الملف"):
    base = df.set_index("اسم العميل")
    ed = edited.set_index("اسم العميل")
    base.update(ed)
    new_rows = ed[~ed.index.isin(base.index)]
    if len(new_rows) > 0:
        base = pd.concat([base, new_rows], axis=0)
    base.reset_index(inplace=True)
    base = ensure_df(base)
    base["نسبة التقدم"] = base.apply(compute_progress, axis=1).round(0)
    base.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    st.success("تم حفظ التعديلات إلى clients.csv")

st.subheader("📈 التقدّم لكل عميل")
if len(filtered) > 0:
    fig_prog = px.bar(
        filtered.sort_values("نسبة التقدم"),
        x="نسبة التقدم",
        y="اسم العميل",
        orientation="h",
        text="نسبة التقدم",
        range_x=[0, 100],
        title="نسبة التقدّم (%)",
    )
    fig_prog.update_traces(texttemplate="%{text:.0f}%", textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_prog, use_container_width=True)
else:
    st.info("لا توجد بيانات بعد الفلترة.")

left, right = st.columns(2)
with left:
    st.subheader("🧮 توزيع العملاء حسب النوع")
    if len(filtered) > 0:
        fig_type = px.histogram(filtered, x="نوع العميل", title="العملاء: جديد vs مستمر")
        st.plotly_chart(fig_type, use_container_width=True)
with right:
    st.subheader("🛠️ حالة الخدمة")
    if len(filtered) > 0:
        fig_status = px.histogram(filtered, x="حالة الخدمة", title="لم تبدأ / قيد التنفيذ / مكتملة")
        st.plotly_chart(fig_status, use_container_width=True)

left2, right2 = st.columns(2)
with left2:
    st.subheader("💳 حالة الفواتير - الأولى")
    if len(filtered) > 0:
        fig_inv1 = px.histogram(filtered, x="فاتورة أولى (50%)", title="الفاتورة الأولى")
        st.plotly_chart(fig_inv1, use_container_width=True)
with right2:
    st.subheader("💳 حالة الفواتير - الثانية")
    if len(filtered) > 0:
        fig_inv2 = px.histogram(filtered, x="فاتورة ثانية (50%)", title="الفاتورة الثانية")
        st.plotly_chart(fig_inv2, use_container_width=True)

st.subheader("📥 استيراد / تصدير البيانات")
c_down, c_up = st.columns(2)
with c_down:
    st.download_button(
        "⬇️ تنزيل الملف الحالي (CSV)",
        data=df.to_csv(index=False, encoding="utf-8-sig"),
        file_name="clients.csv",
        mime="text/csv",
    )
with c_up:
    uploaded = st.file_uploader("⬆️ رفع ملف CSV لتحديث البيانات", type=["csv"])
    if uploaded is not None:
        try:
            new_df = pd.read_csv(uploaded, encoding="utf-8-sig").fillna("")
            for col in ["اسم العميل", "نوع العميل", "حالة الخدمة"]:
                if col not in new_df.columns:
                    st.error(f"العمود الإلزامي مفقود: {col}")
                    st.stop()
            for col in ALL_COLUMNS:
                if col not in new_df.columns:
                    new_df[col] = ""
            new_df = ensure_df(new_df)
            new_df["نسبة التقدم"] = new_df.apply(compute_progress, axis=1).round(0)
            new_df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
            st.success("تم استبدال البيانات بنجاح. أعد تشغيل الصفحة للتحديث.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
st.caption("© لوحة محلية — عدّل بما يناسب عملك.")
