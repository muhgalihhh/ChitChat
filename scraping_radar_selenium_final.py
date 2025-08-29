"""
Scraping Berita Radar Surabaya - Program untuk mengumpulkan data berita
Dibuat oleh: Pradipta Deska Pryanda
Tanggal: 2024
SELENIUM VERSION: Menggunakan browser automation untuk bypass anti-bot
"""

# Import library yang diperlukan
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import pandas as pd
import time
import random
from urllib.parse import quote, urljoin
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Konfigurasi global
RADAR_BASE = "https://radarsurabaya.jawapos.com"

def create_selenium_driver():
    """Buat Selenium WebDriver dengan konfigurasi optimal"""
    print("🚀 Mempersiapkan browser automation...")
    
    chrome_options = Options()
    
    # Basic options
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--disable-javascript')  # Untuk speed
    
    # Anti-detection options
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent yang natural
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    # Window size
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Jika ingin headless (tanpa GUI), uncomment line berikut:
    # chrome_options.add_argument('--headless')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script untuk hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set timeouts
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        
        print("✅ Browser siap digunakan!")
        return driver
        
    except Exception as e:
        print(f"❌ Error membuat driver: {e}")
        print("💡 Pastikan ChromeDriver sudah terinstall dan ada di PATH")
        print("   Download dari: https://chromedriver.chromium.org/")
        return None

def human_like_actions(driver):
    """Simulasi perilaku manusia"""
    try:
        # Random scroll
        if random.random() > 0.5:
            driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
            time.sleep(random.uniform(0.5, 1.5))
        
        # Random mouse movement (simulasi)
        if random.random() > 0.7:
            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(10, 100), random.randint(10, 100))
            actions.perform()
            time.sleep(random.uniform(0.3, 0.8))
        
        # Random delay
        time.sleep(random.uniform(1, 3))
        
    except Exception:
        pass  # Ignore errors in human simulation

def search_google_selenium(driver, keyword, max_results=20):
    """Cari artikel menggunakan Google dengan Selenium"""
    results = []
    
    try:
        print(f"🔍 Mencari di Google: site:radarsurabaya.jawapos.com {keyword}")
        
        # Buka Google
        driver.get("https://www.google.com")
        human_like_actions(driver)
        
        # Cari search box dan ketik query
        search_query = f"site:radarsurabaya.jawapos.com {keyword}"
        
        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            
            # Ketik seperti manusia (karakter per karakter)
            for char in search_query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(0.5, 1))
            search_box.send_keys(Keys.RETURN)
            
        except TimeoutException:
            # Fallback: coba selector lain
            search_box = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
        
        # Tunggu hasil muncul
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.g, div[data-ved]"))
        )
        
        human_like_actions(driver)
        
        # Extract hasil
        selectors = [
            "div.g h3 a",
            "div.yuRUbf a", 
            "h3 a",
            "div[data-ved] a[href*='radarsurabaya']"
        ]
        
        for selector in selectors:
            try:
                links = driver.find_elements(By.CSS_SELECTOR, selector)
                for link in links[:max_results]:
                    try:
                        href = link.get_attribute('href')
                        title = link.text.strip()
                        
                        if href and 'radarsurabaya.jawapos.com' in href and len(title) > 10:
                            results.append({
                                'title': title,
                                'url': href,
                                'date_from_list': None
                            })
                            
                        if len(results) >= max_results:
                            break
                    except Exception:
                        continue
                        
                if len(results) >= max_results:
                    break
            except Exception:
                continue
        
        print(f"   ✅ Google: {len(results)} hasil ditemukan")
        return results
        
    except Exception as e:
        print(f"   ❌ Google search error: {e}")
        return []

