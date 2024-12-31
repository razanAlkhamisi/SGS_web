import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

def main():


   
    # تخصيص التصميم
    st.markdown( 
        """ 
        <style> 
        [data-testid="stToolbar"]{ 
            display: none; /* جعل العنصر غير مرئي */ 
        } 
 
        [data-testid="stApp"]{ 
            background-color: #ffffff; /* لون خلفية */ 
            color: #585958; /* لون النص */ 
            border: 3px solid #2ECC71; /* لون حدود */ 
        } 
 
        [data-testid="stHeader"]{ 
            background-color: #ffffff; /* لون خلفية */ 
            color: #585958; /* لون النص */ 
            border: 2.5px solid #2ECC71; /* لون حدود */ 
        } 
 
        [data-testid="stMainBlockContainer"]{ 
            position: absolute; 
            top: 55%; 
            left: 50%; 
            transform: translate(-50%, -50%); 
            background-color: #f8fcf8; 
            width: 700px; 
            height: 450px;  
            border-radius: 20px; 
            box-shadow: 0 4px 4px rgba(0.3, 0.3, 0.25, 0.25); 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            padding: 50px; 
            overflow-y: scroll; 
        } 
 
        [data-testid="stFileUploaderDropzone"]{ 
            border-radius: 12px; 
        } 
 
        [data-testid="stWidgetLabel"]{ 
            color: #585958; /* لون النص */ 
        } 
 
        [data-testid="stSidebarCollapsedControl"]{ 
            top:10px; 
        } 
 
        [data-testid="stLogo"] { 
            width: 220px; 
            height: 40px; 
        } 
 
        [data-testid="stDecoration"]{ 
            border: 1px solid #2ECC71; /* لون حدود */ 
        } 
        </style> 
        """, 
        unsafe_allow_html=True 
    ) 
 
    st.logo("images/sgs_logo.jpg", size="large")  # تعديل الشعار

    st.title("دمج البيانات")

    # تحميل الملف الرئيسي
    main_file = st.file_uploader("(Excel) "+"تحميل الملف الرئيسي", type=["xlsx"], key="main_file")

    if main_file:
        main_df = pd.read_excel(main_file, engine="openpyxl")
        st.write("### الملف الرئيسي")
        st.write(main_df)

        if "GS" not in main_df.columns:
            st.error("The file must contain GS column")
            return

        # إضافة عمود جديد للتواريخ إذا لم يكن موجودًا
        if "Date" not in main_df.columns:
            main_df["Date"] = None

        # تحميل الملفات الإضافية
        additional_files = st.file_uploader(
            " تحميل الملفات الإضافية ", type=["xlsx"], accept_multiple_files=True, key="additional_files"
        )

        if additional_files:
            for uploaded_file in additional_files:
                additional_df = pd.read_excel(uploaded_file, engine="openpyxl")
                st.write(f"### {uploaded_file.name}")
                st.write(additional_df)

                # اختيار العمود المناسب للمقارنة
                selected_column = st.selectbox(
                    f"GS "+"اختر العمود الذي يحتوي على رقم",
                    additional_df.columns,
                    key=f"select_{uploaded_file.name}"
                )

                # اختيار العمود الذي يحتوي على التواريخ
                date_column = st.selectbox(
                    f"اختر العمود الذي يحتوي على التواريخ في الملف",
                    additional_df.columns,
                    key=f"date_{uploaded_file.name}"
                )

                if selected_column and date_column:
                    # إزالة القيم الفارغة من العمودين
                    additional_df = additional_df[additional_df[selected_column].notna() & additional_df[date_column].notna()]

                    # تحديث التواريخ في الملف الرئيسي
                    for _, row in additional_df.iterrows():
                        gs_value = row[selected_column]
                        date_value = row[date_column]

                        # تحقق من وجود GS في الملف الرئيسي
                        matching_rows = main_df[main_df['GS'] == gs_value]

                        if not matching_rows.empty:
                            # إذا كان لـ GS تاريخ فارغ، قم بتحديث التاريخ
                            for idx in matching_rows.index:
                                if pd.isna(main_df.at[idx, "Date"]):
                                    main_df.at[idx, "Date"] = date_value
                        else:
                            # إذا كانت GS غير موجودة في الملف الرئيسي، أضفها كصف جديد
                            new_row = {"GS": gs_value, "Date": date_value}
                            main_df = pd.concat([main_df, pd.DataFrame([new_row])], ignore_index=True)

            # عرض الملف المحدث
            st.write("### الملف الرئيسي بعد التحديث")
            st.write(main_df)

            # تنزيل الملف المحدث
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                main_df.to_excel(writer, index=False, sheet_name="Updated Data")

            st.download_button(
                label="تحميل الملف المحدث",
                data=output.getvalue(),
                file_name="updated_main_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

  
if __name__ == "__main__":
    main()