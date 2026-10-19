**Fracker是一套PHP函数调用追踪与分析的工具，其目标是在PHP应用程序的手动安全评估期间协助安全研究人员。**  

它包括：

> 需要安装在目标Web应用程序环境中的[PHP扩展](https://github.com/cyrus-and/fracker#php-> extension)，它将跟踪信息发送给侦听器;
>
> 一个[侦听器应用](https://github.com/cyrus-and/fracker#listener-> application)，负责接收跟踪信息并执行一些分析，以向用户显示一些有价值的数据。

##
![68747470733a2f2f692e696d6775722e636f6d2f4e36755a5679792e706e67.png](https://image.3001.net/images/20190425/1556148344_5cc0f078b2bca.png!small)

## Demo

克隆或下载该存储库，然后进入根目录。

Spin一个新的使用PHP支持正在运行Apache的Docker容器：

    
    
    $ docker run --rm -d -p 80:80 --name hello-fracker php:apache

创建一些虚拟PHP脚本作为索引：

    
    
    $ docker exec -i hello-fracker tee /var/www/html/index.php <<\EOF
    <?php
        function foo($cmd) {
            system('echo ' . preg_replace('/[^a-z]/i', '', $cmd));
        }
    
        $a = explode(' ', $_GET['x']);
        var_dump($a);
        foreach ($a as $cmd) {
            foo($cmd);
        }
    EOF

测试PHP文件是否正确提供：

    
    
    $ curl 'http://localhost/?x=Hello+Fracker!'

将Fracker部署到容器：

    
    
    $ scripts/deploy.sh hello-fracker

在本地安装依赖项（这只需要执行一次）：

    
    
    $ npm install -C app

启动Fracker：

    
    
    $ app/bin/fracker.js

再次运行上面的curl命令（输出应与上面的截图类似）。

使用--help再次运行Fracker并尝试其他选项。

停止并移除容器：

    
    
    $ docker stop hello-fracker

## 架构

每个PHP请求或命令行调用都会触发与侦听器的TCP连接。该协议只是从PHP扩展到侦听器的以换行方式终止的JSON对象流，这些对象包含有关当前请求、执行的调用和返回值的信息。

这种分离允许用户实现自己的工具。可以通过将流内容转储到标准输出来检查原始JSON对象，例如：

    
    
    $ socat tcp-listen:6666,fork,reuseaddr 'exec:jq .,fdout=0'

## PHP 扩展

PHP扩展是从Xdebug派生出来的的，因此安装过程完全相同，故障排除也是如此。

使用Fracker最简便的方式可能就是使用提供的脚本，将其部署到Web服务器所在的Docker容器中。使用手动方法获得更通用的解决方案。

 **部署脚本**

这个脚本应该与类Debian发行版开箱即用：

    
    
    $ scripts/deploy.sh <container> [<port> [<host>]]

它将PHP模块配置为连接到指定端口的指定主机（默认为运行Docker和端口6666的主机）。

 **手动设置**

需要在ext目录中执行以下操作。

使用以下代码构建PHP扩展：

    
    
    $ phpize
    $ ./configure
    $ make

（要在重要的代码更改之后重建，只需重新运行make。）

要检查一切是否正常，请启动侦听器应用程序，然后像这样运行PHP：

    
    
    $ php -d "zend_extension=$PWD/.libs/xdebug.so" -r 'var_dump("Hello Fracker!");'

最后，安装PHP扩展：

> make install；
>
> 将zend_extension=xdebug.so放在由PHP解析的INI文件中，以及任何其他自定义设置中。

使用以下方法clean源目录：

    
    
    $ make distclean
    $ phpize --clean

 **设置**

以下为Fracker使用的最常用设置的模板：

    
    
    ; trace only those requests with XDEBUG_TRACE=FRACKER in GET, POST or cookie
    xdebug.auto_trace = 0
    xdebug.trace_enable_trigger = 1
    xdebug.trace_enable_trigger_value = FRACKER
    
    ; do not collect function arguments
    xdebug.collect_params = 0
    
    ; do not collect return values
    xdebug.collect_return = 0
    
    ; custom application address
    xdebug.trace_fracker_host = 127.0.0.1
    xdebug.trace_fracker_port = 6666

## 侦听器应用

提供的侦听器应用是Node.js包。使用以下命令安装依赖项：

    
    
    $ npm install -C app

（可选）通过创建该文件夹的符号链接来全局安装可执行文件：

    
    
    $ npm install -g app

然后只需运行fracker，或使用app/bin/fracker.js在本地运行它。

 **配置**

长格式的命令行选项可以写入yaml文件（camel case），并作为命令行参数传递。可以指定具有更高优先级的多个文件，但命令行选项的优先级最高。

为方便起见，我们为大家提供列出了一些有趣的PHP函数类的[配置文件](https://github.com/cyrus-and/fracker/blob/master/app/configs)。你可以像下面这样使用它们：

    
    
    $ fracker app/configs/file-* # ...

 ***参考来源：[github](https://github.com/cyrus-and/fracker)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

