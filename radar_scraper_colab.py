# RADAR SURABAYA NEWS SCRAPER - GOOGLE COLAB VERSION
# Developed by Senior Data Mining & Full Stack Engineer (30+ years experience)
# Copy dan paste seluruh kode ini ke dalam satu cell di Google Colab

# ===== INSTALL DEPENDENCIES (Jalankan sekali di awal) =====
# !pip install requests beautifulsoup4 pandas lxml

# ===== IMPORT LIBRARIES =====
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin
import warnings
warnings.filterwarnings('ignore')

# ===== MAIN SCRAPER CLASS =====
class RadarSurabayaScraper:
    def __init__(self):
        self.base_url = "https://radarsurabaya.jawapos.com"
        self.search_url = f"{self.base_url}/search"
        self.session = requests.Session()
        
        # Headers anti-bot detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(self.headers)
        self.delay = 1.5  # Delay antar request
        
    def search_news(self, keyword):
        """Pencarian berita berdasarkan keyword"""
        try:
            print(f"🔍 Mencari berita: '{keyword}'")
            params = {'q': keyword}
            response = self.session.get(self.search_url, params=params, timeout=30)
            response.raise_for_status()
            print("✅ Berhasil mengakses halaman pencarian")
            return response.text
        except Exception as e:
            print(f"❌ Error pencarian: {e}")
            return None
    
    def extract_article_links(self, html_content):
        """Ekstrak link artikel dari hasil pencarian"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Cari semua link artikel
        article_links = soup.find_all('a', class_='latest__link')
        print(f"📰 Ditemukan {len(article_links)} artikel")
        
        for link in article_links:
            try:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                if href and not href.startswith('http'):
                    href = urljoin(self.base_url, href)
                
                # Cari tanggal
                date = "Tanggal tidak ditemukan"
                parent = link.parent
                if parent:
                    date_elem = parent.find('date', class_='latest__date')
                    if date_elem:
                        date = date_elem.get_text(strip=True)
                
                if title and href:
                    articles.append({
                        'title': title,
                        'url': href,
                        'date': date
                    })
            except Exception as e:
                continue
        
        return articles
    
    def extract_content(self, url):
        """Ekstrak konten artikel (tanpa iklan)"""
        try:
            time.sleep(self.delay)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Hapus elemen tidak diinginkan
            for tag in ['script', 'style', 'nav', 'header', 'footer', 'aside']:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # Hapus iklan
            ad_patterns = ['ad', 'advertisement', 'banner', 'promo', 'sponsor']
            for pattern in ad_patterns:
                for element in soup.find_all(attrs={'class': re.compile(pattern, re.I)}):
                    element.decompose()
                for element in soup.find_all(attrs={'id': re.compile(pattern, re.I)}):
                    element.decompose()
            
            # Ekstrak konten
            content_text = ""
            selectors = ['.content-detail', '.article-content', '.post-content', 
                        '.entry-content', '.main-content', 'article', '.content']
            
            for selector in selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    paragraphs = content_div.find_all('p')
                    if paragraphs:
                        content_text = ' '.join([p.get_text(strip=True) 
                                               for p in paragraphs if p.get_text(strip=True)])
                    else:
                        content_text = content_div.get_text(separator=' ', strip=True)
                    
                    if len(content_text) > 100:
                        break
            
            # Fallback: ekstrak dari semua paragraf
            if not content_text or len(content_text) < 100:
                paragraphs = soup.find_all('p')
                content_text = ' '.join([p.get_text(strip=True) 
                                       for p in paragraphs 
                                       if len(p.get_text(strip=True)) > 20])
            
            # Bersihkan teks
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            return content_text if content_text else "Konten tidak dapat diekstrak"
            
        except Exception as e:
            print(f"❌ Error ekstrak konten: {e}")
            return "Error mengekstrak konten"
    
    def is_relevant(self, keyword, title, content):
        """Cek relevansi berdasarkan keyword"""
        keyword_lower = keyword.lower()
        return (keyword_lower in title.lower() or 
                keyword_lower in content.lower())
    
    def scrape(self, keyword, max_articles=15):
        """Fungsi utama scraping"""
        print("🚀 RADAR SURABAYA SCRAPER STARTED")
        print("=" * 50)
        
        # Step 1: Pencarian
        search_html = self.search_news(keyword)
        if not search_html:
            return []
        
        # Step 2: Ekstrak links
        articles = self.extract_article_links(search_html)
        if not articles:
            print("❌ Tidak ada artikel ditemukan")
            return []
        
        articles = articles[:max_articles]
        
        # Step 3: Ekstrak konten
        results = []
        for i, article in enumerate(articles, 1):
            print(f"\n📖 Proses artikel {i}/{len(articles)}")
            print(f"   Judul: {article['title'][:60]}...")
            
            content = self.extract_content(article['url'])
            
            if self.is_relevant(keyword, article['title'], content):
                results.append({
                    'No': len(results) + 1,
                    'Judul': article['title'],
                    'Tanggal': article['date'],
                    'URL': article['url'],
                    'Konten': content[:500] + "..." if len(content) > 500 else content,
                    'Konten_Lengkap': content,
                    'Keyword': keyword,
                    'Relevan': 'Ya'
                })
                print("   ✅ Relevan - ditambahkan")
            else:
                print("   ⚠️ Tidak relevan - dilewati")
        
        print(f"\n🎉 SELESAI! {len(results)} artikel relevan ditemukan")
        return results

# ===== FUNGSI UTAMA UNTUK GOOGLE COLAB =====
def scrape_radar_surabaya(keyword, max_articles=15, save_csv=True):
    """
    Fungsi utama untuk scraping Radar Surabaya
    
    Parameters:
    - keyword: kata kunci pencarian (str)
    - max_articles: maksimal artikel yang diproses (int, default: 15)
    - save_csv: simpan hasil ke CSV (bool, default: True)
    
    Returns:
    - DataFrame dengan hasil scraping
    """
    
    scraper = RadarSurabayaScraper()
    
    # Mulai scraping
    start_time = time.time()
    data = scraper.scrape(keyword, max_articles)
    end_time = time.time()
    
    if not data:
        print("❌ Tidak ada data yang berhasil di-scrape")
        return None
    
    # Buat DataFrame
    df = pd.DataFrame(data)
    
    # Simpan ke CSV jika diminta
    if save_csv:
        filename = f"radar_surabaya_{keyword.replace(' ', '_')}_{int(time.time())}.csv"
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"💾 Data disimpan ke: {filename}")
    
    # Statistik
    duration = end_time - start_time
    print(f"\n📊 STATISTIK SCRAPING:")
    print(f"   ⏱️  Waktu: {duration:.2f} detik")
    print(f"   📰 Artikel relevan: {len(data)}")
    print(f"   🔍 Keyword: '{keyword}'")
    print(f"   ⚡ Kecepatan: {len(data)/duration:.2f} artikel/detik")
    
    # Preview hasil
    print(f"\n📋 PREVIEW HASIL:")
    display_df = df[['No', 'Judul', 'Tanggal', 'Relevan']].head(5)
    print(display_df.to_string(index=False))
    
    return df

# ===== CONTOH PENGGUNAAN =====
"""
CARA MENGGUNAKAN DI GOOGLE COLAB:

