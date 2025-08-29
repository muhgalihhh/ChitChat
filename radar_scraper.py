"""
Scraping Berita Radar Surabaya - Program untuk mengumpulkan data berita
Dibuat oleh: Pradipta Deska Pryanda
Tanggal: 2024
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
MAX_ARTICLES_PER_PAGE = 15
MAX_PAGES_TO_CHECK = 1  # Radar umumnya single page
MAX_EXTRA_ARTICLES_TO_FETCH = 300
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

def warmup_homepage(session):
    try:
        r = session.get(RADAR_BASE, timeout=20, verify=False)
        r.raise_for_status()
        # Simulasi navigasi internal agar cookie/anti-bot terpasang
        time.sleep(random.uniform(0.8, 1.6))
        return True
    except Exception as e:
        print(f"⚠️ Warmup gagal: {e}")
        return False

def get_with_referer(session, url, referer):
    headers = {'Referer': referer}
    r = session.get(url, headers=headers, timeout=25, verify=False)
    r.raise_for_status()
    return r

def get_search_url(keyword, page=1):
    encoded_keyword = quote(keyword)
    return f"{RADAR_BASE}/search?q={encoded_keyword}"

def get_page_content(url, session=None, referer=None, retries=2):
    if session is None:
        session = make_session()
    last_err = None
    for attempt in range(retries):
        try:
            if referer:
                resp = get_with_referer(session, url, referer)
            else:
                resp = session.get(url, timeout=25, verify=False)
                resp.raise_for_status()
            return resp.text
        except requests.exceptions.HTTPError as he:
            last_err = he
            code = getattr(he.response, 'status_code', None)
            if code == 403 and attempt == 0:
                print("🔁 Terjadi 403, mencoba ulang dengan warmup dan referer...")
                warmup_homepage(session)
                time.sleep(random.uniform(0.8, 1.6))
                referer = RADAR_BASE + '/'
                continue
            time.sleep(random.uniform(0.6, 1.2))
        except Exception as e:
            last_err = e
            time.sleep(random.uniform(0.6, 1.2))
    print(f"Error saat mengakses {url}: {last_err}")
    return None

# ---------- Fallback: Bing & DuckDuckGo ----------
def search_bing_ddg(keyword, limit=30):
    q = quote(f"site:radarsurabaya.jawapos.com {keyword}")
    ses = make_session()
    results = []

    try:
        url_bing = f"https://www.bing.com/search?q={q}"
        html = get_page_content(url_bing, ses, referer="https://www.bing.com/")
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.select('li.b_algo h2 a, h2 a'):
                href = a.get('href', '')
                title = a.get_text(strip=True)
                if href and 'radarsurabaya.jawapos.com' in href and len(title) > 10:
                    results.append({'title': title, 'url': href, 'date_from_list': None})
                    if len(results) >= limit:
                        return results
    except Exception as e:
        print(f"⚠️ Fallback Bing error: {e}")

    try:
        url_ddg = f"https://duckduckgo.com/html/?q={q}"
        html = get_page_content(url_ddg, ses, referer="https://duckduckgo.com/")
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.select('a.result__a'):
                href = a.get('href', '')
                title = a.get_text(strip=True)
                if href and 'radarsurabaya.jawapos.com' in href and len(title) > 10:
                    results.append({'title': title, 'url': href, 'date_from_list': None})
                    if len(results) >= limit:
                        break
    except Exception as e:
        print(f"⚠️ Fallback DuckDuckGo error: {e}")

    return results

def extract_article_links_from_page(search_html, base_url):
    if not search_html:
        return []

    soup = BeautifulSoup(search_html, 'html.parser')
    links = []
    used_urls = set()

    cards = soup.select('a.latest__link')
    for a in cards:
        href = a.get('href', '').strip()
        title = a.get_text(strip=True)
        if not href or not title:
            continue
        if href.startswith('/'):
            href = urljoin(RADAR_BASE, href)
        if not href.startswith('http'):
            href = urljoin(RADAR_BASE, href)

        date_text = None
        parent = a.parent
        date_tag = None
        if parent:
            date_tag = parent.select_one('date.latest__date') or parent.find('date', class_='latest__date')
            if not date_tag and parent.parent:
                date_tag = parent.parent.select_one('date.latest__date') or parent.parent.find('date', class_='latest__date')
        if date_tag:
            date_text = date_tag.get_text(strip=True)

        if href not in used_urls:
            links.append({'title': title, 'url': href, 'date_from_list': date_text})
            used_urls.add(href)

    if not links:
        all_links = soup.find_all('a', href=True)
        for link_tag in all_links:
            href = link_tag['href'].strip()
            title = link_tag.get_text(strip=True)
            if href.startswith('/'):
                href = urljoin(RADAR_BASE, href)
            if (re.search(r'https?://.*radarsurabaya\.jawapos\.com/', href) and
                not re.search(r'#|\.pdf$|\.jpg$|\.jpeg$|\.png$|/foto/|/video/|/indeks|/tag/|/category/|/search/|/about/|/contact', href, re.IGNORECASE) and
                len(title) > 10):
                if href not in used_urls:
                    links.append({'title': title, 'url': href, 'date_from_list': None})
                    used_urls.add(href)

    return links

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def extract_article_details(article_url):
    session = make_session()
    html_content = get_page_content(article_url, session=session, referer=RADAR_BASE + '/')
    if not html_content:
        return None, None, None

    soup = BeautifulSoup(html_content, 'html.parser')

    title = "Judul tidak ditemukan"
    title_selectors = [
        'h1.article__title',
        'h1.post__title',
        'h1.entry-title',
        'h1.title',
        'h1',
        'meta[property="og:title"]',
        'title'
    ]
    for selector in title_selectors:
        if selector.startswith('meta'):
            tag = soup.select_one(selector)
            if tag and tag.get('content'):
                t = tag['content'].strip()
                if t and len(t) > 10:
                    title = t
                    break
        else:
            title_element = soup.select_one(selector)
            if title_element:
                title_text = title_element.get_text(strip=True)
                if title_text and len(title_text) > 10:
                    title = title_text
                    break

    date_published = None
    date_selectors = [
        'date.latest__date',
        'time[datetime]',
        'time',
        '.article__date',
        '.post__date',
        '.entry-date',
        'meta[property="article:published_time"]',
        'meta[name="pubdate"]',
        'meta[name="publishdate"]',
        'meta[name="date"]'
    ]
    for selector in date_selectors:
        if selector.startswith('meta'):
            tag = soup.select_one(selector)
            if tag and tag.get('content'):
                date_published = tag['content'].strip()
                break
        else:
            date_element = soup.select_one(selector)
            if date_element:
                if date_element.has_attr('datetime'):
                    date_published = date_element['datetime'].strip()
                    break
                else:
                    date_text = date_element.get_text(strip=True)
                    if date_text and len(date_text) > 5:
                        date_published = date_text
                        break

    if not date_published:
        body_text = soup.get_text(separator=' ', strip=True)
        date_patterns = [
            r'(\d{1,2}\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4}\s*,?\s*\d{1,2}:\d{2}\s*(WIB|WITA|WIT)?)',
            r'(\d{1,2}\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}\s*\d{1,2}:\d{2})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(\d{4}[/-]\d{2}[/-]\d{2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, body_text)
            if match:
                date_published = match.group(1)
                break

    content_text = ""
    content_selectors = [
        'div.article__content',
        'div.post__content',
        'article .content',
        'article',
        'div.entry-content',
        'div.content-detail',
        'div.read__content',
        'div.article-content',
        'div#content-article',
        'div.content__wrap'
    ]
    content_element = None
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element and len(content_element.get_text(strip=True)) > 50:
            break

    unwanted_classes = re.compile(r'.*(ads|advert|promo|related|widget|sidebar|footer|breadcrumb|taglist|share|social).*', re.I)
    unwanted_ids = re.compile(r'.*(ads|advert|promo|related|widget|sidebar|footer|breadcrumb|taglist|share|social).*', re.I)

    if content_element:
        for unwanted in content_element(["script", "style", "nav", "aside", "header", "footer", "noscript", "figure"]):
            unwanted.decompose()
        for unwanted in content_element.find_all(class_=unwanted_classes):
            unwanted.decompose()
        for unwanted in content_element.find_all(id=unwanted_ids):
            unwanted.decompose()
        content_text = content_element.get_text(separator=' ', strip=True)
    else:
        body = soup.find('body')
        if body:
            for unwanted in body(["script", "style", "nav", "aside", "header", "footer", "noscript", "figure"]):
                unwanted.decompose()
            for unwanted in body.find_all(class_=unwanted_classes):
                unwanted.decompose()
            for unwanted in body.find_all(id=unwanted_ids):
                unwanted.decompose()
            content_text = body.get_text(separator=' ', strip=True)

    content_text = clean_text(content_text)
    return title, date_published, content_text

def is_title_contains_keyword(title, keyword):
    """
    MODIFIKASI: Fungsi baru untuk mengecek apakah keyword ada di judul berita
    Menggantikan fungsi is_article_relevant_by_content yang lama
    """
    if not title:
        return False
    # Konversi ke lowercase untuk pencarian case-insensitive
    title_lower = title.lower()
    keyword_lower = keyword.lower()
    
    # Cek apakah keyword ada dalam judul
    return keyword_lower in title_lower

# ----------------- clean_dataframe (dipertahankan) -----------------
def clean_dataframe(df):
    print("🔍 Memulai pembersihan dan perbaikan DataFrame...")

    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    date_pattern = re.compile(
        r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})|'
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|'
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})|'
        r'(\d{1,2}:\d{2}(?::\d{2})?\s*(?:WIB|WITA|WIT)?)',
        re.IGNORECASE)

    df_clean = df.copy()
    rows_fixed = 0

    original_valid_titles = df_clean['judul_berita'].apply(lambda x: len(str(x).strip()) > 10).sum()
    original_valid_links = df_clean['link_berita'].apply(lambda x: url_pattern.match(str(x)) is not None).sum()
    original_valid_content = df_clean['detail_konten'].apply(lambda x: len(str(x).strip()) > 100).sum()

    print(f" 📋 Judul memadai: {original_valid_titles}/{len(df_clean)}")
    print(f" 🔗 Link valid: {original_valid_links}/{len(df_clean)}")
    print(f" 📝 Konten memadai: {original_valid_content}/{len(df_clean)}")

    for index, row in df_clean.iterrows():
        try:
            row_fixed = False
            raw_title = str(row.get('judul_berita', '')).strip()
            raw_link = str(row.get('link_berita', '')).strip()
            raw_date = str(row.get('tanggal_rilis', '')).strip()
            raw_content = str(row.get('detail_konten', '')).strip()

            correct_title = raw_title
            correct_link = raw_link
            correct_date = raw_date
            correct_content = raw_content

            if not url_pattern.match(raw_link):
                if len(raw_link) > 10 and not date_pattern.search(raw_link) and len(raw_link) < 200:
                    correct_title = f"{raw_title} {raw_link}".strip()
                    row_fixed = True
                elif date_pattern.search(raw_link):
                    correct_date = raw_link
                    row_fixed = True

                if url_pattern.match(raw_date):
                    correct_link = raw_date
                    row_fixed = True
                elif url_pattern.match(raw_content):
                    correct_link = raw_content
                    row_fixed = True
                else:
                    if not url_pattern.match(correct_link):
                        correct_link = ""
                        row_fixed = True

            if not date_pattern.search(raw_date):
                if url_pattern.match(raw_date):
                    if not url_pattern.match(correct_link):
                        correct_link = raw_date
                        row_fixed = True
                elif len(raw_date) > 50:
                    if len(correct_content) < 50:
                        correct_content = raw_date
                        row_fixed = True

                if date_pattern.search(raw_content):
                    correct_date = raw_content
                    row_fixed = True
                else:
                    if not correct_date.strip():
                        correct_date = "Tanggal tidak ditemukan"
                        row_fixed = True

            if len(raw_content) < 50 or date_pattern.search(raw_content):
                if not correct_content or len(correct_content.strip()) == 0:
                    correct_content = "Konten tidak tersedia"
                    row_fixed = True

            original_row = {
                'judul_berita': raw_title,
                'link_berita': raw_link,
                'tanggal_rilis': raw_date,
                'detail_konten': raw_content
            }
            new_row = {
                'judul_berita': correct_title,
                'link_berita': correct_link,
                'tanggal_rilis': correct_date,
                'detail_konten': correct_content
            }

            if original_row != new_row:
                rows_fixed += 1
                df_clean.at[index, 'judul_berita'] = correct_title
                df_clean.at[index, 'link_berita'] = correct_link
                df_clean.at[index, 'tanggal_rilis'] = correct_date
                df_clean.at[index, 'detail_konten'] = correct_content

        except Exception as e:
            print(f"⚠️ Error saat memproses baris {index} dalam pembersihan: {e}")

    print(f"📊 Total baris diproses: {len(df_clean)}")
    print(f"🔧 Baris yang diperbaiki: {rows_fixed}")
    print(f"📈 Persentase perbaikan: {(rows_fixed/len(df_clean)*100 if len(df_clean) else 0):.1f}%")

    valid_links = df_clean['link_berita'].apply(lambda x: url_pattern.match(str(x)) is not None).sum()
    valid_dates = df_clean['tanggal_rilis'].apply(lambda x: date_pattern.search(str(x)) is not None).sum()

    print(f"🔗 Link valid: {valid_links}/{len(df_clean)} ({(valid_links/len(df_clean)*100 if len(df_clean) else 0):.1f}%)")
    print(f"📅 Tanggal terdeteksi: {valid_dates}/{len(df_clean)} ({(valid_dates/len(df_clean)*100 if len(df_clean) else 0):.1f}%)")

    print("✅ Pembersihan dan perbaikan DataFrame selesai.")
    return df_clean

def scrape_radar_news(keyword, max_articles=5):
    print("=" * 70)
    print(f"MEMULAI SCRAPING BERITA RADAR SURABAYA UNTUK KEYWORD: '{keyword}'")
    print("=" * 70)

    max_articles = min(max_articles, 600)
    target_initial_articles = min(max_articles + MAX_EXTRA_ARTICLES_TO_FETCH, 600)

    session = make_session()
    warmup_homepage(session)

    print(f"Mengumpulkan hingga {target_initial_articles} artikel kandidat...")
    search_url = get_search_url(keyword, 1)
    search_html = get_page_content(search_url, session=session, referer=RADAR_BASE + '/')

    all_article_links = []
    if search_html:
        page_links = extract_article_links_from_page(search_html, search_url)
        all_article_links.extend(page_links)

    if not all_article_links:
        print("ℹ️  Tidak bisa mengambil hasil pencarian langsung. Mencoba fallback mesin pencari...")
        fallback_links = search_bing_ddg(keyword, limit=target_initial_articles)
        all_article_links.extend(fallback_links)

    if not all_article_links:
        print("❌ Tidak menemukan link artikel")
        print("💡 Tips: Pastikan keyword yang dimasukkan relevan")
        return pd.DataFrame()

    print(f"✅ Berhasil mengumpulkan {len(all_article_links)} link artikel kandidat")

    results = []
    processed_count = 0
    total_links_to_process = len(all_article_links)

    print(f"\nMengekstrak detail dan memvalidasi relevansi untuk hingga {max_articles} artikel...")
    print(f"🔍 MODIFIKASI: Hanya artikel dengan keyword '{keyword}' di JUDUL yang akan di-scrape")

    for i, article in enumerate(all_article_links, 1):
        if len(results) >= max_articles:
            break

        print(f"\n[{i}/{total_links_to_process}] Memeriksa judul: {article.get('title','')[:60]}...")
        
        # MODIFIKASI: Cek keyword di judul SEBELUM scraping detail
        article_title = article.get('title', '')
        if not is_title_contains_keyword(article_title, keyword):
            print(f"   ❌ Judul tidak mengandung keyword '{keyword}' - SKIP (tidak di-scrape)")
            processed_count += 1
            continue
        
        print(f"   ✅ Judul mengandung keyword '{keyword}' - Melakukan scraping detail...")
        
        try:
            # Baru scrape detail jika judul sudah relevan
            extracted_title, date_published, content_text = extract_article_details(article['url'])
            final_title = extracted_title or article.get('title', 'Judul tidak ditemukan')
            final_date = date_published or article.get('date_from_list') or "Tanggal tidak ditemukan"

            # Double check: pastikan judul final juga mengandung keyword
            if is_title_contains_keyword(final_title, keyword):
                results.append({
                    'judul_berita': clean_text(final_title),
                    'link_berita': article['url'],
                    'tanggal_rilis': final_date,
                    'detail_konten': content_text if content_text else "Konten tidak dapat diambil"
                })
                print(f"   ✅ Artikel berhasil di-scrape ({len(results)}/{max_articles})")
            else:
                print(f"   ❌ Judul final tidak mengandung keyword '{keyword}' - SKIP")

            processed_count += 1
            time.sleep(random.uniform(0.8, 1.8))

        except Exception as e:
            print(f"❌ Error memproses artikel: {e}")
            # Tetap simpan jika ada error, karena judul sudah relevan
            results.append({
                'judul_berita': clean_text(article.get('title', 'Judul tidak ditemukan')),
                'link_berita': article['url'],
                'tanggal_rilis': "Error saat mengambil data",
                'detail_konten': f"Error: {str(e)}"
            })
            processed_count += 1

        if i < total_links_to_process and len(results) < max_articles:
            time.sleep(0.4)

    if results:
        df = pd.DataFrame(results)
        print(f"\n✅ Scraping selesai!")
        print(f"   • Artikel diperiksa: {processed_count}")
        print(f"   • Artikel dengan keyword di judul: {len(results)}")
        if len(results) < max_articles:
            print(f"   ⚠️  Hanya ditemukan {len(results)} artikel dengan keyword '{keyword}' di judul dari {max_articles} yang diminta.")
        return df
    else:
        print("❌ Tidak ada data yang berhasil diambil")
        print(f"💡 Tidak ada artikel yang judulnya mengandung keyword '{keyword}'")
        return pd.DataFrame()

def save_to_csv(dataframe, keyword):
    if not dataframe.empty:
        print("\n🛠️  Memulai proses pembersihan data sebelum penyimpanan...")
        cleaned_dataframe = clean_dataframe(dataframe.copy())
        print("🛠️  Proses pembersihan data selesai.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"berita_radarsurabaya_{keyword.replace(' ', '_')}_{timestamp}.csv"
        cleaned_dataframe.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 Data disimpan ke: {filename}")
        return filename
    return None

def main():
    print("🎓 PROGRAM SCRAPING BERITA RADAR SURABAYA")
    print("👨‍🏫 Dibuat oleh Pradipta Deska Pryanda")
    print("🔧 Diperbaiki dan dikembangkan oleh Dosen Data Mining")
    print("📊 Untuk keperluan riset")
    print("🔍 MODIFIKASI: Hanya scrape artikel yang judulnya mengandung keyword")
    print("=" * 70)

    while True:
        keyword = input("\n🔍 Masukkan keyword pencarian berita: ").strip()
        if keyword:
            break
        print("❌ Keyword tidak boleh kosong!")

    while True:
        try:
            max_articles = input("📊 Jumlah maksimal artikel (default 5, maks 600): ").strip()
            if not max_articles:
                max_articles = 5
                break
            max_articles = int(max_articles)
            if 1 <= max_articles <= 600:
                break
            else:
                print("❌ Masukkan angka antara 1-600")
        except ValueError:
            print("❌ Masukkan angka yang valid!")

    print(f"\n📝 Keyword yang akan dicari: '{keyword}'")
    print(f"📈 Maksimal artikel yang akan diambil: {max_articles}")
    print(f"🎯 Kriteria: Hanya artikel yang JUDUL-nya mengandung '{keyword}' yang akan di-scrape")

    try:
        df_results = scrape_radar_news(keyword, max_articles)
        if not df_results.empty:
            print("\n" + "=" * 70)
            print("📊 HASIL SCRAPING (Preview 10 baris pertama):")
            print("=" * 70)
            print(df_results.head(10).to_string(index=False, max_colwidth=30))

            print(f"\n📈 Statistik:")
            print(f"   • Total artikel dengan keyword di judul: {len(df_results)}")
            print(f"   • Artikel dengan link valid: {df_results['link_berita'].apply(lambda x: re.match(r'^https?://', str(x)) is not None).sum()}")
            print(f"   • Artikel dengan konten: {df_results['detail_konten'].apply(lambda x: len(str(x).strip()) > 50).sum()}")

            filename = save_to_csv(df_results, keyword)
            if filename:
                print(f"✅ File berhasil disimpan!")

            print("\n📄 PREVIEW DETAIL KONTEN (3 Artikel Pertama):")
            print("=" * 70)
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
            print("   • Pastikan keyword yang dimasukkan ada di judul berita")
            print("   • Periksa koneksi internet")
            print("   • Coba keyword lain yang lebih umum")
    except KeyboardInterrupt:
        print("\n⚠️  Program dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Terjadi error: {e}")
        print("💡 Silakan coba lagi atau hubungi developer")

    print("\n👋 Terima kasih telah menggunakan program ini!")
    print("📚 Gunakan data dengan bijak dan sesuai etika riset")

if __name__ == "__main__":
    main()