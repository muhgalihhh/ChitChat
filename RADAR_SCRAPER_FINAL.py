"""
🌟 RADAR SURABAYA NEWS SCRAPER - FINAL VERSION 🌟
Developed by Senior Data Mining & Full Stack Engineer (30+ years experience)

INSTRUKSI PENGGUNAAN:
1. Copy seluruh kode ini ke Google Colab
2. Ganti keyword pada baris yang ditandai
3. Jalankan cell
4. Download hasil CSV

Website Target: https://radarsurabaya.jawapos.com/
"""

# ===== INSTALL DEPENDENCIES (Uncomment jika belum terinstall) =====
# !pip install requests beautifulsoup4 pandas lxml html5lib

# ===== IMPORT LIBRARIES =====
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin
import warnings
warnings.filterwarnings('ignore')

# ===== KONFIGURASI =====
print("🚀 RADAR SURABAYA SCRAPER LOADING...")
print("Developed by Senior Data Mining Expert (30+ years)")
print("=" * 60)

# ===== SCRAPER CLASS =====
class RadarScraper:
    def __init__(self):
        self.base_url = "https://radarsurabaya.jawapos.com"
        self.session = requests.Session()
        
        # Anti-bot headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def search_articles(self, keyword):
        """Cari artikel berdasarkan keyword"""
        try:
            search_url = f"{self.base_url}/search"
            params = {'q': keyword}
            
            print(f"🔍 Mencari artikel dengan keyword: '{keyword}'")
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ekstrak artikel dari hasil pencarian
            articles = []
            article_links = soup.find_all('a', class_='latest__link')
            
            print(f"📰 Ditemukan {len(article_links)} artikel")
            
            for link in article_links:
                try:
                    title = link.get_text(strip=True)
                    url = link.get('href')
                    
                    if url and not url.startswith('http'):
                        url = urljoin(self.base_url, url)
                    
                    # Cari tanggal
                    date = "Tanggal tidak tersedia"
                    parent = link.parent
                    if parent:
                        date_elem = parent.find('date', class_='latest__date')
                        if not date_elem:
                            date_elem = parent.find('time')
                        if date_elem:
                            date = date_elem.get_text(strip=True)
                    
                    if title and url:
                        articles.append({
                            'title': title,
                            'url': url, 
                            'date': date
                        })
                        
                except Exception:
                    continue
            
            return articles
            
        except Exception as e:
            print(f"❌ Error dalam pencarian: {e}")
            return []
    
    def extract_content(self, article_url):
        """Ekstrak konten artikel (tanpa iklan)"""
        try:
            time.sleep(1.5)  # Delay untuk menghindari rate limiting
            
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Hapus elemen yang tidak diinginkan
            unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']
            for tag in unwanted_tags:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # Hapus iklan berdasarkan class/id
            ad_keywords = ['ad', 'advertisement', 'banner', 'promo', 'sponsor', 'google']
            for keyword in ad_keywords:
                # Hapus berdasarkan class
                for element in soup.find_all(attrs={'class': re.compile(keyword, re.I)}):
                    element.decompose()
                # Hapus berdasarkan id
                for element in soup.find_all(attrs={'id': re.compile(keyword, re.I)}):
                    element.decompose()
            
            # Ekstrak konten artikel
            content_selectors = [
                '.content-detail',
                '.article-content', 
                '.post-content',
                '.entry-content',
                '.main-content',
                'article',
                '.content',
                '[class*="content"]'
            ]
            
            content_text = ""
            
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # Hapus iklan dalam konten
                    for ad_elem in content_div.find_all(attrs={'class': re.compile('ad|banner|promo', re.I)}):
                        ad_elem.decompose()
                    
                    # Ekstrak paragraf
                    paragraphs = content_div.find_all('p')
                    if paragraphs:
                        content_text = ' '.join([
                            p.get_text(strip=True) 
                            for p in paragraphs 
                            if p.get_text(strip=True) and len(p.get_text(strip=True)) > 10
                        ])
                    else:
                        content_text = content_div.get_text(separator=' ', strip=True)
                    
                    if len(content_text) > 100:
                        break
            
            # Fallback: ekstrak dari semua paragraf di body
            if not content_text or len(content_text) < 100:
                body = soup.find('body')
                if body:
                    paragraphs = body.find_all('p')
                    content_text = ' '.join([
                        p.get_text(strip=True) 
                        for p in paragraphs 
                        if len(p.get_text(strip=True)) > 20
                    ])
            
            # Bersihkan teks
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            
            return content_text if content_text else "Konten tidak dapat diekstrak"
            
        except Exception as e:
            return f"Error mengekstrak konten: {str(e)}"
    
    def is_relevant(self, keyword, title, content):
        """Cek apakah artikel relevan dengan keyword"""
        keyword_lower = keyword.lower()
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Keyword harus ada di judul ATAU konten
        return keyword_lower in title_lower or keyword_lower in content_lower
    
    def scrape_news(self, keyword, max_articles=20):
        """Main function untuk scraping"""
        print(f"🚀 Memulai scraping untuk keyword: '{keyword}'")
        print("=" * 60)
        
        # Step 1: Cari artikel
        articles = self.search_articles(keyword)
        if not articles:
            print("❌ Tidak ada artikel ditemukan")
            return []
        
        # Batasi jumlah artikel
        articles = articles[:max_articles]
        
        # Step 2: Ekstrak konten dan filter relevansi
        results = []
        total_processed = 0
        
        for i, article in enumerate(articles, 1):
            print(f"\n📖 Memproses artikel {i}/{len(articles)}")
            print(f"   Judul: {article['title'][:70]}...")
            
            # Ekstrak konten
            content = self.extract_content(article['url'])
            total_processed += 1
            
            # Cek relevansi
            if self.is_relevant(keyword, article['title'], content):
                results.append({
                    'No': len(results) + 1,
                    'Judul': article['title'],
                    'Tanggal': article['date'],
                    'URL': article['url'],
                    'Konten_Preview': content[:300] + "..." if len(content) > 300 else content,
                    'Konten_Lengkap': content,
                    'Keyword_Pencarian': keyword,
                    'Status': 'Relevan'
                })
                print(f"   ✅ RELEVAN - Ditambahkan ke hasil")
            else:
                print(f"   ⚠️ Tidak relevan - Dilewati")
        
        print(f"\n🎉 SCRAPING SELESAI!")
        print(f"   📊 Total diproses: {total_processed} artikel")
        print(f"   ✅ Artikel relevan: {len(results)} artikel")
        
        return results