def extract_article_selenium(driver, article_url):
    """Ekstrak artikel menggunakan Selenium"""
    try:
        print(f"   📄 Mengakses: {article_url[:60]}...")
        
        driver.get(article_url)
        human_like_actions(driver)
        
        # Tunggu halaman load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Extract title
        title = "Judul tidak ditemukan"
        title_selectors = [
            "h1.article__title",
            "h1.post__title", 
            "h1.entry-title",
            "h1.title",
            "h1",
            "title"
        ]
        
        for selector in title_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                title_text = element.text.strip()
                if title_text and len(title_text) > 10:
                    title = title_text
                    break
            except:
                continue
        
        # Extract date
        date_published = "Tanggal tidak ditemukan"
        date_selectors = [
            "time[datetime]",
            "time",
            ".article__date",
            ".post__date", 
            ".entry-date",
            ".date"
        ]
        
        for selector in date_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.get_attribute('datetime'):
                    date_published = element.get_attribute('datetime')
                    break
                else:
                    date_text = element.text.strip()
                    if date_text and len(date_text) > 5:
                        date_published = date_text
                        break
            except:
                continue
        
        # Jika tanggal tidak ditemukan, cari dengan regex
        if date_published == "Tanggal tidak ditemukan":
            try:
                page_source = driver.page_source
                date_patterns = [
                    r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})',
                    r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                    r'(\d{4}[/-]\d{2}[/-]\d{2})'
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, page_source)
                    if match:
                        date_published = match.group(1)
                        break
            except:
                pass
        
        # Extract content
        content_text = "Konten tidak dapat diambil"
        content_selectors = [
            "div.article__content",
            "div.post__content",
            "article .content",
            "div.entry-content",
            "div.content-detail",
            "div.article-content",
            ".article-body",
            ".post-body"
        ]
        
        for selector in content_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                content = element.text.strip()
                if content and len(content) > 100:
                    content_text = clean_text(content)
                    break
            except:
                continue
        
        # Fallback: ambil dari body
        if content_text == "Konten tidak dapat diambil":
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                content_text = clean_text(body.text)
            except:
                pass
        
        return clean_text(title), date_published, content_text
        
    except Exception as e:
        print(f"   ❌ Error ekstrak artikel: {e}")
        return None, None, None

