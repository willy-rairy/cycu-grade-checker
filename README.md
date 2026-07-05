# 🎓 中原大學 iTouch 成績自動追蹤機器人

### 📌 v2.0

這是一個專為中原大學 iTouch 系統寫的成績追蹤小工具，會在成績可能出爐的那段時間自動幫你巡邏成績頁面，老師一登記新成績就寄信通知你，不用自己一直手動刷網頁。(｡･ω･｡)ﾉ

## ✨ 這版有什麼

* **每小時自動巡一次**：時間到就自動登入 iTouch 看一下最新成績
* **不重複吵你**：只有「已出分科目數」變多才會寄信，不會每小時都轟炸信箱
* **學期代碼自動算好了**：程式會自己看今天日期算出目前是哪個學期，不用每學期回來改程式碼
* **會自己休息**：參考中原的行事曆，只有真的接近出分的時間（大概 12月下旬到1月底、5月中到7月中）才會真的登入檢查，其他月份直接跳過不動作。等這學期科目全部出分完，就整學期都不會再登入了，等下學期開始才會重新啟動
* **帳密都放 GitHub Secrets**：不會外流

## 🛠️ 用了什麼

Python 3.9 + Selenium + GitHub Actions，寄信走 Gmail SMTP。

## 📝 檔案說明

* `grade.py`：主程式，負責登入、抓成績、比對、判斷要不要跳過這次檢查
* `.github/workflows/main.yml`：排程設定，每小時觸發一次
* `graded_count.txt`：記錄目前學期、已出分幾科、這學期是不是已經全部出完了。格式是 `學期代碼,已出分數,狀態`，例如 `1142,6,done`

## 🚀 怎麼設定

1. **Fork 這個專案**：點右上角 Fork，複製到你自己的 GitHub

2. **設定 Secrets**：到你 fork 之後的專案 `Settings -> Secrets and variables -> Actions`，新增以下 5 個：

   | Secret 名稱 | 代表意思 |
   |---|---|
   | `STUDENT_ID` | 你的中原大學學號 |
   | `STUDENT_PW` | 你登入 iTouch 用的密碼 |
   | `EMAIL_SENDER` | 用來「寄出」通知信的信箱（建議另外申請一個 Gmail 專門給機器人用） |
   | `EMAIL_PASS` | 上面那個寄件信箱的登入密碼 |
   | `EMAIL_RECEIVER` | 你要「收」通知信的信箱（可以跟 `EMAIL_SENDER` 不同，填自己常看的信箱就好） |

   > ⚠️ 如果 `EMAIL_SENDER` 是 Gmail，`EMAIL_PASS` 要填「應用程式密碼」，不是你平常登入 Gmail 的密碼。

3. **開權限**：`Settings -> Actions -> General`，把 Workflow permissions 改成 **Read and write permissions**，不然沒辦法存檔

4. **手動跑一次試試看**：`Actions -> iTouch Grade Checker -> Run workflow`，成功就會收到信

第一次用的話 `graded_count.txt` 記得改成 `0`，之後機器人自己會更新，不用管它。

## 🤖 維護者

Feng, Ying-chen

---
希望每學期都能順利 Pass！加油加油！(๑•̀ㅂ•́)و✧
