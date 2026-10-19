## 前言

最近看到了大佬写的挖掘SRC漏洞的文章，看了以后就想着自己动手试试，结果一挖连着挖了两个漏洞

首先就是找漏洞，使用谷歌语法 inurl:asp(php/jsp/aspx)/?id=1 找到了疑似有SQL注入的页面，

![kuangstudy709cea6b-02c4-46fb-83f9-3c50f446540a.PNG](https://image.3001.net/images/20210810/1628576579_61121b43ad0bb2d2f938f.png!small)

判断有没有SQL注入漏洞，在后面加and 1=1 和 and 1=2 进行判断，被WAF拦截了，

![3a6313d10c688e0441baaab01f1f417f_76599.png](https://image.3001.net/images/20210810/1628576580_61121b447f2b1f893879f.png!small)

通过WAF识别，判断了这是WTS-WAF ,网上搜索该WAF的拦截方法，可以用 + 代替空格，实验效果如下

![67393a4ad85030736743ae7a13f6f2b9_90362.png](https://image.3001.net/images/20210810/1628576581_61121b45414af1df4bfaf.png!small)

当and 1=1 变成and 1=2 时，页面显示空白，说明确实存在SQL注入漏洞

![e8eacc59946b50eee1157a2f73e6cdae_28870.png](https://image.3001.net/images/20210810/1628576582_61121b4681e695111ca90.png!small)

使用order by 查询字段数，可以看到，order by 1正常，order by 2开始就异常了，说明字段数为1

![8f951e18dd465249723d0ec96db7d4b5_39952.png](https://image.3001.net/images/20210810/1628576583_61121b473c0eacf2a5978.png!small)

![de82262ada43123f68255c35fe5fa0b4_28313.png](https://image.3001.net/images/20210810/1628576583_61121b47e2a301e6c5b8a.png!small)

接下来尝试联合查询注入，union select 1，发现了回显点

![19d2d1976aa985411d148daed23674b4_66744.png](https://image.3001.net/images/20210810/1628576584_61121b4881db4edddcb2e.png!small)

用database（）查询数据库名

![44f3e70a65448b5c0b17aaf2faaaa6d2_66895.png](https://image.3001.net/images/20210810/1628576585_61121b491737f528d50f9.png!small)

接下来得到表名（点到为止）payload：and 1=2 union select 1,2,table_name from
information_schema.tables where table_schema=database() limit 0,1

![f77495f42fe57fd3070d33e8f6c1defa_12344.png](https://image.3001.net/images/20210810/1628576585_61121b499fc263da37d53.png!small)

做到这里，我想，如果数据由前端显示，那么会不会存在XSS注入，让它显示alert(1)效果如何？  
结果被拦截了

![32e437946f6ae228189f02600501ba03_71106.png](https://image.3001.net/images/20210810/1628576586_61121b4a3a3d6ab5310e5.png!small)

绕过办法：用16进制编码绕过，alert(1)转换成16进制编码的结果是：0x3c7363726970743e616c6572742831293c2f7363726970743e，提交，发现成功绕过了

![f1b60993ec2107aa7703137d8b10849c_14647.png](https://image.3001.net/images/20210810/1628576586_61121b4ac572fcab58ea4.png!small)

风险等级：中  
提交结果：被漏洞盒子提交至CNNVD

![808da7ad7308fae1ba7aa5f2018b1862_48210.png](https://image.3001.net/images/20210810/1628576587_61121b4b60936642b0bcc.png!small)

![1628576275_61121a136a3c195991a88.png!small](https://image.3001.net/images/20210810/1628576275_61121a136a3c195991a88.png!small)

  

