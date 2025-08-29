"""
Scraping Berita Radar Surabaya - Program untuk mengumpulkan data berita
Dibuat oleh: Pradipta Deska Pryanda
Tanggal: 2024
Diperbaiki: Anti-detection system yang kuat untuk mengatasi 403 Forbidden
"""

# Import library yang diperlukan
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import quote, urljoin, urlparse
import re
from datetime import datetime
import json

# Untuk menghindari error SSL di Colab
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Konfigurasi global
RADAR_BASE = "https://radarsurabaya.jawapos.com"

# Daftar User Agents untuk rotasi
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
]

# ---------- Advanced Session Management ----------
def make_advanced_session():
    """Buat session dengan konfigurasi anti-detection yang kuat"""
    s = requests.Session()
    
    # Pilih user agent secara random
    user_agent = random.choice(USER_AGENTS)
    
    # Headers yang lebih natural dan lengkap
    s.headers.update({
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
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
    })
    
    return s

def human_like_delay(min_delay=2, max_delay=5):
    """Delay yang meniru perilaku manusia"""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def get_page_with_retry(url, session=None, max_retries=3, use_different_approach=True):
    """Ambil halaman dengan berbagai strategi anti-detection"""
    if session is None:
        session = make_advanced_session()
    
    for attempt in range(max_retries):
        try:
            # Strategi 1: Request normal dengan headers lengkap
            if attempt == 0:
                response = session.get(url, timeout=30, verify=False, allow_redirects=True)
            
            # Strategi 2: Tambah referer dan delay
            elif attempt == 1:
                session.headers.update({'Referer': 'https://www.google.com/'})
                human_like_delay(3, 6)
                response = session.get(url, timeout=30, verify=False, allow_redirects=True)
            
            # Strategi 3: Ganti user agent dan tambah cookies
            else:
                session.headers.update({
                    'User-Agent': random.choice(USER_AGENTS),
                    'Referer': 'https://radarsurabaya.jawapos.com/',
                })
                session.cookies.update({
                    'session_id': f'sess_{random.randint(100000, 999999)}',
                    'visitor_id': f'vis_{random.randint(100000, 999999)}'
                })
                human_like_delay(5, 8)
                response = session.get(url, timeout=30, verify=False, allow_redirects=True)
            
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"   🚫 403 Forbidden pada attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    print(f"   🔄 Mengganti strategi dan mencoba lagi...")
                    human_like_delay(5, 10)  # Delay lebih lama untuk 403
                continue
            else:
                print(f"   ❌ HTTP Error {e.response.status_code} pada attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    human_like_delay(2, 4)
                continue
        except Exception as e:
            print(f"   ⚠️ Error pada attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                human_like_delay(2, 4)
            continue
    
    print(f"   ❌ Gagal mengakses {url} setelah {max_retries} percobaan")
    return None

def search_with_google(keyword, site="radarsurabaya.jawapos.com", num_results=20):
    """Cari artikel menggunakan Google Search sebagai fallback"""
    try:
        session = make_advanced_session()
        
        # Query Google dengan site-specific search
        query = f"site:{site} {keyword}"
        google_url = f"https://www.google.com/search?q={quote(query)}&num={num_results}"
        
        print(f"🔍 Mencoba Google Search: {query}")
        
        html = get_page_with_retry(google_url, session)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Cari link hasil Google
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Extract URL dari Google redirect
            if '/url?q=' in href:
                actual_url = href.split('/url?q=')[1].split('&')[0]
                actual_url = actual_url.replace('%3A', ':').replace('%2F', '/').replace('%3F', '?').replace('%3D', '=').replace('%26', '&')
                
                if site in actual_url:
                    title = link.get_text(strip=True)
                    if len(title) > 10:
                        results.append({
                            'title': title,
                            'url': actual_url,
                            'date_from_list': None
                        })
        
        print(f"   ✅ Google Search menemukan {len(results)} hasil")
        return results[:num_results]
        
    except Exception as e:
        print(f"   ❌ Google Search error: {e}")
        return []

def search_with_bing(keyword, site="radarsurabaya.jawapos.com", num_results=20):
    """Cari artikel menggunakan Bing Search sebagai fallback"""
    try:
        session = make_advanced_session()
        
        # Query Bing dengan site-specific search
        query = f"site:{site} {keyword}"
        bing_url = f"https://www.bing.com/search?q={quote(query)}&count={num_results}"
        
        print(f"🔍 Mencoba Bing Search: {query}")
        
        html = get_page_with_retry(bing_url, session)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Cari link hasil Bing
        for link in soup.select('li.b_algo h2 a, .b_title a'):
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if site in href and len(title) > 10:
                results.append({
                    'title': title,
                    'url': href,
                    'date_from_list': None
                })
        
        print(f"   ✅ Bing Search menemukan {len(results)} hasil")
        return results[:num_results]
        
    except Exception as e:
        print(f"   ❌ Bing Search error: {e}")
        return []

def extract_article_details(article_url, session):
    """Ekstrak detail artikel dengan anti-detection"""
    html_content = get_page_with_retry(article_url, session)
    if not html_content:
        return None, None, None

    soup = BeautifulSoup(html_content, 'html.parser')

    # Ekstrak judul
    title = extract_title(soup)
    
    # Ekstrak tanggal
    date_published = extract_date(soup)
    
    # Ekstrak konten
    content_text = extract_content(soup)

    return title, date_published, content_text

def extract_title(soup):
    """Ekstrak judul artikel"""
    title_selectors = [
        'h1.article__title',
        'h1.post__title', 
        'h1.entry-title',
        'h1.title',
        '.article-title h1',
        '.post-title h1',
        'h1',
        'meta[property="og:title"]',
        'title'
    ]
    
    for selector in title_selectors:
        try:
            if selector.startswith('meta') or selector == 'title':
                element = soup.select_one(selector)
                if element:
                    content = element.get('content') if element.name == 'meta' else element.get_text()
                    if content and len(content.strip()) > 10:
                        return content.strip()
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:
                        return text
        except:
            continue
    
    return "Judul tidak ditemukan"

def extract_date(soup):
    """Ekstrak tanggal artikel dengan berbagai metode"""
    
    # Method 1: Time element dengan datetime
    for time_elem in soup.find_all('time'):
        if time_elem.has_attr('datetime'):
            return time_elem['datetime']
    
    # Method 2: Meta tags
    meta_selectors = [
        'meta[property="article:published_time"]',
        'meta[name="pubdate"]',
        'meta[name="publishdate"]',
        'meta[name="date"]'
    ]
    
    for selector in meta_selectors:
        try:
            tag = soup.select_one(selector)
            if tag and tag.get('content'):
                return tag['content'].strip()
        except:
            continue
    
    # Method 3: Date classes
    date_selectors = [
        '.article__date', '.post__date', '.entry-date', '.date',
        '.publish-date', '.published', '.timestamp'
    ]
    
    for selector in date_selectors:
        try:
            element = soup.select_one(selector)
            if element:
                date_text = element.get_text(strip=True)
                if date_text and len(date_text) > 5:
                    return date_text
        except:
            continue
    
    # Method 4: Regex dalam teks
    body_text = soup.get_text()
    date_patterns = [
        r'(\d{1,2}\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        r'(\d{4}[/-]\d{2}[/-]\d{2})'
    ]
    
    for pattern in date_patterns:
        try:
            match = re.search(pattern, body_text)
            if match:
                return match.group(1)
        except:
            continue
    
    return "Tanggal tidak ditemukan"

def extract_content(soup):
    """Ekstrak konten artikel"""
    content_selectors = [
        'div.article__content', 'div.post__content', 'article .content',
        'div.entry-content', 'div.content-detail', 'div.article-content',
        '.article-body', '.post-body', '.content-body'
    ]
    
    for selector in content_selectors:
        try:
            element = soup.select_one(selector)
            if element and len(element.get_text(strip=True)) > 100:
                # Bersihkan elemen yang tidak diinginkan
                for unwanted in element(['script', 'style', 'nav', 'aside', 'header', 
                                       'footer', 'noscript', 'figure', 'iframe']):
                    unwanted.decompose()
                
                return clean_text(element.get_text(separator=' ', strip=True))
        except:
            continue
    
    # Fallback ke body
    try:
        body = soup.find('body')
        if body:
            for unwanted in body(['script', 'style', 'nav', 'aside', 'header', 
                                'footer', 'noscript', 'figure', 'iframe']):
                unwanted.decompose()
            return clean_text(body.get_text(separator=' ', strip=True))
    except:
        pass
    
    return "Konten tidak dapat diambil"

def clean_text(text):
    """Bersihkan teks"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', ' ', text)
    return text.strip()

def is_keyword_relevant(text, keyword):
    """Cek relevansi keyword dengan teks"""
    if not text or not keyword:
        return False
    
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    # Exact match
    if keyword_lower in text_lower:
        return True
    
    # Word-by-word match
    keyword_words = [w for w in keyword_lower.split() if len(w) > 2]
    if not keyword_words:
        return False
    
    matches = 0
    for word in keyword_words:
        if word in text_lower:
            matches += 1
    
    return matches >= len(keyword_words) * 0.7

def calculate_score(title, content, keyword):
    """Hitung skor relevansi"""
    score = 0
    if not title or not content or not keyword:
        return score
    
    title_lower = title.lower()
    content_lower = content.lower()
    keyword_lower = keyword.lower()
    
    # Skor untuk keyword di judul
    if keyword_lower in title_lower:
        score += 20
    
    # Skor untuk keyword di konten
    if keyword_lower in content_lower:
        score += 10
    
    # Skor untuk kata individual
    for word in keyword_lower.split():
        if len(word) > 2:
            if word in title_lower:
                score += 8
            score += content_lower.count(word) * 2
    
    return score

def scrape_radar_news(keyword, target_articles):
    """Scraping dengan multiple fallback strategies"""
    print("=" * 70)
    print(f"MEMULAI SCRAPING BERITA RADAR SURABAYA")
    print(f"KEYWORD: '{keyword}' | TARGET: {target_articles} artikel")
    print("=" * 70)
    
    session = make_advanced_session()
    all_links = []
    
    # Strategy 1: Coba akses langsung (mungkin berhasil dengan headers yang tepat)
    print("🔍 Strategi 1: Mencoba akses langsung dengan anti-detection...")
    try:
        homepage_html = get_page_with_retry(RADAR_BASE, session)
        if homepage_html:
            soup = BeautifulSoup(homepage_html, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                title = a.get_text(strip=True)
                
                if len(title) > 10 and 'radarsurabaya.jawapos.com' in href:
                    all_links.append({'title': title, 'url': href, 'date_from_list': None})
            
            print(f"   ✅ Berhasil mengumpulkan {len(all_links)} link dari homepage")
    except Exception as e:
        print(f"   ❌ Akses langsung gagal: {e}")
    
    # Strategy 2: Google Search fallback
    if len(all_links) < target_articles * 3:
        print("🔍 Strategi 2: Menggunakan Google Search...")
        google_results = search_with_google(keyword)
        all_links.extend(google_results)
        print(f"   📊 Total link sekarang: {len(all_links)}")
    
    # Strategy 3: Bing Search fallback
    if len(all_links) < target_articles * 3:
        print("🔍 Strategi 3: Menggunakan Bing Search...")
        bing_results = search_with_bing(keyword)
        all_links.extend(bing_results)
        print(f"   📊 Total link sekarang: {len(all_links)}")
    
    # Remove duplicates
    unique_links = []
    seen_urls = set()
    for link in all_links:
        if link['url'] not in seen_urls:
            unique_links.append(link)
            seen_urls.add(link['url'])
    
    all_links = unique_links
    print(f"✅ Total link unik: {len(all_links)}")
    
    if not all_links:
        print("❌ Tidak berhasil mengumpulkan link artikel")
        return pd.DataFrame()
    
    # Process articles
    results = []
    processed = 0
    
    print(f"\n📝 Memproses artikel hingga mendapat {target_articles} artikel relevan...")
    
    for i, link in enumerate(all_links, 1):
        if len(results) >= target_articles:
            print(f"🎉 Target {target_articles} artikel tercapai!")
            break
        
        print(f"\n[{i}/{len(all_links)}] {link['title'][:60]}...")
        
        try:
            title, date, content = extract_article_details(link['url'], session)
            
            if not title or not content:
                print("   ⚠️ Gagal ekstrak konten")
                continue
            
            if is_keyword_relevant(title, keyword) or is_keyword_relevant(content, keyword):
                score = calculate_score(title, content, keyword)
                
                results.append({
                    'judul_berita': title,
                    'link_berita': link['url'],
                    'tanggal_rilis': date,
                    'detail_konten': content,
                    'score': score
                })
                
                print(f"   ✅ Relevan #{len(results)} (skor: {score})")
            else:
                print("   ❌ Tidak relevan")
            
            processed += 1
            human_like_delay(1, 3)  # Natural delay
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            processed += 1
            continue
    
    if results:
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Remove score column
        for result in results:
            del result['score']
        
        df = pd.DataFrame(results)
        print(f"\n✅ Scraping berhasil! Ditemukan {len(results)} artikel relevan")
        return df
    else:
        print("\n❌ Tidak ditemukan artikel yang relevan")
        return pd.DataFrame()

def save_to_csv(dataframe, keyword):
    """Simpan ke CSV"""
    if not dataframe.empty:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"berita_radarsurabaya_{keyword.replace(' ', '_')}_{timestamp}.csv"
        dataframe.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 Data disimpan ke: {filename}")
        return filename
    return None

def main():
    print("🎓 PROGRAM SCRAPING BERITA RADAR SURABAYA")
    print("👨‍🏫 Dibuat oleh Pradipta Deska Pryanda") 
    print("🔧 Diperbaiki: Anti-detection system untuk mengatasi 403 Forbidden")
    print("📊 Multiple fallback strategies (Direct + Google + Bing)")
    print("=" * 70)

    # Input
    while True:
        keyword = input("\n🔍 Masukkan keyword pencarian berita: ").strip()
        if keyword:
            break
        print("❌ Keyword tidak boleh kosong!")

    while True:
        try:
            target = input("📊 Jumlah artikel relevan yang diinginkan (default 5): ").strip()
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
    print(f"📈 Target: {target} artikel relevan")
    print(f"🚀 Menggunakan multiple strategies untuk mengatasi blocking...")

    try:
        start_time = time.time()
        df_results = scrape_radar_news(keyword, target)
        end_time = time.time()
        
        if not df_results.empty:
            print("\n" + "=" * 70)
            print("📊 HASIL SCRAPING:")
            print("=" * 70)
            
            print(f"📈 Statistik:")
            print(f"   • Artikel ditemukan: {len(df_results)}")
            print(f"   • Waktu proses: {end_time - start_time:.1f} detik")
            
            # Simpan
            filename = save_to_csv(df_results, keyword)
            
            # Preview
            print(f"\n📄 PREVIEW HASIL:")
            print("=" * 50)
            
            for idx, (_, row) in enumerate(df_results.iterrows(), 1):
                print(f"\n{idx}. 📋 {row['judul_berita']}")
                print(f"   📅 {row['tanggal_rilis']}")
                print(f"   🔗 {row['link_berita']}")
                
                content_preview = str(row['detail_konten'])[:200]
                if len(str(row['detail_konten'])) > 200:
                    content_preview += "..."
                print(f"   📝 {content_preview}")
                print("-" * 30)
            
            if filename:
                print(f"\n✅ File berhasil disimpan: {filename}")
        else:
            print("\n❌ Tidak ada artikel relevan ditemukan")
            print("💡 Tips:")
            print("   • Coba keyword yang lebih umum")
            print("   • Periksa ejaan keyword")
            print("   • Coba lagi nanti (mungkin ada rate limiting)")
    
    except KeyboardInterrupt:
        print("\n⚠️ Program dihentikan")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n👋 Terima kasih!")

if __name__ == "__main__":
    main()