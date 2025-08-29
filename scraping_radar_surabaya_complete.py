"""
Scraping Berita Radar Surabaya - Program untuk mengumpulkan data berita
Dibuat oleh: Pradipta Deska Pryanda
Tanggal: 2024
Diperbaiki: Scraping hingga mendapat jumlah artikel relevan sesuai input user + ekstraksi tanggal yang akurat
"""

# Import library yang diperlukan
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import quote, urljoin
import re
from datetime import datetime
import math

# Untuk menghindari error SSL di Colab
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Konfigurasi global
RADAR_BASE = "https://radarsurabaya.jawapos.com"

# ---------- Session & headers anti-403 ----------
def make_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Connection': 'keep-alive',
    })
    return s

def get_page_content(url, session=None, retries=3):
    if session is None:
        session = make_session()
    
    for attempt in range(retries):
        try:
            resp = session.get(url, timeout=30, verify=False)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            if attempt < retries - 1:
                print(f"⚠️ Attempt {attempt + 1} failed for {url}, retrying...")
                time.sleep(random.uniform(1, 3))
            else:
                print(f"❌ Failed to access {url} after {retries} attempts: {e}")
                return None

def clean_text(text):
    if not text:
        return ""
    # Hapus karakter khusus dan whitespace berlebih
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', ' ', text)
    text = text.strip()
    return text

