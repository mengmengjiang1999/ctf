学习安全技术，不学习编辑器的漏洞利用怎么行。因为在某个时代，利用编辑器上传shell得到权限是以前web安全的一个时代潮流，这种漏洞的利用在当前大部分安全从业者记忆里还是比较深刻地。为了了解那个时代，本篇文章就编辑器的漏洞利用做一个简单地学习。

![1648480653_6241d18da0b3463f6c860.png!small](https://image.3001.net/images/20220328/1648480653_6241d18da0b3463f6c860.png!small)

## 0x1 fckeditor 编辑器漏洞分析

既然是编辑器 那个就直接找上传点呗。默认的fckeditor 的上传地方是

/editor/filemanager/browser/default/connectors/test.html

/editor/filemanager/upload/test.html

/editor/filemanager/connectors/test.html

/editor/filemanager/connectors/uploadtest.html

本次环境发现上传点是/editor/filemanager/connectors/test.html

![1648480671_6241d19f26314ca3cd21e.png!small](https://image.3001.net/images/20220328/1648480671_6241d19f26314ca3cd21e.png!small)

先别急着上传，fckeditor编辑器可以找到编辑器的版本，如果有版本漏洞可以直接利用。

查看编辑器版本：

 _<http://x.x.x.x:47989/fckeditor/_whatsnew.html>_

![1648480685_6241d1adc46409ac03264.png!small](https://image.3001.net/images/20220328/1648480685_6241d1adc46409ac03264.png!small)

直接搜编辑器版本漏洞

![1648480697_6241d1b9af0003f7c503d.png!small](https://image.3001.net/images/20220328/1648480697_6241d1b9af0003f7c503d.png!small)

找到了，那我们就直接利用，不做无畏的挣扎。哈哈,恰好主机系统windows/iis 6。

抓包 改文件名为a.asp;jpg 利用的就是windows/iis 6解析漏洞

上传成功后点击箭头所指，我忘了点击哪一个了都试一试，然后就能得到路径和文件名

![1648480716_6241d1cc03de021a9b320.png!small](https://image.3001.net/images/20220328/1648480716_6241d1cc03de021a9b320.png!small)

直接菜刀等工具连接就行了。

![1648480734_6241d1de81ede84f082d2.png!small](https://image.3001.net/images/20220328/1648480734_6241d1de81ede84f082d2.png!small)![1648480741_6241d1e5ab87d0a217018.png!small](https://image.3001.net/images/20220328/1648480741_6241d1e5ab87d0a217018.png!small)

## 0x2 eWebEditor编辑器漏洞分析

介绍：

![1648480757_6241d1f5eac595a2aea74.png!small](https://image.3001.net/images/20220328/1648480757_6241d1f5eac595a2aea74.png!small)

![1648480763_6241d1fb66ec2953162da.png!small](https://image.3001.net/images/20220328/1648480763_6241d1fb66ec2953162da.png!small)

访问之后是这样的，你点击是没有办法点击的，由于版本太老，所以需要老的ie 浏览器，windows7 或者win-2008 ，即是是在win10 的ie
浏览器开启兼容型视图模式，也不行。

利用：

它有一个默认数据库路径：/db/ewebeditor.mdb，可直接下载

![1648480775_6241d20770d5c94840925.png!small](https://image.3001.net/images/20220328/1648480775_6241d20770d5c94840925.png!small)

把文件下载下来之后，用数据库管理软件打开

![1648480786_6241d21292579346e6896.png!small](https://image.3001.net/images/20220328/1648480786_6241d21292579346e6896.png!small)

在系统表那块找到管理员的用户密码，不过都是cmd 加密后的拿去碰撞解密

解密后得到账户密码：

![1648480799_6241d21f4314d6c17a91f.png!small](https://image.3001.net/images/20220328/1648480799_6241d21f4314d6c17a91f.png!small)

![1648480806_6241d2261eb8607a9a51f.png!small](https://image.3001.net/images/20220328/1648480806_6241d2261eb8607a9a51f.png!small)

利用编辑器的后台登录管理员，默认后台页面admin_login.asp

![1648480817_6241d23158031f7475b30.png!small](https://image.3001.net/images/20220328/1648480817_6241d23158031f7475b30.png!small)

点击样式管理，然后新增样式

![1648480829_6241d23da29ac0358a506.png!small](https://image.3001.net/images/20220328/1648480829_6241d23da29ac0358a506.png!small)

然后在下面标记的地方更改文件类型

![1648480840_6241d248ad4f02590257e.png!small](https://image.3001.net/images/20220328/1648480840_6241d248ad4f02590257e.png!small)

确认之后。提交

![1648480852_6241d254d201f538e37da.png!small](https://image.3001.net/images/20220328/1648480852_6241d254d201f538e37da.png!small)

接着进入样式管理，选择添加的样式，点击工具栏，为这个样式添加上传图片的工能

![1648480864_6241d260a996f25e35656.png!small](https://image.3001.net/images/20220328/1648480864_6241d260a996f25e35656.png!small)

新增一个工具栏

![1648480875_6241d26bb498bf9055750.png!small](https://image.3001.net/images/20220328/1648480875_6241d26bb498bf9055750.png!small)

![1648480880_6241d270e47e4fd7874af.png!small](https://image.3001.net/images/20220328/1648480880_6241d270e47e4fd7874af.png!small)

然后按钮设置

![1648480891_6241d27b00c013a53efc3.png!small](https://image.3001.net/images/20220328/1648480891_6241d27b00c013a53efc3.png!small)

保存即可

再次进入样式管理

![1648480901_6241d28548cfd6c18f9f1.png!small](https://image.3001.net/images/20220328/1648480901_6241d28548cfd6c18f9f1.png!small)

点击预览

![1648480913_6241d291585ea3bbd6ce4.png!small](https://image.3001.net/images/20220328/1648480913_6241d291585ea3bbd6ce4.png!small)

插入一个cer文件的asp 木马即可

![1648480924_6241d29c3c603bf3e26d6.png!small](https://image.3001.net/images/20220328/1648480924_6241d29c3c603bf3e26d6.png!small)

点击确定

![1648480936_6241d2a810d687d0bcab1.png!small](https://image.3001.net/images/20220328/1648480936_6241d2a810d687d0bcab1.png!small)

然后点击代码得到路径

![1648480947_6241d2b3bb371b86d9e4b.png!small](https://image.3001.net/images/20220328/1648480947_6241d2b3bb371b86d9e4b.png!small)

工具连接即可

![1648480958_6241d2be6a12d9558c2fd.png!small](https://image.3001.net/images/20220328/1648480958_6241d2be6a12d9558c2fd.png!small)

0x3 DotNetTextBox编辑器漏洞利用

DotNetTextBox默认图片上传路径为system_dntb/uploadimg.aspx，

那么我们尝试文件上传

![1648480969_6241d2c9d4ccd9fc8650a.png!small](https://image.3001.net/images/20220328/1648480969_6241d2c9d4ccd9fc8650a.png!small)

发现限制了。前端更改

![1648480981_6241d2d5ab02f86d9f62e.png!small](https://image.3001.net/images/20220328/1648480981_6241d2d5ab02f86d9f62e.png!small)

还是不能，同样是查找漏洞，利用更改cookie 来更改上传的路径

刷新，抓包 在cookie 处更改

Cookie: cookie:UserType=0; IsEdition=0; Info=1;
uploadFolder=../system_dntb/Upload/

![1648480994_6241d2e2b260c7749c536.png!small](https://image.3001.net/images/20220328/1648480994_6241d2e2b260c7749c536.png!small)

![1648481000_6241d2e8365355ffee1a4.png!small](https://image.3001.net/images/20220328/1648481000_6241d2e8365355ffee1a4.png!small)

此时便可以上传了，同样是利用iis/6.0

只不过是 asp;,jpg

上传shell 改名字后缀为asp;,jpg

![1648481019_6241d2fb16bcfd1276cb6.png!small](https://image.3001.net/images/20220328/1648481019_6241d2fb16bcfd1276cb6.png!small)

![1648481023_6241d2ffb52c88f8df67c.png!small](https://image.3001.net/images/20220328/1648481023_6241d2ffb52c88f8df67c.png!small)

然后连接就行了。

