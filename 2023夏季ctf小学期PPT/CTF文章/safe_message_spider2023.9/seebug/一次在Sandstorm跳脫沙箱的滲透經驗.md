作者：[Shaolin@DEVCORE](https://devco.re/blog/2018/01/26/Sandstorm-Security-Review-CVE-2017-6200/ "Shaolin@DEVCORE")  
English Version：[《Sandstorm Security
Review》](https://devco.re/blog/2018/01/26/Sandstorm-Security-Review-CVE-2017-6200-en/ "《Sandstorm Security Review》")

#### 前言

2017 年初，我們有個滲透測試專案，專案的標的架構在 [Sandstorm](https://sandstorm.io/ "Sandstorm")
之上。Sandstorm 是一款 Web 平台，使用者可以輕易的在該平台安裝各種 Web App（如
WordPress、GitLab…），該平台最大的特色在於這些 App 都是在沙箱中執行。因此，即使我們測試中找到多項 App
弱點，也無法對平台本身造成威脅。

為了讓弱點效益最大化，我們將一部分精力轉移到研究 Sandstorm 原始碼，目的是跳脫 App
的沙箱環境看有沒有機會影響整台伺服器。最後，我們找到了幾個少見且有趣的弱點，並申請 CVE 編號如下：

  * 阻斷服務攻擊（Denial of Service），CVE-2017-6198
  * 繞過授權模式（Bypassing Authorization Schema），CVE-2017-6199
  * 不安全的直接存取物件（Insecure Direct Object References），CVE-2017-6200
  * 服務端請求偽造（Server-Side Request Forgery），CVE-2017-6201

#### 漏洞細節

##### CVE-2017-6198

這是一個消耗系統資源造成的 DoS。起因是 Sandstorm 並未完善限制每個 App 所能使用的資源，在
`src/sandstorm/supervisor.c++` 僅限制了每個程序能夠打開的最多檔案數，相關程式碼如下：

    
    
    void SupervisorMain::setResourceLimits() {
      struct rlimit limit;
      memset(&limit, 0, sizeof(limit));
      limit.rlim_cur = 1024;
      limit.rlim_max = 4096;
      KJ_SYSCALL(setrlimit(RLIMIT_NOFILE, &limit));
    }

Ref: <https://github.com/sandstorm-io/sandstorm/blob/v0.202/src/sandstorm/supervisor.c++#L824>

由於 supervisor 未限制子程序數量以及未限制儲存空間用量，因此攻擊者只要讓 App 不斷執行 fork（通常稱為 Fork
Bomb）或是大量使用硬碟空間，就會造成伺服器資源不足而中斷服務。

##### CVE-2017-6199

通常 Sandstorm 會設定特定組織成員才能擁有特殊的權限，而系統預設的組織成員判斷方式是檢查使用者 email
中「@」符號最後的字串是否在白名單內，相關程式碼如下：

    
    
    if (identity.services.email.email.toLowerCase().split("@").pop() === emailDomain) {
        return true;
    }

Ref: <https://github.com/sandstorm-io/sandstorm/blob/v0.202/shell/packages/sandstorm-db/db.js#L1112>

因此，當攻擊者填入的 email 為 `demo@devco.re,ccc@aaa.bbb`，系統便會將攻擊者視為 `aaa.bbb` 組織的使用者。

這項攻擊得以成功還有另外一個關鍵點，發生在 Sandstorm 登入的一個特色上。使用 Sandstorm 服務不需要設定密碼，使用者每次欲登入時填入
email，系統便會發送一組每次皆不同的隨機密碼作為登入使用。上述的例子之所以能夠成功，就是因為系統將
`demo@devco.re,ccc@aaa.bbb` 視為一個 aaa.bbb 網域的使用者，而隨機密碼會發送到 `demo@devco.re` 以及
`ccc@aaa.bbb` 兩個不同信箱中，只要可以收到密碼就可以登入使用服務。

直接案例說明：

1.在 Sandstorm 限定只有用 `aaa.bbb` 網域才可以登入。
![](https://images.seebug.org/content/images/2018/01/8352e4f2-543f-4cde-a0b6-b764ae493613.png-w331s)

2.登入處 email 欄位填入 `demo@devco.re,ccc@aaa.bbb`。（註：email 欄位在前端有用 HTML5
Validation，但後端並無檢查 email 是否合法）
![](https://images.seebug.org/content/images/2018/01/efac2ece-8773-4a41-ae09-3038a5569680.png-w331s)

3.在 demo@devco.re 信箱收到隨機密碼。
![](https://images.seebug.org/content/images/2018/01/f9cb61d2-d604-4038-b7f4-f2f5084224c3.png-w331s)

4.成功登入，demo@devco.re,ccc@aaa.bbb 被視為一個使用者，且為 aaa.bbb 組織成員！
![](https://images.seebug.org/content/images/2018/01/4d521df0-f174-4ff3-a99d-6c21900423a0.png-w331s)

在我們的滲透測試中，標的網站是允許認證的網域使用者自行安裝 App
的。因此透過這項繞過弱點，攻擊者可以再搭配本篇其他漏洞（CVE-2017-6198、CVE-2017-6200、CVE-2017-6201）做更進一步的攻擊。

##### CVE-2017-6200

這是一個有趣的弱點，總共組合了兩個驗證上的小疏忽才能達成攻擊！ 在 Sandstorm 中每個 Grain（Sandstorm
container，簡單來說就是一個 App 沙箱）的擁有者都可以下載該 App 的備份資料，但由於打包流程中存在兩個弱點，因此攻擊者可以打包沙箱外伺服器的
`/etc` 和 `/run` 下的檔案。發生的問題如下：

  1. 打包的流程隱藏了 `/var`、`/proc`、`/etc` 等敏感目錄，卻沒有隱藏 `/etc.host` 及 `/run.host` 這兩個目錄。這兩個目錄分別是伺服器下 `/etc` 和 `/run` 的別名，是較後期的功能。

  2. 系統會將欲打包的合法檔案整理出來透過標準輸入介面傳給 zip 打包，而判斷檔案和檔案間的區隔是靠換行符號(`\n`)。因此，當檔名中出現換行符號，可以插入非法的路徑檔名藉由 zip 打包。程式雖然有檢查檔名是否存在換行符，卻疏忽了檢查目錄名。

Ref: <https://github.com/sandstorm-io/sandstorm/blob/v0.202/src/sandstorm/backup.c%2B%2B#L271>

綜合上述兩個弱點，攻擊者只要在沙箱內建立一個目錄 `/var/exp\n/etc.host/passwd\n`，就可以透過下載備份的功能取得含有伺服器
`/etc/passwd` 檔案的備份檔。

實際情境截圖：

1.先在 Grain 裡新建目錄 `/var/exp\n/etc.host/passwd\n`，並用 Grain Backup 的功能下載備份檔。
![](https://images.seebug.org/content/images/2018/01/3e24e56a-b7f4-40b1-8f7d-5769a548ad33.png-w331s)

2.解開備份檔後在 `etc.host` 目錄下看到沙箱外伺服器的 `/etc/passwd`
![](https://images.seebug.org/content/images/2018/01/3edf8fbf-7903-4f70-b91a-80e7d3a41fdf.png-w331s)

##### CVE-2017-6201

這是經典的 SSRF（Server-Side Request Forgery）問題，在 Sandstorm 安裝 App
流程沒有限制安裝來源，攻擊者提供一個安裝 URL 就能讓伺服器存取該位置。該問題發生在
`https://[target]/install/xxxChangeItEveryTimexxx?url=http://127.0.0.1:22/`，這個範例連結得以確認伺服器的
22 port 是否開啟。

![](https://images.seebug.org/content/images/2018/01/c83c3aa5-c2b2-46c8-870a-11c785caca39.png-w331s)

（Parse Error，代表伺服器 22 port 開啟）

#### 後續

在提交弱點後，Sandstorm 官方非常迅速修正了弱點，並且發表了一篇文章：
<https://sandstorm.io/news/2017-03-02-security-review>

在這次滲透經驗中，我們認為 Sandstorm 是一款安全、有出色防禦機制的平台。主要原因取決於它的一個核心設計理念：就是假設使用者安裝的 App
都是惡意的。以這樣的前提出發去保護核心系統的安全，建立起來的防禦機制自然是全面且完善的。除了伺服器本身的保護，一些常見的客戶端攻擊（例如：XSS、CSRF）也透過
Sandstorm 特殊的隨機 hostname 等機制保護的很好。因此攻擊者很難從 App 本身去破壞伺服器，也很難透過攻擊客戶端去提升使用者的權限。

儘管是如此優秀的平台，仍舊會因一些小地方疏忽導致攻擊者有機可乘。這次發現弱點的地方多半在於 library
的誤用和新功能的撰寫沒有考慮到舊有防禦架構。這在其他專案也是常見的問題，藉機也提醒開發者在開發新功能時應做全面的安全檢視，以避免防禦落差所導致的弱點。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/518/>