def extract_links_from_page(url, session):
    """Ekstrak semua link artikel dari halaman tertentu"""
    html = get_page_content(url, session)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    used_urls = set()
    
    # Berbagai selector untuk mencari link artikel
    selectors = [
        'a[href*="/read/"]',
        'a[href*="/ekonomi/"]',
        'a[href*="/politik/"]',
        'a[href*="/nasional/"]',
        'a[href*="/daerah/"]',
        'a[href*="/olahraga/"]',
        'a[href*="/hukum/"]',
        'a[href*="/lifestyle/"]',
        'a.latest__link',
        'article a',
        '.news-item a',
        '.article-item a',
        '.post-item a',
        '.entry-item a',
        'h2 a',
        'h3 a',
        'h4 a',
        '.title a',
        '.headline a',
        '.news-title a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for a in elements:
            href = a.get('href', '').strip()
            title = a.get_text(strip=True)
            
            if not href or not title or len(title) < 10:
                continue
                
            # Normalisasi URL
            if href.startswith('/'):
                href = urljoin(RADAR_BASE, href)
            elif not href.startswith('http'):
                href = urljoin(RADAR_BASE, href)
            
            # Skip jika bukan artikel berita
            skip_patterns = ['#', '.pdf', '.jpg', '.jpeg', '.png', '/foto/', '/video/', 
                           '/indeks', '/tag/', '/category/', '/search/', '/about/', '/contact',
                           'javascript:', 'mailto:', '/wp-content/', '/author/', '/archive/']
            
            if any(pattern in href.lower() for pattern in skip_patterns):
                continue
                
            # Pastikan URL valid dan dari domain yang benar
            if 'radarsurabaya.jawapos.com' not in href:
                continue
            
            # Cek apakah URL mengandung ID artikel (biasanya angka)
            if not re.search(r'/\d+/', href):
                continue
            
            if href not in used_urls:
                # Ekstrak tanggal dari elemen parent jika ada
                date_from_page = extract_date_from_element(a)
                links.append({
                    'title': title, 
                    'url': href,
                    'date_from_list': date_from_page
                })
                used_urls.add(href)
    
    return links

def extract_date_from_element(element):
    """Ekstrak tanggal dari elemen atau parent element"""
    try:
        # Cari di element itu sendiri
        if element.has_attr('datetime'):
            return element['datetime']
        
        # Cari di parent elements
        parent = element.parent
        for _ in range(3):  # Cek 3 level parent
            if not parent:
                break
                
            # Cari time element dengan datetime
            time_elem = parent.find('time')
            if time_elem and time_elem.has_attr('datetime'):
                return time_elem['datetime']
            
            # Cari date class
            date_elem = parent.find(class_=re.compile(r'date|time', re.I))
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                if date_text and len(date_text) > 5:
                    return date_text
            
            parent = parent.parent
        
        return None
    except:
        return None

def get_all_article_links(session, max_pages=10):
    """Kumpulkan semua link artikel dari berbagai halaman"""
    all_links = []
    used_urls = set()
    
    # Daftar halaman untuk di-crawl
    pages_to_crawl = [
        RADAR_BASE,  # Homepage
        f"{RADAR_BASE}/ekonomi",
        f"{RADAR_BASE}/politik",
        f"{RADAR_BASE}/nasional",
        f"{RADAR_BASE}/daerah",
        f"{RADAR_BASE}/olahraga",
        f"{RADAR_BASE}/hukum",
        f"{RADAR_BASE}/lifestyle"
    ]
    
    # Tambahkan halaman dengan pagination
    for category in ['/ekonomi', '/politik', '/nasional', '/daerah']:
        for page in range(2, max_pages + 1):
            pages_to_crawl.append(f"{RADAR_BASE}{category}/page/{page}")
    
    print(f"🔍 Akan crawl {len(pages_to_crawl)} halaman untuk mengumpulkan artikel...")
    
    for i, page_url in enumerate(pages_to_crawl, 1):
        try:
            print(f"   [{i}/{len(pages_to_crawl)}] Crawling: {page_url}")
            page_links = extract_links_from_page(page_url, session)
            
            # Tambahkan link yang belum ada
            new_links = 0
            for link in page_links:
                if link['url'] not in used_urls:
                    all_links.append(link)
                    used_urls.add(link['url'])
                    new_links += 1
            
            print(f"       ✅ Ditemukan {new_links} link baru")
            time.sleep(random.uniform(1, 2))  # Delay antar halaman
            
        except Exception as e:
            print(f"       ❌ Error crawling {page_url}: {e}")
            continue
    
    print(f"✅ Total link artikel terkumpul: {len(all_links)}")
    return all_links

def extract_article_details(article_url, session):
    """Ekstrak detail artikel dari URL dengan fokus pada tanggal yang akurat"""
    html_content = get_page_content(article_url, session)
    if not html_content:
        return None, None, None

    soup = BeautifulSoup(html_content, 'html.parser')

    # Ekstrak judul dengan prioritas selector
    title = "Judul tidak ditemukan"
    title_selectors = [
        'h1.article__title',
        'h1.post__title', 
        'h1.entry-title',
        'h1.title',
        '.article-title h1',
        '.post-title h1',
        'h1',
        'meta[property="og:title"]'
    ]
    
    for selector in title_selectors:
        try:
            if selector.startswith('meta'):
                tag = soup.select_one(selector)
                if tag and tag.get('content'):
                    title = tag['content'].strip()
                    break
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:
                        title = text
                        break
        except:
            continue

    # Ekstrak tanggal dengan berbagai metode
    date_published = extract_article_date(soup)

    # Ekstrak konten artikel
    content_text = extract_article_content(soup)

    return title, date_published, content_text

def extract_article_date(soup):
    """Ekstrak tanggal artikel dengan berbagai metode"""
    
    # Method 1: Cari time element dengan datetime
    time_elements = soup.find_all('time')
    for time_elem in time_elements:
        if time_elem.has_attr('datetime'):
            datetime_str = time_elem['datetime']
            if datetime_str and len(datetime_str) > 8:
                return datetime_str
    
    # Method 2: Cari meta tag untuk tanggal
    meta_selectors = [
        'meta[property="article:published_time"]',
        'meta[name="pubdate"]',
        'meta[name="publishdate"]',
        'meta[name="date"]',
        'meta[property="article:modified_time"]'
    ]
    
    for selector in meta_selectors:
        try:
            tag = soup.select_one(selector)
            if tag and tag.get('content'):
                return tag['content'].strip()
        except:
            continue
    
    # Method 3: Cari berdasarkan class yang mengandung kata 'date' atau 'time'
    date_classes = [
        '.article__date',
        '.post__date',
        '.entry-date',
        '.date',
        '.publish-date',
        '.published',
        '.timestamp',
        '.article-date',
        '.post-date'
    ]
    
    for selector in date_classes:
        try:
            element = soup.select_one(selector)
            if element:
                date_text = element.get_text(strip=True)
                if date_text and len(date_text) > 5:
                    return date_text
        except:
            continue
    
    # Method 4: Cari dalam teks dengan regex pattern
    body_text = soup.get_text(separator=' ', strip=True)
    date_patterns = [
        # Format: 15 Januari 2024, 10:30 WIB
        r'(\d{1,2}\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4}\s*,?\s*\d{1,2}:\d{2}\s*(WIB|WITA|WIT)?)',
        # Format: 15 Januari 2024
        r'(\d{1,2}\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})',
        # Format: 15/01/2024 10:30
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}\s*\d{1,2}:\d{2})',
        # Format: 15/01/2024
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        # Format: 2024-01-15
        r'(\d{4}[/-]\d{2}[/-]\d{2})',
        # Format: Senin, 15 Januari 2024
        r'((?:Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu),?\s*\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})'
    ]
    
    for pattern in date_patterns:
        try:
            match = re.search(pattern, body_text)
            if match:
                return match.group(1)
        except:
            continue
    
    # Method 5: Cari dalam URL (kadang tanggal ada di URL)
    try:
        url_date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', body_text)
        if url_date_match:
            year, month, day = url_date_match.groups()
            return f"{day}/{month}/{year}"
    except:
        pass
    
    return "Tanggal tidak ditemukan"

