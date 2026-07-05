import time
import os
import re
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- 讀取 GitHub Secrets (環境變數) ---
STUDENT_ID = os.environ.get('STUDENT_ID')
STUDENT_PW = os.environ.get('STUDENT_PW')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')

RECORD_FILE = "graded_count.txt"


def get_current_semester_code():
    """
    根據執行當下的日期，自動算出目前學期代碼（民國年+學期）。
    Automatically compute the current semester code (ROC year + semester)
    based on today's date, so we don't need to hardcode it every term.

    8月~1月 -> 上學期 (semester 1)
    2月~7月 -> 下學期 (semester 2)
    """
    today = datetime.now()
    roc_year = today.year - 1911 - 1  # 民國年 -1
    if today.month >= 8:
        academic_year, semester = roc_year + 1, 1
    elif today.month == 1:
        academic_year, semester = roc_year, 1
    else:
        academic_year, semester = roc_year, 2
    return f"{academic_year}{semester}"


def is_grading_season(today=None):
    """
    參考中原大學 114 學年度行事曆判斷的「可能出分季節」：
    Based on CYCU's official 114 academic-year calendar, the periods when
    grades are actually likely to be posted:

    - 上學期 (semester 1)：學期考試週約 1/5~1/9，教師成績繳交截止約 1/25
      -> 抓寬鬆一點：12月下旬 ~ 1月底
    - 下學期 (semester 2)：畢業班學期考試週約 5/25~5/29 (截止 6/7)，
      非畢業班學期考試週約 6/22~6/26 (截止 7/12)
      -> 抓寬鬆一點：5月中 ~ 7月中

    這兩段時間之外，老師基本上不會登記成績，所以不需要真的登入檢查。
    Outside these windows professors essentially never post grades, so
    there's no need to actually log in and check.
    """
    today = today or datetime.now()
    m, d = today.month, today.day

    if (m == 12 and d >= 20) or (m == 1):
        return True
    if (m == 5 and d >= 15) or (m == 6) or (m == 7 and d <= 15):
        return True
    return False


def read_record():
    """讀取上次記錄：學期代碼、已出分科目數、是否已全部出完。"""
    if not os.path.exists(RECORD_FILE):
        return "", 0, False

    with open(RECORD_FILE, "r") as f:
        saved = f.read().strip()

    parts = saved.split(",")
    if len(parts) == 3:
        semester, count, status = parts
        return semester, int(count) if count.isdigit() else 0, status == "done"
    if len(parts) == 2:
        semester, count = parts
        return semester, int(count) if count.isdigit() else 0, False
    # 最舊格式：純數字，沒有學期代碼
    return "", int(saved) if saved.isdigit() else 0, False


def write_record(semester_code, count, done):
    with open(RECORD_FILE, "w") as f:
        f.write(f"{semester_code},{count},{'done' if done else 'pending'}")


def send_grade_email(grade_list, count):
    msg = MIMEText(f"嗨！(｡･ω･｡)ﾉ\n\niTouch 成績更新囉！目前已有 {count} 科出分。\n\n清單如下：\n" + "\n".join(grade_list))
    msg['Subject'] = f"🔔 iTouch 成績更新通知 ({count}科)"
    msg['From'] = f"成績機器人 <{EMAIL_SENDER}>"
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASS)
            server.send_message(msg)
        print("✅ 通知信件已發送。")
    except Exception as e:
        print(f"❌ 郵件發送失敗：{e}")


def run_grade_check():
    semester_code = get_current_semester_code()
    old_semester, old_count, old_done = read_record()

    # 換學期了，先把舊紀錄的完成狀態清掉，讓新學期重新開始追蹤
    if old_semester != semester_code:
        print(f"🔄 偵測到學期切換（{old_semester or '無'} -> {semester_code}），計數與完成狀態歸零。")
        old_count, old_done = 0, False

    # 這學期已經全部出分過了，不用再登入檢查
    if old_done:
        print(f"✅ {semester_code} 學期成績已全部出齊，暫停檢查，不進行登入。")
        return

    # 不在預期的出分季節，直接跳過，不登入、不開瀏覽器，節省資源
    if not is_grading_season():
        print(f"😴 目前不在預期的出分季節（參考中原行事曆：12月下旬~1月底、5月中~7月中），暫停檢查。")
        return

    options = Options()
    # GitHub Actions 必須使用無頭模式 (headless)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://itouch.cycu.edu.tw/")
        time.sleep(3)

        # 登入流程
        xpath_user = "/html/body/div/div[2]/div[1]/div/div[1]/div/div/div/form/div[1]/input"
        xpath_pass = "/html/body/div/div[2]/div[1]/div/div[1]/div/div/div/form/div[2]/input"
        xpath_btn  = "/html/body/div/div[2]/div[1]/div/div[1]/div/div/div/form/div[3]/div[1]/button"

        wait.until(EC.presence_of_element_located((By.XPATH, xpath_user))).send_keys(STUDENT_ID)
        driver.find_element(By.XPATH, xpath_pass).send_keys(STUDENT_PW)
        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, xpath_btn))

        # 跳轉至成績頁
        wait.until(EC.url_contains("#/ann"))
        driver.get("https://itouch.cycu.edu.tw/home/?p=8672#/includeProc/id=20HS0003&f=3&p=520074")

        time.sleep(5)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "includeFrame")))
        content = driver.find_element(By.TAG_NAME, "body").text

        print(f"🗓️ 目前判斷學期代碼為：{semester_code}")

        lines = [l.strip() for l in content.splitlines() if l.strip()]
        grade_list, graded_count = [], 0
        for i in range(len(lines)):
            if lines[i] == semester_code and i + 8 < len(lines):
                subject = lines[i+4]
                if "Rank" in subject or "排名" in subject: continue
                val8, val9 = lines[i+8], (lines[i+9] if i+9 < len(lines) else "")
                if val8.isdigit() and val9.isdigit() and val9 != semester_code:
                    score, graded_count = val8, graded_count + 1
                else: score = "尚未出分"
                grade_list.append(f"• {subject} -> {score}")

        total_subjects = len(grade_list)
        all_done = total_subjects > 0 and graded_count >= total_subjects

        if graded_count > old_count:
            send_grade_email(grade_list, graded_count)
            write_record(semester_code, graded_count, all_done)
        else:
            print(f"目前已有 {graded_count} 科出分，與上次相同。")
            write_record(semester_code, old_count, all_done)

        if all_done:
            print(f"🎉 {semester_code} 學期 {total_subjects} 科已全部出分完畢，之後將暫停檢查直到下學期。")

    except Exception as e:
        print(f"❌ 錯誤：{e}")
    finally:
        driver.quit()


if __name__ == "__main__":

    run_grade_check()
