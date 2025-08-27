# -*- coding: utf-8 -*-
"""
Web Scraping Berita dari RadarSurabaya.JawaPos.com - Versi Simple & Powerful
Dikembangkan oleh Dosen Data Mining dengan 40 tahun pengalaman
Anti-blocking techniques applied
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin
import re
from datetime import datetime
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RadarSurabayaSimpleScraper:
    """Scraper sederhana namun powerful untuk RadarSurabaya"""
    
    def __init__(self):
        """Initialize dengan teknik anti-blocking terbaru"""
        # Daftar User-Agent yang sering diupdate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        self.base_url = "https://radarsurabaya.jawapos.com"
        
        # Session dengan konfigurasi optimal
        self.session = requests.Session()
        self.setup_session()
        
        print("🔧 Simple Scraper initialized dengan anti-blocking")
    
    def setup_session(self):
        """Setup session dengan konfigurasi anti-blocking"""
        # Headers dasar yang natural
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session.headers.update(headers)
        
        # Disable SSL verification untuk menghindari error
        self.session.verify = False
    
    def get_page_with_simple_method(self, url, retries=3):
        """Method sederhana untuk mengambil halaman"""
        for attempt in range(retries):
            try:
                print(f"🔄 Percobaan {attempt + 1}: {url}")
                
                # Rotasi User-Agent setiap percobaan
                self.session.headers['User-Agent'] = random.choice(self.user_agents)
                
                # Delay random
                time.sleep(random.uniform(3, 7))
                
                # Request dengan timeout yang cukup
                response = self.session.get(url, timeout=30)
                
                print(f"📊 Status: {response.status_code}, Size: {len(response.content)} bytes")
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    print("🚫 403 Forbidden - Website memblokir request")
                    if attempt < retries - 1:
                        print("🔄 Mencoba dengan delay lebih lama...")
                        time.sleep(random.uniform(10, 20))
                else:
                    print(f"⚠️ Status code: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(5, 15))
        
        return None
    
    def scrape_from_category_pages(self, keyword):
        """Scraping dari halaman kategori sebagai alternatif"""
        print("🔍 Mencoba scraping dari halaman kategori...")
        
        # Daftar kategori yang mungkin relevan
        categories = ['ekonomi', 'nasional', 'daerah', 'bisnis', 'politik']
        
        all_articles = []
        
        for category in categories:
            print(f"\n📂 Mengecek kategori: {category}")
            category_url = f"{self.base_url}/tag/{category}"
            
            response = self.get_page_with_simple_method(category_url, retries=2)
            if response:
                articles = self.extract_articles_simple(response.text, keyword)
                all_articles.extend(articles)
                print(f"✅ Ditemukan {len(articles)} artikel relevan dari kategori {category}")
                
                # Jangan terlalu agresif
                time.sleep(random.uniform(5, 10))
            else:
                print(f"❌ Gagal mengakses kategori {category}")
        
        return all_articles
    
    def extract_articles_simple(self, html_content, keyword):
        """Ekstrak artikel dengan method yang sederhana dan robust"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        
        print("🔍 Mencari artikel dengan berbagai pattern...")
        
        # Pattern 1: Cari semua link yang seperti artikel
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            title = link.get_text(strip=True)
            
            # Filter URL yang seperti artikel berita
            if href and title and len(title) > 15:
                # Pastikan URL lengkap
                if href.startswith('/'):
                    full_url = urljoin(self.base_url, href)
                elif 'radarsurabaya.jawapos.com' not in href:
                    continue
                else:
                    full_url = href
                
                # Filter URL yang seperti artikel (bukan halaman admin/tag/category)
                if any(pattern in full_url for pattern in ['/2024/', '/2023/', '/ekonomi/', '/nasional/', '/daerah/']):
                    # Check relevance dengan keyword
                    if self.is_relevant(title, keyword):
                        articles.append({
                            'title': title,
                            'url': full_url
                        })
        
        # Hapus duplikat berdasarkan URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        print(f"📰 Ditemukan {len(unique_articles)} artikel unik yang relevan")
        return unique_articles[:20]  # Batasi untuk efisiensi
    
    def is_relevant(self, title, keyword):
        """Cek relevansi artikel dengan keyword"""
        title_lower = title.lower()
        keyword_lower = keyword.lower()
        
        # Cek jika ada kata dari keyword yang ada di title
        keyword_words = keyword_lower.split()
        return any(word in title_lower for word in keyword_words if len(word) > 2)
    
    def get_article_content(self, article_url):
        """Ambil konten artikel"""
        print(f"📄 Mengambil konten dari: {article_url}")
        
        response = self.get_page_with_simple_method(article_url, retries=2)
        if not response:
            return "Tanggal tidak ditemukan", "Konten tidak dapat diambil"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ekstrak tanggal
        date_published = self.extract_date_simple(soup)
        
        # Ekstrak konten
        content = self.extract_content_simple(soup)
        
        return date_published, content
    
    def extract_date_simple(self, soup):
        """Ekstrak tanggal dengan method sederhana"""
        # Cari berbagai pattern tanggal
        date_selectors = ['time', 'date', '.date', '.time', '.published']
        
        for selector in date_selectors:
            elements = soup.select(selector)
            for elem in elements:
                date_text = elem.get_text(strip=True)
                if date_text and len(date_text) > 5:
                    return date_text
                
                # Cek atribut datetime
                if elem.has_attr('datetime'):
                    return elem['datetime']
        
        # Fallback: cari dengan regex
        page_text = soup.get_text()
        date_pattern = r'(\d{1,2}\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})'
        match = re.search(date_pattern, page_text)
        if match:
            return match.group(1)
        
        return "Tanggal tidak ditemukan"
    
    def extract_content_simple(self, soup):
        """Ekstrak konten dengan method sederhana"""
        # Hapus elemen yang tidak diinginkan
        for unwanted in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            unwanted.decompose()
        
        # Cari container konten
        content_selectors = [
            'article', '.article-content', '.post-content', 
            '.content', '[class*="content"]', '.entry-content'
        ]
        
        best_content = ""
        max_length = 0
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator=' ', strip=True)
                if len(text) > max_length:
                    max_length = len(text)
                    best_content = text
        
        # Jika tidak ada yang cocok, ambil semua paragraf
        if not best_content:
            paragraphs = soup.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 30:
                    content_parts.append(text)
            best_content = ' '.join(content_parts)
        
        # Bersihkan teks
        best_content = re.sub(r'\s+', ' ', best_content).strip()
        
        if len(best_content) > 15000:
            best_content = best_content[:15000] + "... (dipotong)"
        
        return best_content if best_content else "Konten tidak dapat diambil"
    
    def scrape_news(self, keyword, max_articles=20):
        """Method utama untuk scraping"""
        print(f"🚀 MEMULAI SCRAPING UNTUK KEYWORD: '{keyword}'")
        print(f"📊 Target: {max_articles} artikel")
        
        start_time = datetime.now()
        
        # Method 1: Coba scraping dari halaman kategori
        articles = self.scrape_from_category_pages(keyword)
        
        if not articles:
            print("❌ Tidak menemukan artikel relevan")
            return pd.DataFrame()
        
        print(f"✅ Total artikel ditemukan: {len(articles)}")
        
        # Ambil detail artikel
        results = []
        target_count = min(max_articles, len(articles))
        
        print(f"\n📄 Mengambil detail dari {target_count} artikel...")
        
        for i, article in enumerate(articles[:target_count], 1):
            print(f"\n[{i}/{target_count}] {article['title'][:50]}...")
            
            try:
                date, content = self.get_article_content(article['url'])
                
                results.append({
                    'judul_berita': article['title'],
                    'link_berita': article['url'],
                    'tanggal_rilis': date,
                    'detail_konten': content
                })
                print("   ✅ Berhasil")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    'judul_berita': article['title'],
                    'link_berita': article['url'],
                    'tanggal_rilis': "Error",
                    'detail_konten': f"Error: {str(e)}"
                })
            
            # Delay antar artikel
            if i < target_count:
                time.sleep(random.uniform(4, 8))
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if results:
            df = pd.DataFrame(results)
            print(f"\n✅ SCRAPING SELESAI! ({duration})")
            print(f"📊 {len(results)} artikel berhasil diambil")
            return df
        else:
            print("❌ Tidak ada data berhasil diambil")
            return pd.DataFrame()
    
    def save_results(self, df, keyword):
        """Simpan hasil ke file"""
        if df.empty:
            print("❌ Tidak ada data untuk disimpan")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to CSV
        csv_file = f"radar_surabaya_{keyword.replace(' ', '_')}_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"💾 Saved to: {csv_file}")
        
        # Save to JSON
        json_file = f"radar_surabaya_{keyword.replace(' ', '_')}_{timestamp}.json"
        df.to_json(json_file, orient='records', indent=2, force_ascii=False)
        print(f"💾 Saved to: {json_file}")

