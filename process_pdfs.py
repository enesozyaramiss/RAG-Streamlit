from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import os


pdf_path = "PTN.pdf" # Burayı kendi PDF dosyanızın yoluyla değiştirin!
persist_directory = "D:/Projects/Sentinel/chatbot/chroma_db"
# Eğer dizin yoksa oluştur
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)

print(f"PDF'ten metinler yükleniyor: {pdf_path}")
# PDF'i yükle
loader = PyPDFLoader(pdf_path)
documents = loader.load()

print(f"Yüklenen belge sayısı: {len(documents)}")

# --- 3. Metinleri Parçalama (Chunking) ---
# RecursiveCharacterTextSplitter, metni belirlenen boyutta parçalara böler.
# Belirli karakterleri (örn. yeni satır, boşluk) kullanarak daha akıllı bölünme sağlar.
# chunk_overlap: Parçalar arasında ne kadar çakışma olacağı (anlam bütünlüğü için).
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

print(f"Parçalanan belge sayısı: {len(chunks)}")

# --- 4. Vektör Temsili Oluşturma (Embedding) ---
# OllamaEmbeddings: Ollama'dan bir embedding modeli kullanır (örn. 'nomic-embed-text' veya 'llama2')
# Modelinizin adı, Ollama'ya `ollama run <model_adı>` komutuyla indirmeniz gereken modeldir.
# Örn: ollama pull nomic-embed-text
print("Embedding modeli yükleniyor...")
embeddings = OllamaEmbeddings(model="nomic-embed-text") # <-- Bu modeli Ollama'ya indirdiğinizden emin olun!

# --- 5. Vektör Veritabanında Saklama (ChromaDB) ---
# Chroma.from_documents: Metin parçalarını alır, vektörlerini oluşturur ve ChromaDB'ye kaydeder.
print(f"Vektör veritabanı oluşturuluyor ve kaydediliyor: {persist_directory}")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=persist_directory
)

# Kaydedildikten sonra diske yazılmasını sağlar
vectorstore.persist()
print("Vektör veritabanı başarıyla oluşturuldu ve kaydedildi.")