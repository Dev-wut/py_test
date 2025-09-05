#!/usr/bin/env python3
"""
PriceZA Hot Deals Scraper
สคริปต์สำหรับดึงข้อมูลสินค้าฮอตดีลจาก priceza.com
(ปรับปรุงให้ใช้ Selenium เพื่อโหลดข้อมูลแบบ Dynamic โดยการคลิกปุ่ม 'Load More')
"""

import json
import csv
from datetime import datetime
import time
import logging
from urllib.parse import urljoin
import re
from utils.logging import setup_logging
from database import insert_deals

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


# --- Logging Setup ---
setup_logging()

class PriceZAScraper:
    def __init__(self, config: dict, allowed_merchants=None):
        self.base_url = config["base_url"]
        self.selectors = config["selectors"]
        self.json_keys = config["json_keys"]
        self.hot_deals = []
        
        if allowed_merchants:
            self.allowed_merchants = [m.strip().upper() for m in allowed_merchants]
        else:
            self.allowed_merchants = []

        # --- ตั้งค่า Selenium WebDriver ---
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/5.0 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        try:
            logging.info("กำลังติดตั้ง/ตั้งค่า ChromeDriver...")
            service = ChromeService('/usr/local/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.info("ChromeDriver ตั้งค่าสำเร็จ")
        except Exception as e:
            logging.error(f"เกิดข้อผิดพลาดตอนตั้งค่า Selenium WebDriver: {e}")
            self.driver = None

    def _find_element_with_selector(self, parent_element, selector_detail: dict, find_all=False):
        tag = selector_detail.get("tag")
        class_name = selector_detail.get("class")
        element_id = selector_detail.get("id")
        attrs = selector_detail.get("attrs")

        find_args = {}
        if class_name: find_args["class_"] = class_name
        if element_id: find_args["id"] = element_id
        if attrs: find_args["attrs"] = attrs

        if find_all:
            return parent_element.find_all(tag, **find_args)
        else:
            return parent_element.find(tag, **find_args)

    def get_page_content_with_selenium(self, url):
        """
        ดึงเนื้อหาของหน้าเว็บด้วย Selenium และคลิกปุ่ม 'Load More' จนกว่าจะไม่มีปุ่มให้คลิก
        """
        if not self.driver:
            logging.error("WebDriver ไม่ได้ถูก khởi tạo, ไม่สามารถดึงข้อมูลได้")
            return None
            
        logging.info(f"กำลังดึงข้อมูลจาก: {url} ด้วย Selenium...")
        try:
            self.driver.get(url)
            time.sleep(3)  # รอให้หน้าเว็บโหลดครั้งแรก

            logging.info("กำลังค้นหาและคลิกปุ่ม 'Load More'...")
            click_count = 0
            while True:
                try:
                    # Use By.CLASS_NAME for Selenium find_element
                    load_more_button = self.driver.find_element(By.CLASS_NAME, self.selectors["load_more_button"]["class"])
                    self.driver.execute_script("arguments[0].click();", load_more_button)
                    click_count += 1
                    logging.info(f"คลิกปุ่ม 'Load More' ครั้งที่ {click_count}")
                    time.sleep(2)  # รอให้ข้อมูลใหม่โหลด
                except NoSuchElementException:
                    logging.info("ไม่พบปุ่ม 'Load More' แล้ว, โหลดข้อมูลสำเร็จ")
                    break
                except Exception as e:
                    logging.error(f"เกิดข้อผิดพลาดขณะพยายามคลิกปุ่ม 'Load More': {e}")
                    break

            return self.driver.page_source
        except Exception as e:
            logging.error(f"เกิดข้อผิดพลาดขณะใช้ Selenium ดึงข้อมูล: {e}")
            return None

    def close_driver(self):
        """ปิด WebDriver"""
        if self.driver:
            logging.info("กำลังปิด WebDriver...")
            self.driver.quit()
            logging.info("WebDriver ปิดเรียบร้อย")

    def parse_product_info(self, product_element):
        """
        แยกข้อมูลสินค้าจาก element (ปรับปรุงตาม HTML ที่ให้มา)
        """
        product_info = {
            self.json_keys['title']: '', self.json_keys['price']: '', self.json_keys['original_price']: '', self.json_keys['discount']: '',
            self.json_keys['image_url']: '', self.json_keys['product_url']: '', self.json_keys['merchant']: '',
            self.json_keys['merchant_image']: '', self.json_keys['rating']: '', self.json_keys['reviews_count']: ''
        }
        
        try:
            title_elem = self._find_element_with_selector(product_element, self.selectors['title'])
            if title_elem:
                product_info[self.json_keys['title']] = title_elem.get('title', '').replace('ราคา ', '').strip()

            original_price_elem = self._find_element_with_selector(product_element, self.selectors['original_price'])
            if original_price_elem:
                product_info[self.json_keys['original_price']] = original_price_elem.get_text(strip=True).replace('฿', '')

            price_elem = self._find_element_with_selector(product_element, self.selectors['price'])
            if price_elem:
                op_tag_to_remove = self._find_element_with_selector(price_elem, self.selectors['original_price'])
                if op_tag_to_remove:
                    op_tag_to_remove.extract() 
                product_info[self.json_keys['price']] = price_elem.get_text(strip=True).replace('฿', '')
            
            discount_elem = self._find_element_with_selector(product_element, self.selectors['discount'])
            if discount_elem:
                product_info[self.json_keys['discount']] = discount_elem.get_text(strip=True)
            
            img_elem = self._find_element_with_selector(product_element, self.selectors['image'])
            if img_elem:
                img_src = img_elem.get('data-original') or img_elem.get('src')
                if img_src:
                    product_info[self.json_keys['image_url']] = urljoin(self.base_url, img_src)
            
            merchant_img_elem = self._find_element_with_selector(product_element, self.selectors['merchant_image'])
            if merchant_img_elem:
                merchant_img_src = merchant_img_elem.get('data-original') or merchant_img_elem.get('src')
                if merchant_img_src:
                    product_info[self.json_keys['merchant_image']] = urljoin(self.base_url, merchant_img_src)
                    try:
                        merchant_name = merchant_img_src.split('/')[-1].split('.')[0]
                        merchant_name = re.sub(r'N\d+$', '', merchant_name, flags=re.IGNORECASE)
                        product_info[self.json_keys['merchant']] = merchant_name.strip().upper()
                    except Exception:
                        pass

            link_elem = self._find_element_with_selector(product_element, self.selectors['product_link'])
            if link_elem:
                product_info[self.json_keys['product_url']] = urljoin(self.base_url, link_elem['href'])
                if not product_info.get(self.json_keys['merchant']):
                    onmousedown_attr = link_elem.get('onmousedown', '')
                    match = re.search(r"addGAInteractionEvent\('MerchantProducts','([^']*)'\)", onmousedown_attr)
                    if match:
                        product_info[self.json_keys['merchant']] = match.group(1).strip().upper()
            
            if not product_info.get(self.json_keys['merchant']) and merchant_img_elem:
                merchant_alt = merchant_img_elem.get('alt')
                if merchant_alt and "logo" in merchant_alt.lower():
                    product_info[self.json_keys['merchant']] = merchant_alt.replace("logo", "").strip().upper()
            
            rating_elem = self._find_element_with_selector(product_element, self.selectors['rating'])
            if rating_elem:
                product_info[self.json_keys['rating']] = rating_elem.get_text(strip=True)
                review_match = re.search(r'\((\d+)\)', product_info[self.json_keys['rating']])
                if review_match:
                    product_info[self.json_keys['reviews_count']] = review_match.group(1)

        except Exception as e:
            logging.warning(f"เกิดข้อผิดพลาดในการแยกข้อมูลสินค้า: {e}")
        
        return product_info

    def scrape_hot_deals(self):
        """
        ดึงข้อมูลสินค้าฮอตดีลโดยใช้ Selenium
        """
        if self.allowed_merchants:
            logging.info(f"เริ่มดึงข้อมูลสินค้าฮอตดีล (กรองเฉพาะ: {', '.join(self.allowed_merchants)})")
        else:
            logging.info("เริ่มดึงข้อมูลสินค้าฮอตดีลด้วย Selenium (วิธีคลิกปุ่ม Load More)...")

        html_content = self.get_page_content_with_selenium(self.base_url)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        hot_deals_container = self._find_element_with_selector(soup, self.selectors["hot_deals_container"])
        
        if hot_deals_container:
            logging.info("พบส่วนฮอตดีล - เริ่มดึงข้อมูลสินค้า...")
            product_elements = self._find_element_with_selector(hot_deals_container, self.selectors["product_item"], find_all=True)
            logging.info(f"พบสินค้า {len(product_elements)} รายการ (หลังจากการคลิก 'Load More')")
            
            for i, product_elem in enumerate(product_elements, 1):
                product_info = self.parse_product_info(product_elem)
                if product_info.get(self.json_keys['title']) and product_info.get(self.json_keys['price']):
                    if not self.allowed_merchants or product_info.get(self.json_keys['merchant']) in self.allowed_merchants:
                        self.hot_deals.append(product_info)
                else:
                    logging.warning(f"ข้ามรายการที่ {i} เนื่องจากไม่มีข้อมูลสำคัญ (ชื่อหรือราคา)")
        
        else:
            logging.warning("ไม่พบส่วนฮอตดีลในหน้าเว็บหลังใช้ Selenium")
            
        logging.info(f"ดึงข้อมูลสำเร็จ: {len(self.hot_deals)} รายการ")
        return self.hot_deals

    def save_to_json(self, filename=None):
        """ส่วนนี้เหมือนเดิม"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"priceza_hot_deals_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_products': len(self.hot_deals),
                    'products': self.hot_deals
                }, f, ensure_ascii=False, indent=2)
            logging.info(f"บันทึกข้อมูล JSON สำเร็จ: {filename}")
            try:
                logging.info("กำลังเพิ่มข้อมูลลงในฐานข้อมูล...")
                deals_data = {
                    'timestamp': datetime.now().isoformat(),
                    'total_products': len(self.hot_deals),
                    'products': self.hot_deals
                }
                insert_deals(deals_data)
                logging.info("เพิ่มข้อมูลลงในฐานข้อมูลสำเร็จ")
            except Exception as e:
                logging.error(f"ไม่สามารถเพิ่มข้อมูลลงในฐานข้อมูล: {e}")
            return filename
        except Exception as e:
            logging.error(f"ไม่สามารถบันทึกไฟล์ JSON: {e}")
            return None

    def save_to_csv(self, filename=None):
        """ส่วนนี้เหมือนเดิม"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"priceza_hot_deals_{timestamp}.csv"
        
        if not self.hot_deals:
            logging.warning("ไม่มีข้อมูลสำหรับบันทึก")
            return None
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = [self.json_keys['title'], self.json_keys['price'], self.json_keys['original_price'], self.json_keys['discount'], 
                              self.json_keys['merchant'], self.json_keys['rating'], self.json_keys['reviews_count'], 
                              self.json_keys['image_url'], self.json_keys['product_url'], self.json_keys['merchant_image']]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.hot_deals)
            logging.info(f"บันทึกข้อมูล CSV สำเร็จ: {filename}")
            return filename
        except Exception as e:
            logging.error(f"ไม่สามารถบันทึกไฟล์ CSV: {e}")
            return None