def extract_article_content(soup):
    """Ekstrak konten artikel dengan berbagai selector"""
    content_text = ""
    
    # Selector untuk konten artikel
    content_selectors = [
        'div.article__content',
        'div.post__content',
        'article .content',
        'div.entry-content',
        'div.content-detail',
        'div.article-content',
        '.article-body',
        '.post-body',
        '.content-body',
        '.article-text',
        '.post-text',
        'div[class*="content"]',
        'div[class*="article"]',
        'div[id*="content"]'
    ]
    
    content_element = None
    for selector in content_selectors:
        try:
            content_element = soup.select_one(selector)
            if content_element and len(content_element.get_text(strip=True)) > 100:
                break
        except:
            continue
    
    if content_element:
        # Hapus elemen yang tidak diinginkan
        unwanted_tags = ['script', 'style', 'nav', 'aside', 'header', 
                        'footer', 'noscript', 'figure', 'iframe', 'form',
                        'advertisement', 'ads']
        
        unwanted_classes = re.compile(r'.*(ads|advert|promo|related|widget|sidebar|footer|breadcrumb|taglist|share|social|comment|nav|menu|advertisement).*', re.I)
        
        for unwanted in content_element(unwanted_tags):
            unwanted.decompose()
        
        for unwanted in content_element.find_all(class_=unwanted_classes):
            unwanted.decompose()
        
        content_text = content_element.get_text(separator=' ', strip=True)
    else:
        # Fallback: ambil dari body dengan filtering
        body = soup.find('body')
        if body:
            # Hapus elemen yang tidak diinginkan
            for unwanted in body(['script', 'style', 'nav', 'aside', 'header', 
                                'footer', 'noscript', 'figure', 'iframe', 'form']):
                unwanted.decompose()
            content_text = body.get_text(separator=' ', strip=True)

    return clean_text(content_text)

