import streamlit as st
from rag import process_urls, generate_answer

st.set_page_config(page_title="Real Estate AI Tool")

st.title("🏠 Real Estate Research Tool")

# -------- Sidebar --------
st.sidebar.header("Enter URLs")

url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")
url3 = st.sidebar.text_input("URL 3")

urls = [u for u in [url1, url2, url3] if u and u.strip()]

# -------- Process --------
if st.sidebar.button("Process URLs"):
    if not urls:
        st.warning("Please enter at least one URL")
    else:
        with st.spinner("Processing URLs..."):
            msg = process_urls(urls)   # 👈 yahan change
            st.success(msg)

# -------- Query --------
query = st.text_input("Ask a question")

if query:
    with st.spinner("Generating answer..."):
        answer, sources = generate_answer(query)

    st.subheader("Answer")
    st.write(answer)

    if sources:
        st.subheader("Sources")
        for src in sources.split("\n"):
            if src.strip():
                st.write(src)