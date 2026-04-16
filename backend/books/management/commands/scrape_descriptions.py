import time
import re

from django.core.management.base import BaseCommand
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from books.models import Book


class Command(BaseCommand):
    help = 'Scrape descriptions from Audible detail pages'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--headful', action='store_true', default=False)

    def handle(self, *args, **options):
        limit = options['limit']
        headful = options['headful']
        
        books = Book.objects.filter(description__isnull=True)
        if limit:
            books = books[:limit]
        
        total = books.count()
        self.stdout.write(f'Scraping {total} descriptions')
        
        if total == 0:
            self.stdout.write('All books have descriptions')
            return
        
        driver = self._get_driver(headful)
        updated = 0
        
        try:
            for i, book in enumerate(books):
                self.stdout.write(f'{i+1}/{total}...')
                url = book.book_url.split('?')[0]
                desc = self._get_description(driver, url, book.title)
                if desc:
                    book.description = desc
                    book.save(update_fields=['description'])
                    updated += 1
                time.sleep(0.3)
            
            self.stdout.write(self.style.SUCCESS(f'Updated {updated}/{total}'))
            
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
        driver.set_page_load_timeout(15)
        return driver

    def _get_description(self, driver, url, title):
        try:
            driver.get(url)
            time.sleep(1.2)
            
            try:
                el = driver.find_element(By.CSS_SELECTOR, 'adbl-text-block[slot="summary"]')
                text = el.get_attribute('innerHTML')
                if text and len(text) > 100:
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = re.sub(r'\s+', ' ', text)
                    text = text.strip()
                    if 'PRAISE' in text.upper():
                        text = text.split('PRAISE')[0].strip()
                    return text[:2000]
            except:
                pass
            
            try:
                scripts = driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
                for script in scripts:
                    text = script.get_attribute('innerHTML')
                    if '"description"' in text and title[:5].lower() in text.lower():
                        match = re.search(r'"description"\s*:\s*"(.+?)"', text, re.DOTALL)
                        if match:
                            desc = match.group(1)
                            desc = re.sub(r'<[^>]+>', '', desc)
                            desc = desc.strip()[:2000]
                            if len(desc) > 50:
                                return desc
            except:
                pass
            
            return ''
        except:
            return ''