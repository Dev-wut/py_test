#!/usr/bin/env python3
"""
PriceZA Hot Deals Scraper
สคริปต์สำหรับดึงข้อมูลสินค้าฮอตดีลจาก priceza.com
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import time
import logging
from urllib.parse import urljoin, urlparse
import os
import re # Import re for regular expressions

# ตั้งค่า logging พร้อมระบุ encoding='utf-8'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('priceza_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ],
    encoding='utf-8' 
)

class PriceZAScraper:
    # (แก้ไข) เพิ่ม argument allowed_merchants ตอน khởi tạo
    def __init__(self, allowed_merchants=None):
        self.base_url = "https://www.priceza.com"
        self.session = requests.Session()
        
        # (แก้ไข) เก็บรายชื่อร้านค้าที่ต้องการ ถ้ามี
        if allowed_merchants:
            # ทำให้เป็นตัวพิมพ์ใหญ่ทั้งหมดและลบช่องว่าง เพื่อให้เทียบง่าย
            self.allowed_merchants = [m.strip().upper() for m in allowed_merchants]
        else:
            self.allowed_merchants = []

        # ตั้งค่า headers เพื่อหลีกเลี่ยงการถูก block
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/5.0 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'th-TH,th;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.hot_deals = []

    def get_page_content(self, url, max_retries=3):
        """ดึงเนื้อหาของหน้าเว็บ"""
        for attempt in range(max_retries):
            try:
                logging.info(f"กำลังดึงข้อมูลจาก: {url} (ครั้งที่ {attempt + 1})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                logging.warning(f"ไม่สามารถดึงข้อมูลได้: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logging.error(f"ไม่สามารถดึงข้อมูลจาก {url} หลังจากพยายาม {max_retries} ครั้ง")
                    return None

    def parse_product_info(self, product_element):
        """
        แยกข้อมูลสินค้าจาก element (ปรับปรุงตาม HTML ที่ให้มา)
        """
        product_info = {
            'title': '',
            'price': '',
            'original_price': '',
            'discount': '',
            'image_url': '',
            'product_url': '',
            'merchant': '',
            'merchant_image': '',
            'rating': '',
            'reviews_count': ''
        }
        
        try:
            # ชื่อสินค้า
            title_elem = product_element.find('h3', class_='pz-pdb_name')
            if title_elem:
                product_info['title'] = title_elem.get('title', '').replace('ราคา ', '').strip()

            # ราคาเดิม: ดึงข้อมูลและลบ '฿'
            original_price_elem = product_element.find('del', class_='pz-base-price')
            if original_price_elem:
                product_info['original_price'] = original_price_elem.get_text(strip=True).replace('฿', '')

            # ราคาปัจจุบัน
            price_elem = product_element.find('span', class_='pz-pdb-price')
            if price_elem:
                op_tag_to_remove = price_elem.find('del')
                if op_tag_to_remove:
                    op_tag_to_remove.extract() 
                product_info['price'] = price_elem.get_text(strip=True).replace('฿', '')
            
            # ส่วนลด
            discount_elem = product_element.find('div', class_='pz-label--discount')
            if discount_elem:
                product_info['discount'] = discount_elem.get_text(strip=True)
            
            # รูปภาพสินค้า
            img_elem = product_element.find('img', class_='pz-pdb_media--img')
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-original')
                if img_src:
                    product_info['image_url'] = urljoin(self.base_url, img_src)
            
            # ลิงก์สินค้า และ ร้านค้า (Merchant)
            link_elem = product_element.find('a', href=True, onmousedown=True)
            if link_elem:
                product_info['product_url'] = urljoin(self.base_url, link_elem['href'])
                
                onmousedown_attr = link_elem.get('onmousedown', '')
                match = re.search(r"addGAInteractionEvent\('MerchantProducts','([^']*)'", onmousedown_attr)
                if match:
                    product_info['merchant'] = match.group(1).strip().upper() # แปลงเป็นตัวพิมพ์ใหญ่

            # รูปภาพร้านค้า
            merchant_img_elem = product_element.find('img', class_='pz-pdb_store--img')
            if merchant_img_elem:
                merchant_img_src = merchant_img_elem.get('src') or merchant_img_elem.get('data-original')
                if merchant_img_src:
                    product_info['merchant_image'] = urljoin(self.base_url, merchant_img_src)
            
            # คะแนน
            rating_elem = product_element.find('div', class_='pz-rating-score-text')
            if rating_elem:
                product_info['rating'] = rating_elem.get_text(strip=True)
                
                review_match = re.search(r'\((\d+)\)', product_info['rating'])
                if review_match:
                    product_info['reviews_count'] = review_match.group(1)

        except Exception as e:
            logging.warning(f"เกิดข้อผิดพลาดในการแยกข้อมูลสินค้า: {e}")
        
        return product_info


    def scrape_hot_deals(self):
        """ดึงข้อมูลสินค้าฮอตดีลจากหน้าแรก"""
        if self.allowed_merchants:
            logging.info(f"เริ่มดึงข้อมูลสินค้าฮอตดีล (กรองเฉพาะ: {', '.join(self.allowed_merchants)})")
        else:
            logging.info("เริ่มดึงข้อมูลสินค้าฮอตดีล...")

        
        html_content = self.get_page_content(self.base_url)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        hot_deals_container = soup.find('div', class_='pz-pdb-section') or soup.find('div', id='home-specials')
        
        if not hot_deals_container:
            logging.warning("ไม่พบ container หลักของ hot deals - ลองหาด้วยวิธีอื่น...")
            hot_deals_container = soup.find('div', class_=lambda x: x and 'special' in x.lower()) or \
                                  soup.find('div', class_=lambda x: x and 'hot' in x.lower()) or \
                                  soup.find('div', class_=lambda x: x and 'deal' in x.lower())
        
        if hot_deals_container:
            logging.info("พบส่วนฮอตดีล - เริ่มดึงข้อมูลสินค้า...")
            
            product_elements = hot_deals_container.find_all('div', class_='pz-pdb-item')
            
            if not product_elements:
                 product_elements = hot_deals_container.find_all(['div', 'article', 'li'], 
                                                                class_=lambda x: x and any(keyword in x.lower() 
                                                                for keyword in ['product', 'item', 'card', 'deal']))
            
            logging.info(f"พบสินค้า {len(product_elements)} รายการ")
            
            for i, product_elem in enumerate(product_elements, 1):
                product_info = self.parse_product_info(product_elem)
                
                # ตรวจสอบว่ามีข้อมูลสำคัญหรือไม่
                if product_info['title'] and product_info['price']:
                    
                    # (แก้ไข) เพิ่มเงื่อนไขการกรองร้านค้า
                    # ถ้าไม่ได้กำหนดร้านค้า หรือ ร้านค้าอยู่ในลิสต์ที่อนุญาต -> ให้เพิ่มข้อมูล
                    if not self.allowed_merchants or product_info['merchant'] in self.allowed_merchants:
                        self.hot_deals.append(product_info)
                        logging.info(f"สินค้าที่ {i} [{product_info['merchant']}]: {product_info['title'][:50]}...")
                    else:
                        logging.info(f"ข้ามสินค้าที่ {i} [{product_info['merchant']}] เนื่องจากไม่ตรงตามที่กรองไว้")
                else:
                    logging.warning(f"ข้ามรายการที่ {i} เนื่องจากไม่มีข้อมูลสำคัญ (ชื่อหรือราคา)")
                
                time.sleep(0.1)
        
        else:
            logging.warning("ไม่พบส่วนฮอตดีลในหน้าเว็บ")
            
        logging.info(f"ดึงข้อมูลสำเร็จ: {len(self.hot_deals)} รายการ")
        return self.hot_deals

    def save_to_json(self, filename=None):
        """บันทึกข้อมูลเป็น JSON"""
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
            return filename
        except Exception as e:
            logging.error(f"ไม่สามารถบันทึกไฟล์ JSON: {e}")
            return None

    def save_to_csv(self, filename=None):
        """บันทึกข้อมูลเป็น CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"priceza_hot_deals_{timestamp}.csv"
        
        if not self.hot_deals:
            logging.warning("ไม่มีข้อมูลสำหรับบันทึก")
            return None
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = ['title', 'price', 'original_price', 'discount', 
                              'merchant', 'rating', 'reviews_count', 
                              'image_url', 'product_url', 'merchant_image']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in self.hot_deals:
                    writer.writerow(product)
            
            logging.info(f"บันทึกข้อมูล CSV สำเร็จ: {filename}")
            return filename
        except Exception as e:
            logging.error(f"ไม่สามารถบันทึกไฟล์ CSV: {e}")
            return None

    def print_summary(self):
        """แสดงสรุปข้อมูล"""
        print(f"\n{'='*50}")
        print(f"สรุปผลการดึงข้อมูล PriceZA Hot Deals")
        print(f"{'='*50}")
        print(f"จำนวนสินค้าทั้งหมด: {len(self.hot_deals)} รายการ")
        print(f"เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.hot_deals:
            print(f"\nตัวอย่างสินค้า 5 รายการแรก:")
            print("-" * 50)
            for i, product in enumerate(self.hot_deals[:5], 1):
                print(f"{i}. {product['title'][:60]}")
                print(f"   ราคา: {product['price']}")
                if product['original_price']:
                    print(f"   ราคาเดิม: {product['original_price']}")
                if product['merchant']:
                    print(f"   ร้านค้า: {product['merchant']}")
                print()

def main():
    """ฟังก์ชันหลัก"""
    print("🔍 PriceZA Hot Deals Scraper")
    print("=" * 40)
    
    # (แก้ไข) รับชื่อร้านค้าจากผู้ใช้
    merchant_input = input("ระบุชื่อร้านค้าที่ต้องการ (เช่น LAZADA, SHOPEE) คั่นด้วยจุลภาค (,) \nหากไม่ระบุ ให้กด Enter เพื่อดึงข้อมูลทั้งหมด: ")
    
    # แปลง input เป็น list
    merchants_to_scrape = [m.strip() for m in merchant_input.split(',') if m.strip()]

    # (แก้ไข) สร้าง scraper object พร้อมส่งรายชื่อร้านค้า
    scraper = PriceZAScraper(allowed_merchants=merchants_to_scrape)
    
    try:
        hot_deals = scraper.scrape_hot_deals()
        
        if hot_deals:
            scraper.print_summary()
            
            print("\n💾 กำลังบันทึกข้อมูล...")
            json_file = scraper.save_to_json()
            csv_file = scraper.save_to_csv()
            
            print(f"✅ บันทึกเสร็จสิ้น!")
            if json_file:
                print(f"   📄 JSON: {json_file}")
            if csv_file:
                print(f"   📊 CSV: {csv_file}")
        else:
            print("❌ ไม่พบข้อมูลสินค้าตามเงื่อนไขที่กำหนด")
            
    except KeyboardInterrupt:
        print("\n⏹️ ผู้ใช้ยกเลิกการทำงาน")
    except Exception as e:
        logging.error(f"เกิดข้อผิดพลาด: {e}")
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()