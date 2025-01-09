import streamlit as st
import pandas as pd
from io import BytesIO

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
    main_file = st.file_uploader("(Excel) تحميل الملف الرئيسي", type=["xlsx"], key="main_file")

    if main_file:
        # قراءة الملف الرئيسي مع الاحتفاظ بأسماء الأعمدة
        main_df = pd.read_excel(main_file, engine="openpyxl", header=0)
        st.write("### الملف الرئيسي")
        st.write(main_df)

        if "GS" not in main_df.columns:
            st.error("The file must contain a 'GS' column")
            return

        # إضافة أعمدة جديدة إذا لم تكن موجودة
        if "Date" not in main_df.columns:
            main_df["Date"] = None
        if "OOS" not in main_df.columns:
            main_df["OOS"] = None
        if "ST" not in main_df.columns:
            main_df["ST"] = None
            ###
        if "ST" not in main_df.columns:
            main_df["Next Action"] = None


        # تحميل الملفات الإضافية
        additional_files = st.file_uploader(
            "تحميل الملفات الإضافية", type=["xlsx"], accept_multiple_files=True, key="additional_files"
        )

        if additional_files:
            for uploaded_file in additional_files:
                # قراءة جميع الأوراق من الملف الإضافي مع تجاهل الأوراق الفارغة
                sheets = pd.read_excel(uploaded_file, engine="openpyxl", sheet_name=None, header=0)

                # تصفية الأوراق غير الفارغة التي تحتوي على بيانات GS
                valid_sheets = {}
                for sheet_name, df in sheets.items():
                    if df.apply(lambda x: x.astype(str).str.contains(r"^GS\d+$").any()).any():
                        valid_sheets[sheet_name] = df

                if not valid_sheets:
                    st.warning(f'"GS "+"في الملف لا توجد قيم  {uploaded_file.name}"')
                    continue

                for sheet_name, additional_df in valid_sheets.items():
                    st.write(f"### {uploaded_file.name} - الورقة: {sheet_name}")

                    # اختيار عمود GS وعمود التاريخ
                    selected_column = st.selectbox(
                        f"GS "+" اختر العمود الذي يحتوي على رقم",
                        additional_df.columns,
                        key=f"select_{sheet_name}_{uploaded_file.name}"
                    )

                    date_column = st.selectbox(
                        f"اختر العمود الذي يحتوي على التواريخ",
                        additional_df.columns,
                        key=f"date_{sheet_name}_{uploaded_file.name}"
                    )

                    reason_column = "Reason NMC" if "Reason NMC" in additional_df.columns else None
                    remarks_column = "Next Action" if "Next Action" in additional_df.columns else None

                    if selected_column and date_column:
                        # تصفية الصفوف التي تحتوي على قيم GS صالحة
                        additional_df = additional_df[
                            additional_df[selected_column].astype(str).str.match(r"^GS\d+$") &
                            additional_df[date_column].notna()
                        ]

                        st.write("### الجدول بعد التصفية:")
                        st.write(additional_df)

                        # تحديث البيانات
                        for _, row in additional_df.iterrows():
                            gs_value = row[selected_column]
                            date_value = row[date_column]
                            reason_nmc_value = row[reason_column]  if reason_column in additional_df.columns else None
                            remarks_value = row[remarks_column]  if remarks_column in additional_df.columns else None

            
                            if "Jeddah" in uploaded_file.name:
                                file_identifier = "JED"
                            elif "Riyadh" in uploaded_file.name:
                                file_identifier = "RUH"
                            elif "Medina" in uploaded_file.name:
                                file_identifier = "MED"
                            elif "Dammam" in uploaded_file.name:
                                file_identifier = "DMM"
                            elif "DHA" in uploaded_file.name:
                                file_identifier = "DHA"
                            elif "HOF" in uploaded_file.name:
                                file_identifier = "HOF"
                            elif "Local Station" in uploaded_file.name:
                                file_identifier = "LS"
                            else:
                                file_identifier = uploaded_file.name
                                    

                            
                            # تحقق من وجود GS في الملف الرئيسي
                            matching_rows = main_df[main_df["GS"] == gs_value]

                            if not matching_rows.empty:
                                # تحديث التواريخ وReason NMC وST إذا كانت فارغة
                                for idx in matching_rows.index:
                                    if pd.isna(main_df.at[idx, "Date"]):
                                        main_df.at[idx, "Date"] = date_value
                                    if pd.isna(main_df.at[idx, "OOS"]) and reason_nmc_value:
                                        main_df.at[idx, "OOS"] = reason_nmc_value
                                    if pd.isna(main_df.at[idx, "ST"]):
                                        main_df.at[idx, "ST"] = file_identifier

                                    if pd.isna(main_df.at[idx, "Remarks"]) and remarks_value:
                                        main_df.at[idx, "Remarks"] = remarks_value
                            else:
                                # إضافة صف جديد
                                new_row = {
                                    "GS": gs_value,
                                    "Date": date_value,
                                    "OOS": reason_nmc_value,
                                    "ST": file_identifier,
                                    "Remarks": remarks_value
                                }
                                main_df = pd.concat([main_df, pd.DataFrame([new_row])], ignore_index=True)

            # عرض الملف المحدث
            st.write("### الملف الرئيسي بعد التحديث")
            st.write(main_df)

            # تنزيل الملف المحدث
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                main_df.to_excel(writer, index=False, sheet_name="Updated Data")

            st.download_button(
                label="تحميل الملف المحدث",
                data=output.getvalue(),
                file_name="updated_main_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
  
if __name__ == "__main__":
    main()
