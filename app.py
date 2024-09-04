import streamlit as st
import pandas as pd
import deepl
import io
import os

# Function to translate text with character limit handling
def translate_text(text, source_lang, target_lang, max_chars=5000):
    if len(text) <= max_chars:
        return translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
    else:
        # Split the text into chunks
        chunks = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
        translated_chunks = [translator.translate_text(chunk, source_lang=source_lang, target_lang=target_lang) for chunk in chunks]
        return ' '.join(translated_chunks)

# Function to translate the document
def translate_document(file_content, file_name, source_lang, target_lang):
    # Load the data
    if file_name.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_content))
    elif file_name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(io.BytesIO(file_content))
    else:
        st.error("Invalid file format. Please upload a CSV or Excel file.")
        return

    # Translate column names
    translated_columns = [translator.translate_text(col, source_lang=source_lang, target_lang=target_lang) for col in df.columns]

    # Set the new translated column names
    df.columns = translated_columns

    # Translate each cell in the DataFrame
    for col in df.columns:
        st.write(f"Translating column: {col}")
        df[col] = df[col].apply(
            lambda x: translate_text(str(x), source_lang, target_lang) if pd.notnull(x) and isinstance(x, str) else x)
        st.write(f"Finished translating column: {col}")

    # Save the translated DataFrame to a new CSV or Excel file
    output_file_path = 'Translated.csv' if file_name.endswith('.csv') else 'Translated.xlsx'
    output = io.BytesIO()
    if file_name.endswith('.csv'):
        df.to_csv(output, index=False)
    else:
        df.to_excel(output, index=False)
    output.seek(0)

    return output, output_file_path

# Load the API key
api_key = os.getenv("API_KEY")

# Initialize the DeepL translator
translator = deepl.Translator(api_key)

# Streamlit app
st.title("Document Translator")

# Language options
language_options = {
    'English': 'EN-US',
    'German': 'de',
    'French': 'fr',
    'Spanish': 'es',
    'Portuguese': 'pt-pt',
    'Korean': 'ko',
    'Italian': 'it',
    'Russian': 'ru',
    'Chinese (simplified)': 'zh'
}

# Select source and target languages
source_lang = st.selectbox("Select source language", list(language_options.keys()))
target_lang = st.selectbox("Select target language", list(language_options.keys()))

# Get the language codes based on the selected language names
source_code = language_options[source_lang]
target_code = language_options[target_lang]

# Upload file
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    file_content = uploaded_file.getvalue()  # Get the file content as bytes
    file_name = uploaded_file.name  # Get the file name

    # Translate the document
    output, output_path = translate_document(file_content, file_name, source_code, target_code)
    st.success("Translation completed.")

    # Add a download button for the translated file
    st.download_button(
        label="Download Translated File",
        data=output,
        file_name=output_path,
        mime='text/csv' if file_name.endswith('.csv') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
