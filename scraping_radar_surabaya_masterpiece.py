"""
Scraping Berita Radar Surabaya - Program untuk mengumpulkan data berita
Dibuat oleh: Pradipta Deska Pryanda
Tanggal: 2024
MASTERPIECE VERSION: Solusi ultimate dengan multiple strategies dan anti-detection canggih
"""

# Import library yang diperlukan
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import quote, urljoin, unquote, urlparse, parse_qs
import re
from datetime import datetime
import json
import base64

# Untuk menghindari error SSL di Colab
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Konfigurasi global
RADAR_BASE = "https://radarsurabaya.jawapos.com"

# Daftar User Agents premium untuk rotasi
PREMIUM_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
]

# Referer pool untuk natural browsing
REFERERS = [
    'https://www.google.com/',
    'https://www.google.co.id/',
    'https://www.bing.com/',
    'https://duckduckgo.com/',
    'https://search.yahoo.com/',
    'https://radarsurabaya.jawapos.com/'
]

def create_stealth_session():
    """Buat session dengan stealth mode canggih"""
    session = requests.Session()
    
    # Pilih user agent dan referer secara random
    user_agent = random.choice(PREMIUM_USER_AGENTS)
    referer = random.choice(REFERERS)
    
    # Headers yang sangat natural dan lengkap
    session.headers.update({
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7,ms;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Referer': referer,
        'Origin': referer.rstrip('/'),
        'X-Requested-With': 'XMLHttpRequest' if random.random() > 0.7 else None
    })
    
    # Set cookies yang natural
    session.cookies.update({
        'session_token': base64.b64encode(f'sess_{random.randint(100000, 999999)}'.encode()).decode()[:16],
        'visitor_id': f'vis_{random.randint(1000000, 9999999)}',
        'last_visit': str(int(time.time() - random.randint(3600, 86400))),
        'user_pref': 'id-ID',
        '_ga': f'GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}',
        '_gid': f'GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}'
    })
    
    return session

def human_delay(min_seconds=2, max_seconds=8):
    """Delay yang meniru perilaku manusia dengan variasi natural"""
    base_delay = random.uniform(min_seconds, max_seconds)
    
    # Tambah variasi micro-delay untuk meniru gerakan mouse/keyboard
    micro_delays = [random.uniform(0.1, 0.3) for _ in range(random.randint(2, 5))]
    
    # Simulasi reading time
    if random.random() > 0.8:  # 20% chance untuk "reading" delay
        base_delay += random.uniform(3, 10)
    
    total_delay = base_delay + sum(micro_delays)
    time.sleep(total_delay)

def extract_real_url(problematic_url):
    """Ekstrak URL asli dari URL bermasalah dengan berbagai metode"""
    try:
        # Method 1: Fix missing protocol
        if problematic_url.startswith('//'):
            problematic_url = 'https:' + problematic_url
        
        # Method 2: Parse DuckDuckGo redirect
        if 'duckduckgo.com/l/' in problematic_url:
            parsed = urlparse(problematic_url)
            query_params = parse_qs(parsed.query)
            if 'uddg' in query_params:
                real_url = unquote(query_params['uddg'][0])
                return real_url
        
        # Method 3: Parse Bing redirect  
        if 'bing.com' in problematic_url and '/ck/' in problematic_url:
            # Extract from Bing click tracking
            if 'u=' in problematic_url:
                url_part = problematic_url.split('u=')[1].split('&')[0]
                real_url = unquote(url_part)
                return real_url
        
        # Method 4: Direct URL validation
        if 'radarsurabaya.jawapos.com' in problematic_url:
            # Ensure proper protocol
            if not problematic_url.startswith('http'):
                problematic_url = 'https://' + problematic_url.lstrip('/')
            return problematic_url
        
        return problematic_url
        
    except Exception as e:
        print(f"   ⚠️ URL extraction error: {e}")
        return problematic_url

