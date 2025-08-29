#!/usr/bin/env python3
"""
Radar Surabaya News Scraper
Developed by: Senior Data Mining & Full Stack Engineer (30+ years experience)
Website: https://radarsurabaya.jawapos.com/

This comprehensive scraper extracts news articles based on user search queries,
filtering for keyword relevance in both titles and content.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin, quote_plus
import warnings
warnings.filterwarnings('ignore')

class RadarSurabayaScraper:
    def __init__(self):
        self.base_url = "https://radarsurabaya.jawapos.com"
        self.search_url = f"{self.base_url}/search"
        self.session = requests.Session()
        
        # Headers untuk menghindari deteksi bot
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(self.headers)
        
        # Delay antar request untuk menghindari rate limiting
        self.delay = 2
        
    def search_news(self, keyword):
        """
        Melakukan pencarian berita berdasarkan keyword
        """
        search_params = {'q': keyword}
        
        try:
            print(f"🔍 Mencari berita dengan keyword: '{keyword}'")
            response = self.session.get(self.search_url, params=search_params, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Berhasil mengakses halaman pencarian")
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error saat mengakses halaman pencarian: {e}")
            return None
    
    def extract_article_links(self, html_content):
        """
        Mengekstrak link artikel dari halaman pencarian
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        # Mencari semua link artikel dengan class 'latest__link'
        article_links = soup.find_all('a', class_='latest__link')
        
        print(f"📰 Ditemukan {len(article_links)} artikel")
        
        for link in article_links:
            try:
                # Ekstrak informasi artikel
                title = link.get_text(strip=True)
                href = link.get('href')
                
                # Pastikan URL lengkap
                if href and not href.startswith('http'):
                    href = urljoin(self.base_url, href)
                
                # Cari tanggal dari elemen selanjutnya
                date_element = None
                
                # Coba beberapa metode untuk mencari tanggal
                parent = link.parent
                if parent:
                    # Metode 1: Cari sibling dengan class 'latest__date'
                    date_element = parent.find('date', class_='latest__date')
                    
                    # Metode 2: Cari dalam parent
                    if not date_element:
                        date_element = parent.find('time')
                    
                    # Metode 3: Cari dengan berbagai class tanggal
                    if not date_element:
                        date_element = parent.find(class_=re.compile(r'date|time'))
                
                date = date_element.get_text(strip=True) if date_element else "Tanggal tidak ditemukan"
                
                if title and href:
                    articles.append({
                        'title': title,
                        'url': href,
                        'date': date
                    })
                    
            except Exception as e:
                print(f"⚠️ Error saat mengekstrak artikel: {e}")
                continue
        
        return articles
    
    def extract_article_content(self, article_url):
        """
        Mengekstrak konten lengkap dari artikel
        """
        try:
            time.sleep(self.delay)  # Delay untuk menghindari rate limiting
            
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Hapus elemen yang tidak diinginkan (iklan, script, dll)
            unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside']
            for tag in unwanted_tags:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # Hapus elemen iklan berdasarkan class/id
            ad_selectors = [
                '[class*="ad"]', '[id*="ad"]', '[class*="advertisement"]',
                '[class*="banner"]', '[class*="promo"]', '[class*="sponsor"]'
            ]
            
            for selector in ad_selectors:
                for element in soup.select(selector):
                    element.decompose()
            
            # Ekstrak konten artikel
            content_text = ""
            
            # Coba berbagai selector untuk konten artikel
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
            
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # Hapus elemen iklan dalam konten
                    for ad_element in content_div.find_all(['div', 'span'], class_=re.compile(r'ad|banner|promo')):
                        ad_element.decompose()
                    
                    # Ekstrak teks
                    paragraphs = content_div.find_all(['p', 'div'], string=True)
                    if paragraphs:
                        content_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    else:
                        content_text = content_div.get_text(separator=' ', strip=True)
                    
                    if len(content_text) > 100:  # Pastikan konten cukup panjang
                        break
            
            # Jika tidak menemukan konten dengan selector khusus, coba ekstrak dari body
            if not content_text or len(content_text) < 100:
                body = soup.find('body')
                if body:
                    # Hapus navigasi, header, footer
                    for unwanted in body.find_all(['nav', 'header', 'footer', 'aside']):
                        unwanted.decompose()
                    
                    paragraphs = body.find_all('p')
                    if paragraphs:
                        content_text = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
            # Bersihkan teks
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            
            return content_text if content_text else "Konten tidak dapat diekstrak"
            
        except Exception as e:
            print(f"❌ Error saat mengekstrak konten dari {article_url}: {e}")
            return "Error mengekstrak konten"
    
    def is_relevant(self, keyword, title, content):
        """
        Memeriksa relevansi artikel berdasarkan keyword
        """
        keyword_lower = keyword.lower()
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Cek keberadaan keyword di judul atau konten
        return keyword_lower in title_lower or keyword_lower in content_lower
    
    def scrape_news(self, keyword, max_articles=20):
        """
        Fungsi utama untuk scraping berita
        """
        print("🚀 Memulai scraping Radar Surabaya...")
        print("=" * 60)
        
        # Step 1: Cari artikel
        search_html = self.search_news(keyword)
        if not search_html:
            print("❌ Gagal mengakses halaman pencarian")
            return []
        
        # Step 2: Ekstrak link artikel
        articles = self.extract_article_links(search_html)
        if not articles:
            print("❌ Tidak ditemukan artikel")
            return []
        
        # Batasi jumlah artikel
        articles = articles[:max_articles]
        
        # Step 3: Ekstrak konten setiap artikel
        scraped_data = []
        
        for i, article in enumerate(articles, 1):
            print(f"\n📖 Memproses artikel {i}/{len(articles)}: {article['title'][:50]}...")
            
            # Ekstrak konten
            content = self.extract_article_content(article['url'])
            
            # Cek relevansi
            if self.is_relevant(keyword, article['title'], content):
                scraped_data.append({
                    'No': len(scraped_data) + 1,
                    'Judul': article['title'],
                    'Tanggal': article['date'],
                    'URL': article['url'],
                    'Konten': content,
                    'Keyword': keyword,
                    'Relevan': 'Ya'
                })
                print(f"✅ Artikel relevan - ditambahkan ke dataset")
            else:
                print(f"⚠️ Artikel tidak relevan - dilewati")
        
        print(f"\n🎉 Selesai! Ditemukan {len(scraped_data)} artikel yang relevan")
        return scraped_data
    
    def save_to_csv(self, data, filename=None):
        """
        Menyimpan data ke file CSV
        """
        if not data:
            print("❌ Tidak ada data untuk disimpan")
            return
        
        if not filename:
            keyword = data[0]['Keyword'].replace(' ', '_')
            filename = f"radar_surabaya_{keyword}_{int(time.time())}.csv"
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"💾 Data berhasil disimpan ke: {filename}")
        
        # Tampilkan statistik
        print(f"\n📊 Statistik Scraping:")
        print(f"   - Total artikel: {len(data)}")
        print(f"   - Keyword: {data[0]['Keyword']}")
        print(f"   - File: {filename}")
        
        return filename

