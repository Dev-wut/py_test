# PriceZA Hot Deals Scraper & Dashboard (ภาษาไทย)

โปรเจกต์นี้เป็นโซลูชันแบบ Full-stack สำหรับการดึงข้อมูล Hot Deals จาก priceza.com, จัดเก็บข้อมูล และแสดงผลผ่าน Web Interface ที่ทันสมัย

## คุณสมบัติ

*   **เกณฑ์การดึงข้อมูลที่กำหนดค่าได้:** สามารถปรับแต่งพารามิเตอร์การดึงข้อมูล (URL, ตัวเลือก HTML, คีย์ JSON) ได้แบบไดนามิกผ่าน UI เฉพาะ
*   **การดึงข้อมูลอัตโนมัติ:** ดึงข้อมูล Hot Deals จาก priceza.com โดยใช้ Selenium เพื่อจัดการเนื้อหาแบบ Dynamic (เช่น ปุ่ม "Load More")
*   **การจัดเก็บข้อมูลตามกำหนดเวลา:** Scraper จะทำงานโดยอัตโนมัติทุกๆ 30 นาที
*   **API แบบ RESTful:** แสดงข้อมูลที่ดึงมาผ่าน Backend ที่สร้างด้วย FastAPI
*   **User Interface ที่ทันสมัย:** Dashboard ที่ตอบสนองและโต้ตอบได้ สร้างด้วย React และ Ant Design
*   **ตัวบ่งชี้สถานะ Scraper:** UI จะแสดงข้อความเมื่อ Scraper กำลังทำงานอยู่ เพื่อให้ข้อมูลแบบ Real-time เกี่ยวกับการเก็บข้อมูล
*   **รูปแบบข้อมูลที่เป็นระเบียบ:** ข้อมูลที่ดึงมาจะถูกบันทึกในรูปแบบ JSON

## การติดตั้ง

ในการทำให้โปรเจกต์นี้ทำงานได้ ให้ทำตามขั้นตอนเหล่านี้:

1.  **Backend Setup:**
    ไปที่ไดเรกทอรี `backend` และติดตั้งแพ็คเกจ Python ที่จำเป็น:
    ```bash
    cd backend
    pip install fastapi uvicorn selenium beautifulsoup4 webdriver-manager python-multipart apscheduler
    ```

2.  **Frontend Setup:**
    ไปที่ไดเรกทอรี `frontend` และติดตั้งแพ็คเกจ Node.js ที่จำเป็น:
    ```bash
    cd frontend
    npm install
    ```

## ตัวแปรสภาพแวดล้อม

ต้องกำหนดตัวแปรสภาพแวดล้อมเหล่านี้เมื่อใช้งานจริง:

* `ALLOWED_ORIGINS` – รายการของ origin ที่อนุญาตให้เรียก API (คั่นด้วยเครื่องหมายจุลภาค). หากไม่ได้ตั้งค่า ระบบจะใช้ค่าเริ่มต้น `http://localhost` และบันทึกข้อความเตือน ดังนั้นควรกำหนดค่าให้เหมาะสมในสภาพแวดล้อม production.
* `DATABASE_URL` – URL สำหรับเชื่อมต่อ PostgreSQL (เช่น `postgresql://user:password@localhost:5432/priceza`) ผู้ใช้ที่ระบุใน URL นี้ต้องมีสิทธิ์เชื่อมต่อกับฐานข้อมูลเริ่มต้น `postgres` และมีสิทธิ์รันคำสั่ง `CREATE DATABASE` เพื่อให้ระบบสามารถสร้างฐานข้อมูลเป้าหมายให้อัตโนมัติเมื่อยังไม่ถูกสร้าง

## วิธีรัน

คุณต้องรัน FastAPI UI Server, Scraper และ Frontend Development Server พร้อมกันใน Terminal ที่แยกกัน:

### 1. รัน FastAPI UI Server

เปิด Terminal แรก, ไปที่ไดเรกทอรี `backend` และเริ่ม FastAPI Server:

```bash
cd backend
uvicorn main:app --reload
```
*   Server จะเริ่มทำงานที่ `http://localhost:8000`
*   คุณสามารถดูเอกสาร API ได้ที่ `http://localhost:8000/docs`

### 2. รัน Scraper

เปิด Terminal ที่สอง, ไปที่ไดเรกทอรี `backend` และเริ่ม Scraper:

```bash
cd backend
python scraper_runner.py
```
*   การดึงข้อมูลเริ่มต้นจะทำงานทันที และการดึงข้อมูลครั้งต่อไปจะเกิดขึ้นทุกๆ 30 นาที
*   กระบวนการนี้จะทำงานใน Background และอัปเดตไฟล์ `backend/data/latest_deals.json` อย่างต่อเนื่อง

### 3. รัน Frontend Development Server

