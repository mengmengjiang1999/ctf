**作者：Orange Tsai  
来源：<https://devco.re/blog/2019/01/16/hacking-Jenkins-part1-play-with-dynamic-routing/> 相关阅读：[Hacking Jenkins Part 2 - Abusing Meta Programming for
Unauthenticated RCE!](https://paper.seebug.org/818/ "Hacking Jenkins Part 2 -Abusing Meta Programming for Unauthenticated RCE!")**

在軟體工程中, [Continuous
Integration](https://en.wikipedia.org/wiki/Continuous_integration) 及
[Continuous Delivery](https://en.wikipedia.org/wiki/Continuous_delivery)
一直都被譽為是軟體開發上的必備流程, 有多少優點就不多談, 光是幫助開發者減少許多雜事就是很大的優勢了! 而在 CI/CD 的領域中, Jenkins
是最為老牌且廣為人知的一套工具, 由於它的易用性, 強大的 Pipeline 系統以及對於容器完美的整合使得 Jenkins 也成為目前最多人使用的
CI/CD 應用, 根據 Snyk 在 2018 年所做出的 [JVM 生態報告](https://snyk.io/blog/jvm-ecosystem-report-2018-tools) 中, Jenkins 在 CI/CD 應用中約佔六成的市佔率!

對於 [紅隊演練(Red Team)](https://devco.re/services/red-team) 來說, Jenkins 更是兵家必爭之地,
只要能掌握企業暴露在外的 Jenkins 即可掌握大量的原始碼, 登入憑證甚至控制大量的 Jenkins 節點! 在過去 DEVCORE
所經手過的滲透案子中也出現過數次由 Jenkins 當成進入點, 一步一步從一個小裂縫將目標撕開到完整滲透整間公司的經典案例!

這篇文章主要是分享去年中針對 Jenkins 所做的一次簡單 Security Review, 過程中共發現了五個 CVE:

  * [CVE-2018-1999002 - Arbitrary file read vulnerability](https://jenkins.io/security/advisory/2018-07-18/#SECURITY-914)
  * [CVE-2018-1000600 - CSRF and missing permission checks in GitHub Plugin](https://jenkins.io/security/advisory/2018-06-25/#SECURITY-915)
  * [CVE-2018-1999046 - Unauthorized users could access agent logs](https://jenkins.io/security/advisory/2018-08-15/#SECURITY-1071)
  * [CVE-2018-1000861 - Code execution through crafted URLs](https://jenkins.io/security/advisory/2018-12-05/#SECURITY-595)
  * [CVE-2019-1003000 - Sandbox Bypass in Script Security and Pipeline Plugins](https://jenkins.io/security/advisory/2019-01-08/#jenkins-security-advisory-2019-01-08)
  * [CVE-2019-1003001 - Sandbox Bypass in Script Security and Pipeline Plugins](https://jenkins.io/security/advisory/2019-01-08/#jenkins-security-advisory-2019-01-08)
  * [CVE-2019-1003002 - Sandbox Bypass in Script Security and Pipeline Plugins](https://jenkins.io/security/advisory/2019-01-08/#jenkins-security-advisory-2019-01-08)

其中比較被大家所討論的應該是 CVE-2018-1999002, 這是一個在 Windows 下的任意檔案讀取, 由於攻擊方式稍微有趣所以討論聲量較高一點,
這個弱點在外邊也有人做了詳細的分析, 詳情可以參考由騰訊雲鼎實驗室所做的分析([Jenkins
任意文件读取漏洞分析](https://cloud.tencent.com/developer/article/1165414)), 他們也成功的展示從
[Shodan](https://www.shodan.io/search?query=jenkins) 找到一台未修補的 Jenkins
實現任意讀檔到遠端代碼執行取得權限的過程!

但這篇文章要提的並不是這個, 而是當時為了嘗試繞過 CVE-2018-1999002 所需的最小權限 Overall/Read 時跟進 Jenkins
所使用的核心框架 Stapler 挖掘所發現的另外一個問題 - CVE-2018-1000861! 如果光從官方的漏洞敘述應該會覺得很神奇,
真的可以光從隨便一個網址去達成代碼執行嗎?

針對這個漏洞, 我的觀點是它就是一個存取控制清單(ACL)上的繞過, 但由於這是 Jenkins 架構上的問題並不是單一的程式編寫失誤,
進而導致了這個漏洞利用上的多樣性! 而為了這個技術債, Jenkins 官方也花費了一番心力([Jenkins
Patch](https://github.com/jenkinsci/jenkins/commit/47f38d714c99e1841fb737ad1005618eb26ed852)
及 [Stapler
Patch](https://github.com/stapler/stapler/commit/28e8eba822a0df9dcd64d20eb63d8ab5f6ee2980))去修復這個漏洞,
不但在原有的架構上介紹了新的路由黑名單及白名單, 也擴展了原有架構的 [Service Provider Interface
(SPI)](https://wiki.jenkins.io/display/JENKINS/Plugins+affected+by+the+SECURITY-595+fix)
去保護 Jenkins 路由, 下面就來解釋為何 Jenkins 要花了那麼多心力去修復這個漏洞!

### 代碼審查範圍

首先要聲明的是, 這並不是一次完整的代碼審查(畢竟要做一次太花時間了…), 因此只針對高風險漏洞進行挖掘, 著眼的範圍包括:

  * Jenkins 核心
  * Stapler 網頁框架
  * 建議安裝插件

Jenkins 在安裝過程中會詢問是否安裝建議的套件(像是 Git, GitHub, SVN 與 Pipeline… 等等),
基本上大多數人都會同意不然就只會得到一個半殘的 Jenkins 很不方便XD

![img](https://images.seebug.org/content/images/2019/02/18/1550479185000-1-1550479133129.png-w331s)

![img](https://images.seebug.org/content/images/2019/02/18/1550479185000-2.png-w331s)

### Jenkins 中的權限機制

因為這是一個基於 ACL 上的繞過, 所以在解釋漏洞之前, 先來介紹一下 Jenkins 中的權限機制! 在 Jenkins 中有數種不同的角色權限,
甚至有專門的 [Matrix Authorization Strategy
Plugin](https://plugins.jenkins.io/matrix-auth) (同為建議安裝套件)可針對各專案進行細部的權限設定,
從攻擊者的角度我們粗略分成三種:

#### 1\. Full Access

對於 Jenkins 有完整的控制權, 可對 Jenkins 做任何事! 基本上有這個權限即可透過 [Script
Console](http://jenkins.local/script) 介面使用 Groovy 執行任意代碼!

    
    
    print "uname -a".execute().text

這個權限對於駭客來說也是最渴望得到的權限, 但基本上由於安全意識的提升及網路上各種殭屍網路對全網進行掃描, 這種配置已經很少見(或只見於內網)

#### 2\. Read-only Mode

可從 [Configure Global Security](http://jenkins.local/configureSecurity)
介面中勾選下面選項來開啟這個模式

> Allow anonymous read access

在這個模式下, 所有的內容皆是可讀的, 例如可看到工作日誌或是一些 job/node 等敏感資訊,
對於攻擊者來說在這個模式下最大的好處就是可以獲得大量的原始碼! 但與 Full Access 模式最大的差異則是無法進行更進一步的操作或是執行 Groovy
代碼以取得控制權!

雖然這不是 Jenkins 的預設設定, 但對於一些習慣自動化的 DevOps 來說還是有可能開啟這個選項, 根據實際在
[Shodan](https://www.shodan.io/search?query=jenkins) 上的調查約 12% 的機器還是開啟這個選項!
以下使用 `ANONYMOUS_READ=True` 來代稱這個模式

#### 3\. Authenticated Mode

這是 Jenkins 預設安裝好的設定, 在沒有一組有效的帳號密碼狀況下無法看到任何資訊及進行任何操作! 以下使用
`ANONYMOUS_READ=False` 來代稱此模式

### 漏洞分析

整個漏洞要從 Jenkins 的 [動態路由](https://jenkins.io/doc/developer/handling-requests/routing/) 講起, 為了給開發者更大的彈性, Jenkins(嚴格來講是 Stapler)使用了一套 Naming
Convention 去匹配路由及動態的執行! 首先 Jenkins 以 `/` 為分隔將 URL 符號化, 接著由
[jenkins.model.Jenkins](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/jenkins/model/Jenkins.java)
為入口點開始往下搜尋, 如果符號符合 (1) Public 屬性的成員或是 (2) Public 屬性的方法符合下列命名規則, 則調用並繼續往下呼叫:

    
    
    1. get<token>()
    2. get<token>(String)
    3. get<token>(Int)
    4. get<token>(Long)
    5. get<token>(StaplerRequest)
    6. getDynamic(String, …)
    7. doDynamic(…)
    8. do<token>(…)
    9. js<token>(…)
    10. Class method with @WebMethod annotation
    11. Class method with @JavaScriptMethod annotation

看起來 Jenkins 給予開發者很大程度的自由去訪問各個物件, 但過於自由總是不好的，根據這種調用方式這裡就出現了兩個問題!

#### 1\. 萬物皆繼承 java.lang.Object

在 Java 中, 所有的物件皆繼承
[java.lang.Object](https://docs.oracle.com/javase/7/docs/api/java/lang/Object.html)
這個類別, 因此所有在 Java 中的物件皆存在著 `getClass()` 這個方法! 而恰巧這個方法又符合命名規則 `#1`, 因此
`getClass()` 可在 Jenkins 調用鏈中被動態呼叫!

#### 2\. 跨物件操作導致白名單繞過

前面所提到的 `ANONYMOUS_READ`, 其中 `True` 與 `False` 間最大的不同在於當在禁止的狀況下, 最初的入口點會透過
[jenkins.model.Jenkins#getTarget()](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/jenkins/model/Jenkins.java#L4682)
多做一個基於白名單的 URL 前綴檢查, 這個白名單如下:

    
    
    private static final ImmutableSet<String> ALWAYS_READABLE_PATHS = ImmutableSet.of(
        "/login",
        "/logout",
        "/accessDenied",
        "/adjuncts/",
        "/error",
        "/oops",
        "/signup",
        "/tcpSlaveAgentListener",
        "/federatedLoginService/",
        "/securityRealm",
        "/instance-identity"
    );

這也代表著一開始可選的入口限制更嚴格選擇更少, 但如果能在一個白名單上的入口找到其他物件參考, 跳到非白名單上的成員豈不可以繞過前述的 URL 前綴限制?
可能有點難理解, 這裡先來一個簡單的範例來解釋 Jenkins 的動態路由機制:

    
    
    http://jenkin.local/adjuncts/whatever/class/classLoader/resource/index.jsp/content

以上網址會依序執行下列方法

    
    
    jenkins.model.Jenkins.getAdjuncts("whatever") 
    .getClass()
    .getClassLoader()
    .getResource("index.jsp")
    .getContent()

上面的執行鏈一個串一個雖然看起來很流暢, 但難過的是無法取得回傳內容, 因此嚴格來說不能算是一個風險, 但這個例子對於理解整個漏洞核心卻有很大的幫助!

在了解原理後, 剩下的事就像是在解一個迷宮, 從
[jenkins.model.Jenkins](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/jenkins/model/Jenkins.java)
這個入口點開始, 物件中的每個成員又可以參考到一個新的物件, 接著要做的就是想辦法把中間錯綜複雜各種物件與物件間的關聯找出來, 一層一層的串下去直到迷宮出口
- 也就是危險的函數呼叫!

值得一提的是, 這個漏洞最可惜的地方應該是無法針對 SETTER 進行操作, 不然的話應該就又是另外一個有趣的 [Struts2
RCE](https://cwiki.apache.org/confluence/display/WW/S2-020) 或是 [Spring
Framework RCE](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2010-1622)
了!

### 如何利用

所以該如何利用這個漏洞呢? 簡單說, 這個漏洞所能做到的事情就只是透過物件間的參考去繞過 ACL 政策,
但在此之前我們必須先找到一個好的跳板好讓我們可以更方便的在物件中跳來跳去, 這裡我們選用了下面這個跳板:

    
    
    /securityRealm/user/[username]/descriptorByName/[descriptor_name]/

這個跳板會依序執行下面方法

    
    
    jenkins.model.Jenkins.getSecurityRealm()
    .getUser([username])
    .getDescriptorByName([descriptor_name])

在 Jenkins 中可以被操作的物件都會繼承一個
[hudson.model.Descriptor](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/Descriptor.java)
類別, 而繼承這個類別的物件都可以透過
[hudson.model.DescriptorByNameOwner#getDescriptorByName(String)](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/DescriptorByNameOwner.java#L51)
去存取, 所以總體來說, 可透過這個跳板取得在 Jenkins 中約 500 個 Despicable 的物件類別!

不過雖是如此, 由於 Jenkins 的設計模式, 大部分開發者在危險動作之前都會再做一次權限檢查, 所以即使可呼叫到 [Script
Console](http://jenkins.local/script) 但在沒有 `Jenkins.RUN_SCRIPTS` 權限的情況下也無法做任何事
:(

但這個漏洞依然不失成為一個很好的膠水去繞過第一層的 ACL 限制串起其他的漏洞, 為後續的利用開啟了一道窗! 以下我們給出三個串出漏洞鏈的例子!
(雖然只介紹三種, 但由於這個漏洞玩法非常自由可串的絕不只如此, 推薦有興趣的同學可在尋找更多的漏洞鏈!)

P.S. 值得注意的一點是, 在 `getUser([username])` 的實現中會呼叫到 `getOrCreateById(...)` 並且傳入
`create=True` 導致在記憶體中創造出一個暫存使用者(會出現在使用者列表但無法進行登入操作), 雖然無用不過也被當成一個漏洞記錄在
[SECURITY-1128](https://jenkins.io/security/advisory/2018-10-10/)

#### 1\. 免登入的使用者資訊洩漏

在測試 Jenkins 時, 最怕的就是要進行字典檔攻擊時卻不知道該攻擊哪個帳號, 畢竟帳號永遠比密碼難猜! 這時這個漏洞就很好用了XD

由於 Jenkins 對搜尋的功能並沒有加上適當的權限檢查, 因此在 `ANONYMOUS_READ=False` 的狀況下可以透過修改 `keyword`
參數從 a 到 z 去列舉出所有使用者!

##### PoC:

    
    
    http://jenkins.local/securityRealm/user/admin/search/index?q=[keyword]

![img](https://images.seebug.org/content/images/2019/02/18/1550479185000-3.png-w331s)

除此之外也可搭配由 `Ananthapadmanabhan S R` 所回報的
[SECURITY-514](https://jenkins.io/security/advisory/2017-10-11/#user-remote-api-disclosed-users-email-addresses) 進一步取得使用者信箱, 如:

    
    
    http://jenkins.local/securityRealm/user/admin/api/xml

#### 2\. 與 CVE-2018-1000600 搭配成免登入且有完整回顯的 SSRF

下一個要串的漏洞則是
[CVE-2018-1000600](https://jenkins.io/security/advisory/2018-06-25/#SECURITY-915),
這是一個由 [Orange Tsai](https://twitter.com/orange_8361)(對就是我XD) 所回報的漏洞,
關於這個漏洞官方的描述是:

> CSRF vulnerability and missing permission checks in GitHub Plugin allowed
> capturing credentials

在已知 Credentials ID 的情形下可以洩漏任意 Jenkins 儲存的帳密, 但 Credentials ID 在沒指定的情況下會是一組隨機的
UUID 所以造成要利用這個漏洞似乎變得不太可能 (如果有人知道怎麼取得 Credentials ID 請告訴我!)

雖然在不知道 Credentials ID 的情況下無法洩漏任何帳密, 但這個漏洞其實不只這樣, 還有另一個玩法! 關於這個漏洞最大的危害其實不是
CSRF, 而是 SSRF!

不僅如此, 這個 SSRF 還是一個有回顯的 SSRF! 沒有回顯的 SSRF 要利用起來有多困難我想大家都知道 :P 因此一個有回顯的 SSRF
也就顯得何其珍貴!

##### PoC:

    
    
    http://jenkins.local/securityRealm/user/admin/descriptorByName/org.jenkinsci.plugins.github.config.GitHubTokenCredentialsCreator/createTokenByPassword
    ?apiUrl=http://169.254.169.254/%23
    &login=orange
    &password=tsai

![img](https://images.seebug.org/content/images/2019/02/18/1550479185000-4-1550479133129.png-w331s)

#### 3\. 未認證的遠端代碼執行

> 所以廢話少說, RCE 在哪?

為了最大程度的去利用這個漏洞, 我也挖了一個 **非常有趣** 的 RCE 可以與這個漏洞搭配使用成為一個真正意義上不用認證的 RCE!
但由於這個漏洞目前還在 Responsible Disclosure 的時程內, 就請先期待 Hacking Jenkins Part 2 囉!
(預計二月中釋出!)

### TODO

這裡是一些我想繼續研究的方向, 可以讓這個漏洞變得更完美! 如果你發現了下面任何一個的解法請務必告訴我, 我會很感激的XD

  * 在 `ANONYMOUS_READ=False` 的權限下拿到 `Plugin` 的物件參考, 如果拿到的可以繞過 [CVE-2018-1999002](https://jenkins.io/security/advisory/2018-07-18/#SECURITY-914) 與 [CVE-2018-6356](https://jenkins.io/security/advisory/2018-02-14/#SECURITY-705) 所需的最小權限限制, 成為一個真正意義上的免登入任意讀檔!
  * 在 `ANONYMOUS_READ=False` 的權限下找出另一組跳板去呼叫 `getDescriptorByName(String)`. 為了修復 [SECURITY-672](https://jenkins.io/security/advisory/2018-08-15/#SECURITY-672), Jenkins 從 2.138 開始對 [hudson.model.User](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/User.java) 增加判斷 `Jenkins.READ` 的[檢查](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/User.java#L1026), 導致原有的跳板失效!

### 致謝

最後, 感謝 Jenkins Security 團隊尤其是 Daniel Beck 的溝通協調與漏洞修復! 這裡是一個簡單的回報時間軸:

  * May 30, 2018 - 回報漏洞給 Jenkins
  * Jun 15, 2018 - Jenkins 修補並分配 CVE-2018-1000600
  * Jul 18, 2018 - Jenkins 修補並分配 CVE-2018-1999002
  * Aug 15, 2018 - Jenkins 修復並分配 CVE-2018-1999046
  * Dec 05, 2018 - Jenkins 修補並分配 CVE-2018-1000861
  * Dec 20, 2018 - 回報 Groovy 漏洞給 Jenkins
  * Jan 08, 2019 - Jenkins 修復 Groovy 漏洞並分配 CVE-2019-1003000, CVE-2019-1003001, CVE-2019-1003002

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/816/>

