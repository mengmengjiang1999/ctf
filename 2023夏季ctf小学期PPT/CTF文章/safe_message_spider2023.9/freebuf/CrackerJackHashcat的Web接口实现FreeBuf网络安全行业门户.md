![](https://image.3001.net/images/20210313/1615649122_604cd9626e561ef9b8c3d.jpg!small)

## CrackerJack介绍及架构

CrackerJack是Hashcat的Web
GUI实现，该项目基于Python编程语言开发，旨在维持Hashcat工具独立的情况下实现GUI接口。简而言之，CrackerJack能够实现下列功能：

> 用户可以上传哈希、选择字典、规则和掩码等等，然后点击“开始”即可。
>
> Web服务器将生成一个新的[
> _screen_](https://www.gnu.org/software/screen/)，可以根据配置生成hashcat命令，在界面上运行命令，监控和解析screen输出数据，并在GUI中给用户显示处理结果。

![](https://image.3001.net/images/20210313/1615649130_604cd96ad2b7a1d2716d1.jpg!small)

这使得CrackerJack与Hashcat的输入/输出相关联，另外，如果GUI由于任何原因无法工作，hashcat将继续运行。

## 功能介绍

> 最少的依赖关系：使用sqlite3、screen和hashcat；
>
> 完整的hashcat会话管理，支持开启、终止、暂停和恢复正在运行的会话，在指定时间过后终止破解任务；
>
> Web接口支持掩码生成（?a?l?u）；
>
> 密码破解后Web推送通知；
>
> Swagger 2.0 API；
>
> 根据已破解密码生成字典，并用于破解会话中；
>
> 多用户支持；
>
> 字典/掩码/规则支持；
>
> 操作简单，所有配置可通过GUI操作，无需编辑配置文件，支持在Linux和Windows本地运行；
>
> 支持备份，所有的用户数据均存储在./data目录中；

## 限制条件

> 不支持排队作业，只能用于按需密码破解。
>
> 其目标并非替代命令行工具，CrackerJack是免费的，仅支持基本和最常见的破解任务。
>
> 不会安装任何GPU驱动程序。
>
> 字典和规则已经存在于系统中了。

## 工具要求

> Python >= 3.6
>
> Screen >= 4.06.00
>
> Hashcat

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ctxis/crackerjack

### 虚拟环境

在命令行终端中切换到项目所在目录，然后运行下列命令：

    
    
    python3 -m venv venv    # You might need to change python3 to python3.6
    
    . venv/bin/activate
    
    pip install -r requirements.txt
    
    flask db init
    
    flask db migrate
    
    flask db upgrade
    
    Deactivate

### 设置www-data所有者

由于Web服务器需要在www-data下运行，因此我们需要给应用程序提供用户权限：

    
    
    sudo chown -R www-data:www-data /path/to/crackerjack

## 本地运行

我们可以在不需要使用Apache/Nginx的情况下在本地使用CrackerJack，导航至项目目录下，然后运行下列命令：

    
    
    . venv/bin/activate
    
    export FLASK_ENV=development
    
    export FLASK_APP=app
    
    flask run

运行之后，大家将看到如下所示的信息：

    
    
    (venv) $ flask run
    
     * Serving Flask app "app" (lazy loading)
    
     * Environment: development
    
     * Debug mode: on
    
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    
     * Restarting with stat
    
     * Debugger is active!
    
     * Debugger PIN: 182-315-751

接下来，我们就可以在浏览器中访问http://127.0.0.1:5000/来使用CrackerJack了。

## 工具运行截图

 **运行中的会话：**

**![](https://image.3001.net/images/20210313/1615649187_604cd9a35cff97dd60f63.png!small)**

 **仪表盘：**

**![](https://image.3001.net/images/20210313/1615649194_604cd9aa2d88b9f91cbd9.png!small)**

 **会话：**

**![](https://image.3001.net/images/20210313/1615649200_604cd9b099ce5eb665774.png!small)**

 **选择哈希：**

**![](https://image.3001.net/images/20210313/1615649207_604cd9b79f0a2f673ef31.png!small)**

 **哈希类型选择：**

**![](https://image.3001.net/images/20210313/1615649214_604cd9be4fa0437f86e02.png!small)**

 **字典选择：**

**![](https://image.3001.net/images/20210313/1615649220_604cd9c4d3d4b2bc38d1f.png!small)**

 **掩码生成：**

**![](https://image.3001.net/images/20210313/1615649228_604cd9cc57d0921050813.png!small)**

 **通用会话设置：**

**![](https://image.3001.net/images/20210313/1615649236_604cd9d41fb7ee77b1fd4.png!small)**

## 工具使用演示

视频地址：[ _https://www.油管.com/watch?v=9Ol48qQtuk4_](https://www.xn--uvwy13a.com/watch?v=9Ol48qQtuk4)

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

CrackerJack：【[ _GitHub传送门_](https://github.com/ctxis/crackerjack)】

## 参考资料

  * [ _https://www.contextis.com/en/_](https://www.contextis.com/en/)
  * [ _https://hashcat.net/hashcat/_](https://hashcat.net/hashcat/)
  * [ _https://www.gnu.org/software/screen/_](https://www.gnu.org/software/screen/)
  * [ _https://www.sqlite.org/index.html_](https://www.sqlite.org/index.html)
  * [ _https://bootswatch.com/_](https://bootswatch.com/)
  * [ _https://github.com/ctxis/crackerjack/blob/master/docs/installation.md_](https://github.com/ctxis/crackerjack/blob/master/docs/installation.md)