# ===== FUNGSI UTAMA =====
def scrape_radar_surabaya_news(keyword, max_articles=20, save_to_csv=True):
    """
    Fungsi utama untuk scraping berita Radar Surabaya
    
    Parameters:
    - keyword (str): Kata kunci pencarian
    - max_articles (int): Maksimal artikel yang diproses
    - save_to_csv (bool): Simpan hasil ke CSV
    
    Returns:
    - pandas.DataFrame: Hasil scraping
    """
    
    # Inisialisasi scraper
    scraper = RadarScraper()
    
    # Mulai scraping
    start_time = time.time()
    scraped_data = scraper.scrape_news(keyword, max_articles)
    end_time = time.time()
    
    if not scraped_data:
        print("❌ TIDAK ADA DATA YANG BERHASIL DI-SCRAPE")
        return None
    
    # Buat DataFrame
    df = pd.DataFrame(scraped_data)
    
    # Statistik
    duration = end_time - start_time
    print(f"\n📈 STATISTIK SCRAPING:")
    print(f"   ⏱️ Waktu total: {duration:.2f} detik")
    print(f"   📰 Artikel relevan: {len(scraped_data)}")
    print(f"   🔍 Keyword: '{keyword}'")
    print(f"   ⚡ Kecepatan: {len(scraped_data)/duration:.2f} artikel/detik")
    
    # Simpan ke CSV
    if save_to_csv:
        timestamp = int(time.time())
        filename = f"radar_surabaya_{keyword.replace(' ', '_')}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"   💾 File disimpan: {filename}")
    
    # Preview hasil
    print(f"\n📋 PREVIEW HASIL (5 artikel pertama):")
    preview_df = df[['No', 'Judul', 'Tanggal']].head(5)
    print(preview_df.to_string(index=False, max_colwidth=60))
    
    return df

