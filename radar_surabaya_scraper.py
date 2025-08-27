# -*- coding: utf-8 -*-
"""
Web Scraping Berita dari RadarSurabaya.JawaPos.com
Dibuat untuk: Keperluan riset dan akademis
Dosen Data Mining dengan 40 tahun pengalaman scraping
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import quote, urljoin
import re
from datetime import datetime
import json
# Untuk menghindari error SSL
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Tambahan untuk bypass CloudFlare dan proteksi
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("⚠️ Beberapa modul tambahan tidak tersedia, menggunakan metode standar")

class RadarSurabayaScraper:
    """Scraper untuk mengambil data berita dari RadarSurabaya.JawaPos.com"""

    def __init__(self):
        """Inisialisasi session dan headers dengan teknik anti-detection advanced"""
        self.session = requests.Session()
        
        # Rotasi User-Agent untuk menghindari deteksi
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Setup headers yang lebih lengkap dan realistis
        self.setup_headers()
        
        # Base URL untuk website
        self.base_url = "https://radarsurabaya.jawapos.com"
        
        # Cookie jar untuk menyimpan session
        self.session.cookies.clear()
        
        # Setup retry strategy yang lebih robust
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        print("🔧 Session initialized dengan advanced anti-detection")
    
    def setup_headers(self):
        """Setup headers yang rotasi dan realistis"""
        user_agent = random.choice(self.user_agents)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7,ms;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        self.session.headers.clear()
        self.session.headers.update(headers)
    
    def simulate_browser_visit(self):
        """Simulasi kunjungan browser normal ke homepage terlebih dahulu"""
        try:
            print("🌐 Mengakses homepage untuk simulasi browser...")
            
            # Reset headers
            self.setup_headers()
            
            # Kunjungi homepage dulu
            homepage_response = self.session.get(
                self.base_url, 
                timeout=15,
                allow_redirects=True,
                verify=False
            )
            
            if homepage_response.status_code == 200:
                print("✅ Homepage berhasil diakses")
                
                # Ambil cookies yang diberikan
                print(f"🍪 Cookies diterima: {len(self.session.cookies)} cookies")
                
                # Update referer untuk request selanjutnya
                self.session.headers.update({
                    'Referer': self.base_url + '/'
                })
                
                # Delay setelah homepage
                time.sleep(random.uniform(3, 6))
                return True
            else:
                print(f"⚠️ Homepage response: {homepage_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error mengakses homepage: {e}")
            return False

    def get_search_url(self, keyword):
        """
        Membangun URL pencarian RadarSurabaya berdasarkan keyword
        Format: https://radarsurabaya.jawapos.com/search?q=keyword
        """
        # Encode keyword untuk URL (spasi menjadi +)
        encoded_keyword = keyword.replace(' ', '+')
        search_url = f"{self.base_url}/search?q={encoded_keyword}"
        print(f"🔍 URL Pencarian yang Dibuat: {search_url}")
        return search_url

    def get_page_content(self, url, max_retries=3, is_search=False):
        """
        Mendapatkan konten halaman dengan teknik advanced anti-detection
        """
        for attempt in range(max_retries):
            try:
                print(f"🔄 Mengakses halaman (Percobaan {attempt + 1})...")
                
                # Rotasi User-Agent setiap percobaan
                self.setup_headers()
                
                # Update referer berdasarkan konteks
                if is_search:
                    self.session.headers.update({
                        'Referer': self.base_url + '/',
                        'Sec-Fetch-Site': 'same-origin'
                    })
                else:
                    self.session.headers.update({
                        'Referer': self.base_url + '/search',
                        'Sec-Fetch-Site': 'same-origin'
                    })
                
                # Delay yang lebih bervariasi
                delay = random.uniform(5, 10) if attempt > 0 else random.uniform(2, 4)
                time.sleep(delay)
                
                # Request dengan parameter tambahan
                response = self.session.get(
                    url, 
                    timeout=20,
                    verify=False,
                    allow_redirects=True,
                    stream=False
                )
                
                print(f"📊 Response Status: {response.status_code}")
                print(f"📊 Response Size: {len(response.content):,} bytes")
                print(f"📊 Response Headers: {dict(list(response.headers.items())[:3])}")
                
                if response.status_code == 200:
                    if len(response.content) > 1000:
                        print(f"✅ Berhasil mengakses halaman")
                        return response
                    else:
                        print(f"⚠️ Response terlalu kecil, mungkin halaman kosong")
                elif response.status_code == 403:
                    print(f"🚫 403 Forbidden - Mencoba teknik bypass...")
                    # Coba dengan headers yang berbeda
                    if attempt < max_retries - 1:
                        self.simulate_browser_visit()
                elif response.status_code == 404:
                    print(f"❌ 404 Not Found - URL mungkin tidak valid")
                    break
                else:
                    print(f"⚠️ Status code tidak terduga: {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout pada percobaan {attempt + 1}")
            except requests.exceptions.ConnectionError:
                print(f"🔌 Connection error pada percobaan {attempt + 1}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error: {e} (Percobaan {attempt + 1})")

            # Delay progresif untuk retry
            if attempt < max_retries - 1:
                retry_delay = random.uniform(15, 30) * (attempt + 1)
                print(f"⏳ Menunggu {retry_delay:.1f} detik sebelum retry...")
                time.sleep(retry_delay)

        print("❌ Gagal mengakses halaman setelah semua percobaan")
        return None

    def filter_articles_by_keyword(self, articles_data, keyword):
        """
        Filter artikel berdasarkan keyword - pastikan judul mengandung keyword
        """
        keyword_lower = keyword.lower()
        filtered_articles = []
        
        for article in articles_data:
            title_lower = article['title'].lower()
            if any(word in title_lower for word in keyword_lower.split()):
                filtered_articles.append(article)
                
        print(f"🔍 Filter keyword '{keyword}': {len(filtered_articles)} dari {len(articles_data)} artikel")
        return filtered_articles

    def extract_article_links_from_search(self, search_html, keyword):
        """
        Mengekstrak link dan judul artikel dari halaman hasil pencarian RadarSurabaya
        Berdasarkan XPath: /html/body/div[3]/div/div/div[2]/section/div[3]/div[1]/div[2]/h2/a
        """
        if not search_html:
            return []

        soup = BeautifulSoup(search_html, 'html.parser')
        articles_data = []

        # Strategi 1: Gunakan selector berdasarkan XPath yang diberikan
        # XPath: /html/body/div[3]/div/div/div[2]/section/div[3]/div[1]/div[2]/h2/a
        # Konversi ke CSS selector yang lebih fleksibel
        print("🔍 Mencari artikel dengan berbagai strategi...")
        
        # Strategi 1: Cari semua link dalam tag h2 yang ada di section
        h2_links = soup.select('section h2 a, h2 a')
        print(f"📰 Strategi 1 - H2 links ditemukan: {len(h2_links)}")
        
        for link in h2_links:
            href = link.get('href')
            title = link.get_text(strip=True)
            
            if href and title and len(title) > 5:
                # Pastikan URL lengkap
                if href.startswith('/'):
                    full_url = urljoin(self.base_url, href)
                elif not href.startswith('http'):
                    full_url = urljoin(self.base_url, '/' + href)
                else:
                    full_url = href
                
                # Validasi URL dari domain radarsurabaya
                if 'radarsurabaya.jawapos.com' in full_url:
                    articles_data.append({
                        'title': title,
                        'url': full_url
                    })

        # Strategi 2: Cari berdasarkan class atau struktur umum berita
        if len(articles_data) < 5:  # Jika hasil masih sedikit
            print("📰 Strategi 2 - Mencari dengan pattern umum...")
            
            # Cari semua link yang mengarah ke artikel
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if not href or not title or len(title) < 10:
                    continue
                    
                # Filter URL yang seperti artikel berita
                if (href.startswith('/') or 'radarsurabaya.jawapos.com' in href) and \
                   any(category in href for category in ['ekonomi', 'nasional', 'daerah', 'politik', 'olahraga', 'lifestyle']):
                    
                    # Pastikan URL lengkap
                    if href.startswith('/'):
                        full_url = urljoin(self.base_url, href)
                    else:
                        full_url = href
                    
                    # Hindari duplikat
                    if not any(art['url'] == full_url for art in articles_data):
                        articles_data.append({
                            'title': title,
                            'url': full_url
                        })

        # Strategi 3: Fallback - cari dari struktur div dan card
        if len(articles_data) < 3:
            print("📰 Strategi 3 - Fallback search...")
            
            # Cari container artikel
            containers = soup.find_all(['div', 'article'], class_=re.compile(r'(card|item|post|news|article)', re.I))
            for container in containers:
                link = container.find('a', href=True)
                if link:
                    href = link.get('href')
                    
                    # Cari judul di dalam container
                    title_elem = container.find(['h1', 'h2', 'h3', 'h4'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    else:
                        title = link.get_text(strip=True)
                    
                    if href and title and len(title) > 10:
                        if href.startswith('/'):
                            full_url = urljoin(self.base_url, href)
                        else:
                            full_url = href
                            
                        if 'radarsurabaya.jawapos.com' in full_url:
                            # Hindari duplikat
                            if not any(art['url'] == full_url for art in articles_data):
                                articles_data.append({
                                    'title': title,
                                    'url': full_url
                                })

        print(f"✅ Total artikel ditemukan: {len(articles_data)}")
        
        # Filter artikel berdasarkan keyword
        filtered_articles = self.filter_articles_by_keyword(articles_data, keyword)
        
        # Tampilkan beberapa contoh
        if filtered_articles:
            print("📋 Contoh artikel yang ditemukan:")
            for i, article in enumerate(filtered_articles[:3], 1):
                print(f"   {i}. {article['title'][:60]}...")
        
        return filtered_articles

    def extract_date_from_article(self, soup):
        """
        Mengekstrak tanggal rilis dari artikel
        Berdasarkan XPath: /html/body/div[3]/div/div/div[2]/section/div[3]/div[1]/div[2]/date
        """
        date_published = None
        
        # Strategi 1: Cari tag date
        date_elements = soup.find_all('date')
        for date_elem in date_elements:
            date_text = date_elem.get_text(strip=True)
            if date_text and len(date_text) > 5:
                date_published = date_text
                break
        
        # Strategi 2: Cari tag time dengan datetime
        if not date_published:
            time_elements = soup.find_all('time', datetime=True)
            for time_elem in time_elements:
                date_published = time_elem.get('datetime')
                if date_published:
                    break
        
        # Strategi 3: Cari dengan class yang mengandung date/time
        if not date_published:
            date_classes = soup.find_all(class_=re.compile(r'(date|time|publish)', re.I))
            for elem in date_classes:
                date_text = elem.get_text(strip=True)
                if date_text and len(date_text) > 5:
                    date_published = date_text
                    break
        
        # Strategi 4: Regex pattern di seluruh halaman
        if not date_published:
            page_text = soup.get_text()
            date_patterns = [
                r'(\d{1,2}\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{4}[/-]\d{2}[/-]\d{2})'
            ]
            for pattern in date_patterns:
                match = re.search(pattern, page_text)
                if match:
                    date_published = match.group(1)
                    break
        
        return date_published if date_published else "Tanggal tidak ditemukan"

    def extract_article_content(self, soup):
        """
        Mengekstrak konten artikel berdasarkan XPath yang diberikan
        XPath: /html/body/div[4]/div/div/div[2]/div/div[1]
        """
        content_text = ""
        
        # Strategi 1: Cari berdasarkan struktur XPath yang diberikan
        # Konversi XPath ke selector CSS yang lebih fleksibel
        content_selectors = [
            'body > div:nth-child(4) > div > div > div:nth-child(2) > div > div:first-child',  # XPath exact
            'div[class*="content"] div:first-child',  # Content container
            'article div:first-child',  # Article content
            '.article-content',  # Class umum
            '.post-content',  # Class umum
            '.news-content',  # Class umum
            '[class*="content"]',  # Any content class
        ]
        
        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element and len(content_element.get_text(strip=True)) > 100:
                print(f"   📝 Konten ditemukan dengan selector: {selector}")
                break
        
        # Strategi 2: Cari container artikel yang paling besar
        if not content_element:
            print("   🔍 Mencari container konten terbesar...")
            all_divs = soup.find_all('div')
            max_text_length = 0
            best_div = None
            
            for div in all_divs:
                # Bersihkan elemen yang tidak diinginkan
                temp_div = div.__copy__()
                for unwanted in temp_div(['script', 'style', 'nav', 'aside', 'header', 'footer']):
                    unwanted.decompose()
                
                text_length = len(temp_div.get_text(strip=True))
                if text_length > max_text_length and text_length > 200:
                    max_text_length = text_length
                    best_div = div
            
            if best_div:
                content_element = best_div
                print(f"   📝 Menggunakan container terbesar ({max_text_length} karakter)")

        if content_element:
            # Bersihkan elemen yang tidak diinginkan (iklan, sidebar, dll)
            for unwanted in content_element(['script', 'style', 'nav', 'aside', 'header', 'footer', 'noscript']):
                unwanted.decompose()
            
            # Hapus elemen dengan class yang mengandung ads, iklan, etc
            for unwanted in content_element.find_all(class_=re.compile(r'.*(ads|advertisement|iklan|promo|related|widget|sidebar|footer|banner).*', re.I)):
                unwanted.decompose()
            
            for unwanted in content_element.find_all(id=re.compile(r'.*(ads|advertisement|iklan|promo|related|widget|banner).*', re.I)):
                unwanted.decompose()
            
            # Ambil teks konten
            content_text = content_element.get_text(separator=' ', strip=True)
        else:
            print("   ⚠️ Tidak menemukan container konten, menggunakan fallback...")
            # Fallback: ambil semua paragraf
            paragraphs = soup.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 20:  # Hanya paragraf yang cukup panjang
                    content_parts.append(text)
            content_text = ' '.join(content_parts)

        # Bersihkan teks
        content_text = re.sub(r'\s+', ' ', content_text).strip()
        
        # Potong jika terlalu panjang
        if len(content_text) > 20000:
            content_text = content_text[:20000] + "... (konten dipotong)"
        
        return content_text if content_text else "Konten tidak dapat diambil"

    def extract_article_details(self, article_url, keyword):
        """
        Mengekstrak detail artikel: tanggal dan konten
        Juga memfilter konten berdasarkan keyword
        """
        print(f"📄 Mengambil detail dari: {article_url}")
        html_content = self.get_page_content(article_url)
        if not html_content:
            return None, None

        soup = BeautifulSoup(html_content.text, 'html.parser')

        # Ekstrak tanggal
        date_published = self.extract_date_from_article(soup)
        
        # Ekstrak konten
        content_text = self.extract_article_content(soup)
        
        # Filter konten berdasarkan keyword
        keyword_lower = keyword.lower()
        content_lower = content_text.lower()
        
        # Cek apakah konten mengandung keyword
        if not any(word in content_lower for word in keyword_lower.split()):
            print(f"   ⚠️ Konten tidak relevan dengan keyword '{keyword}'")
            return date_published, "Konten tidak relevan dengan keyword pencarian"

        return date_published, content_text

    def try_alternative_search_methods(self, keyword):
        """
        Mencoba metode pencarian alternatif jika metode utama gagal
        """
        print("🔄 Mencoba metode pencarian alternatif...")
        
        alternative_urls = [
            f"{self.base_url}/tag/{keyword.replace(' ', '-')}",  # Tag-based search
            f"{self.base_url}/category/ekonomi",  # Category search untuk keyword ekonomi
            f"{self.base_url}/",  # Homepage untuk scraping artikel terbaru
        ]
        
        for i, alt_url in enumerate(alternative_urls, 1):
            print(f"🔍 Alternatif {i}: {alt_url}")
            response = self.get_page_content(alt_url, max_retries=2)
            if response:
                print(f"✅ Berhasil mengakses alternatif {i}")
                return response, alt_url
        
        return None, None

    def scrape_radar_surabaya_news(self, keyword, max_articles=50):
        """
        Scraping berita dari RadarSurabaya berdasarkan keyword dengan teknik advanced
        """
        print(f"🚀 MEMULAI SCRAPING BERITA RADAR SURABAYA UNTUK KEYWORD: '{keyword}'")
        print(f"📊 Target: {max_articles} artikel maksimal")
        start_time = datetime.now()

        # Tahap 0: Simulasi browser visit ke homepage
        print("\n🌐 TAHAP 0: Simulasi kunjungan browser...")
        if not self.simulate_browser_visit():
            print("⚠️ Gagal mengakses homepage, tetapi melanjutkan...")

        # Tahap 1: Dapatkan hasil pencarian
        print("\n🔍 TAHAP 1: Mengakses halaman pencarian...")
        search_url = self.get_search_url(keyword)
        response = self.get_page_content(search_url, max_retries=3, is_search=True)

        # Jika gagal, coba metode alternatif
        if not response:
            print("🔄 Mencoba metode pencarian alternatif...")
            response, used_url = self.try_alternative_search_methods(keyword)
            if response:
                print(f"✅ Berhasil dengan metode alternatif: {used_url}")
            else:
                print("❌ Semua metode pencarian gagal")
                return pd.DataFrame()

        # Tahap 2: Ekstrak link artikel dari hasil pencarian
        print("\n📋 TAHAP 2: Mengekstrak link artikel...")
        article_links = self.extract_article_links_from_search(response.text, keyword)

        if not article_links:
            print("❌ Tidak menemukan artikel yang relevan")
            # Coba scraping artikel terbaru dari homepage
            print("🔄 Mencoba scraping artikel terbaru dari homepage...")
            homepage_response = self.get_page_content(self.base_url)
            if homepage_response:
                article_links = self.extract_article_links_from_search(homepage_response.text, keyword)
            
            if not article_links:
                print("❌ Tetap tidak menemukan artikel yang relevan")
                return pd.DataFrame()

        print(f"✅ Berhasil menemukan {len(article_links)} artikel yang relevan")

        # Tahap 3: Ekstrak detail dari setiap artikel
        results = []
        target_count = min(max_articles, len(article_links))
        print(f"\n📄 TAHAP 3: Mengekstrak detail dari {target_count} artikel...")

        for i, article_data in enumerate(article_links[:target_count], 1):
            url = article_data['url']
            title = article_data['title']
            print(f"\n[{i}/{target_count}] Memproses: {title[:60]}...")

            try:
                date_published, content_text = self.extract_article_details(url, keyword)

                results.append({
                    'judul_berita': title,
                    'link_berita': url,
                    'tanggal_rilis': date_published if date_published else "Tanggal tidak ditemukan",
                    'detail_konten': content_text if content_text else "Konten tidak dapat diambil"
                })
                print(f"   ✅ Detail artikel berhasil diekstrak")

            except Exception as e:
                print(f"   ❌ Error memproses artikel: {e}")
                results.append({
                    'judul_berita': title,
                    'link_berita': url,
                    'tanggal_rilis': "Error saat mengambil data",
                    'detail_konten': f"Error: {str(e)}"
                })

            # Delay antar artikel yang lebih bervariasi
            if i < target_count:
                delay = random.uniform(5, 10)
                print(f"   ⏳ Delay {delay:.1f} detik...")
                time.sleep(delay)

        end_time = datetime.now()
        duration = end_time - start_time

        if results:
            df = pd.DataFrame(results)
            print(f"\n✅ SCRAPING SELESAI!")
            print(f"⏱️ Waktu eksekusi: {duration}")
            print(f"📊 Artikel berhasil diekstrak: {len(results)}")
            return df
        else:
            print("❌ Tidak ada data yang berhasil diekstrak")
            return pd.DataFrame()

    def display_statistics(self, df):
        """Menampilkan statistik hasil scraping"""
        if df.empty:
            print("📊 Tidak ada data untuk ditampilkan")
            return

        print("\n📈 STATISTIK HASIL SCRAPING:")
        print(f"   • Total Artikel: {len(df)}")

        # Statistik Tanggal
        valid_dates = df['tanggal_rilis'].apply(
            lambda x: x != "Tanggal tidak ditemukan" and not str(x).startswith("Error")
        ).sum()
        print(f"   • Tanggal Valid: {valid_dates} ({(valid_dates/len(df)*100):.1f}%)")

        # Statistik Konten
        valid_content = df['detail_konten'].apply(
            lambda x: isinstance(x, str) and len(x) > 100 and not str(x).startswith("Error") and "tidak relevan" not in x
        ).sum()
        print(f"   • Konten Valid & Relevan: {valid_content} ({(valid_content/len(df)*100):.1f}%)")

        # Rata-rata panjang konten
        if valid_content > 0:
            avg_content_len = df[df['detail_konten'].apply(
                lambda x: isinstance(x, str) and len(x) > 100 and "tidak relevan" not in x
            )]['detail_konten'].str.len().mean()
            print(f"   • Rata-rata Panjang Konten: {avg_content_len:.0f} karakter")

    def save_results(self, df_results, keyword):
        """Menyimpan hasil ke file CSV dan JSON"""
        if df_results.empty:
            print("❌ Tidak ada data untuk disimpan.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Nama file
        csv_filename = f"berita_radar_surabaya_{keyword.replace(' ', '_')}_{timestamp}.csv"
        json_filename = f"berita_radar_surabaya_{keyword.replace(' ', '_')}_{timestamp}.json"

        # Simpan ke CSV
        try:
            df_results.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"💾 Hasil disimpan ke CSV: {csv_filename}")
        except Exception as e:
            print(f"❌ Gagal menyimpan ke CSV: {e}")

        # Simpan ke JSON
        try:
            df_results.to_json(json_filename, orient='records', indent=4, force_ascii=False)
            print(f"💾 Hasil disimpan ke JSON: {json_filename}")
        except Exception as e:
            print(f"❌ Gagal menyimpan ke JSON: {e}")

def main():
    """Fungsi utama program"""
    print("=" * 90)
    print("🎓 PROGRAM SCRAPING BERITA RADAR SURABAYA")
    print("👨‍🏫 Dikembangkan oleh: Dosen Data Mining (40 tahun pengalaman)")
    print("🎯 Target Website: https://radarsurabaya.jawapos.com/")
    print("=" * 90)
    print("⚠️ PENTING:")
    print(" • Gunakan scraper ini dengan bijak dan etis")
    print(" • Patuhi ketentuan layanan RadarSurabaya.JawaPos.com")
    print(" • Data hasil scraping hanya untuk keperluan penelitian/analisis")
    print(" • Scraper akan memfilter artikel berdasarkan relevansi keyword")
    print("=" * 90)

    # Inisialisasi scraper
    scraper = RadarSurabayaScraper()

    try:
        # Input keyword
        keyword = input("\n🔍 Masukkan keyword pencarian berita (contoh: 'Harga jagung'): ").strip()
        if not keyword:
            print("❌ Keyword tidak boleh kosong!")
            return

        # Input jumlah artikel
        while True:
            try:
                max_articles_input = input("📊 Jumlah maksimal artikel (default 20, maks 100): ").strip()
                if not max_articles_input:
                    max_articles = 20
                    break
                max_articles = int(max_articles_input)
                if 1 <= max_articles <= 100:
                    break
                else:
                    print("❌ Masukkan angka antara 1-100")
            except ValueError:
                print("❌ Masukkan angka yang valid!")

        print(f"\n📝 Konfigurasi scraping:")
        print(f"   • Keyword: '{keyword}'")
        print(f"   • Maksimal artikel: {max_articles}")
        print(f"   • URL Pencarian: https://radarsurabaya.jawapos.com/search?q={keyword.replace(' ', '+')}")

        # Mulai scraping
        print(f"\n🚀 Memulai proses scraping...")
        df_results = scraper.scrape_radar_surabaya_news(keyword, max_articles)

        if not df_results.empty:
            # Tampilkan statistik
            scraper.display_statistics(df_results)

            # Tampilkan preview hasil
            print("\n" + "=" * 90)
            print("📊 HASIL SCRAPING (Preview 5 baris pertama):")
            print("=" * 90)
            print(df_results.head().to_string(index=False, max_colwidth=40))

            # Simpan hasil
            print(f"\n💾 Menyimpan hasil ke file...")
            scraper.save_results(df_results, keyword)

            # Tampilkan preview konten
            print("\n📄 PREVIEW DETAIL KONTEN (3 Artikel Pertama):")
            print("=" * 90)
            for idx, row in df_results.head(3).iterrows():
                print(f"\n📋 Judul: {row['judul_berita']}")
                print(f"📅 Tanggal: {row['tanggal_rilis']}")
                print(f"🔗 URL: {row['link_berita']}")
                konten_preview = str(row['detail_konten'])[:500] + ("..." if len(str(row['detail_konten'])) > 500 else "")
                print(f"📝 Konten (preview 500 karakter):")
                print(f"   {konten_preview}")
                print("-" * 50)

        else:
            print("\n❌ Maaf, tidak ada data yang berhasil diambil.")
            print("💡 Tips:")
            print("   • Pastikan keyword yang dimasukkan spesifik dan relevan")
            print("   • Periksa koneksi internet")
            print("   • Coba keyword yang lebih umum atau berbeda")
            print("   • Pastikan website RadarSurabaya dapat diakses")

    except KeyboardInterrupt:
        print("\n⚠️ Program dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Terjadi error: {e}")
        print("💡 Silakan coba lagi atau periksa koneksi internet")

    print("\n👋 Terima kasih telah menggunakan program scraper RadarSurabaya!")
    print("📚 Gunakan data dengan bijak dan sesuai etika riset")
    print("🎓 Program ini dibuat oleh Dosen Data Mining dengan 40 tahun pengalaman")

# Jalankan program
if __name__ == "__main__":
    main()