เปิด Terminal ที่สาม, ไปที่ไดเรกทอรี `frontend` และเริ่ม React Development Server:

```bash
cd frontend
npm start
```
*   UI จะรีเฟรชโดยอัตโนมัติเมื่อคุณทำการเปลี่ยนแปลงโค้ด Frontend

## การรันด้วย Docker

โปรเจกต์นี้สามารถรันได้อย่างง่ายดายโดยใช้ Docker และ Docker Compose นี่คือวิธีที่แนะนำในการรันบริการทั้งหมด (Backend API, Scraper และ Frontend) พร้อมกัน

### ข้อกำหนดเบื้องต้น

ตรวจสอบให้แน่ใจว่าคุณได้ติดตั้ง Docker และ Docker Compose บนระบบของคุณแล้ว คุณสามารถดาวน์โหลดได้จากเว็บไซต์ทางการของ Docker

### สร้างและรันแอปพลิเคชัน

ไปที่ไดเรกทอรีรากของโปรเจกต์ (ที่ไฟล์ `docker-compose.yml` อยู่) และรันคำสั่งต่อไปนี้:

```bash
docker-compose up --build
```

คำสั่งนี้จะ:
*   สร้าง Docker images สำหรับบริการ Backend และ Frontend
*   เริ่มบริการ `backend_api` (FastAPI server), `scraper_runner` (Python scraper) และ `frontend` (แอปพลิเคชัน React ที่ให้บริการโดย Nginx)
*   `scraper_runner` จะเริ่มดึงข้อมูลโดยอัตโนมัติและอัปเดตไฟล์ `backend/data/latest_deals.json`

### การเข้าถึงแอปพลิเคชัน

เมื่อบริการทั้งหมดทำงานแล้ว:
*   **Backend API:** เข้าถึงเอกสาร FastAPI ได้ที่ `http://localhost:8000/docs`
*   **Frontend Dashboard:** เข้าถึงแอปพลิเคชัน React ได้ที่ `http://localhost:3000`

### การหยุดแอปพลิเคชัน

หากต้องการหยุดคอนเทนเนอร์ Docker ทั้งหมดที่กำลังทำงานอยู่และลบเครือข่ายที่สร้างโดย Docker Compose ให้รันคำสั่งต่อไปนี้จากไดเรกทอรีรากของโปรเจกต์:

```bash
docker-compose down
```

### การคงอยู่ของข้อมูล (Data Persistence)

ไดเรกทอรี `backend/data` ถูกเมาท์เป็น Volume ในบริการ `scraper_runner` สิ่งนี้ทำให้มั่นใจได้ว่าข้อมูลที่ดึงมา (`latest_deals.json` และ `scraper_status.json`) จะยังคงอยู่ในเครื่องโฮสต์ของคุณแม้ว่าคอนเทนเนอร์ Docker จะถูกลบไปแล้วก็ตาม

## ข้อควรรู้

*   **การแยกส่วน:** Backend ถูกแบ่งออกเป็นสองส่วนหลัก: FastAPI UI Server และ Scraper Server ที่ทำงานแยกกัน สิ่งนี้ทำให้ UI Server ยังคงตอบสนองได้แม้ในขณะที่ Scraper กำลังทำงานอยู่
*   **สถานะ Scraper:** Scraper จะสร้างและอัปเดตไฟล์ `backend/data/scraper_status.json` เพื่อระบุว่ากำลังทำงานอยู่หรือไม่ UI Server จะอ่านไฟล์นี้ผ่าน API Endpoint `/api/scraper_status` และ Frontend จะใช้ข้อมูลนี้เพื่อแสดงข้อความ "Scraping in progress..." ให้ผู้ใช้ทราบ
*   **การกำหนดค่า Scraper:** Scraper ใช้ไฟล์ `backend/data/scraper_config.json` ในการกำหนดค่า URL, ตัวเลือก HTML (เช่น `tag`, `class`, `id`, `attrs`) และคีย์ JSON สำหรับข้อมูลที่ดึงมา คุณสามารถแก้ไขการกำหนดค่านี้ได้ผ่านหน้า UI `/scraper-criteria` โดยเฉพาะ `attrs` เป็น Dictionary ของแอตทริบิวต์ HTML เพิ่มเติมที่ใช้ในการระบุ Element ได้อย่างแม่นยำ (เช่น `{"href": true, "onmousedown": true}` สำหรับลิงก์)

## การมีส่วนร่วม

โปรดหลีกเลี่ยงการคอมมิตไฟล์ที่สร้างขึ้นโดยอัตโนมัติ เช่น ไฟล์สำรอง, ไดเรกทอรี __pycache__, ไฟล์ล็อก และชุดข้อมูลที่ขูดมา ไฟล์เหล่านี้จะถูกละเว้นโดย `.gitignore` และควรสร้างขึ้นใหม่ในเครื่อง