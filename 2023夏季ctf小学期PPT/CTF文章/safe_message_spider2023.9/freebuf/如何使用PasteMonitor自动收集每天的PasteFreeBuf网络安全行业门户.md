![](https://image.3001.net/images/20220119/1642605066_61e82a0a7bba4751609e9.png!small)

## 关于PasteMonitor

PasteMonitor是一款针对Pastebin的数据爬取工具，该工具可以通过爬取Pastebin
API来收集站点上用户每天发布的Paste。除此之外，广大研究人员还可以通过设置字典来爬取与关键词匹配的Paste内容。

PasteMonitor工具允许我们执行下列两大主要任务（仅供教育目的使用）：

 **1、下载每日新发布的公开Paste：**

![](https://image.3001.net/images/20220119/1642605080_61e82a182d7d51aae3855.png!small)

平均每天发布的Paste数量：1000-3000，文件类型为“.txt”。

 **2、自动发送电子邮件通知**

我们可以设置一个字典文件，然后当PasteMonitor爬取到了跟字典中关键词匹配的内容时，工具便会给用户发送电子邮件通知：

![](https://image.3001.net/images/20220119/1642605088_61e82a20dfeee489f23aa.png!small)

如果目标Paste已经无法直接访问的话，我们还可以在自己的电脑或服务器上通过Paste的ID来寻找到Paste内容（下图中的Paste
ID为“WJq2YxPg”）：

![](https://image.3001.net/images/20220119/1642605095_61e82a274122cd6fb691b.png!small)

## 工具准备

在开始使用PasteMonitor之前，我们需要准备好下列内容：

> 1、获取一个[ _Pastebin专业版账号_](https://pastebin.com/pro)
>
> 2、在“[ _账号_ _&_
> _白名单IP_](https://pastebin.com/doc_scraping_api)”中输入自己电脑/服务器的IP地址
>
> 3、激活电子邮箱账号，并授权第三方应用程序访问
>
> 4、启用[ _两步验证功能_](https://myaccount.google.com/u/2/signinoptions/two-step-> verification)
>
> 5、[ _生成一个App密码_](https://myaccount.google.com/u/2/apppasswords)【[
> _参考资料_](https://ljmocic.medium.com/send-an-email-using-python-and-> gmail-4ebc980eae9b)】

接下来，将下列内容写入至“pastemonitor.py”中：

> 1、电子邮箱凭证（邮件地址和密码）
>
> 2、邮箱通知接收人（收件人）

## 字典文件

在项目提供的“wordlist.txt”文件中，我们可以按行添加需要匹配的关键词。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/pixelbubble/PasteMonitor.git

## 工具依赖安装

    
    
    pip3 install -r requirements.txt

## 工具使用

该工具的使用也非常简单，在配置好相关的参数选项之后，直接运行下列命令即可：

    
    
    python3 pastemonitor.py

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://choosealicense.com/licenses/mit/)开源许可证协议。

## 项目地址

 **PasteMonitor：** 【[
_GitHub传送门_](https://github.com/pixelbubble/PasteMonitor)】

## 参考资料

> [
> _https://pastebin.com/doc_scraping_api_](https://pastebin.com/doc_scraping_api)
>
> [ _https://pastebin.com/pro_](https://pastebin.com/pro)
>
> [ _https://myaccount.google.com/u/2/signinoptions/two-step-> verification_](https://myaccount.google.com/u/2/signinoptions/two-step-> verification)
>
> [
> _https://myaccount.google.com/u/2/apppasswords_](https://myaccount.google.com/u/2/apppasswords)
>
> [ _https://ljmocic.medium.com/send-an-email-using-python-and-> gmail-4ebc980eae9b_](https://ljmocic.medium.com/send-an-email-using-python-> and-gmail-4ebc980eae9b)

