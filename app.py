import streamlit as st
import pandas as pd
import tempfile
# Updated import to use the new regex function
from utils import (
    extract_text_from_pdf,
    extract_text_from_image,
    extract_details_with_regex 
)

st.set_page_config(page_title="Invoice Extractor", layout="wide")
st.image("logo.png", width=150) 
st.title("🧾 Invoice Data Extractor")

uploaded_files = st.file_uploader(
    "Upload Invoice Files (PDF or Image)", 
    type=["pdf", "png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    extracted_data_list = []

    with st.spinner("🔍 Extracting data locally..."):
        for file in uploaded_files:
            filename = file.name.lower()
            try:
                if filename.endswith(".pdf"):
                    # Use a temporary file to handle PDF uploads
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(file.getvalue())
                        text = extract_text_from_pdf(tmp.name)
                elif filename.endswith((".png", ".jpg", ".jpeg")):
                    text = extract_text_from_image(file)
                else:
                    st.warning(f"Unsupported file type: {filename}")
                    continue

                # --- CHANGE IS HERE ---
                # Directly call the regex function to get the final dictionary
                parsed_data = extract_details_with_regex(text)
                parsed_data["Filename"] = file.name
                extracted_data_list.append(parsed_data)

            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {e}")

    if extracted_data_list:
        df = pd.DataFrame(extracted_data_list)
        st.success("✅ Extraction complete!")
        st.dataframe(df)

        # Create an in-memory Excel file
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Invoices')
        
        excel_data = output.getvalue()

        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="Extracted_Invoice_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )