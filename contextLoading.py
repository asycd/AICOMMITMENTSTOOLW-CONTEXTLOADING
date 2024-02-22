import streamlit as st
import PyPDF2
import openai
openai.api_key = "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"

# SETTING UP CONTEXT
if 'CONTEXT' not in st.session_state:
    st.session_state.CONTEXT = ""

def pdf_extractor(file):
    text_data = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        text_data += page.extract_text()
    return text_data

def file_converter(file):
    # You can add more conditions for other file types (e.g., docx) if needed
    if file.type == "application/pdf":
        return pdf_extractor(file)
    elif file.type == "text/plain":
        return file.read()
    else:
        st.warning("Unsupported file type. Please upload a supported file.")
        return None

def fund_retrieval(context, fund_name):
    if fund_name:
        message = f"""Check if the fund names {fund_name} or any similar names or acronyms are present in the context. If so, provide details about the fund. Keep in mind the following conditions:

1. If the fund series does not match, it is not a match regardless of whether any other criteria are met. Fund series refers to the number that follows the fund name. Remember that roman numeral numbering and traditional numbering are equivalent when checking for a match e.g. 'II' is equal to '2'.
2. If there is an acronym potentially being used, check whether the acronym expanded would look like a fund already on the backend. For example, “Thoma Bravo SOF II” should match “Thoma Bravo Special Opportunities Fund II” because the series is a match, and the acronym, “SOF”, sounds like it could be “Special Opportunities Fund”.

If more than one fund is entered for checking, create a markdown table where the first column is the fund name, and the second column is "Match," where it should be "YES" if there exists a match according to the guidelines provided above. It should be "NO" if there are no matching funds according to the guidelines provisioned above. The last column should contain the matched fund/funds name depending on whether it matches more than one possible fund."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message}
            ],
            max_tokens=1000
        )
        result = response.choices[0].message['content']
        return result

def main():
    st.title("File to Text Converter and Fund Checker")

    uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])

    if uploaded_file is not None:
        st.success("File uploaded successfully!")

        if st.button("Load Data"):
            text_result = file_converter(uploaded_file)
            st.session_state.CONTEXT = text_result
            st.success("Data was loaded successfully")

    custom_css = """
    <style>
    body {
        background-color: black;
        color: white;
        font-family: 'Poppins', sans-serif;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    st.title("Commitments Checker AI Tool")
    st.write("What funds would you like to check?")

    FUND_NAME = st.text_input("Enter a fund name to check whether it is on the backend for the LP")

    if st.button("Generate Description"):
        output = fund_retrieval(st.session_state.CONTEXT, FUND_NAME)
        if output:
            st.header("Result:")
            st.write(str(output))

    st.write("Powered by OpenAI's GPT-4")

if __name__ == "__main__":
    main()