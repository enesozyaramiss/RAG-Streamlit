# my_chatbot_app.py
import datetime
import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import os

# --- 1. Vektör Veritabani Yolu ---
# process_pdfs.py dosyasinda kullandiğiniz yolla ayni olmali
persist_directory = "D:/Projects/Sentinel/chatbot/chroma_db"

# --- 2. LLM Modelini Yükleme ---
# Ollama LLM'i başlat
llm = OllamaLLM(model="gemma3") # Model adiniz "gemma3" ise kontrol edin.

# --- 3. Embedding Modelini Yükleme ---
# Ollama'dan embedding modeli başlat (process_pdfs.py'deki ile ayni olmali)
embeddings = OllamaEmbeddings(model="nomic-embed-text") # <-- Bu modeli Ollama'ya indirdiğinizden emin olun!

# --- 4. Vektör Veritabanini Yükleme ---
# Oluşturduğunuz ChromaDB'yi yükleyin
try:
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    print("Vektör veritabani başariyla yüklendi.")
except Exception as e:
    st.error(f"Vektör veritabani yüklenirken bir hata oluştu: {e}")
    st.info("Lütfen `process_pdfs.py` dosyasini çaliştirdiğinizdan ve `nomic-embed-text` modelini Ollama'ya indirdiğinizden emin olun.")
    st.stop() # Hata durumunda uygulamayi durdur

# --- 5. Retriever Oluşturma ---
# Vektör veritabanindan ilgili belgeleri çekecek retriever'i oluştur
retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # En alakali 3 belgeyi çek

# --- 6. Prompt Tanimi ---
# Kullanicinin sorusunu ve retriever'dan gelen bağlami alacak prompt
# Ayrica güncel tarihi de prompt'a ekliyoruz (basit RAG)
current_date = datetime.date.today().strftime("%d %B %Y")

prompt = ChatPromptTemplate.from_template(f"""
Yanitinizi yalnizca saglanan baglama dayandirin.
Eger verilen baglamda cevap yoksa, "Verilen bilgilerle bu soruyu cevaplayamiyorum." deyin.
Bağlamdaki bilgiler eksik veya yeterli değilse, bunu belirtin.

Bugünün tarihi: {current_date}.

Bağlam:
{{context}}

Soru: {{input}}
Cevap:
""")

# --- 7. Belge Zincirini Oluşturma ---
# Bu zincir, alinan belgeleri ve soruyu kullanarak LLM'den cevap üretir
document_chain = create_stuff_documents_chain(llm, prompt)

# --- 8. Retrieval Zincirini Oluşturma ---
# Bu ana zincir, retriever'dan belgeleri alir ve sonra belge zincirine gönderir
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# --- Streamlit Uygulamasi ---
st.title("PDF Bilgileriyle Desteklenmis Enes'in Chatbot'u")

user_input = st.text_input("PDF'lerinizle ilgili sorunuzu yaziniz: ")

if user_input:
    with st.spinner("Cevap oluşturuluyor..."):s
        try:
            # Zinciri çaliştirma
            response = retrieval_chain.invoke({"input": user_input})

            # Cevabi göster
            st.write("Cevap:", response["answer"])

            # Hangi belgelerden yararlanildiğini göstermek isteyebilirsiniz (isteğe bağli)
            # if "context" in response and response["context"]:
            #     st.subheader("Kullanilan Belgeler:")
            #     for i, doc in enumerate(response["context"]):
            #         st.write(f"**{i+1}. Belge:**")
            #         st.info(doc.page_content[:500] + "...") # İlk 500 karakteri göster
            #         if doc.metadata:
            #             st.text(f"Kaynak: {doc.metadata.get('source', 'Bilinmiyor')}, Sayfa: {doc.metadata.get('page', 'Bilinmiyor')}")

        except Exception as e:
            st.error(f"Sorgu işlenirken bir hata oluştu: {e}")
            st.info("Ollama sunucusunun çaliştigindan ve modellerin (gemma3, nomic-embed-text) yüklü olduğundan emin olun.")



