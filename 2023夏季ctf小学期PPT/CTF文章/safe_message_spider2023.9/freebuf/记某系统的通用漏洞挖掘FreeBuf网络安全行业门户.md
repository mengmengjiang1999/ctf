****程序员写在文章前：****

在攻防演练前给客户做资产自查时，我对某个内网系统进行了渗透测试，发现系统存在较多漏洞。我也在互联网上搜索了该系统，发现挺多厂家的注册资金大于5000万，于是我就挖掘了一些漏洞提交到CNVD平台。以下是我的操作分享：

 ** **1\. 页面出现登录框****

首先，页面会出现一个登录框。这种情况一般就是爆破弱口令、sql注入、修改数据返回包、翻js看有没有未授权的接口。所以我对这个系统进行了目录扫描，但没有发现到可利用的信息，它只是泄漏了一些网站的内网地址和网站的物理路径。

![1661927023_630efe6f66efbc666d99b.png!small](https://image.3001.net/images/20220831/1661927023_630efe6f66efbc666d99b.png!small)

 ** **2\. 测试用户名枚举****

我测试了登录存在用户名的枚举，但是只枚举出了admin账户，对admin账户的密码进行爆破也没有成功。我查看源代码后发现原来在code==0时，会跳转到/home/main.html。

![1661927044_630efe844fe0d85a6243b.png!small](https://image.3001.net/images/20220831/1661927044_630efe844fe0d85a6243b.png!small)

 ** **3\. 构造数据返回包****

构造数据返回包后，会跳转到静态页面，但是会提示token not exist。

![1661927062_630efe96ad05b8fb2e2be.png!small](https://image.3001.net/images/20220831/1661927062_630efe96ad05b8fb2e2be.png!small)

 ** **4\. 查看页面源代码****

我查看了一下页面源代码，发现在js中某处功能点泄漏了password的值。

![1661927079_630efea73391ac64a9d18.png!small](https://image.3001.net/images/20220831/1661927079_630efea73391ac64a9d18.png!small)

 ** **5\. 登录系统查看功能点****

我使用此密码直接登录系统，可以看到功能点下又有多个下载的功能点，如录音管理、系统维护备份。

![1661927098_630efebad852e54ffaecf.png!small](https://image.3001.net/images/20220831/1661927098_630efebad852e54ffaecf.png!small)

![1661927106_630efec204d575b1d4fba.png!small](https://image.3001.net/images/20220831/1661927106_630efec204d575b1d4fba.png!small)

 ** **6\. 测试系统****

我测试后发现，其中系统维护处的备份是存在任意文件下载的，录音管理处则做了过滤。

![1661927128_630efed86d67c028f734c.png!small](https://image.3001.net/images/20220831/1661927128_630efed86d67c028f734c.png!small)

 ** **7\. sql注入****

（1）在IP电话用户查询功能处存在sql注入,根据提示，用户号码支持通配符[x|X|.]查询，“x”和“X”匹配一位，“.”配置任一位。

![1661927150_630efeeedf5a227ac1a0a.png!small](https://image.3001.net/images/20220831/1661927150_630efeeedf5a227ac1a0a.png!small)

（2）测试存在sql注入；

![1661927165_630efefd80cd2de54688b.png!small](https://image.3001.net/images/20220831/1661927165_630efefd80cd2de54688b.png!small)

（3）通话录音查询处也存在sql注入。

![1661927182_630eff0e304bb9d3c3bd2.png!small](https://image.3001.net/images/20220831/1661927182_630eff0e304bb9d3c3bd2.png!small)

![1661927190_630eff164debe72e4703c.png!small](https://image.3001.net/images/20220831/1661927190_630eff164debe72e4703c.png!small)

 ** **8\. token值登录系统****

此外，我还发现在输入正确的用户名和密码时，生产的token的值是固定的，也就是说我们可以使用这个token值来登录互联网上所有的此系统。

![1661927208_630eff28c689cb5f5c9c2.png!small](https://image.3001.net/images/20220831/1661927208_630eff28c689cb5f5c9c2.png!small)

在互联网搜索该系统时，发现有个别系统是低版本，测试后发现登录成功后，生成的token的值也是固定的，只是跟新版本的token值不同。

![1661927222_630eff36a704b4465afda.png!small](https://image.3001.net/images/20220831/1661927222_630eff36a704b4465afda.png!small)

 ** **9\. 发现**** ** **低版本录音管理**** ** **漏洞****

在低版本的录音管理也是存在任意文件读取，但在新版已被修复。

![1661927245_630eff4d0b62f82abed73.png!small](https://image.3001.net/images/20220831/1661927245_630eff4d0b62f82abed73.png!small)

![1661927249_630eff517eecd94a6935f.png!small](https://image.3001.net/images/20220831/1661927249_630eff517eecd94a6935f.png!small)

 **总结：**

整个测试下来，我最终发现了几处漏洞，并已整理好报告提交到CNVD，现在等待证书下发。

![1661927279_630eff6f38d1622f82bb5.png!small](https://image.3001.net/images/20220831/1661927279_630eff6f38d1622f82bb5.png!small)

此次测试的起因还是因为在做内网系统资产自查的时候，发现了该系统的一些漏洞。然后利用互联网搜索时，我发现此系统的低版本还存在其他漏洞，所以整理了漏洞报告，希望能够获得几个通用证书。