def is_keyword_match(text, keyword):
    """Cek apakah keyword cocok dengan teks (case insensitive) dengan logika yang lebih fleksibel"""
    if not text or not keyword:
        return False
    
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    # Cek keyword utuh dulu (prioritas tertinggi)
    if keyword_lower in text_lower:
        return True
    
    # Split keyword dan teks menjadi kata-kata
    keyword_words = [w for w in keyword_lower.split() if len(w) > 2]  # Skip kata pendek
    text_words = text_lower.split()
    
    if not keyword_words:
        return False
    
    # Jika keyword hanya 1 kata
    if len(keyword_words) == 1:
        keyword_word = keyword_words[0]
        # Cek exact match atau partial match
        for text_word in text_words:
            if keyword_word in text_word or text_word in keyword_word:
                return True
        return False
    
    # Jika keyword multi-kata, cek berapa persen yang cocok
    matches = 0
    for kw in keyword_words:
        for text_word in text_words:
            if kw in text_word or text_word in kw:
                matches += 1
                break
    
    # Jika minimal 70% kata keyword ditemukan
    return matches >= len(keyword_words) * 0.7

def calculate_relevance_score(title, content, keyword):
    """Hitung skor relevansi dengan bobot yang lebih akurat"""
    score = 0
    
    if not title or not content or not keyword:
        return score
    
    title_lower = title.lower()
    content_lower = content.lower()
    keyword_lower = keyword.lower()
    
    # Skor tinggi untuk keyword utuh di judul
    if keyword_lower in title_lower:
        score += 20
    
    # Skor untuk keyword utuh di konten
    if keyword_lower in content_lower:
        score += 10
    
    # Skor untuk setiap kata keyword
    keyword_words = [w for w in keyword_lower.split() if len(w) > 2]
    
    for word in keyword_words:
        # Di judul (bobot tinggi)
        if word in title_lower:
            score += 8
        
        # Di konten (bobot sedang)
        word_count_in_content = content_lower.count(word)
        score += min(word_count_in_content * 2, 10)  # Max 10 poin per kata
    
    return score

def scrape_radar_news(keyword, target_articles):
    """Scraping hingga mendapat jumlah artikel relevan sesuai target"""
    print("=" * 70)
    print(f"MEMULAI SCRAPING BERITA RADAR SURABAYA UNTUK KEYWORD: '{keyword}'")
    print(f"TARGET: {target_articles} artikel relevan")
    print("=" * 70)
    
    session = make_session()
    
    # Step 1: Kumpulkan semua link artikel dari berbagai halaman
    print("🔍 Mengumpulkan link artikel dari berbagai halaman...")
    all_links = get_all_article_links(session, max_pages=5)
    
    if not all_links:
        print("❌ Tidak berhasil mengumpulkan link artikel")
        return pd.DataFrame()
    
    # Step 2: Filter cepat berdasarkan judul
    print(f"\n🎯 Melakukan quick filter berdasarkan keyword '{keyword}' di judul...")
    quick_relevant = []
    
    for link in all_links:
        if is_keyword_match(link['title'], keyword):
            quick_relevant.append(link)
    
    print(f"   ✅ Ditemukan {len(quick_relevant)} artikel dengan judul relevan")
    
    # Step 3: Proses artikel hingga mendapat target yang diinginkan
    results = []
    articles_with_scores = []
    processed_count = 0
    
    print(f"\n📝 Memproses artikel hingga mendapat {target_articles} artikel relevan...")
    
    # Urutkan: yang relevan di judul dulu, baru yang lain
    processing_queue = quick_relevant + [link for link in all_links if link not in quick_relevant]
    
    for i, link in enumerate(processing_queue, 1):
        if len(articles_with_scores) >= target_articles:
            print(f"🎉 Target {target_articles} artikel relevan tercapai!")
            break
        
        print(f"\n[{i}] Memproses: {link['title'][:70]}...")
        
        try:
            # Ekstrak detail artikel
            title, date, content = extract_article_details(link['url'], session)
            
            if not title or not content:
                print("   ⚠️ Gagal mengekstrak konten artikel")
                processed_count += 1
                continue
            
            # Cek relevansi berdasarkan title + content
            if is_keyword_match(title, keyword) or is_keyword_match(content, keyword):
                score = calculate_relevance_score(title, content, keyword)
                
                # Gunakan tanggal dari ekstraksi detail, fallback ke tanggal dari list
                final_date = date if date != "Tanggal tidak ditemukan" else link.get('date_from_list', "Tanggal tidak ditemukan")
                
                article_data = {
                    'judul_berita': clean_text(title),
                    'link_berita': link['url'],
                    'tanggal_rilis': final_date,
                    'detail_konten': content,
                    'relevance_score': score
                }
                
                articles_with_scores.append(article_data)
                print(f"   ✅ Artikel relevan #{len(articles_with_scores)} (skor: {score})")
            else:
                print(f"   ❌ Artikel tidak relevan dengan keyword '{keyword}'")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        processed_count += 1
        
        # Delay untuk menghindari rate limiting
        time.sleep(random.uniform(0.8, 1.5))
        
        # Break jika sudah memproses terlalu banyak tanpa hasil
        if processed_count > target_articles * 10 and len(articles_with_scores) == 0:
            print("⚠️ Sudah memproses banyak artikel tapi tidak ada yang relevan")
            break
    
    # Step 4: Urutkan dan return hasil
    if articles_with_scores:
        # Urutkan berdasarkan skor relevansi
        articles_with_scores.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Ambil sesuai target
        results = articles_with_scores[:target_articles]
        
        # Hapus kolom skor untuk hasil akhir
        for article in results:
            del article['relevance_score']
        
        df = pd.DataFrame(results)
        print(f"\n✅ Scraping berhasil!")
        print(f"   • Total artikel diproses: {processed_count}")
        print(f"   • Artikel relevan ditemukan: {len(results)}")
        return df
    else:
        print(f"\n❌ Tidak ditemukan artikel yang relevan dengan keyword '{keyword}'")
        print(f"   • Total artikel diproses: {processed_count}")
        return pd.DataFrame()

