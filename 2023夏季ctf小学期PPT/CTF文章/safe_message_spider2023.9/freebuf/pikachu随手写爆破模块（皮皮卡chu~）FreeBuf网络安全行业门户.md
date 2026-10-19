## **一、暴力破解模块**

###  **1** **、基于表单的暴力破解**

 **进入环境**

![1630325968_612cccd01e9ce7b3c15e2.png!small](https://image.3001.net/images/20210830/1630325968_612cccd01e9ce7b3c15e2.png!small)

 **随便输入点什么**

![1630325979_612cccdb47ee2411ae6a4.png!small](https://image.3001.net/images/20210830/1630325979_612cccdb47ee2411ae6a4.png!small)

 **提示的是账号密码不存在，因为不涉及到验证码所以可以采用爆破**

 **使用** **Burp suite** **进行爆破，先在浏览器中打开代理（采用的火狐的** **FoxyProxy** **）**

 **配置如下** **ip** **：** **127.0.0.1** **端口** **8080**

![1630325988_612ccce4bc9b751d52d0c.png!small](https://image.3001.net/images/20210830/1630325988_612ccce4bc9b751d52d0c.png!small)

 **打开代理后打开** **Burp suite** **抓包**

![1630326000_612cccf054e7e9f07f598.png!small](https://image.3001.net/images/20210830/1630326000_612cccf054e7e9f07f598.png!small)

 **然后右键发送到** **intruder**

![1630326007_612cccf74ff752846d4b2.png!small](https://image.3001.net/images/20210830/1630326007_612cccf74ff752846d4b2.png!small)

 **选中** **username** **和** **password** **后的内容点击右侧** **add**
**，将账号密码选定为要爆破的对象**

 **选择爆破模式为** **Cluster bomb**

 **爆破模式四种类型介绍**

 **Sniper** **:** **只针对一个目标，配置一个** **payload** **，适用于单一爆破**

 **Battering ram** **：可以设置多个目标，配置一个** **payload** **，**

 **Pitchfork** **：可以设置多个目标，设置多个** **payload** **，按顺序内容顺序对应一一配对爆破（这有啥用？）**

 **Clusterbomb** **：可以设置多个目标，设置多个** **payload** **，遍历所有组合爆破，最好用**

 **设置完爆破模式后进入** **payloads** **界面，给每个目标设置爆破字典**

 **（可以使用自己的比较高级的字典，这里仅做测试，所以就连上正确的账户密码又随便手写几个）**

![1630326020_612ccd044dd2e5003372a.png!small](https://image.3001.net/images/20210830/1630326020_612ccd044dd2e5003372a.png!small)

![1630326029_612ccd0ddb21235541515.png!small](https://image.3001.net/images/20210830/1630326029_612ccd0ddb21235541515.png!small)

 **配置完成后开始爆破**

![1630326038_612ccd16de3df487c935b.png!small](https://image.3001.net/images/20210830/1630326038_612ccd16de3df487c935b.png!small)

 **结果按长度排序后，与其他不同的就是爆破到的正确的信息**

 **输入一下，测试结果，成功**

![1630326049_612ccd21856a1e4b9380e.png!small](https://image.3001.net/images/20210830/1630326049_612ccd21856a1e4b9380e.png!small)

###  **2.** **验证码绕过（** **on server** **）**

 **进入环境**

![1630326056_612ccd28799abfca04df6.png!small](https://image.3001.net/images/20210830/1630326056_612ccd28799abfca04df6.png!small)

 **发现有验证码，先测试验证码效果**

![1630326062_612ccd2e3ebe8aaf20dd4.png!small](https://image.3001.net/images/20210830/1630326062_612ccd2e3ebe8aaf20dd4.png!small)

![1630326105_612ccd59442264666704d.png!small](https://image.3001.net/images/20210830/1630326105_612ccd59442264666704d.png!small)

 **输入错误验证码会提示验证码错误，输入正确验证码会提示账号密码错误**

 **打开** **Burp suite,** **将** **proxy** **下的** **intercept** **打开（中间选项卡为**
**intercept is on** **）随便输入数据开始抓包**

![1630326118_612ccd6654871ae489f08.png!small](https://image.3001.net/images/20210830/1630326118_612ccd6654871ae489f08.png!small)

![1630326125_612ccd6d9c93c66ebce55.png!small](https://image.3001.net/images/20210830/1630326125_612ccd6d9c93c66ebce55.png!small)

 **右键发送到** **repeater** **，修改账号密码** **send** **一次**

![1630326131_612ccd730e089d25171f4.png!small](https://image.3001.net/images/20210830/1630326131_612ccd730e089d25171f4.png!small)

 **提示用户名或密码错误，再修改一次数据，再** **send** **一下**

![1630326139_612ccd7b322ace5ad335b.png!small](https://image.3001.net/images/20210830/1630326139_612ccd7b322ace5ad335b.png!small)

 **依旧提示用户名或密码错误，说明了验证码没有失效，那么可以一直使用，那么直接爆破用户名和密码就好**

 **重复上面的暴力破解内容，直接成功**

![1630326148_612ccd84935dd08b76584.png!small](https://image.3001.net/images/20210830/1630326148_612ccd84935dd08b76584.png!small)

###  **3.** **验证码绕过（** **on client** **）**

 **进入环境**

![1630326154_612ccd8abf88bec9ddba2.png!small](https://image.3001.net/images/20210830/1630326154_612ccd8abf88bec9ddba2.png!small)

 **第一种方法：随便输入点什么（验证码要输入对），打开** **Burp suite** **抓包，送入** **repeater** **，**
**send** **一下**

![1630326161_612ccd9170e9a1fd4613d.png!small](https://image.3001.net/images/20210830/1630326161_612ccd9170e9a1fd4613d.png!small)

 **提示用户名或验证码错误，在改一下信息再查看**

![1630326167_612ccd97a6ccaee08ef15.png!small](https://image.3001.net/images/20210830/1630326167_612ccd97a6ccaee08ef15.png!small)

 **依旧提示用户名或验证码错误，证明可以绕过，直接爆破就好，重复爆破步骤**

 **第二种方法：利用浏览器的** **js** **禁用插件，我采用的火狐浏览器的** **script blocker ultimate**
**，选择** **block all** **模式**

 **禁用后，验证码会失效**

![1630326187_612ccdab385835321e4ce.png!small](https://image.3001.net/images/20210830/1630326187_612ccdab385835321e4ce.png!small)

  

 **然后直接按照普通爆破做就好**

##  **4.token** **放爆破？**

 **进入环境**

![1630326199_612ccdb70267aef81bcab.png!small](https://image.3001.net/images/20210830/1630326199_612ccdb70267aef81bcab.png!small)

 **随便输入点什么，打开** **Burp suite** **抓包，送入** **repeater** **，看到多了个** **token**
**值，先** **send** **一下**

![1630326204_612ccdbc90753d47e1eec.png!small](https://image.3001.net/images/20210830/1630326204_612ccdbc90753d47e1eec.png!small)

 **提示用户名或验证码错误，在改一下信息再查看**

![1630326213_612ccdc545addc6136b63.png!small](https://image.3001.net/images/20210830/1630326213_612ccdc545addc6136b63.png!small)

 **再次输入后提示** **token** **出错，说明每次发次发送消息，** **token** **值也要一起改变。**

 **右键发送到** **intruder** **，用** **cluster bomb** **模式将用户名，密码和** **token**
**设置为爆破目标**

![1630326220_612ccdccb1027d417475c.png!small](https://image.3001.net/images/20210830/1630326220_612ccdccb1027d417475c.png!small)

 **依次配置** **payload** **，针对** **token** **的** **payload** **选用** **recursive
grep** **类型**

![1630326231_612ccdd70491bde82636b.png!small](https://image.3001.net/images/20210830/1630326231_612ccdd70491bde82636b.png!small)

 **再点入** **options** **，线程设置为** **1** **，在** **Grep - Extract ，点 Add ，弹出页面**
**后再** **点击 Refetch response ，** **选中** **token** **的值，自动获取范围，保存**

![1630326236_612ccddc5bf182af478da.png!small](https://image.3001.net/images/20210830/1630326236_612ccddc5bf182af478da.png!small)

 **在** **Redirections 选择Always；**

![1630326242_612ccde2cb62a76088364.png!small](https://image.3001.net/images/20210830/1630326242_612ccde2cb62a76088364.png!small)

 **在Payloads中的“Initial payload for first request”添加** **包里的** **token** **值**

 **开始爆破，筛选长度，最后得到账户密码**

![1630326248_612ccde844d44332f90e0.png!small](https://image.3001.net/images/20210830/1630326248_612ccde844d44332f90e0.png!small)

  

