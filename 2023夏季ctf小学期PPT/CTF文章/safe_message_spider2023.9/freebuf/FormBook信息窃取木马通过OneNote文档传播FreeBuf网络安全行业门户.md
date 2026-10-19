攻击者长期以来一直使用 Office 文档来传播恶意软件，也没有放弃尝试新的攻击方式。近期，研究人员发现 Formbook 攻击者开始使用 OneNote
文档文件。

Formbook 是信息窃取木马，2016 年开始在地下论坛出售，2018
年启动恶意软件即服务。该恶意软件可以从各种浏览器和应用程序窃取数据，还有按键记录与屏幕截图功能。

2022 年 12 月 6 日，研究人员注意到垃圾邮件检测系统检出了 .one 扩展名的 OnoNote 附件文件。通过电子邮件发送 .one
文件并不常见，引起了研究人员的注意。

![image.png-537.8kB](https://image.3001.net/images/20221213/1670943843_63989463c0ac1a4855392.png!small)查看电子邮件

内容的大意为：

> 亲爱的客户下午好，希望您一切顺利。
>
> 我叫 xxx，来自 xxx 公司的采购团队。
>
> 请您提供以下信息的报价：
>
> 期待您的恢复，非常感谢！
>
> 祝好！
>
> 联系方式：

打开 OneNote 附件后，会显示图片诱饵。点击图片的“查看文档”时，会弹出安全警告。

![image.png-171.9kB](https://image.3001.net/images/20221213/1670943845_63989465a43828bc7fa23.png!small)OneNote
附件文件

解析了 pdf172.one 的内容后，发现与图片中“查看文档”相关的有 Windows 脚本文件（WSF）。一旦点击“查看文档”，就会执行 WSF 文件。

可能是为了逃避检测，WSF 文件名在 invoice 后包含一个从右到左的覆盖字符，这会导致后面的文本反向显示。因此，应用程序可能不显示为
docx.wsf，而是将其显示为 fsw.xcoD。

![image.png-466.3kB](https://image.3001.net/images/20221213/1670943847_6398946729548ac1a7a73.png!small)覆盖在诱饵图片上的
WSF 文件

用户无视警告仍然打开时，恶意行为就触发了。启动 PowerShell 通过 a0745450[.]xsph[.]ru 下载并执行两个文件。

![image.png-1357.2kB](https://image.3001.net/images/20221213/1670943848_639894684da9578c59600.png!small)OneNote
附件中包含的 WSF

通过 a0745450[.]xsph[.]ru/INVESTEMENT[.]one 下载 OneNote 诱饵文件并保存为
%temp%\invoice.one。启动诱饵文件，隐藏第二个文件的下载。

第二个文件为可执行文件，通过 a0745450[.]xsph[.]ru/DT6832.exe 下载并保存为
%temp%\system32.exe，该可执行文件为 Formbook 恶意软件。

![image.png-117.1kB](https://image.3001.net/images/20221213/1670943850_6398946a59058e2043c36.png!small)Formbook
恶意软件

OneNote 已经正式加入了攻击者利用的范畴，在对 Office 恶意文档进行分析时不要忘了此类文档。

## IOC

> 81bd8c431811f83f335735847d42fb4f64f80960  
> d5ee9183be486bf153d7666ca4301e600ea06087  
> 33d8fb75f471bdc4ebaff053e87146721f32667a  
> a0745450[.]xsph[.]ru/DT6832[.]exe  
> a0745450[.]xsph[.]ru/INVESTEMENT[.]one

## 参考来源

> [Trustwave](https://www.trustwave.com/en-us/resources/blogs/spiderlabs-> blog/trojanized-onenote-document-leads-to-formbook-malware/)