def clean_dataframe(df):
    """Bersihkan dan perbaiki DataFrame"""
    print("🔍 Memulai pembersihan DataFrame...")
    
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # Bersihkan kolom
    df_clean['judul_berita'] = df_clean['judul_berita'].apply(lambda x: clean_text(str(x)))
    df_clean['detail_konten'] = df_clean['detail_konten'].apply(lambda x: clean_text(str(x)))
    
    # Pastikan tanggal tidak kosong
    df_clean['tanggal_rilis'] = df_clean['tanggal_rilis'].apply(lambda x: str(x) if x and str(x).strip() else "Tanggal tidak ditemukan")
    
    # Hapus duplikat berdasarkan URL
    df_clean = df_clean.drop_duplicates(subset=['link_berita'], keep='first')
    
    # Hapus artikel dengan konten terlalu pendek
    df_clean = df_clean[df_clean['detail_konten'].apply(lambda x: len(str(x)) > 100)]
    
    print(f"✅ Pembersihan selesai. Artikel tersisa: {len(df_clean)}")
    return df_clean

def save_to_csv(dataframe, keyword):
    """Simpan DataFrame ke CSV"""
    if not dataframe.empty:
        cleaned_df = clean_dataframe(dataframe)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"berita_radarsurabaya_{keyword.replace(' ', '_')}_{timestamp}.csv"
        cleaned_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 Data disimpan ke: {filename}")
        return filename
    return None

