![](https://image.3001.net/images/20230718/1689647652_64b5fa246cfdf82d992fd.png!small)  

## 关于Artemis

Artemis是一款功能强大的模块化网络侦查和漏洞扫描工具，该工具基于[ _Karton_](https://github.com/CERT-Polska/karton)项目开发，可以优化和增强CERT
PL扫描活动。除此之外，该工具不仅可以帮助广大研究人员从多个方面扫描和检测目标网站的安全性，而且还可以生成简单易读的安全报告来帮助和指引广大研究人员提升自己站点的网络安全性。

## 功能介绍

> 1、使用crt.sh和[ _gau_](https://github.com/lc/gau)执行子域名扫描；
>
> 2、整合了Shodan搜索引擎（需要提供SHODAN_API_KEY）；
>
> 3、爆破目标路径，例如.env；
>
> 4、爆破WordPress、MySQL、PostgreSQL、FTP密码；
>
> 5、通过电子邮件发送检测和扫描报告；
>
> 6、电子邮件电子邮件配置验证；
>
> 7、WordPress和Joomla版本检测；
>
> 8、支持检测VSC目录，例如.git；
>
> 9、支持检测已启用的目录索引；
>
> 10、端口扫描；
>
> 11、支持通过“加插即用”模块扩展工具功能；

## 功能模块

下面的图表中显示的是Artemis模块的功能子集和运行流程：

![](https://image.3001.net/images/20230718/1689647675_64b5fa3b1e451982f5e33.png!small)

## 工具使用

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/CERT-Polska/Artemis.git

当前版本的Artemis仅支持通过Docker Compose使用或扩展功能。

### 使用Docker Compose

打开命令行终端，并运行下列两行命令：

    
    
    cp env.example .env  # you may also configure the settings (e.g. by providing a User-Agent to override the default one)
    
    docker compose up --build

接下来，你就可以通过访问下列地址来使用Artemis了：

    
    
    localhost:5000

如果你想要开启多个模块实例来提升扫描速度，可以使用如下所示的命令：

    
    
    docker compose up --build \
    
        --scale=karton-nuclei=10 \
    
        --scale=karton-bruter=10 \
    
    --scale=karton-port_scanner=10

## 开发自定义模块

由于Artemis基于Karton框架开发，模块将以Karton服务运行：

    
    
    from karton.core import Task
    
    from artemis.binds import Service, TaskStatus, TaskType
    
    from artemis.module_base import ArtemisBase
    
    from artemis.task_utils import get_target_url
    
     
    
    class CustomScanner(ArtemisBase):
    
        """
    
        My first custom Artemis module
    
        """
    
     
    
        # Module name that will be displayed
    
        identity = "custom"
    
     
    
        # Types of tasks that will be consumed by the module - here, open ports that were identified
    
        # to contain a HTTP/HTTPS service. To know what types are possible, look at other modules' source:
    
        # https://github.com/CERT-Polska/Artemis/tree/main/artemis/modules
    
        filters = [
    
            {"type": TaskType.SERVICE, "service": Service.HTTP},
    
        ]
    
     
    
        def run(self, current_task: Task) -> None:
    
            url = get_target_url(current_task)
    
            self.log.info(f"custom module running {url}")
    
     
    
            status = TaskStatus.OK
    
            status_reason = None
    
     
    
            if "sus" in url:
    
                # On the default task result view only the interesting task results will be displayed
    
                status = TaskStatus.INTERESTING
    
                status_reason = "suspicious link detected!"
    
     
    
            # In the data dictionary, you may provide any additional results - the user will be able to view them
    
            # in the interface on the single task result page.
    
            self.db.save_task_result(task=current_task, status=status, status_reason=status_reason, data={})
    
     
    
    if __name__ == "__main__":
    
    CustomScanner().loop()

需要注意的是，当前版本的Artemis使用了MongoDB来存储任务执行结果。

## 工具扫描结果

![](https://image.3001.net/images/20230718/1689647737_64b5fa79ab708e377a837.png!small)

## 许可证协议

本项目的开发与发布遵循[ _BSD_ _-3-Clause_](https://github.com/CERT-Polska/Artemis/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Artemis** ：【[ _GitHub传送门_](https://github.com/CERT-Polska/Artemis)】

## 参考资料

> [ _https://github.com/CERT-Polska/karton_](https://github.com/CERT-> Polska/karton)
>
> [ _https://artemis-> scanner.readthedocs.io/en/latest/features.html_](https://artemis-> scanner.readthedocs.io/en/latest/features.html)
>
> [ _https://artemis-scanner.readthedocs.io/en/latest/generating-> emails.html_](https://artemis-scanner.readthedocs.io/en/latest/generating-> emails.html)
>
> [ _https://kncyber.pl/_](https://kncyber.pl/)
>
> [ _https://pw.edu.pl/_](https://pw.edu.pl/)
>
> [ _https://cert.pl/_](https://cert.pl/)
>
> [ _https://discord.gg/GfUW4mZmy9_](https://discord.gg/GfUW4mZmy9)

