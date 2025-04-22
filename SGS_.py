import streamlit as st
import pandas as pd
from io import BytesIO

repairing_in_progress = [
    "Repairing in Progress", "Under Diagnosis/Troubleshooting", "Differential Overhaul in Progress",
    "Engine Overhaul in Progress", "Engine OVH in progress", "Refurbishment in progress",
    "Refurbishment in Progress", "Under Fabrication process", "Under line",
    "Under Troubleshooting / Diagnosis", "Waiting for customer response",
    "Work in Progress", "Under Troubleshooting /Diagnosis", "waiting for customer response"
]

tuv_pm = ["Under TUV Preparation","Preventive Maintenance in progress"]

oem=[
    "Under Warranty Waiting for Manufacturer Support",
    "Waiting for Manufacturer Support","Waiting for OEM Support"]

waiting_for_parts=[
    "Waiting for Engine to be delivered","Engine OVH in progress | Waiting For Parts",
    "Waiting For Parts","Waiting For Parts ( Control Valve )","Waiting for Parts to be delivered",
    "Waiting for spare parts to be deliverd","Waiting for the part to be delivered.",
    "Waiting part to be delivered","Wiaitng for parts to be delivered"]


def classify_remarks(remarks_value):
 
    remarks_value = str(remarks_value).strip()  # تنظيف النص وإزالة المسافات الزائدة
    
    for category in repairing_in_progress:
        if category.lower() in remarks_value.lower():
            return "Repairing in Progress"  # تعيين التصنيف المطابق
    
    for category in tuv_pm:
        if category.lower() in remarks_value.lower():
            return "TUV + PM"  # تعيين التصنيف المطابق

    for category in oem:
        if category.lower() in remarks_value.lower():
            return "Waiting for OEM Support"  # تعيين التصنيف المطابق

    for category in waiting_for_parts:
        if category.lower() in remarks_value.lower():
            return "Waiting for Parts"  # تعيين التصنيف المطابق
    
    return "N/A"  # في حال لم يكن هناك تطابق


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
        main_df = pd.read_excel(main_file, engine="openpyxl", header=0)
        st.write("### الملف الرئيسي")
        st.write(main_df)
        
        main_df["Remarks_1"]=classify_remarks(main_df["Remarks"])
        # تحقق من وجود عمود GS
        if "GS" not in main_df.columns:
            st.error("GS "+"الملف الرئيسي يجب أن يحتوي على عمود ")
            return
   
       
        # إضافة أعمدة جديدة إذا لم تكن موجودة
        if "SRA" in main_df.columns:
            main_df["SRA"]=0

        
        if "Reason NMC" in main_df.columns:
            main_df["OOS"]=main_df["Reason NMC"]
            main_df.drop(columns=["Reason NMC"],inplace=True)

        for col in ["Date", "OOS", "ST", "Remarks"]:
            if col not in main_df.columns:
                main_df[col] = None

        # تحميل الملفات الإضافية
        additional_files = st.file_uploader(
            "تحميل الملفات الإضافية", type=["xlsx"], accept_multiple_files=True, key="additional_files"
        )

       
        if additional_files:

            for uploaded_file in additional_files:
                sheets = pd.read_excel(uploaded_file, engine="openpyxl", sheet_name=None, header=0,skiprows=4)

                    
                valid_sheets = {}
                for sheet_name, df in sheets.items():
                    if df.apply(lambda x: x.astype(str).str.contains(r"^GS\d+$").any()).any():
                        valid_sheets[sheet_name] = df

                if not valid_sheets:
                    st.warning(f'"GS "+"في الملف لا توجد قيم  {uploaded_file.name}"')
                    continue

                for sheet_name, additional_df in valid_sheets.items():
                    st.write(f"### {uploaded_file.name} - sheet: {sheet_name} -")

                    # اختيار الأعمدة
                    selected_column = st.selectbox(
                        f"GS "+" اختر العمود الذي يحتوي على رقم",
                        additional_df.columns,
                        key=f"select_{sheet_name}_{uploaded_file.name}"
                    )
                    date_column = st.selectbox(
                        "اختر العمود الذي يحتوي على التواريخ",
                        additional_df.columns,
                        key=f"date_{sheet_name}_{uploaded_file.name}"
                    )

                    if selected_column and date_column:
                        # تصفية البيانات بناءً على GS
                        additional_df = additional_df[
                            additional_df[selected_column].astype(str).str.contains(r"(GS\d+|[A-Za-z]*\d+[A-Za-z]*)", na=False)
                        ]

                        st.write("###  الجدول بعد التصفية")
                        st.write(additional_df)

                        

                        # دمج البيانات
                        for _, row in additional_df.iterrows():
                            gs_value = row[selected_column]
                            date_value = row[date_column]
                            loc=row["Location"]
                            loc=str(loc)[2:]
                            reason_nmc_value = row.get("Reason NMC", None)
                            remarks_value = row.get("Next Action", None)
                            sra = "SRA" if "SRA" in uploaded_file.name else 0 

                            classification= classify_remarks(remarks_value)

                            if gs_value in main_df["GS"].values:
                                # تحديث الصفوف الموجودة
                                main_df.loc[main_df["GS"] == gs_value, ["Date", "OOS", "Remarks","SRA", "Remarks_1"]] = [
                                    date_value, reason_nmc_value, remarks_value,sra,classification
                                ]
                          
                            else:
                            
                                # إضافة صف جديد
                                new_row = {
                                    "GS": gs_value,
                                    "Date": date_value,
                                    "OOS": reason_nmc_value,
                                    "ST": loc, 
                                    "Remarks": remarks_value,
                                    "Remarks_1":classification
                                }
                                if "SRA" in main_df.columns:
                                    new_row = {
                                    "GS": gs_value,
                                    "Date": date_value,
                                    "OOS": reason_nmc_value,
                                    "ST": loc, 
                                    "Remarks": remarks_value,
                                    "Remarks_1":classification,
                                    'SRA':sra
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
                file_name="Updated_File.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

if __name__ == "__main__":
    main()