def advanced_get_page(url, session=None, max_attempts=5):
    """Advanced page fetching dengan multiple strategies"""
    if session is None:
        session = create_stealth_session()
    
    strategies = [
        {'name': 'Direct Request', 'method': 'direct'},
        {'name': 'With Random Referer', 'method': 'referer'},
        {'name': 'Stealth Mode', 'method': 'stealth'},
        {'name': 'Mobile Mode', 'method': 'mobile'},
        {'name': 'Bypass Mode', 'method': 'bypass'}
    ]
    
    for attempt, strategy in enumerate(strategies[:max_attempts], 1):
        try:
            print(f"   🔄 Strategy {attempt}: {strategy['name']}")
            
            # Reset session untuk setiap strategy
            if attempt > 1:
                session = create_stealth_session()
            
            if strategy['method'] == 'direct':
                response = session.get(url, timeout=30, verify=False, allow_redirects=True)
                
            elif strategy['method'] == 'referer':
                session.headers.update({
                    'Referer': random.choice(REFERERS),
                    'X-Forwarded-For': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'
                })
                human_delay(3, 6)
                response = session.get(url, timeout=30, verify=False, allow_redirects=True)
                
            elif strategy['method'] == 'stealth':
                session.headers.update({
                    'User-Agent': random.choice(PREMIUM_USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                })
                human_delay(4, 8)
                response = session.get(url, timeout=30, verify=False, allow_redirects=True)
                
            elif strategy['method'] == 'mobile':
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'sec-ch-ua-mobile': '?1'
                })
                human_delay(2, 5)
                response = session.get(url, timeout=30, verify=False, allow_redirects=True)
                
            else:  # bypass mode
                session.headers.update({
                    'User-Agent': random.choice(PREMIUM_USER_AGENTS),
                    'Referer': 'https://www.google.com/search?q=radar+surabaya',
                    'X-Real-IP': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}',
                    'X-Forwarded-Proto': 'https'
                })
                human_delay(5, 10)
                response = session.get(url, timeout=30, verify=False, allow_redirects=True)
            
            response.raise_for_status()
            print(f"   ✅ Success with {strategy['name']}")
            return response.text
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 'Unknown'
            print(f"   ❌ {strategy['name']} failed: HTTP {status_code}")
            if attempt < max_attempts:
                human_delay(3, 8)
            continue
            
        except Exception as e:
            print(f"   ❌ {strategy['name']} failed: {str(e)[:100]}")
            if attempt < max_attempts:
                human_delay(2, 5)
            continue
    
    print(f"   💥 All strategies failed for {url}")
    return None

