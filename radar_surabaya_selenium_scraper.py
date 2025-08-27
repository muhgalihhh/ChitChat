# -*- coding: utf-8 -*-
"""
WEB SCRAPER RADAR SURABAYA - CLOUDFLARE BYPASS
Dikembangkan oleh Dosen Data Mining dengan 40 tahun pengalaman
Menggunakan Selenium + Undetected ChromeDriver untuk bypass Cloudflare
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from datetime import datetime
import json

class RadarSurabayaCloudflareBypass:
    """Scraper dengan kemampuan bypass Cloudflare"""
    
    def __init__(self):
        """Initialize scraper dengan konfigurasi anti-detection"""
        print("🔧 Initializing Cloudflare Bypass Scraper...")
        self.driver = None
        self.base_url = "https://radarsurabaya.jawapos.com"
        self.setup_driver()
        
    def setup_driver(self):
        """Setup undetected ChromeDriver dengan konfigurasi optimal"""
        print("🚀 Setting up undetected ChromeDriver...")
        
        # Konfigurasi Chrome options
        options = uc.ChromeOptions()
        
        # Anti-detection settings
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-default-apps")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-gpu-logging")
        options.add_argument("--silent")
        
        # Window size for better compatibility
        options.add_argument("--window-size=1920,1080")
        
        # User data directory (optional - untuk persistensi session)
        # options.add_argument("--user-data-dir=/tmp/chrome_user_data")
        
        # Initialize driver
        try:
            self.driver = uc.Chrome(options=options, version_main=None)
            print("✅ ChromeDriver initialized successfully")
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            
            # Maximize window
            self.driver.maximize_window()
            
        except Exception as e:
            print(f"❌ Error initializing driver: {e}")
            raise e
    
    def human_like_delay(self, min_seconds=2, max_seconds=5):
        """Delay yang menyerupai perilaku manusia"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def bypass_cloudflare(self):
        """Bypass Cloudflare protection dengan mengakses homepage terlebih dahulu"""
        print("🛡️ Bypassing Cloudflare protection...")
        
        try:
            # Akses homepage
            print(f"🌐 Accessing homepage: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait dan check apakah ada Cloudflare challenge
            self.human_like_delay(5, 10)
            
            # Check if we got through
            page_title = self.driver.title
            print(f"📄 Page title: {page_title}")
            
            # Jika ada challenge Cloudflare, tunggu sampai selesai
            wait_time = 0
            max_wait = 30
            while "cloudflare" in page_title.lower() or "just a moment" in page_title.lower():
                print(f"⏳ Waiting for Cloudflare challenge to complete... ({wait_time}s)")
                time.sleep(2)
                wait_time += 2
                page_title = self.driver.title
                
                if wait_time > max_wait:
                    print("⚠️ Cloudflare challenge taking too long, continuing anyway...")
                    break
            
            print("✅ Successfully bypassed Cloudflare protection")
            return True
            
        except Exception as e:
            print(f"❌ Error bypassing Cloudflare: {e}")
            return False
    
    def search_news(self, keyword):
        """Mencari berita berdasarkan keyword"""
        print(f"🔍 Searching for keyword: '{keyword}'")
        
        try:
            # Method 1: Coba akses halaman pencarian langsung
            search_url = f"{self.base_url}/search?q={keyword.replace(' ', '+')}"
            print(f"🔗 Trying direct search URL: {search_url}")
            
            self.driver.get(search_url)
            self.human_like_delay(3, 6)
            
            # Check if search worked
            current_url = self.driver.current_url
            if "search" in current_url:
                print("✅ Direct search successful")
                return True
            
            # Method 2: Jika direct search gagal, coba via form pencarian
            print("🔄 Trying search via form...")
            self.driver.get(self.base_url)
            self.human_like_delay(2, 4)
            
            # Cari form pencarian
            search_selectors = [
                'input[name="q"]',
                'input[type="search"]',
                'input[placeholder*="cari"]',
                'input[placeholder*="search"]',
                '.search-input',
                '#search'
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found search box with selector: {selector}")
                    break
                except:
                    continue
            
            if search_box:
                # Clear dan isi search box
                search_box.clear()
                search_box.send_keys(keyword)
                self.human_like_delay(1, 2)
                search_box.send_keys(Keys.ENTER)
                self.human_like_delay(3, 6)
                print("✅ Search form submitted")
                return True
            else:
                print("⚠️ Search box not found, will try category pages")
                return False
                
        except Exception as e:
            print(f"❌ Error during search: {e}")
            return False
    
    def extract_articles_from_current_page(self, keyword):
        """Ekstrak artikel dari halaman yang sedang dibuka"""
        print("📰 Extracting articles from current page...")
        
        try:
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            articles = []
            
            # Multiple strategies untuk mencari artikel
            print("🔍 Using multiple extraction strategies...")
            
            # Strategy 1: Cari link artikel berdasarkan pattern URL
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if href and text and len(text) > 15:
                    # Filter URL yang seperti artikel
                    if any(pattern in href for pattern in ['/2024/', '/2023/', '/ekonomi/', '/nasional/', '/daerah/', '/bisnis/']):
                        # Pastikan URL lengkap
                        if href.startswith('/'):
                            full_url = self.base_url + href
                        else:
                            full_url = href
                        
                        # Check relevance
                        if self.is_article_relevant(text, keyword):
                            articles.append({
                                'title': text,
                                'url': full_url
                            })
            
            # Strategy 2: Cari berdasarkan struktur HTML umum
            article_containers = soup.find_all(['article', 'div'], class_=re.compile(r'(article|post|news|item)', re.I))
            for container in article_containers:
                link = container.find('a', href=True)
                if link:
                    href = link.get('href')
                    
                    # Cari judul
                    title_elem = container.find(['h1', 'h2', 'h3', 'h4'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    else:
                        title = link.get_text(strip=True)
                    
                    if href and title and len(title) > 15:
                        if href.startswith('/'):
                            full_url = self.base_url + href
                        else:
                            full_url = href
                        
                        if self.is_article_relevant(title, keyword):
                            articles.append({
                                'title': title,
                                'url': full_url
                            })
            
            # Remove duplicates
            unique_articles = []
            seen_urls = set()
            for article in articles:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    unique_articles.append(article)
            
            print(f"📊 Found {len(unique_articles)} relevant articles")
            
            # Tampilkan sample
            if unique_articles:
                print("📋 Sample articles found:")
                for i, article in enumerate(unique_articles[:3], 1):
                    print(f"   {i}. {article['title'][:60]}...")
            
            return unique_articles
            
        except Exception as e:
            print(f"❌ Error extracting articles: {e}")
            return []
    
    def is_article_relevant(self, title, keyword):
        """Check apakah artikel relevan dengan keyword"""
        title_lower = title.lower()
        keyword_lower = keyword.lower()
        
        # Split keyword dan check individual words
        keyword_words = [word for word in keyword_lower.split() if len(word) > 2]
        return any(word in title_lower for word in keyword_words)
    
    def get_article_content(self, article_url):
        """Ambil konten artikel dari URL"""
        print(f"📄 Getting content from: {article_url}")
        
        try:
            self.driver.get(article_url)
            self.human_like_delay(3, 6)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Ekstrak tanggal
            date_published = self.extract_date(soup)
            
            # Ekstrak konten
            content = self.extract_content(soup)
            
            return date_published, content
            
        except Exception as e:
            print(f"❌ Error getting article content: {e}")
            return "Error getting date", f"Error: {str(e)}"
    
    def extract_date(self, soup):
        """Ekstrak tanggal publikasi"""
        # Cari berbagai pattern tanggal
        date_selectors = [
            'time[datetime]',
            'time',
            'date',
            '.date',
            '.time',
            '.published',
            '.publish-date',
            '[class*="date"]',
            '[class*="time"]'
        ]
        
        for selector in date_selectors:
            elements = soup.select(selector)
            for elem in elements:
                # Check datetime attribute
                if elem.has_attr('datetime'):
                    return elem['datetime']
                
                # Check text content
                date_text = elem.get_text(strip=True)
                if date_text and len(date_text) > 5:
                    return date_text
        
        # Fallback: regex search
        page_text = soup.get_text()
        date_patterns = [
            r'(\d{1,2}\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(\d{4}[/-]\d{2}[/-]\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                return match.group(1)
        
        return "Tanggal tidak ditemukan"
    
    def extract_content(self, soup):
        """Ekstrak konten artikel"""
        # Hapus elemen yang tidak diinginkan
        for unwanted in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            unwanted.decompose()
        
        # Cari container konten
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.content',
            '.entry-content',
            '[class*="content"]',
            '.article-body',
            '.post-body'
        ]
        
        best_content = ""
        max_length = 0
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Remove ads and unwanted elements
                for unwanted in element.find_all(class_=re.compile(r'(ads|advertisement|promo|related|share)', re.I)):
                    unwanted.decompose()
                
                text = element.get_text(separator=' ', strip=True)
                if len(text) > max_length:
                    max_length = len(text)
                    best_content = text
        
        # Fallback: ambil semua paragraf
        if not best_content or len(best_content) < 100:
            paragraphs = soup.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 30:
                    content_parts.append(text)
            best_content = ' '.join(content_parts)
        
        # Clean up text
        best_content = re.sub(r'\s+', ' ', best_content).strip()
        
        if len(best_content) > 15000:
            best_content = best_content[:15000] + "... (content truncated)"
        
        return best_content if best_content else "Konten tidak dapat diambil"
    
    def try_category_pages(self, keyword):
        """Coba scraping dari halaman kategori"""
        print("🔄 Trying category pages as fallback...")
        
        categories = ['ekonomi', 'nasional', 'daerah', 'bisnis', 'politik']
        all_articles = []
        
        for category in categories:
            print(f"📂 Checking category: {category}")
            category_url = f"{self.base_url}/tag/{category}"
            
            try:
                self.driver.get(category_url)
                self.human_like_delay(3, 5)
                
                articles = self.extract_articles_from_current_page(keyword)
                all_articles.extend(articles)
                
                if articles:
                    print(f"✅ Found {len(articles)} articles in {category}")
                
            except Exception as e:
                print(f"❌ Error with category {category}: {e}")
        
        return all_articles
    
    def scrape_news(self, keyword, max_articles=20):
        """Method utama untuk scraping"""
        print(f"🚀 STARTING RADAR SURABAYA SCRAPING")
        print(f"🎯 Keyword: '{keyword}'")
        print(f"📊 Max articles: {max_articles}")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Bypass Cloudflare
            if not self.bypass_cloudflare():
                print("❌ Failed to bypass Cloudflare")
                return pd.DataFrame()
            
            # Step 2: Search for news
            search_success = self.search_news(keyword)
            
            # Step 3: Extract articles
            if search_success:
                articles = self.extract_articles_from_current_page(keyword)
            else:
                articles = self.try_category_pages(keyword)
            
            if not articles:
                print("❌ No relevant articles found")
                return pd.DataFrame()
            
            print(f"✅ Found {len(articles)} relevant articles")
            
            # Step 4: Get article details
            results = []
            target_count = min(max_articles, len(articles))
            
            print(f"📰 Getting details for {target_count} articles...")
            
            for i, article in enumerate(articles[:target_count], 1):
                print(f"\n[{i}/{target_count}] Processing: {article['title'][:50]}...")
                
                try:
                    date, content = self.get_article_content(article['url'])
                    
                    results.append({
                        'judul_berita': article['title'],
                        'link_berita': article['url'],
                        'tanggal_rilis': date,
                        'detail_konten': content
                    })
                    
                    print("   ✅ Success")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    results.append({
                        'judul_berita': article['title'],
                        'link_berita': article['url'],
                        'tanggal_rilis': "Error",
                        'detail_konten': f"Error: {str(e)}"
                    })
                
                # Human-like delay between articles
                if i < target_count:
                    self.human_like_delay(3, 7)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            if results:
                df = pd.DataFrame(results)
                print(f"\n✅ SCRAPING COMPLETED!")
                print(f"⏱️ Duration: {duration}")
                print(f"📊 Articles extracted: {len(results)}")
                return df
            else:
                print("❌ No data extracted")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Critical error in scraping: {e}")
            return pd.DataFrame()
    
    def save_results(self, df, keyword):
        """Save results to files"""
        if df.empty:
            print("❌ No data to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV
        csv_file = f"radar_surabaya_{keyword.replace(' ', '_')}_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"💾 Saved to CSV: {csv_file}")
        
        # JSON
        json_file = f"radar_surabaya_{keyword.replace(' ', '_')}_{timestamp}.json"
        df.to_json(json_file, orient='records', indent=2, force_ascii=False)
        print(f"💾 Saved to JSON: {json_file}")
    
    def close(self):
        """Tutup browser"""
        if self.driver:
            self.driver.quit()
            print("🔐 Browser closed")

def main():
    """Main function"""
    print("=" * 80)
    print("🎓 RADAR SURABAYA SCRAPER - CLOUDFLARE BYPASS")
    print("👨‍🏫 Dosen Data Mining - 40 tahun pengalaman")
    print("🛡️ Menggunakan Selenium + Undetected ChromeDriver")
    print("=" * 80)
    
    scraper = None
    
    try:
        # Input dari user
        keyword = input("\n🔍 Masukkan keyword pencarian (contoh: 'harga jagung'): ").strip()
        if not keyword:
            print("❌ Keyword tidak boleh kosong!")
            return
        
        while True:
            try:
                max_input = input("📊 Jumlah artikel maksimal (default 15): ").strip()
                if not max_input:
                    max_articles = 15
                    break
                max_articles = int(max_input)
                if 1 <= max_articles <= 50:
                    break
                else:
                    print("❌ Masukkan angka 1-50")
            except ValueError:
                print("❌ Masukkan angka yang valid!")
        
        print(f"\n📝 Konfigurasi:")
        print(f"   • Keyword: '{keyword}'")
        print(f"   • Max articles: {max_articles}")
        print(f"   • Target website: RadarSurabaya.JawaPos.com")
        
        # Initialize scraper
        scraper = RadarSurabayaCloudflareBypass()
        
        # Start scraping
        df_results = scraper.scrape_news(keyword, max_articles)
        
        if not df_results.empty:
            # Statistics
            print(f"\n📈 STATISTICS:")
            print(f"   • Total articles: {len(df_results)}")
            
            valid_content = df_results['detail_konten'].apply(
                lambda x: len(str(x)) > 100 and 'Error' not in str(x)
            ).sum()
            print(f"   • Valid content: {valid_content}")
            
            # Save results
            scraper.save_results(df_results, keyword)
            
            # Preview
            print(f"\n📄 PREVIEW (first 3 articles):")
            print("=" * 80)
            for idx, row in df_results.head(3).iterrows():
                print(f"\n📰 {row['judul_berita']}")
                print(f"📅 {row['tanggal_rilis']}")
                print(f"🔗 {row['link_berita']}")
                content_preview = str(row['detail_konten'])[:300] + "..."
                print(f"📝 {content_preview}")
                print("-" * 60)
        
        else:
            print("\n❌ No data retrieved")
            print("💡 Possible solutions:")
            print("   • Try different keywords")
            print("   • Check internet connection")
            print("   • Website might be temporarily down")
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if scraper:
            scraper.close()
    
    print("\n👋 Thank you for using Radar Surabaya Scraper!")

if __name__ == "__main__":
    main()