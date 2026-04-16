import time
import re

from django.core.management.base import BaseCommand
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from books.models import Book


class Command(BaseCommand):
    help = 'Scrape audiobooks from Audible India'

    CATEGORIES = [
        {"name": "mystery_thriller", "node": "21881896031"},
        {"name": "true_crime", "node": "21881891031"},
        {"name": "biographies", "node": "21881789031"},
        {"name": "religion", "node": "21881911031"},
        {"name": "self_improvement", "node": "21881925031"},
        {"name": "romance", "node": "21881899031"},
        {"name": "fantasy", "node": "21881897031"},
        {"name": "science_fiction", "node": "21881901031"},
        {"name": "history", "node": "21881892031"},
        {"name": "politics", "node": "21881938031"},
        {"name": "health", "node": "21881888031"},
        {"name": "sports", "node": "21881914031"},
        {"name": "technology", "node": "21881955031"},
        {"name": "psychology", "node": "21881942031"},
        {"name": "business", "node": "21881921031"},
    ]

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=50)
        parser.add_argument('--category', type=str, default=None)
        parser.add_argument('--headful', action='store_true', default=False)

    def handle(self, *args, **options):
        limit = options['limit']
        headful = options['headful']
        
        if options['category']:
            categories = [c for c in self.CATEGORIES if c['name'] == options['category']]
            if not categories:
                self.stdout.write(f'Category not found: {options["category"]}')
                return
        else:
            categories = [c for c in self.CATEGORIES if c['node']]

        if limit < len(categories) * 50:
            limit = len(categories) * 50
            self.stdout.write(f'Adjusted limit to {limit} for {len(categories)} categories')

        self.stdout.write(f'Scraping up to {limit} books from {len(categories)} categories')
        
        driver = self._get_driver(headful)
        total = 0
        
        try:
            for cat in categories:
                if total >= limit:
                    break
                remaining = limit - total
                self.stdout.write(f'\n--- {cat["name"]} ({remaining} remaining) ---')
                count = self._scrape_category(driver, cat, remaining)
                total += count

            self.stdout.write(self.style.SUCCESS(f'Done. Total: {total} books saved.'))
            
        finally:
            try:
                driver.quit()
            except:
                pass

    def _get_driver(self, headful):
        options = uc.ChromeOptions()
        if not headful:
            options.add_argument('--headless=new')
        else:
            options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1400,2000')
        
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(25)
        return driver

    def _scrape_category(self, driver, category, limit):
        node = category['node']
        name = category['name']
        page = 1
        count = 0

        while count < limit:
            url = f'https://www.audible.in/search?node={node}&pageSize=50&page={page}'
            self.stdout.write(f'Page {page}...')
            
            try:
                driver.get(url)
            except:
                self.stdout.write(f'Page load timeout, skipping page {page}')
                break
            
            time.sleep(2.5)
            
            if 'captcha' in driver.page_source.lower() or 'blocked' in driver.page_source.lower():
                self.stdout.write('Captcha or blocking detected, skipping category')
                break
            
            cards = self._scrape_page(driver, name)
            
            if not cards:
                self.stdout.write(f'No cards found on page {page}, stopping')
                # Save page source for debug
                with open(f'debug_{name}_page{page}.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source[:50000])
                break
            
            for card in cards:
                if count >= limit:
                    break
                if self._save_book(card):
                    count += 1
                    if count % 10 == 0:
                        self.stdout.write(f'Saved {count}/{limit} books...')
            
            page += 1
            time.sleep(0.8)

        self.stdout.write(f'{name}: {count} books saved')
        return count

    def _scrape_page(self, driver, category_name):
        cards = []
        items = driver.find_elements(By.CSS_SELECTOR, 'li.productListItem')
        
        for item in items:
            card = self._parse_card(item, category_name)
            if card and card.get('title'):
                cards.append(card)
        
        return cards

    def _parse_card(self, item, category_name):
        title = ''
        author = ''
        book_url = ''
        cover_url = ''
        rating_average = None
        rating_count = None
        description = None

        try:
            title_link = item.find_element(By.CSS_SELECTOR, 'h3 a[href*="/pd/"]')
            title = title_link.text.strip()
            book_url = self.make_absolute_url(title_link.get_attribute('href'))
        except:
            pass
        if not title:
            return None

        try:
            author_item = item.find_element(By.CSS_SELECTOR, 'li.authorLabel')
            author_link = author_item.find_element(By.CSS_SELECTOR, 'a.bc-link')
            author = author_link.text.strip()
        except:
            pass

        try:
            rating_item = item.find_element(By.CSS_SELECTOR, 'li.ratingsLabel')
            rating_span = rating_item.find_element(By.CSS_SELECTOR, 'span.bc-text')
            rating_text = rating_span.text.strip()
            rating_average = self.parse_float(rating_text)
            
            spans = rating_item.find_elements(By.CSS_SELECTOR, 'span.bc-text')
            for span in spans:
                text = span.text.strip()
                if 'rating' in text.lower():
                    rating_count = self.parse_int(text)
                    break
        except:
            pass

        try:
            img = item.find_element(By.CSS_SELECTOR, 'picture img, img')
            cover_url = img.get_attribute('src') or img.get_attribute('data-lazy-src')
            if cover_url and cover_url.startswith('//'):
                cover_url = 'https:' + cover_url
        except:
            pass

        olid = self.extract_audible_id(book_url)

        return {
            'title': title,
            'author': author or None,
            'description': description,
            'book_url': book_url,
            'cover_url': cover_url or None,
            'publish_year': None,
            'first_publish_year': None,
            'rating_average': rating_average,
            'rating_count': rating_count,
            'subjects': category_name,
            'olid': olid,
        }

    def _save_book(self, card):
        if not card.get('book_url'):
            return False
        
        try:
            Book.objects.update_or_create(
                book_url=card['book_url'],
                defaults=card
            )
            return True
        except Exception as e:
            self.stdout.write(f'Failed to save: {card.get("title", "unknown")}')
            return False

    def make_absolute_url(self, href):
        if not href:
            return ''
        if href.startswith('http'):
            return href
        if href.startswith('//'):
            return 'https:' + href
        if href.startswith('/'):
            return 'https://www.audible.in' + href
        return 'https://www.audible.in/' + href

    def extract_audible_id(self, url):
        if not url:
            return ''
        match = re.search(r'/pd/([^/?]+)', url)
        if match:
            return match.group(1)
        return ''

    def parse_int(self, text):
        if not text:
            return None
        nums = re.findall(r'[\d,]+', text)
        for n in nums:
            try:
                return int(n.replace(',', ''))
            except:
                continue
        return None

    def parse_float(self, text):
        if not text:
            return None
        nums = re.findall(r'[\d.]+', text)
        for n in nums:
            try:
                return float(n)
            except:
                continue
        return None