def search_with_multiple_engines(keyword, max_results=30):
    """Pencarian dengan multiple search engines"""
    all_results = []
    session = create_stealth_session()
    
    # Google Search
    try:
        print("🔍 Mencoba Google Search...")
        google_query = f"site:radarsurabaya.jawapos.com {keyword}"
        google_url = f"https://www.google.com/search?q={quote(google_query)}&num={max_results}"
        
        html = advanced_get_page(google_url, session)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Multiple selectors untuk Google results
            selectors = [
                'div.g h3 a', 'h3 a', 'a h3', 'div.yuRUbf a',
                'div[data-ved] a', 'div.g a[href*="radarsurabaya"]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # Clean Google tracking URLs
                    if '/url?q=' in href:
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        actual_url = unquote(actual_url)
                        href = actual_url
                    
                    if 'radarsurabaya.jawapos.com' in href and len(title) > 10:
                        all_results.append({
                            'title': title,
                            'url': href,
                            'date_from_list': None,
                            'source': 'Google'
                        })
            
            print(f"   ✅ Google: {len([r for r in all_results if r['source'] == 'Google'])} results")
    except Exception as e:
        print(f"   ❌ Google Search error: {e}")
    
    # Bing Search
    try:
        print("🔍 Mencoba Bing Search...")
        bing_query = f"site:radarsurabaya.jawapos.com {keyword}"
        bing_url = f"https://www.bing.com/search?q={quote(bing_query)}&count={max_results}"
        
        html = advanced_get_page(bing_url, session)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Bing result selectors
            for link in soup.select('li.b_algo h2 a, .b_title a, h2 a'):
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                if 'radarsurabaya.jawapos.com' in href and len(title) > 10:
                    all_results.append({
                        'title': title,
                        'url': href,
                        'date_from_list': None,
                        'source': 'Bing'
                    })
            
            bing_count = len([r for r in all_results if r['source'] == 'Bing'])
            print(f"   ✅ Bing: {bing_count} results")
    except Exception as e:
        print(f"   ❌ Bing Search error: {e}")
    
    # Yahoo Search (bonus)
    try:
        print("🔍 Mencoba Yahoo Search...")
        yahoo_query = f"site:radarsurabaya.jawapos.com {keyword}"
        yahoo_url = f"https://search.yahoo.com/search?p={quote(yahoo_query)}&n={max_results}"
        
        html = advanced_get_page(yahoo_url, session)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            for link in soup.select('h3 a, .title a'):
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                if 'radarsurabaya.jawapos.com' in href and len(title) > 10:
                    all_results.append({
                        'title': title,
                        'url': href,
                        'date_from_list': None,
                        'source': 'Yahoo'
                    })
            
            yahoo_count = len([r for r in all_results if r['source'] == 'Yahoo'])
            print(f"   ✅ Yahoo: {yahoo_count} results")
    except Exception as e:
        print(f"   ❌ Yahoo Search error: {e}")
    
    # Remove duplicates
    unique_results = []
    seen_urls = set()
    
    for result in all_results:
        clean_url = extract_real_url(result['url'])
        if clean_url not in seen_urls and 'radarsurabaya.jawapos.com' in clean_url:
            result['url'] = clean_url
            unique_results.append(result)
            seen_urls.add(clean_url)
    
    print(f"📊 Total unique results: {len(unique_results)}")
    return unique_results

def extract_article_content(article_url, session):
    """Ekstrak konten artikel dengan advanced parsing"""
    html = advanced_get_page(article_url, session)
    if not html:
        return None, None, None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract title
    title = extract_title_advanced(soup)
    
    # Extract date  
    date_published = extract_date_advanced(soup)
    
    # Extract content
    content = extract_content_advanced(soup)
    
    return title, date_published, content

def extract_title_advanced(soup):
    """Ekstrak judul dengan metode advanced"""
    title_selectors = [
        'h1.article__title', 'h1.post__title', 'h1.entry-title',
        'h1.title', '.article-title h1', '.post-title h1',
        'article h1', '.content h1', 'h1',
        'meta[property="og:title"]', 'title'
    ]
    
    for selector in title_selectors:
        try:
            if selector.startswith('meta') or selector == 'title':
                element = soup.select_one(selector)
                if element:
                    content = element.get('content') if element.name == 'meta' else element.get_text()
                    if content and len(content.strip()) > 10:
                        return clean_text(content.strip())
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:
                        return clean_text(text)
        except:
            continue
    
    return "Judul tidak ditemukan"

def extract_date_advanced(soup):
    """Ekstrak tanggal dengan metode advanced"""
    
    # Method 1: Time elements
    for time_elem in soup.find_all('time'):
        if time_elem.has_attr('datetime'):
            return time_elem['datetime']
        if time_elem.has_attr('pubdate'):
            return time_elem.get_text(strip=True)
    
    # Method 2: Meta tags
    meta_selectors = [
        'meta[property="article:published_time"]',
        'meta[name="pubdate"]', 'meta[name="publishdate"]',
        'meta[name="date"]', 'meta[property="article:modified_time"]'
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
        '.publish-date', '.published', '.timestamp', '.article-date',
        '.post-meta time', '.entry-meta time'
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
    
    # Method 4: Regex patterns
    body_text = soup.get_text()
    date_patterns = [
        r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4}\s*,?\s*\d{1,2}:\d{2}\s*(?:WIB|WITA|WIT)?)',
        r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}\s*\d{1,2}:\d{2})',
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