def clean_text(text):
    """Bersihkan teks"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove unwanted characters but keep Indonesian
    text = re.sub(r'[^\w\s.,!?;:()\-\'"àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]', ' ', text)
    
    return text.strip()

def is_relevant(title, content, keyword):
    """Cek relevansi artikel"""
    if not title or not content or not keyword:
        return False
    
    title_lower = title.lower()
    content_lower = content.lower() 
    keyword_lower = keyword.lower()
    
    full_text = f"{title_lower} {content_lower}"
    
    # Exact match
    if keyword_lower in full_text:
        return True
    
    # Word by word
    keyword_words = [w for w in keyword_lower.split() if len(w) > 2]
    if not keyword_words:
        return False
    
    matches = 0
    for word in keyword_words:
        if word in full_text:
            matches += 1
    
    return matches >= len(keyword_words) * 0.7

def calculate_score(title, content, keyword):
    """Hitung skor relevansi"""
    if not title or not content or not keyword:
        return 0
    
    score = 0
    title_lower = title.lower()
    content_lower = content.lower()
    keyword_lower = keyword.lower()
    
    # Keyword di judul
    if keyword_lower in title_lower:
        score += 20
    
    # Keyword di konten
    if keyword_lower in content_lower:
        score += 10
    
    # Individual words
    for word in keyword_lower.split():
        if len(word) > 2:
            if word in title_lower:
                score += 5
            score += content_lower.count(word) * 2
    
    return score

def scrape_with_selenium(keyword, target_articles):
    """Main scraping function dengan Selenium"""
    print("=" * 70)
    print("🤖 SELENIUM RADAR SURABAYA SCRAPER")
    print(f"🎯 Keyword: '{keyword}' | Target: {target_articles} artikel")
    print("=" * 70)
    
    # Create driver
    driver = create_selenium_driver()
    if not driver:
        return pd.DataFrame()
    
    try:
        # Step 1: Search dengan Google
        print("\n🔍 FASE 1: PENCARIAN ARTIKEL")
        print("-" * 40)
        
        all_links = search_google_selenium(driver, keyword, max_results=50)
        
        if not all_links:
            print("❌ Tidak ditemukan artikel dari Google")
            return pd.DataFrame()
        
        print(f"✅ Total kandidat: {len(all_links)}")
        
        # Step 2: Process articles
        print(f"\n📝 FASE 2: EKSTRAKSI ARTIKEL")
        print(f"🎯 Target: {target_articles} artikel relevan")
        print("-" * 40)
        
        results = []
        processed = 0
        
        for i, link in enumerate(all_links, 1):
            if len(results) >= target_articles:
                print(f"\n🎉 TARGET TERCAPAI! {target_articles} artikel relevan!")
                break
            
            print(f"\n[{i}/{len(all_links)}] {link['title'][:50]}...")
            
            try:
                title, date, content = extract_article_selenium(driver, link['url'])
                
                if not title or not content:
                    print("   ⚠️ Gagal ekstrak konten")
                    processed += 1
                    continue
                
                if is_relevant(title, content, keyword):
                    score = calculate_score(title, content, keyword)
                    
                    results.append({
                        'judul_berita': title,
                        'link_berita': link['url'],
                        'tanggal_rilis': date,
                        'detail_konten': content,
                        'relevance_score': score
                    })
                    
                    print(f"   ✅ RELEVAN #{len(results)} (skor: {score})")
                else:
                    print(f"   ❌ Tidak relevan dengan '{keyword}'")
                
                processed += 1
                
                # Human delay
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:80]}")
                processed += 1
                continue
        
        # Step 3: Results
        if results:
            # Sort by score
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Remove score column
            for result in results:
                del result['relevance_score']
            
            df = pd.DataFrame(results)
            
            print(f"\n" + "=" * 70)
            print("🎊 SCRAPING BERHASIL!")
            print(f"📊 Artikel diproses: {processed}")
            print(f"✅ Artikel relevan: {len(results)}")
            print("=" * 70)
            
            return df
        else:
            print(f"\n❌ TIDAK ADA ARTIKEL RELEVAN")
            print(f"📊 Total diproses: {processed}")
            return pd.DataFrame()
    
    finally:
        # Tutup browser
        try:
            driver.quit()
            print("\n🔒 Browser ditutup")
        except:
            pass

def save_to_csv(dataframe, keyword):
    """Simpan ke CSV"""
    if not dataframe.empty:
        # Clean data
        df_clean = dataframe.copy()
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['link_berita'], keep='first')
        
        # Clean text
        df_clean['judul_berita'] = df_clean['judul_berita'].apply(lambda x: clean_text(str(x)))
        df_clean['detail_konten'] = df_clean['detail_konten'].apply(lambda x: clean_text(str(x)))
        
        # Filter minimum content
        df_clean = df_clean[df_clean['detail_konten'].apply(lambda x: len(str(x)) > 100)]
        
        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"radar_selenium_{keyword.replace(' ', '_')}_{timestamp}.csv"
        df_clean.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"💾 Data disimpan: {filename}")
        return filename
    return None

def main():
    print("🤖 SELENIUM RADAR SURABAYA SCRAPER")
    print("👨‍🏫 Created by Pradipta Deska Pryanda")
    print("🚀 Browser Automation untuk Bypass Anti-Bot")
    print("=" * 70)
    
    print("\n📋 PERSYARATAN:")
    print("1. ChromeDriver harus terinstall")
    print("2. Chrome browser harus ada")
    print("3. Koneksi internet stabil")
    print("4. selenium package: pip install selenium")

    # Input keyword
    while True:
        keyword = input("\n🔍 Masukkan keyword pencarian: ").strip()
        if keyword:
            break
        print("❌ Keyword tidak boleh kosong!")

    # Input target
    while True:
        try:
            target = input("📊 Jumlah artikel relevan (default 5, max 20): ").strip()
            if not target:
                target = 5
                break
            target = int(target)
            if 1 <= target <= 20:
                break
            else:
                print("❌ Masukkan angka antara 1-20")
        except ValueError:
            print("❌ Masukkan angka yang valid!")

    print(f"\n📝 Keyword: '{keyword}'")
    print(f"🎯 Target: {target} artikel relevan")
    print("🤖 Memulai browser automation...")
    
    # Konfirmasi
    confirm = input("\n⚠️  Browser akan terbuka. Lanjutkan? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Dibatalkan")
        return

    try:
        start_time = time.time()
        df_results = scrape_with_selenium(keyword, target)
        end_time = time.time()
        
        if not df_results.empty:
            # Statistics
            print(f"\n📈 STATISTIK FINAL:")
            print(f"   ⏱️  Waktu: {end_time - start_time:.1f} detik")
            print(f"   📊 Artikel: {len(df_results)}")
            
            # Keyword analysis
            keyword_lower = keyword.lower()
            in_title = sum(1 for _, row in df_results.iterrows() 
                          if keyword_lower in str(row['judul_berita']).lower())
            in_content = sum(1 for _, row in df_results.iterrows() 
                           if keyword_lower in str(row['detail_konten']).lower())
            
            print(f"   🎯 Di judul: {in_title}/{len(df_results)}")
            print(f"   📝 Di konten: {in_content}/{len(df_results)}")
            
            # Save
            filename = save_to_csv(df_results, keyword)
            
            # Preview
            print(f"\n📄 PREVIEW HASIL:")
            print("=" * 50)
            
            for idx, (_, row) in enumerate(df_results.head(3).iterrows(), 1):
                print(f"\n{idx}. 📋 {row['judul_berita']}")
                print(f"   📅 {row['tanggal_rilis']}")
                print(f"   🔗 {row['link_berita']}")
                
                content_preview = str(row['detail_konten'])[:200]
                if len(str(row['detail_konten'])) > 200:
                    content_preview += "..."
                print(f"   📝 {content_preview}")
                print("-" * 30)
            
            if filename:
                print(f"\n✅ SUKSES! File: {filename}")
        else:
            print("\n💡 TIPS UNTUK HASIL LEBIH BAIK:")
            print("   • Gunakan keyword lebih umum")
            print("   • Periksa ejaan keyword")
            print("   • Coba variasi keyword")
    
    except KeyboardInterrupt:
        print("\n⚠️ Program dihentikan")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n🎊 TERIMA KASIH!")

if __name__ == "__main__":
    main()