# ===== EKSEKUSI UTAMA =====
if __name__ == "__main__":
    
    # 🔥 GANTI KEYWORD INI SESUAI KEBUTUHAN ANDA 🔥
    KEYWORD_PENCARIAN = "harga jagung"  # <-- GANTI INI
    
    # Konfigurasi scraping
    MAX_ARTIKEL = 15  # Maksimal artikel yang akan diproses
    SIMPAN_CSV = True  # True = simpan ke CSV, False = tidak simpan
    
    print("🌟 RADAR SURABAYA NEWS SCRAPER 🌟")
    print("Specialized Web Scraping Tool")
    print("=" * 60)
    print(f"🎯 Target Keyword: '{KEYWORD_PENCARIAN}'")
    print(f"📊 Max Articles: {MAX_ARTIKEL}")
    print("=" * 60)
    
    # Jalankan scraping
    try:
        hasil_scraping = scrape_radar_surabaya_news(
            keyword=KEYWORD_PENCARIAN,
            max_articles=MAX_ARTIKEL,
            save_to_csv=SIMPAN_CSV
        )
        
        if hasil_scraping is not None:
            print(f"\n✅ SCRAPING BERHASIL!")
            print(f"📊 Total artikel relevan: {len(hasil_scraping)}")
            
            # Tampilkan contoh artikel
            if len(hasil_scraping) > 0:
                print(f"\n📖 CONTOH ARTIKEL PERTAMA:")
                first_article = hasil_scraping.iloc[0]
                print(f"   Judul: {first_article['Judul']}")
                print(f"   Tanggal: {first_article['Tanggal']}")
                print(f"   Preview: {first_article['Konten_Preview'][:200]}...")
                print(f"   URL: {first_article['URL']}")
            
            # Instruksi download (untuk Google Colab)
            print(f"\n📥 CARA DOWNLOAD FILE CSV DI GOOGLE COLAB:")
            print(f"   from google.colab import files")
            print(f"   files.download('nama_file.csv')")
            
        else:
            print(f"\n❌ SCRAPING GAGAL!")
            print(f"Kemungkinan penyebab:")
            print(f"- Keyword terlalu spesifik")
            print(f"- Website tidak dapat diakses")
            print(f"- Tidak ada artikel yang relevan")
            
    except Exception as e:
        print(f"\n💥 ERROR FATAL: {e}")
        print(f"Silakan coba lagi atau ganti keyword")

# ===== INSTRUKSI TAMBAHAN =====
print(f"""

🔥 CARA MENGGUNAKAN SCRAPER INI:

1️⃣ GANTI KEYWORD:
   Cari baris: KEYWORD_PENCARIAN = "harga jagung"
   Ganti dengan keyword yang Anda inginkan

2️⃣ ATUR KONFIGURASI:
   - MAX_ARTIKEL: Jumlah maksimal artikel (default: 15)
   - SIMPAN_CSV: True/False untuk menyimpan hasil

3️⃣ JALANKAN SCRAPER:
   Jalankan cell ini dan tunggu prosesnya selesai

4️⃣ DOWNLOAD HASIL:
   File CSV akan tersimpan otomatis
   Di Google Colab gunakan: files.download('nama_file.csv')

🎯 CONTOH KEYWORD YANG BAGUS:
   - "harga bahan pokok"
   - "inflasi indonesia"
   - "kebijakan ekonomi"
   - "pembangunan infrastruktur"
   - "pendidikan surabaya"

⚡ FITUR UNGGULAN:
   ✅ Filter artikel relevan otomatis
   ✅ Ekstrak konten tanpa iklan
   ✅ Export ke CSV otomatis
   ✅ Progress monitoring real-time
   ✅ Anti-bot protection

💡 TIPS:
   - Gunakan keyword yang tidak terlalu spesifik
   - Maksimal 20 artikel untuk performa optimal
   - Tunggu proses selesai, jangan interrupt

🛠️ Developed by Senior Data Mining Expert
   30+ Years Experience in Web Scraping & Data Mining
""")