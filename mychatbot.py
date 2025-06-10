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

# --- 1. Vektör Veritabanı Yolu ---
# process_pdfs.py dosyasında kullandığınız yolla aynı olmalı
persist_directory = "D:/Projects/Sentinel/chatbot/chroma_db"

# --- 2. LLM Modelini Yükleme ---
# Ollama LLM'i başlat
llm = OllamaLLM(model="gemma3") # Model adınız "gemma3" ise kontrol edin.

# --- 3. Embedding Modelini Yükleme ---
# Ollama'dan embedding modeli başlat (process_pdfs.py'deki ile aynı olmalı)
embeddings = OllamaEmbeddings(model="nomic-embed-text") # <-- Bu modeli Ollama'ya indirdiğinizden emin olun!

# --- 4. Vektör Veritabanını Yükleme ---
# Oluşturduğunuz ChromaDB'yi yükleyin
try:
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    print("Vektör veritabanı başarıyla yüklendi.")
except Exception as e:
    st.error(f"Vektör veritabanı yüklenirken bir hata oluştu: {e}")
    st.info("Lütfen `process_pdfs.py` dosyasını çalıştırdığınızdan ve `nomic-embed-text` modelini Ollama'ya indirdiğinizden emin olun.")
    st.stop() # Hata durumunda uygulamayı durdur

# --- 5. Retriever Oluşturma ---
# Vektör veritabanından ilgili belgeleri çekecek retriever'ı oluştur
retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # En alakalı 3 belgeyi çek

# --- 6. Prompt Tanımı ---
# Kullanıcının sorusunu ve retriever'dan gelen bağlamı alacak prompt
# Ayrıca güncel tarihi de prompt'a ekliyoruz (basit RAG)
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
# Bu zincir, alınan belgeleri ve soruyu kullanarak LLM'den cevap üretir
document_chain = create_stuff_documents_chain(llm, prompt)

# --- 8. Retrieval Zincirini Oluşturma ---
# Bu ana zincir, retriever'dan belgeleri alır ve sonra belge zincirine gönderir
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# --- Streamlit Uygulaması ---
st.title("PDF Bilgileriyle Desteklenmiş Enes'in Chatbot'u")

user_input = st.text_input("PDF'lerinizle ilgili sorunuzu yazınız: ")

if user_input:
    with st.spinner("Cevap oluşturuluyor..."):s
        try:
            # Zinciri çalıştırma
            response = retrieval_chain.invoke({"input": user_input})

            # Cevabı göster
            st.write("Cevap:", response["answer"])

            # Hangi belgelerden yararlanıldığını göstermek isteyebilirsiniz (isteğe bağlı)
            # if "context" in response and response["context"]:
            #     st.subheader("Kullanılan Belgeler:")
            #     for i, doc in enumerate(response["context"]):
            #         st.write(f"**{i+1}. Belge:**")
            #         st.info(doc.page_content[:500] + "...") # İlk 500 karakteri göster
            #         if doc.metadata:
            #             st.text(f"Kaynak: {doc.metadata.get('source', 'Bilinmiyor')}, Sayfa: {doc.metadata.get('page', 'Bilinmiyor')}")

        except Exception as e:
            st.error(f"Sorgu işlenirken bir hata oluştu: {e}")
            st.info("Ollama sunucusunun çalıştığından ve modellerin (gemma3, nomic-embed-text) yüklü olduğundan emin olun.")



