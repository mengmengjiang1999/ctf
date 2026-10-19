近日，研究人员发现安卓平台上冒充 ChatGPT 的恶意软件激增。随着 OpenAI 研发的 GPT 3.5 与 GPT 4.0
的发布，全世界越来越多的人对其感兴趣并想要尝试。本文对两种较为活跃的恶意软件进行了深入分析：一种是伪装成 SuperGPT 的 Meterpreter
木马、另一种则是伪装成 ChatGPT 的恶意扣费应用程序。

尽管 Google Play 的的安卓平台的官方应用商店，但用户也可以通过网站或者电子邮件等其他来源安装应用程序，用户是能够获得未经 Google
安全审查的应用程序的。

## 介绍

OpenAI 创建了一个名为 Chat Generative Pre-trained Transformer（简称
ChatGPT）的应用程序，该程序由大模型（LLM）驱动，目前已经开发到第四个版本。ChatGPT 于 2022 年 11 月 30
首次公开发布，由于其非凡的交互问答能力，迅速引起了世人的注意。尽管 ChatGPT 的回答并不一定准确，但在前期用户为了使用仍然排了大长队。

如此流行的社会风潮，也被攻击者盯上了。就像之前攻击者利用 COVID-19
在全世界范围内的大流行，来传播那些打着“健康与保健”旗号的恶意程序。过去已经发现了与 ChatGPT 话题相关的恶意软件，攻击者并未放弃而是越发关注。

## Meterpreter 木马

名为 SuperGPT - AI with GPT-4 的恶意程序，将自身描述为是由 GPT-4 驱动的 AI 助手。SuperGPT
不仅能够帮助用户撰写电子邮件、编写文章，还能够进行语音识别与跨语言翻译。

该恶意软件的 MainActivity 类中包含一个引用 ChatGPT 官方 URL 地址的字符串变量。名为 v3.v 是一个自定义
WebViewClient 实现，主要实现了两个重定向规则：

  * 如果 URL 包含 <https://openai.com/blog/chatgpt/>则重定向到 <https://chat.openai.com/chat>
  * 如果 URL 包含 beta.openai.com，则在延迟 1 秒后重定向到 <https://chat.openai.com/chat>

