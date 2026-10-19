![](https://image.3001.net/images/20221206/1670331808_638f3da0929fbd6c2d14e.jpg!small)  

## 关于Neton

Neton是一款功能强大的沙盒信息收集工具，该工具可以帮助广大研究人员从联网的沙盒环境中提取和收集信息。

该工具由一个代理和一个Web接口组成，代理负责从目标系统中收集信息，然后通过HTTPS将其收集到的数据提取到Web服务器中，而Web接口负责将收集到的信息显示给
研究人员。

## 支持收集的信息

> 1、操作系统和硬件信息；
>
> 2、从挂载的驱动器上搜索文件信息；
>
> 3、枚举没有签名的微软驱动程序；
>
> 4、运行SharpEDRChecker；
>
> 5、运行Pafish；
>
> 6、运行AI-Khaser；
>
> 7、钩子检测；
>
> 8、获取目标系统桌面截图；

上述这些所有的信息都可以帮助广大红队研究人员提升自己的工作效率，并更好地了解沙盒的工作机制以及如何保证沙盒环境的安全。

## 工具部署

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Aetsu/Neton.git

### NetonWeb

首先，使用virtualenv安装：

    
    
    python3 -m venv venv
    
    source venv/bin/activate
    
    pip3 install -r requirements.txt

接下来，配置数据库：

    
    
    python3 manage.py migrate
    
    python3 manage.py makemigrations core
    
    python3 manage.py migrate core

然后创建一个用户：

    
    
    python3 manage.py createsuperuser

## 工具启动

### 测试环境

    
    
    python3 manage.py runserver

### 生产环境

生成一个证书，并将其存储在certs目录中：

    
    
    openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout server.key -out server.crt

启动gunicorn：

    
    
    ./launch_prod.sh

## 代理

使用Visual Studio构建解决方案，代理配置可以通过Program.cs类来完成：

> 1、url变量：用于提取信息的URL（NetonWeb的URL）；
>
> 2、sandboxid变量：沙盒识别符，用于上传样本；
>
> 3、wave变量：组织样本发送的不同时间和方式；

## 样本数据

sample data目录中有一个sqlite数据库文件，其中包含了从下列服务中收集到的一些样本：

> Virustotal
>
> Tria.ge
>
> Metadefender
>
> Hybrid Analysis
>
> Any.run
>
> Intezer Analyze
>
> Pikker
>
> AlienVault OTX
>
> Threat.Zone

### 凭证信息

> 用户名：raccoon
>
> 密码：jAmb.Abj3.j11pmMa

## 工具运行截图

![](https://image.3001.net/images/20221206/1670331934_638f3e1e3e8a174007d29.png!small)![](https://image.3001.net/images/20221206/1670331940_638f3e24937cb32c246b2.png!small)

![](https://image.3001.net/images/20221206/1670331947_638f3e2bf18f36f8325f8.png!small)

![](https://image.3001.net/images/20221206/1670331955_638f3e33c93825eec79e4.png!small)

![](https://image.3001.net/images/20221206/1670331962_638f3e3a4d124f1874358.png!small)

![](https://image.3001.net/images/20221206/1670331969_638f3e412821831f3a223.png!small)

![](https://image.3001.net/images/20221206/1670331975_638f3e47de3968a6357e2.png!small)

## 项目地址

 **Neton** ：【[ _GitHub传送门_](https://github.com/Aetsu/Neton)】

## 参考资料

> [
> _https://github.com/Aetsu/Presentaciones/blob/master/Sandbox%20fingerprinting%20-%20Evadiendo%20entornos%20de%20analisis.pdf_](https://github.com/Aetsu/Presentaciones/blob/master/Sandbox%20fingerprinting%20-%20Evadiendo%20entornos%20de%20analisis.pdf)
>
> [ _https://www.you_ _*_
> _tube.com/watch?v=AyVgIttiUpQ_](https://www.youtube.com/watch?v=AyVgIttiUpQ)
>
> [ _https://www.you_ _*_
> _tube.com/watch?v=KzwEddl80OQ_](https://www.youtube.com/watch?v=KzwEddl80OQ)
>
> [
> _https://github.com/PwnDexter/SharpEDRChecker_](https://github.com/PwnDexter/SharpEDRChecker)
>
> [ _https://github.com/a0rtega/pafish_](https://github.com/a0rtega/pafish)
>
> [ _https://github.com/LordNoteworthy/al-> khaser_](https://github.com/LordNoteworthy/al-khaser)
>
> [
> _https://github.com/matterpreter/OffensiveCSharp/tree/master/HookDetector_](https://github.com/matterpreter/OffensiveCSharp/tree/master/HookDetector)
>
> [
> _https://github.com/matterpreter/OffensiveCSharp/tree/master/DriverQuery_](https://github.com/matterpreter/OffensiveCSharp/tree/master/DriverQuery)

