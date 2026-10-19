最近比赛出现JWT的题目，利用WebGoat靶场对JWT知识点进行进行学习，不过JWT利用点挺少的，基础学习即可。  
[![xRGBx.png](https://image.3001.net/images/20220421/1650533131_6261230b7b08a1ac46837.png!small)](https://imgtg.com/image/xRGBx)

## WebGoat靶场搭建

WebGoat是一款很好的学习网络安全知识和技巧的入门应用。  
这里我利用docker一键部署，方便，目的是为了学习JWT。

    
    
    mkdir webgoat //新建webgoat文件夹
    docker run -d -p 8081:8080 -p 9090:9090 -e TZ=Europe/Amsterdam webgoat/goatandwolf //
    docker ps //显示webgoat
    

IP:8081/WebGoat进行注册，IP:9090/login用户平台

先进行注册  
[![xRQKj.png](https://image.3001.net/images/20220421/1650533132_6261230c956a80ce0cb8b.png!small)](https://imgtg.com/image/xRQKj)

## 什么是JWT

jwt在网络应用环境间传递声明而执行的一种基于JSON的开放标准，jwt用来在身份提供者和服务提供者间传递被认证的用户身份信息，以便于从资源服务器获取资源，也可以增加一些额外的其它业务逻辑所必须的声明信息，该token也可直接被用于认证，也可被加密。

### JWT构造

[![xRS0p.png](https://image.3001.net/images/20220421/1650533133_6261230d94dc9223bb210.png!small)](https://imgtg.com/image/xRS0p)  
JWT的token组成：Header、Payload、Signature

    
    
    1.header是base64编码后的头部信息    
    	{'typ': 'JWT','alg': 'HS256'}    
    	定义了声明type和签名算法alg   
    2.payload是base编码的载荷部分，用来包含用户名，权限     
    	iss (issuer)：签发人       
    	sub (subject)：主题   
    	aud (audience)：受众     
    	exp (expiration time)：过期时间   
    	nbf (Not Before)：生效时间，在此之前是无效的     
    	iat (Issued At)：签发时间  
    	jti (JWT ID)：编号    
    	-定义一个payload:{
    	"sub": "l3ife",
    	"name": "l3ife",
    	 "iat": 888888}
    	 对其进行base64加密，得到jwt的第二部分
    	eyJzdWIiOiJsM2lmZSIsIm5hbWUiOiJsM2lmZSIsImlhdCI6ODg4ODg4fQ
    3.signature是加密后的base64(header)
    

+base64(payload)内容，防止篡改。

头和声明都由JSON对象表示。标题描述了应用于JWT的加密操作，以及JWT的附加属性（可选）。声明代表一个JSON对象，其成员是JWT传递的声明。

### 身份验证和获取JWT令牌的过程

[![xRcMU.png](https://image.3001.net/images/20220421/1650533134_6261230e5cc8e58b9bde6.png!small)](https://imgtg.com/image/xRcMU)

用户在服务器成功返回身份验证时使用用户名和密码登录。服务器创建一个新令牌并将其返回给客户端。当客户端连续呼叫服务器时，它会在“授权”头中附加新令牌。服务器读取令牌，并在成功验证后首先验证签名。服务器使用令牌中的信息来标识用户。

## 方式

### 基础

解码jwt令牌，把令牌放到jwt.io下  
[![xRd1Y.png](https://image.3001.net/images/20220421/1650533135_6261230f8e79ac8ccd2ce.png!small)](https://imgtg.com/image/xRd1Y)  
查看到user，将user填到表下  
[![xRsHv.png](https://image.3001.net/images/20220421/1650533136_6261231064467becec61a.png!small)](https://imgtg.com/image/xRsHv)

### alg字段设为none（JWT-5）

用户无法投票，只有成为管理员才可以投票，需要更改令牌成为管理员用户，成了管理员用户才可以重置投票  
[![xRVXq.png](https://image.3001.net/images/20220421/1650533137_6261231123560a90ff07a.png!small)](https://imgtg.com/image/xRVXq)  
点击Vote Now，抓包发现cookie_session的宝，为jwt令牌，解密得到  
[![xRfxc.png](https://image.3001.net/images/20220421/1650533138_626123120438d2d5dfda5.png!small)](https://imgtg.com/image/xRfxc)  
声明加密方法为HS512，第二部分声明用户名和权限，可以看到管理员权限为false

将admin改为true，由于加密方法是HS512，且不知道秘钥，所以只能将alg的值改为none，即无加密方法。  
[![xRlJr.png](https://image.3001.net/images/20220421/1650533138_62612312deddc6925a9b9.png!small)](https://imgtg.com/image/xRlJr)  
ewogICJhbGciOiAib9uZSIKfQ==  
[![xR9lM.png](https://image.3001.net/images/20220421/1650533139_626123139733a9231accd.png!small)](https://imgtg.com/image/xR9lM)  
ewogICJpYXQiOiAxNjUxMzg0MzMzLAogICJhZG1pbiI6ICJ0cnVlIiwKICAidXNlciI6ICJUb20iCn0=

无加密，不需要Signature部分，点击普通用户旁边的垃圾桶，实现重置

将每部分的值拿去base64加密，去掉=号，并且不需要signature部分，末尾加一个.  
[![xR2BG.png](https://image.3001.net/images/20220421/1650533140_626123149a7306218f37f.png!small)](https://imgtg.com/image/xR2BG)  
通过伪造令牌，越权执行管理员权限

    
    
    try {
    	Jwt jwt = Jwts.parser().setSigningKey(JWT_PASSWORD).parseClaimsJws(accessToken);
    	Claims claims = (Claims) jwt.getBody();
      	String user = (String) claims.get("user");
    	boolean isAdmin = Boolean.valueOf((String) claims.get("admin"));
    	if (isAdmin) {
     		removeAllUsers();
    	} else {
     		log.error("You are not an admin user");
    	 }
    	} catch (JwtException e) {
    		throw new InvalidTokenException(e);
    	}
    

第十二行抛出错误异常。parseClaimsJwt方法是解析没有进行签名的token，token进行签名再调用该方法就会报错。

### 暴力破解密钥(jwt-8)

如果签名算法，加密后的载荷和最终得到的加密字符串都已知，且密钥不够复杂的话，使用暴力破解便有可能将密钥解出。

本关给了token，根据token得到密钥，再自己做一个账户名为webgoat的token再重新加密后提交

    
    
    token：eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJXZWJHb2F0IFRva2VuIEJ1aWxkZXIiLCJhdWQiOiJ3ZWJnb2F0L9yZyIsImlhdCI6MTY1MDUyMTY0MSwiZXhwIjoxNjUwNTIxNzAxLCJzdWIiOiJ0b21Ad2ViZ29hdC5vcmciLCJ1c2VybmFtZSI6IlRvbSIsIkVtYWlsIjoidG9tQHdlYmdvYXQub3JnIiwiU9sZSI6WyJNYW5hZ2VyIiwiUHJvamVjdCBBZG1pbmlzdHJhdG9yIl19.QBM_gpY6JTu3j_JOSHN1ro4IpQ7G6MB73jxdwVUXUPI
    

[![xR6Z1.png](https://image.3001.net/images/20220421/1650533141_62612315a67f38bdbe291.png!small)](https://imgtg.com/image/xR6Z1)  
给了header和payload，未知公钥

将原来token保存为jwt.txt,去网上下载常见的英文，使用hashcat爆破

    
    
    hashcat -m 16500 jwt.txt  -a 3 -w 3 /home/l3ife/桌面/20k.txt --force
    

16500代表是破解JWT，jwt.txt代表原始的token -a 3以及-w 3代表暴力高速破解，后面是字典的位置，–force表示忽略错误。  
破解出公钥为washington，由于token设置了时间戳，往后延迟几秒就可以  
[![xR80I.png](https://image.3001.net/images/20220421/1650533142_626123169f7339b1bf00f.png!small)](https://imgtg.com/image/xR80I)

### 密钥泄露(jwt-10)

本关需要找之前的日志，找到一种方法去让tom花钱订购书，在日志中发现token

修改时间戳修改为今天，抓包利用。

### 其他利用

    
    
    1.kid字段被控制
    	kid字段可以被用户控制，如果kid字段存在薄弱点，那么就容易被攻击者利用，从而造成危害。比如：目录遍历，SQL注入攻击
    2.信息泄露
    	JWT用来访问控制，里面的内容包含用户登录信息。
    

### CTF例题

> T-star挑战赛第一题

注册就是个显摆，通过jwt发现头部存在加密的base64，得到验证码进入后台。

> ImgWeb

查看session好像为jwt的格式，将得到的密钥加进去，通过刷新网页，得到管理员权限。

> [PASECA2019]honey_shop

通过任意文件下载，找到密钥。

## 番外

自己搭的图床竟然显示不了图片，还是先用TG先吧。  
测试（Lsky）  
![1650529725288.png](https://image.3001.net/images/20220421/1650533143_62612317d343d5012ec1c.png!small)