![image.png-22.1kB](https://image.3001.net/images/20230619/1687187528_649070488ad32e36225b4.png!small)应用程序图标

![image.png-75.9kB](https://image.3001.net/images/20230619/1687187529_6490704950b723a5cf0e0.png!small)应用程序截图

根据 VirusTotal 的信息，该样本最早在 2023 年 3 月 16 日 02:06:04 在尼加拉瓜提交的，文件名为 2021id.apk。

### 载荷植入

比较恶意应用程序与合法应用程序之间的差异，很明显可以发现恶意代码为以下 Smali 代码的部分：

![image.png-47.6kB](https://image.3001.net/images/20230619/1687187529_64907049e17f8abc70b8a.png!small)新增恶意
Smail 代码

Rapid 7 发布了最早基于 Java 的安卓平台 Meterpreter Stager 的源代码。通过 MainService 类调用 Payload
类的 start 方法实现恶意功能，而 MainService 类可以：

  * 由 MainActivity 类启动
  * 在设备启动完成后由 MainBroadcastReceiver 类启动

该恶意代码主要执行如下操作：

  1. 解析存储在 configBytes 字节数组的硬编码配置，该部分未经混淆
  2. 通过 Power Manager 系统服务的部分唤醒锁定功能确保 CPU 持续运行
  3. 按需隐藏应用程序的图标
  4. 与攻击者建立远程连接
  5. 连接后下载其他 Payload，实现完整功能

![image.png-172.8kB](https://image.3001.net/images/20230619/1687187530_6490704a7d1c68aa070a0.png!small)配置字节数组

对 SuperGPT 这个特定的样本来说，以下操作会触发 Meterpreter：

  1. 名为 com.dominapp.supergpt.eluad.Vojnd 的服务在 BOOT_COMPLETED 操作后启动
  2. 名为 com.dominapp.supergpt.eluad.C2094e 的线程生成并运行
  3. 名为 com.dominapp.supergpt.eluad.Dapjs 类的 Main 方法被调用

该样本中的 C&C 服务器为 tcp://Gwdidkfkf-47070.portmap[.]io:47070，而 portmap.io
是一个提供免费端口转发的服务。

### 证书信息

签发该样本的数字签名证书是属于攻击者的，特征如下所示：

  * 电子邮件地址：lkpandey950@gmail.com
  * 组织名称：Hax4Us
  * 地址位置：印度德里的 Shahdara 地区
  * 证书有效期：2020 年 7 月 17 日至 2047 年 12 月 2 日
  * 序列号：1a505d53b1c75046a81acb021fdb5f99936b75db
  * SHA-1 指纹：65094A64233F818AEF5A4EDE90AC1D0C5A569A8B

在 VirusTotal 上查询，与该证书相关的其余一百多个样本文件都是恶意的：

![image.png-134.6kB](https://image.3001.net/images/20230619/1687187531_6490704baf306430d717b.png!small)相关的样本文件

## 恶意扣费

另一组恶意应用程序则是通过与 ChatGPT 描述相关的网页进行分发：

![image.png-596.9kB](https://image.3001.net/images/20230619/1687187532_6490704c690492d062aff.png!small)钓鱼网页

这些恶意应用程序都会以 OpenAI 的图标作为应用程序的图标，还会使用与 ChatGPT 相关的虚假描述信息，非常具有迷惑性。

![image.png-153.4kB](https://image.3001.net/images/20230619/1687187533_6490704dcb25273d49af6.png!small)OpenAI
图标

这些恶意应用程序会向泰国的付费号码发送短信，以进行恶意高额扣费。具体实现依靠发送短信的安卓权限
android.permission.SEND_SMS，并且对泰国进行了限定。恶意应用程序还使用了OneSignal，这是帮助应用程序通过推送通知发送消息的服务。

例如应用程序通过
hxxps[://]api[.]onesignal[.]com/apps/af63b434-ec50-46a0-9374-d57a383f2e03/android_params[.]js
获取的配置信息如下所示。其中，android_sender_id 字段被硬编码为 +661-9406-4544。

    
    
    {"awl_list": {},"android_sender_id": "660194064544","chnl_lst": [],"outcomes": {"direct": {"enabled": false},"indirect": {"notification_attribution": {"minutes_since_displayed": 60,"limit": 10},"enabled": false},"unattributed": {"enabled": false}},"receive_receipts_enable": false}

这些样本文件使用通用证书进行签名，典型属性如下所示：

  * 证书有效期：2008 年 0 月 29 日至 2035 年 7 月 17 日
  * 序列号：936eacbe07f201df
  * SHA-1 指纹：61ED377E85D386A8DFEE6B864BD85B0BFAA5AF81

样本大概分为两批：第一批样本向一个硬编码的泰国付费号码发送短信，并使用 OneSignal
服务；第二批样本向另外两个硬编码的泰国付费号码发送短信，并且不再使用 OneSignal 获取配置信息。第一批样本大约在 2023 年 2
月被使用，第二批样本大约在 2023 年 3 月被使用。

### 第一批样本

![image.png-72.2kB](https://image.3001.net/images/20230619/1687187534_6490704eede6d24c2a477.png!small)第一批样本的静态信息汇总

### 第二批样本

![image.png-71.1kB](https://image.3001.net/images/20230619/1687187535_6490704fb2a6f2e793758.png!small)第二批样本的静态信息汇总

## 结论

ChatGPT 相关主体的恶意应用程序对移动设备的安全与隐私带来了极大的挑战与威胁，攻击者可能会窃取敏感信息、监视用户活动并且给受害者带来巨大的经济损失。

## IOC

> af19ca9213a20263c30584a2bf260dcdb3b4eafa4f43af10824af781573a2314  
> 2980329fa5eaed0f5625e961572f7ae8136ca7df30cca9e9c8783c827627b692  
> 391e8f394af425f1e7edff6aea1605aa89f2fb0233c44e70cff265fc60ec3b1b  
> d1844bf3865c7d2e4745baa2496297937821171d7a3ad4412b0a4e767bc32b5e  
> d1b1813f7975b7117931477571a2476decff41f124b84cc7a2074dd00b5eba7c  
> b787d5ef4a0c350a9f62f55907c8ef6d92bf7699b8544fabff5a263e52a2d0d1  
> be757541584cc2dc2e7adacf7a5186be07d474f06c8698a938589f86ce56ea34  
> e9bb6d04d796eb147b9d73a7df91fb9e6a99e0be8a41a61329d600a9dfe8b1ae  
>
> hxxps://api.onesignal[.]com/apps/af63b434-ec50-46a0-9374-d57a383f2e03/android_params.js  
> tcp://Gwdidkfkf-47070.portmap[.]io

## 参考来源

> [Unit42](https://unit42.paloaltonetworks.com/android-malware-poses-as-> chatgpt/)

