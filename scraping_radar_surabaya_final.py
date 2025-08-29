"""
Scraping Berita Radar Surabaya - Program untuk mengumpulkan data berita
Dibuat oleh: Pradipta Deska Pryanda
Tanggal: 2024
Diperbaiki: Pendekatan baru dengan crawling langsung tanpa search engine eksternal
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

def extract_links_from_homepage():
    """Ekstrak semua link artikel dari homepage"""
    session = make_session()
    html = get_page_content(RADAR_BASE, session)
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
        'a.latest__link',
        'article a',
        '.news-item a',
        '.article-item a',
        'h2 a',
        'h3 a',
        '.title a'
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
                           'javascript:', 'mailto:', '/wp-content/']
            
            if any(pattern in href.lower() for pattern in skip_patterns):
                continue
                
            # Pastikan URL valid dan dari domain yang benar
            if 'radarsurabaya.jawapos.com' not in href:
                continue
            
            if href not in used_urls:
                links.append({'title': title, 'url': href})
                used_urls.add(href)
    
    return links

def extract_links_from_categories():
    """Ekstrak link dari halaman kategori"""
    session = make_session()
    categories = [
        '/ekonomi',
        '/politik', 
        '/nasional',
        '/daerah',
        '/olahraga'
    ]
    
    all_links = []
    used_urls = set()
    
    for category in categories:
        try:
            category_url = RADAR_BASE + category
            html = get_page_content(category_url, session)
            if not html:
                continue
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # Cari semua link artikel di halaman kategori
            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                title = a.get_text(strip=True)
                
                if not href or not title or len(title) < 10:
                    continue
                    
                # Normalisasi URL
                if href.startswith('/'):
                    href = urljoin(RADAR_BASE, href)
                elif not href.startswith('http'):
                    href = urljoin(RADAR_BASE, href)
                
                # Skip jika bukan artikel berita
                if any(pattern in href.lower() for pattern in ['#', '.pdf', '.jpg', '.jpeg', '.png', 
                                                              '/foto/', '/video/', '/indeks', '/tag/', 
                                                              '/category/', '/search/', '/about/', '/contact']):
                    continue
                
                # Pastikan URL valid dan dari domain yang benar
                if 'radarsurabaya.jawapos.com' not in href:
                    continue
                
                if href not in used_urls:
                    all_links.append({'title': title, 'url': href})
                    used_urls.add(href)
            
            time.sleep(random.uniform(1, 2))  # Delay antar kategori
            
        except Exception as e:
            print(f"⚠️ Error accessing category {category}: {e}")
            continue
    
    return all_links

def extract_article_details(article_url):
    """Ekstrak detail artikel dari URL"""
    session = make_session()
    html_content = get_page_content(article_url, session)
    if not html_content:
        return None, None, None

    soup = BeautifulSoup(html_content, 'html.parser')

    # Ekstrak judul
    title = "Judul tidak ditemukan"
    title_selectors = [
        'h1.article__title',
        'h1.post__title', 
        'h1.entry-title',
        'h1.title',
        'h1',
        'meta[property="og:title"]'
    ]
    
    for selector in title_selectors:
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

    # Ekstrak tanggal
    date_published = "Tanggal tidak ditemukan"
    date_selectors = [
        'time[datetime]',
        'time',
        '.article__date',
        '.post__date',
        '.entry-date',
        '.date',
        'meta[property="article:published_time"]'
    ]
    
    for selector in date_selectors:
        if selector.startswith('meta'):
            tag = soup.select_one(selector)
            if tag and tag.get('content'):
                date_published = tag['content'].strip()
                break
        else:
            element = soup.select_one(selector)
            if element:
                if element.has_attr('datetime'):
                    date_published = element['datetime'].strip()
                    break
                else:
                    text = element.get_text(strip=True)
                    if text and len(text) > 5:
                        date_published = text
                        break

    # Ekstrak konten
    content_text = ""
    content_selectors = [
        'div.article__content',
        'div.post__content',
        'article .content',
        'div.entry-content',
        'div.content-detail',
        'div.article-content',
        '.article-body',
        '.post-body'
    ]
    
    content_element = None
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element and len(content_element.get_text(strip=True)) > 50:
            break
    
    if content_element:
        # Hapus elemen yang tidak diinginkan
        for unwanted in content_element(['script', 'style', 'nav', 'aside', 'header', 
                                       'footer', 'noscript', 'figure', 'iframe', 'form']):
            unwanted.decompose()
        content_text = content_element.get_text(separator=' ', strip=True)
    else:
        # Fallback ke body
        body = soup.find('body')
        if body:
            for unwanted in body(['script', 'style', 'nav', 'aside', 'header', 
                                'footer', 'noscript', 'figure', 'iframe', 'form']):
                unwanted.decompose()
            content_text = body.get_text(separator=' ', strip=True)

    content_text = clean_text(content_text)
    return title, date_published, content_text

def is_keyword_match(text, keyword):
    """Cek apakah keyword cocok dengan teks (case insensitive)"""
    if not text or not keyword:
        return False
    
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    # Cek keyword utuh
    if keyword_lower in text_lower:
        return True
    
    # Cek kata per kata
    keyword_words = keyword_lower.split()
    text_words = text_lower.split()
    
    # Jika keyword hanya 1 kata
    if len(keyword_words) == 1:
        return keyword_words[0] in text_lower
    
    # Jika keyword multi-kata, cek berapa persen yang cocok
    matches = 0
    for kw in keyword_words:
        if len(kw) > 2:  # Skip kata yang terlalu pendek
            if any(kw in word for word in text_words):
                matches += 1
    
    # Jika minimal 70% kata keyword ditemukan
    return matches >= len(keyword_words) * 0.7

def calculate_relevance_score(title, content, keyword):
    """Hitung skor relevansi"""
    score = 0
    
    if not title or not content or not keyword:
        return score
    
    title_lower = title.lower()
    content_lower = content.lower()
    keyword_lower = keyword.lower()
    
    # Skor untuk keyword di judul (bobot tinggi)
    if keyword_lower in title_lower:
        score += 10
    
    # Skor untuk setiap kata keyword di judul
    for word in keyword_lower.split():
        if len(word) > 2 and word in title_lower:
            score += 5
    
    # Skor untuk keyword di konten
    if keyword_lower in content_lower:
        score += 3
    
    # Skor untuk setiap kata keyword di konten
    for word in keyword_lower.split():
        if len(word) > 2:
            score += content_lower.count(word)
    
    return score

def scrape_radar_news(keyword, max_articles=5):
    print("=" * 70)
    print(f"MEMULAI SCRAPING BERITA RADAR SURABAYA UNTUK KEYWORD: '{keyword}'")
    print("=" * 70)
    
    max_articles = min(max_articles, 600)
    
    # Step 1: Kumpulkan semua link artikel
    print("🔍 Mengumpulkan link artikel dari homepage...")
    homepage_links = extract_links_from_homepage()
    print(f"   ✅ Ditemukan {len(homepage_links)} link dari homepage")
    
    print("🔍 Mengumpulkan link artikel dari kategori...")
    category_links = extract_links_from_categories()
    print(f"   ✅ Ditemukan {len(category_links)} link dari kategori")
    
    # Gabungkan dan hapus duplikat
    all_links = []
    used_urls = set()
    
    for link in homepage_links + category_links:
        if link['url'] not in used_urls:
            all_links.append(link)
            used_urls.add(link['url'])
    
    print(f"📊 Total link unik: {len(all_links)}")
    
    if not all_links:
        print("❌ Tidak berhasil mengumpulkan link artikel")
        return pd.DataFrame()
    
    # Step 2: Filter berdasarkan keyword di judul (quick filter)
    print(f"\n🎯 Melakukan quick filter berdasarkan keyword '{keyword}' di judul...")
    relevant_links = []
    
    for link in all_links:
        if is_keyword_match(link['title'], keyword):
            relevant_links.append(link)
    
    print(f"   ✅ Ditemukan {len(relevant_links)} artikel dengan judul relevan")
    
    # Jika tidak ada yang relevan di judul, ambil semua untuk dicek kontennya
    if not relevant_links:
        print("   ⚠️ Tidak ada artikel dengan judul relevan, akan cek semua konten...")
        relevant_links = all_links[:min(100, len(all_links))]  # Batasi untuk efisiensi
    
    # Step 3: Ekstrak detail dan validasi konten
    results = []
    articles_with_scores = []
    
    print(f"\n📝 Mengekstrak detail artikel dan validasi konten...")
    total_to_process = min(len(relevant_links), max_articles * 3)  # Proses 3x lipat untuk buffer
    
    for i, link in enumerate(relevant_links[:total_to_process], 1):
        print(f"\n[{i}/{total_to_process}] Memproses: {link['title'][:60]}...")
        
        try:
            title, date, content = extract_article_details(link['url'])
            
            if not title or not content:
                print("   ⚠️ Gagal mengekstrak konten artikel")
                continue
            
            # Cek relevansi berdasarkan title + content
            if is_keyword_match(title, keyword) or is_keyword_match(content, keyword):
                score = calculate_relevance_score(title, content, keyword)
                
                article_data = {
                    'judul_berita': clean_text(title),
                    'link_berita': link['url'],
                    'tanggal_rilis': date,
                    'detail_konten': content,
                    'relevance_score': score
                }
                
                articles_with_scores.append(article_data)
                print(f"   ✅ Artikel relevan (skor: {score})")
                
                # Break early jika sudah cukup
                if len(articles_with_scores) >= max_articles:
                    print(f"   🎉 Sudah mengumpulkan {max_articles} artikel relevan")
                    break
            else:
                print(f"   ❌ Artikel tidak relevan dengan keyword '{keyword}'")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Delay untuk menghindari rate limiting
        time.sleep(random.uniform(1, 2))
    
    # Step 4: Urutkan berdasarkan skor dan return hasil
    if articles_with_scores:
        articles_with_scores.sort(key=lambda x: x['relevance_score'], reverse=True)
        results = articles_with_scores[:max_articles]
        
        # Hapus kolom skor
        for article in results:
            del article['relevance_score']
        
        df = pd.DataFrame(results)
        print(f"\n✅ Scraping selesai!")
        print(f"   • Total artikel relevan ditemukan: {len(results)}")
        return df
    else:
        print("\n❌ Tidak ada artikel relevan yang ditemukan")
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
    print("🔧 Diperbaiki: Pendekatan crawling langsung tanpa search engine eksternal")
    print("📊 Untuk keperluan riset")
    print("=" * 70)

    # Input keyword
    while True:
        keyword = input("\n🔍 Masukkan keyword pencarian berita: ").strip()
        if keyword:
            break
        print("❌ Keyword tidak boleh kosong!")

    # Input jumlah artikel
    while True:
        try:
            max_articles = input("📊 Jumlah maksimal artikel (default 5, maks 50): ").strip()
            if not max_articles:
                max_articles = 5
                break
            max_articles = int(max_articles)
            if 1 <= max_articles <= 50:
                break
            else:
                print("❌ Masukkan angka antara 1-50")
        except ValueError:
            print("❌ Masukkan angka yang valid!")

    print(f"\n📝 Keyword: '{keyword}'")
    print(f"📈 Maksimal artikel: {max_articles}")
    print(f"🎯 Mencari artikel yang mengandung keyword di judul atau konten")

    try:
        # Scraping
        df_results = scrape_radar_news(keyword, max_articles)
        
        if not df_results.empty:
            print("\n" + "=" * 70)
            print("📊 HASIL SCRAPING:")
            print("=" * 70)
            
            # Statistik
            print(f"📈 Statistik:")
            print(f"   • Total artikel: {len(df_results)}")
            print(f"   • Artikel dengan konten memadai: {df_results['detail_konten'].apply(lambda x: len(str(x)) > 100).sum()}")
            
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
            print(f"\n📄 PREVIEW HASIL (3 artikel teratas):")
            print("=" * 70)
            
            for idx, (_, row) in enumerate(df_results.head(3).iterrows(), 1):
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
            print("   • Coba keyword yang lebih umum")
            print("   • Periksa ejaan keyword")
            print("   • Gunakan keyword dalam bahasa Indonesia")
    
    except KeyboardInterrupt:
        print("\n⚠️ Program dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Terjadi error: {e}")
        import traceback
        traceback.print_exc()

    print("\n👋 Terima kasih telah menggunakan program ini!")

if __name__ == "__main__":
    main()