##### CVE-2016-4437 反序列化

猜测：  
进入靶场之后发现是个登录框，bp抓包，在历史记录中发现了rememberMe，怀疑存在shiro反序列化漏洞  
![](https://image.3001.net/images/20220905/1662376550_6315da6630132f0c8fc6c.png!small)  
验证猜测：  
先在bp项目选项处设置使用默认的burp collaborator服务器  
![](https://image.3001.net/images/20220905/1662376745_6315db29990aefa7fb978.png!small)  
接下来点击bp左上角的burp->burp collaborator客户端  
![](https://image.3001.net/images/20220905/1662376910_6315dbce3b7b1d74a9829.png!small)  
复制生成的dnslog的url  
![](https://image.3001.net/images/20220905/1662377014_6315dc366575dade76469.png!small)  
用python脚本生成dnslog记录的payload  
![](https://image.3001.net/images/20220905/1662377215_6315dcffbc6bd70b35327.png!small)  
复制payload，构造cookie，发至重发模块点击发送  
![](https://image.3001.net/images/20220905/1662377378_6315dda22087cfb7b7112.png!small)  
成功接收到dnslog记录，猜测正确  
![](https://image.3001.net/images/20220905/1662377657_6315deb9ee3a364bff3f9.png!small)  
利用漏洞：  
打开反序列化漏洞利用工具，输入url，点击爆破密钥和爆破利用链及回显  
![](https://image.3001.net/images/20220905/1662377945_6315dfd932fac5be599c0.png!small)  
点击命令执行，输入whoami，成功执行  
![](https://image.3001.net/images/20220905/1662378015_6315e01f5835a4a8e8939.png!small)

##### CVE-2020-1957 未授权访问

进入靶场，随便点了一下就302跳转到登录页面了  
![](https://image.3001.net/images/20220905/1662383261_6315f49d4da6cdafd11fa.png!small)  
bp抓包，在响应包中发现rememberMe  
![](https://image.3001.net/images/20220905/1662383489_6315f581d4c7a91188720.png!small)  
构造url，成功登录到管理界面  
![](https://image.3001.net/images/20220905/1662384047_6315f7afc15090399b115.png!small)