def main():
    """
    Fungsi utama untuk menjalankan scraper
    """
    print("🌟 RADAR SURABAYA NEWS SCRAPER 🌟")
    print("Developed by Senior Data Mining Expert (30+ years)")
    print("=" * 60)
    
    # Inisialisasi scraper
    scraper = RadarSurabayaScraper()
    
    # Input keyword dari user
    while True:
        keyword = input("\n🔍 Masukkan keyword pencarian (atau 'quit' untuk keluar): ").strip()
        
        if keyword.lower() in ['quit', 'exit', 'q']:
            print("👋 Terima kasih telah menggunakan scraper!")
            break
        
        if not keyword:
            print("❌ Keyword tidak boleh kosong!")
            continue
        
        # Input jumlah artikel maksimal
        try:
            max_articles = int(input("📊 Maksimal artikel yang akan di-scrape (default: 20): ") or "20")
        except ValueError:
            max_articles = 20
        
        # Mulai scraping
        print(f"\n🚀 Memulai scraping untuk keyword: '{keyword}'")
        start_time = time.time()
        
        scraped_data = scraper.scrape_news(keyword, max_articles)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if scraped_data:
            # Simpan hasil
            filename = scraper.save_to_csv(scraped_data)
            
            print(f"\n⏱️ Waktu scraping: {duration:.2f} detik")
            print(f"⚡ Kecepatan: {len(scraped_data)/duration:.2f} artikel/detik")
            
            # Tampilkan preview data
            print(f"\n📋 Preview 3 artikel pertama:")
            df = pd.DataFrame(scraped_data)
            print(df[['No', 'Judul', 'Tanggal']].head(3).to_string(index=False))
            
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
        
        print("\n" + "="*60)

# Fungsi untuk Google Colab
def scrape_radar_surabaya_colab(keyword, max_articles=20, save_file=True):
    """
    Fungsi khusus untuk Google Colab
    """
    scraper = RadarSurabayaScraper()
    
    print(f"🔍 Scraping keyword: '{keyword}'")
    scraped_data = scraper.scrape_news(keyword, max_articles)
    
    if scraped_data and save_file:
        filename = scraper.save_to_csv(scraped_data)
        return scraped_data, filename
    
    return scraped_data, None

if __name__ == "__main__":
    # Untuk penggunaan langsung
    main()
    
# CONTOH PENGGUNAAN DI GOOGLE COLAB:
"""
# Install dependencies (jalankan di cell pertama)
!pip install requests beautifulsoup4 pandas lxml

# Import dan jalankan scraper (jalankan di cell kedua)
from radar_surabaya_scraper import scrape_radar_surabaya_colab
import pandas as pd

# Scraping dengan keyword
keyword = "harga jagung"  # Ganti dengan keyword yang diinginkan
data, filename = scrape_radar_surabaya_colab(keyword, max_articles=15)

# Tampilkan hasil
if data:
    df = pd.DataFrame(data)
    print("📊 Hasil Scraping:")
    print(df[['No', 'Judul', 'Tanggal']].head(10))
    
    # Download file CSV (opsional)
    if filename:
        from google.colab import files
        files.download(filename)
else:
    print("Tidak ada data yang berhasil di-scrape")
"""