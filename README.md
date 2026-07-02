# cycu-grade-checker
# 🎓 中原大學 iTouch 成績自動追蹤機器人 (CYCU Grade Checker)

這是一個專為中原大學 iTouch 系統設計的成績追蹤工具。它會自動巡邏成績頁面，並在老師送出新成績時發送 Email 通知。 (｡･ω･｡)ﾉ

## ✨ 功能特色
* **自動巡邏**：每小時自動登入 iTouch 檢查最新成績。
* **精準通知**：只有當「已出分科目數」增加時才會發信，不重複吵人。
* **隱私保護**：帳號密碼與 Email 密鑰皆儲存於 GitHub Secrets，安全不外洩。
* **簡單易用**：完全在雲端運行，不需開啟電腦。

## 🛠️ 技術架構
* **語言**：Python 3.9
* **自動化工具**：Selenium + Chrome WebDriver
* **執行環境**：GitHub Actions
* **通知系統**：Gmail SMTP (smtplib)

## 📝 專案結構
* `grade.py`: 核心爬蟲腳本，負責登入、解析成績及比對邏輯。
* `.github/workflows/main.yml`: 自動化排程設定。
* `graded_count.txt`: 紀錄上次已出分的科目數量，用於比對更新。

## How to use this
「嘿！這是我寫的 iTouch 成績自動通知機器人，你可以點進來照著設定：

Fork 專案：點網頁右上角的 Fork，把程式碼複製到你的 GitHub。

設定 Secrets：在你自己的專案 Settings -> Secrets and variables -> Actions，新增這 5 個金鑰（填你自己的資訊）：STUDENT_ID、STUDENT_PW、EMAIL_SENDER、EMAIL_PASS、EMAIL_RECEIVER。

開啟權限：到 Settings -> Actions -> General，把 Workflow permissions 改成 Read and write permissions 才能存檔。

手動啟動：到 Actions 分頁點 iTouch Grade Checker -> Run workflow，成功的話就會收到信了！」

第一次使用TXT請改成0 那是紀錄有沒有登記的成績 他會自己改 之後不用理他
## 🤖 維護者
* **Feng, Ying-chen**

---
希望每學期都能順利 Pass！加油加油！ (๑•̀ㅂ•́)و✧