def main():
    print("🎓 PROGRAM SCRAPING BERITA RADAR SURABAYA")
    print("👨‍🏫 Dibuat oleh Pradipta Deska Pryanda")
    print("🔧 Diperbaiki: Scraping hingga mendapat jumlah artikel relevan sesuai target + ekstraksi tanggal akurat")
    print("📊 Untuk keperluan riset")
    print("=" * 70)

    # Input keyword
    while True:
        keyword = input("\n🔍 Masukkan keyword pencarian berita: ").strip()
        if keyword:
            break
        print("❌ Keyword tidak boleh kosong!")

    # Input jumlah artikel target
    while True:
        try:
            target_articles = input("📊 Jumlah artikel relevan yang diinginkan (default 5, maks 50): ").strip()
            if not target_articles:
                target_articles = 5
                break
            target_articles = int(target_articles)
            if 1 <= target_articles <= 50:
                break
            else:
                print("❌ Masukkan angka antara 1-50")
        except ValueError:
            print("❌ Masukkan angka yang valid!")

    print(f"\n📝 Keyword: '{keyword}'")
    print(f"📈 Target artikel relevan: {target_articles}")
    print(f"🎯 Sistem akan mencari hingga mendapat {target_articles} artikel yang relevan")
    print(f"⏰ Proses mungkin memakan waktu beberapa menit...")

    try:
        # Mulai scraping
        start_time = time.time()
        df_results = scrape_radar_news(keyword, target_articles)
        end_time = time.time()
        
        if not df_results.empty:
            print("\n" + "=" * 70)
            print("📊 HASIL SCRAPING:")
            print("=" * 70)
            
            # Statistik
            print(f"📈 Statistik:")
            print(f"   • Artikel relevan ditemukan: {len(df_results)}")
            print(f"   • Waktu proses: {end_time - start_time:.1f} detik")
            print(f"   • Artikel dengan konten memadai: {df_results['detail_konten'].apply(lambda x: len(str(x)) > 100).sum()}")
            print(f"   • Artikel dengan tanggal valid: {df_results['tanggal_rilis'].apply(lambda x: str(x) != 'Tanggal tidak ditemukan').sum()}")
            
            # Cek keyword di judul vs konten
            keyword_lower = keyword.lower()
            keyword_in_title = sum(1 for _, row in df_results.iterrows() 
                                 if keyword_lower in str(row['judul_berita']).lower())
            keyword_in_content = sum(1 for _, row in df_results.iterrows() 
                                   if keyword_lower in str(row['detail_konten']).lower())
            
            print(f"   🎯 Keyword ditemukan di judul: {keyword_in_title}")
            print(f"   📝 Keyword ditemukan di konten: {keyword_in_content}")
            
            # Simpan ke CSV
            filename = save_to_csv(df_results, keyword)
            
            # Preview hasil
            print(f"\n📄 PREVIEW HASIL:")
            print("=" * 70)
            
            for idx, (_, row) in enumerate(df_results.iterrows(), 1):
                print(f"\n{idx}. 📋 {row['judul_berita']}")
                print(f"   📅 {row['tanggal_rilis']}")
                print(f"   🔗 {row['link_berita']}")
                
                # Preview konten
                content_preview = str(row['detail_konten'])[:300]
                if len(str(row['detail_konten'])) > 300:
                    content_preview += "..."
                print(f"   📝 {content_preview}")
                
                # Highlight keyword
                title_lower = str(row['judul_berita']).lower()
                content_lower = str(row['detail_konten']).lower()
                
                found_in = []
                if keyword_lower in title_lower:
                    found_in.append("judul")
                if keyword_lower in content_lower:
                    found_in.append("konten")
                
                if found_in:
                    print(f"   🎯 Keyword '{keyword}' ditemukan di: {', '.join(found_in)}")
                
                print("-" * 50)
            
            if filename:
                print(f"\n✅ File berhasil disimpan: {filename}")
        else:
            print("\n❌ Tidak ada artikel relevan yang ditemukan")
            print("💡 Tips:")
            print("   • Coba keyword yang lebih umum (contoh: 'ekonomi', 'politik')")
            print("   • Periksa ejaan keyword")
            print("   • Gunakan keyword dalam bahasa Indonesia")
            print("   • Coba keyword yang lebih pendek")
    
    except KeyboardInterrupt:
        print("\n⚠️ Program dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Terjadi error: {e}")
        import traceback
        traceback.print_exc()

    print("\n👋 Terima kasih telah menggunakan program ini!")
    print("📚 Gunakan data dengan bijak dan sesuai etika riset")

if __name__ == "__main__":
    main()