def extract_content_advanced(soup):
    """Ekstrak konten dengan metode advanced"""
    
    # Content selectors dengan prioritas
    content_selectors = [
        'div.article__content', 'div.post__content', 'article .content',
        'div.entry-content', 'div.content-detail', 'div.article-content',
        '.article-body', '.post-body', '.content-body', '.article-text',
        'div[class*="content"]', 'div[class*="article"]', 'article'
    ]
    
    for selector in content_selectors:
        try:
            element = soup.select_one(selector)
            if element and len(element.get_text(strip=True)) > 100:
                
                # Remove unwanted elements
                unwanted_tags = [
                    'script', 'style', 'nav', 'aside', 'header', 'footer',
                    'noscript', 'figure', 'iframe', 'form', 'advertisement'
                ]
                
                unwanted_classes = re.compile(
                    r'.*(ads|advert|promo|related|widget|sidebar|footer|breadcrumb|'
                    r'taglist|share|social|comment|nav|menu|advertisement|banner).*', 
                    re.I
                )
                
                # Remove unwanted tags
                for tag in unwanted_tags:
                    for elem in element.find_all(tag):
                        elem.decompose()
                
                # Remove unwanted classes
                for elem in element.find_all(class_=unwanted_classes):
                    elem.decompose()
                
                content_text = element.get_text(separator=' ', strip=True)
                if len(content_text) > 100:
                    return clean_text(content_text)
        except:
            continue
    
    # Fallback to body
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
    """Bersihkan teks dengan advanced cleaning"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep Indonesian characters
    text = re.sub(r'[^\w\s.,!?;:()\-\'"àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]', ' ', text)
    
    # Remove multiple punctuation
    text = re.sub(r'[.]{3,}', '...', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    return text.strip()

def is_content_relevant(title, content, keyword):
    """Advanced relevance checking"""
    if not title or not content or not keyword:
        return False
    
    # Normalize text
    title_lower = title.lower().strip()
    content_lower = content.lower().strip()
    keyword_lower = keyword.lower().strip()
    
    # Combined text for searching
    full_text = f"{title_lower} {content_lower}"
    
    # Exact keyword match (highest priority)
    if keyword_lower in full_text:
        return True
    
    # Word-by-word matching
    keyword_words = [w for w in keyword_lower.split() if len(w) > 2]
    if not keyword_words:
        return False
    
    # Check individual words
    matches = 0
    for word in keyword_words:
        if word in full_text:
            matches += 1
    
    # Relevance threshold: 70% of words must match
    relevance_threshold = len(keyword_words) * 0.7
    if matches >= relevance_threshold:
        return True
    
    # Check variations (Indonesian language)
    variations = []
    for word in keyword_words:
        if len(word) > 3:
            variations.extend([
                word, f"ber{word}", f"me{word}", f"{word}an", 
                f"{word}nya", f"ke{word}an", f"per{word}an"
            ])
    
    for variation in variations:
        if variation in full_text:
            return True
    
    return False

def calculate_relevance_score(title, content, keyword):
    """Calculate advanced relevance score"""
    if not title or not content or not keyword:
        return 0
    
    score = 0
    title_lower = title.lower()
    content_lower = content.lower()
    keyword_lower = keyword.lower()
    
    # Exact keyword in title (highest weight)
    if keyword_lower in title_lower:
        score += 50
    
    # Exact keyword in content
    if keyword_lower in content_lower:
        score += 20
    
    # Individual words
    keyword_words = keyword_lower.split()
    for word in keyword_words:
        if len(word) > 2:
            # Word in title
            if word in title_lower:
                score += 15
            
            # Word frequency in content
            word_count = content_lower.count(word)
            score += min(word_count * 3, 15)  # Max 15 points per word
    
    # Bonus for keyword density
    if len(content_lower) > 0:
        keyword_density = content_lower.count(keyword_lower) / len(content_lower.split()) * 1000
        score += min(keyword_density * 10, 20)
    
    return int(score)

def scrape_radar_news_ultimate(keyword, target_articles):
    """Ultimate scraping function dengan semua strategy terbaik"""
    print("=" * 80)
    print("🚀 RADAR SURABAYA SCRAPER MASTERPIECE")
    print(f"🎯 KEYWORD: '{keyword}' | TARGET: {target_articles} artikel relevan")
    print("=" * 80)
    
    # Step 1: Multi-engine search
    print("\n🔍 FASE 1: PENCARIAN MULTI-ENGINE")
    print("-" * 50)
    
    all_links = search_with_multiple_engines(keyword, max_results=50)
    
    if not all_links:
        print("❌ Tidak ditemukan hasil dari search engines")
        return pd.DataFrame()
    
    print(f"✅ Total kandidat artikel: {len(all_links)}")
    
    # Step 2: Process articles
    print(f"\n📝 FASE 2: PROCESSING ARTIKEL")
    print(f"🎯 Target: {target_articles} artikel relevan")
    print("-" * 50)
    
    session = create_stealth_session()
    results = []
    processed = 0
    
    for i, link in enumerate(all_links, 1):
        if len(results) >= target_articles:
            print(f"\n🎉 TARGET TERCAPAI! {target_articles} artikel relevan ditemukan!")
            break
        
        print(f"\n[{i}/{len(all_links)}] Processing: {link['title'][:60]}...")
        
        try:
            # Extract article details
            title, date, content = extract_article_content(link['url'], session)
            
            if not title or not content:
                print("   ⚠️ Gagal ekstrak konten")
                processed += 1
                continue
            
            # Check relevance
            if is_content_relevant(title, content, keyword):
                score = calculate_relevance_score(title, content, keyword)
                
                article_data = {
                    'judul_berita': title,
                    'link_berita': link['url'],
                    'tanggal_rilis': date,
                    'detail_konten': content,
                    'source_engine': link['source'],
                    'relevance_score': score
                }
                
                results.append(article_data)
                print(f"   ✅ RELEVAN #{len(results)} (skor: {score}) - {link['source']}")
            else:
                print(f"   ❌ Tidak relevan dengan '{keyword}'")
            
            processed += 1
            
            # Human-like delay
            human_delay(1, 3)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            processed += 1
            continue
    
    # Step 3: Results processing
    if results:
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Remove score column for final output
        for result in results:
            del result['relevance_score']
            del result['source_engine']
        
        df = pd.DataFrame(results)
        
        print(f"\n" + "=" * 80)
        print("🎊 SCRAPING BERHASIL!")
        print(f"📊 Artikel diproses: {processed}")
        print(f"✅ Artikel relevan: {len(results)}")
        print(f"🎯 Success rate: {len(results)/processed*100:.1f}%")
        print("=" * 80)
        
        return df
    else:
        print(f"\n❌ TIDAK ADA ARTIKEL RELEVAN DITEMUKAN")
        print(f"📊 Total diproses: {processed}")
        print("💡 Tips: Coba keyword yang lebih umum atau spesifik")
        return pd.DataFrame()

def clean_dataframe_ultimate(df):
    """Ultimate dataframe cleaning"""
    if df.empty:
        return df
    
    print("\n🛠️ MEMBERSIHKAN DATA...")
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['link_berita'], keep='first')
    
    # Clean text columns
    df['judul_berita'] = df['judul_berita'].apply(lambda x: clean_text(str(x)))
    df['detail_konten'] = df['detail_konten'].apply(lambda x: clean_text(str(x)))
    
    # Ensure minimum content length
    df = df[df['detail_konten'].apply(lambda x: len(str(x)) > 100)]
    
    # Fix missing dates
    df['tanggal_rilis'] = df['tanggal_rilis'].apply(
        lambda x: str(x) if x and str(x) != 'nan' else "Tanggal tidak ditemukan"
    )
    
    print(f"✅ Data dibersihkan. Artikel final: {len(df)}")
    return df

def save_to_csv_ultimate(dataframe, keyword):
    """Ultimate CSV saving"""
    if not dataframe.empty:
        cleaned_df = clean_dataframe_ultimate(dataframe)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"radar_surabaya_{keyword.replace(' ', '_')}_{timestamp}.csv"
        
        cleaned_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 Data disimpan: {filename}")
        return filename
    return None

def main():
    print("🎓 RADAR SURABAYA SCRAPER MASTERPIECE")
    print("👨‍🏫 Created by Pradipta Deska Pryanda")
    print("🚀 Ultimate Version - Anti-Detection + Multi-Engine + Advanced Processing")
    print("=" * 80)

    # Input keyword
    while True:
        keyword = input("\n🔍 Masukkan keyword pencarian: ").strip()
        if keyword:
            break
        print("❌ Keyword tidak boleh kosong!")

    # Input target articles
    while True:
        try:
            target = input("📊 Jumlah artikel relevan (default 5, max 25): ").strip()
            if not target:
                target = 5
                break
            target = int(target)
            if 1 <= target <= 25:
                break
            else:
                print("❌ Masukkan angka antara 1-25")
        except ValueError:
            print("❌ Masukkan angka yang valid!")

    print(f"\n📝 Keyword: '{keyword}'")
    print(f"🎯 Target: {target} artikel relevan")
    print("🚀 Memulai scraping dengan teknologi canggih...")

    try:
        start_time = time.time()
        df_results = scrape_radar_news_ultimate(keyword, target)
        end_time = time.time()
        
        if not df_results.empty:
            # Statistics
            print(f"\n📈 STATISTIK FINAL:")
            print(f"   ⏱️  Waktu eksekusi: {end_time - start_time:.1f} detik")
            print(f"   📊 Artikel ditemukan: {len(df_results)}")
            print(f"   🎯 Target tercapai: {'✅ YA' if len(df_results) >= target else '⚠️ SEBAGIAN'}")
            
            # Keyword analysis
            keyword_lower = keyword.lower()
            in_title = sum(1 for _, row in df_results.iterrows() 
                          if keyword_lower in str(row['judul_berita']).lower())
            in_content = sum(1 for _, row in df_results.iterrows() 
                           if keyword_lower in str(row['detail_konten']).lower())
            
            print(f"   🎯 Keyword di judul: {in_title}/{len(df_results)}")
            print(f"   📝 Keyword di konten: {in_content}/{len(df_results)}")
            
            # Save to CSV
            filename = save_to_csv_ultimate(df_results, keyword)
            
            # Preview results
            print(f"\n📄 PREVIEW HASIL (Top 3):")
            print("=" * 60)
            
            for idx, (_, row) in enumerate(df_results.head(3).iterrows(), 1):
                print(f"\n{idx}. 📋 {row['judul_berita']}")
                print(f"   📅 {row['tanggal_rilis']}")
                print(f"   🔗 {row['link_berita']}")
                
                # Content preview
                content_preview = str(row['detail_konten'])[:250]
                if len(str(row['detail_konten'])) > 250:
                    content_preview += "..."
                print(f"   📝 {content_preview}")
                
                # Keyword highlighting
                title_has_keyword = keyword_lower in str(row['judul_berita']).lower()
                content_has_keyword = keyword_lower in str(row['detail_konten']).lower()
                
                found_in = []
                if title_has_keyword:
                    found_in.append("judul")
                if content_has_keyword:
                    found_in.append("konten")
                
                if found_in:
                    print(f"   🎯 Keyword '{keyword}' ditemukan di: {', '.join(found_in)}")
                
                print("-" * 40)
            
            if filename:
                print(f"\n✅ SUKSES! File tersimpan: {filename}")
                
        else:
            print("\n💡 SARAN UNTUK HASIL LEBIH BAIK:")
            print("   • Gunakan keyword yang lebih umum (contoh: 'ekonomi', 'politik')")
            print("   • Periksa ejaan keyword")
            print("   • Coba variasi keyword (sinonim)")
            print("   • Gunakan keyword dalam Bahasa Indonesia")
    
    except KeyboardInterrupt:
        print("\n⚠️ Program dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Terjadi error: {e}")
        import traceback
        print("🔧 Debug info:")
        traceback.print_exc()

    print("\n🎊 TERIMA KASIH TELAH MENGGUNAKAN RADAR SURABAYA SCRAPER!")
    print("📚 Gunakan data dengan bijak dan etis")

if __name__ == "__main__":
    main()