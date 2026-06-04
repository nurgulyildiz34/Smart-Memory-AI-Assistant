import chromadb
from langchain_core.documents import Document

class LocalMemoryManager:
    def __init__(self, db_path="./ai_memory_db"):
        """
        Nesne tabanlı bellek yöneticisi.
        Proje klasörünün içinde './ai_memory_db' adında hafif bir veri tabanı klasörü oluşturur.
        """
        # Bilgisayarımızda local olarak çalışacak ChromaDB istemcisini başlatıyoruz
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # 'user_profile' adında bir hafıza tablosu (collection) oluşturuyoruz veya varsa onu alıyoruz
        self.collection = self.chroma_client.get_or_create_collection(name="user_profile")

    def save_information(self, info_text, info_id):
        """
        Kullanıcı hakkında öğrenilen kritik bir bilgiyi (örn: 'İsmim Nurgül') veri tabanına kaydeder.
        """
        # ChromaDB metinleri akıllıca arayabilmek için listeler halinde kabul eder
        self.collection.add(
            documents=[info_text],
            ids=[info_id]
        )

    def get_all_memories(self):
        """
        Veri tabanında kayıtlı olan tüm hafıza parçalarını listeler halinde geri döndürür.
        Bunu Streamlit web sitemizin sol panelinde göstermek için kullanacağız.
        """
        results = self.collection.get()
        return results.get('documents', [])

    def get_relevant_context(self, user_query):
        """
        Kullanıcının sorduğu soruya en uygun olan geçmiş hafıza kayıtlarını bulur.
        (Örn: Kullanıcı 'Kahve öner' dediğinde veri tabanındaki 'Kahveyi şekersiz sever' bilgisini yakalar)
        """
        # Kullanıcının sorusuna anlamsal (semantik) olarak en yakın 3 hafıza kaydını sorguluyoruz
        results = self.collection.query(
            query_texts=[user_query],
            n_results=3
        )
        
        # Bulunan hafıza kayıtlarını düz bir metin haline getirip yapay zekaya 'bağlam' olarak sunuyoruz
        memories = results.get('documents', [[]])[0]
        if memories:
            return "\n".join([f"- {m}" for m in memories])
        return "Kullanıcı hakkında henüz geçmiş bir bilgi yok."