def main():
    """Fungsi utama"""
    print("=" * 80)
    print("🎓 RADAR SURABAYA SCRAPER - SIMPLE & POWERFUL")
    print("👨‍🏫 Dosen Data Mining - 40 tahun pengalaman")
    print("🎯 Anti-blocking techniques applied")
    print("=" * 80)
    
    scraper = RadarSurabayaSimpleScraper()
    
    try:
        # Input dari user
        keyword = input("\n🔍 Masukkan keyword pencarian (contoh: 'harga jagung'): ").strip()
        if not keyword:
            print("❌ Keyword tidak boleh kosong!")
            return
        
        # Input jumlah artikel
        while True:
            try:
                max_input = input("📊 Jumlah artikel maksimal (default 20): ").strip()
                if not max_input:
                    max_articles = 20
                    break
                max_articles = int(max_input)
                if 1 <= max_articles <= 100:
                    break
                else:
                    print("❌ Masukkan angka 1-100")
            except ValueError:
                print("❌ Masukkan angka yang valid!")
        
        print(f"\n📝 Konfigurasi:")
        print(f"   • Keyword: '{keyword}'")
        print(f"   • Max artikel: {max_articles}")
        
        # Mulai scraping
        df_results = scraper.scrape_news(keyword, max_articles)
        
        if not df_results.empty:
            # Tampilkan statistik
            print(f"\n📈 STATISTIK:")
            print(f"   • Total artikel: {len(df_results)}")
            
            valid_content = df_results['detail_konten'].apply(
                lambda x: len(str(x)) > 100 and 'Error' not in str(x)
            ).sum()
            print(f"   • Konten valid: {valid_content}")
            
            # Simpan hasil
            scraper.save_results(df_results, keyword)
            
            # Preview hasil
            print(f"\n📄 PREVIEW (3 artikel pertama):")
            print("=" * 80)
            for idx, row in df_results.head(3).iterrows():
                print(f"\n📰 {row['judul_berita']}")
                print(f"📅 {row['tanggal_rilis']}")
                print(f"🔗 {row['link_berita']}")
                content_preview = str(row['detail_konten'])[:300] + "..."
                print(f"📝 {content_preview}")
                print("-" * 50)
        
        else:
            print("\n❌ Tidak ada data berhasil diambil")
            print("💡 Tips:")
            print("   • Coba keyword yang lebih umum")
            print("   • Periksa koneksi internet")
            print("   • Website mungkin sedang down")
    
    except KeyboardInterrupt:
        print("\n⚠️ Program dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n👋 Terima kasih!")

if __name__ == "__main__":
    main()