1. Copy seluruh kode ini ke dalam satu cell di Google Colab
2. Jalankan cell tersebut
3. Gunakan fungsi scrape_radar_surabaya() untuk scraping

Contoh:
"""

# CONTOH SCRAPING
if __name__ == "__main__":
    # Ganti keyword sesuai kebutuhan
    keyword_pencarian = "harga jagung"  # GANTI INI DENGAN KEYWORD ANDA
    
    print("🌟 MEMULAI SCRAPING RADAR SURABAYA 🌟")
    print(f"Keyword: {keyword_pencarian}")
    print("=" * 60)
    
    # Jalankan scraping
    hasil = scrape_radar_surabaya(
        keyword=keyword_pencarian,
        max_articles=20,  # Maksimal 20 artikel
        save_csv=True     # Simpan ke CSV
    )
    
    if hasil is not None:
        print(f"\n✅ SCRAPING BERHASIL!")
        print(f"Total artikel relevan: {len(hasil)}")
        
        # Tampilkan 3 artikel pertama
        print(f"\n📖 CONTOH 3 ARTIKEL PERTAMA:")
        for i in range(min(3, len(hasil))):
            article = hasil.iloc[i]
            print(f"\n{i+1}. {article['Judul']}")
            print(f"   Tanggal: {article['Tanggal']}")
            print(f"   Konten: {article['Konten'][:200]}...")
            print(f"   URL: {article['URL']}")
    else:
        print("❌ SCRAPING GAGAL - Tidak ada data ditemukan")

# ===== INSTRUKSI PENGGUNAAN =====
print("""
🔥 RADAR SURABAYA SCRAPER SIAP DIGUNAKAN! 🔥

CARA MENGGUNAKAN:
1. Ganti variabel 'keyword_pencarian' dengan keyword yang Anda inginkan
2. Jalankan cell ini
3. Hasil akan disimpan dalam file CSV dan ditampilkan di output

CONTOH KEYWORD:
- "harga jagung"
- "inflasi indonesia" 
- "kebijakan pemerintah"
- "ekonomi surabaya"

FITUR:
✅ Scraping otomatis berdasarkan keyword
✅ Filter artikel relevan (keyword ada di judul/konten)
✅ Ekstrak konten tanpa iklan
✅ Simpan hasil ke CSV
✅ Tampilkan statistik dan preview

Developed by Senior Data Mining Expert (30+ years experience)
""")