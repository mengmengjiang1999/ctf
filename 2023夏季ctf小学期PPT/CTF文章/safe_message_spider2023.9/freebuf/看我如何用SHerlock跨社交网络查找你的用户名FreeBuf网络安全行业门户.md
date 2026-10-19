![1.png](https://image.3001.net/images/20190724/1563906610_5d375232b54a9.png!small)

**今天给大家介绍的就是这个名叫Sherlock的半社工工具，在它的帮助下，我们可以跨社交网络来查找目标用户的用户名。话不多说，我们直奔主题。**

我们可以点击【[这里](https://github.com/sherlock-project/sherlock)】直接在浏览器中测试Sherlock的功能。

![2.gif](https://image.3001.net/images/20190724/1563906619_5d37523b48e17.gif!small)

## 工具安装

注意：该工具需要Python 3.6或更高版本。

首先，使用git命令将项目代码克隆到本地：

    
    
    $ git clone https://github.com/sherlock-project/sherlock.git

切换到Sherlock项目目录：

    
    
    $ cd Sherlock

安装依赖组件：

    
    
    $ pip3 install -r requirements.txt

## 工具使用

    
    
    $ python3 sherlock.py --help
    
    usage:sherlock.py [-h] [--version] [--verbose] [--rank]
    
                       [--folderoutputFOLDEROUTPUT] [--output OUTPUT] [--tor]
    
                       [--unique-tor] [--csv][--site SITE_NAME]
    
                       [--proxy PROXY_URL] [--jsonJSON_FILE]
    
                       [--proxy_list PROXY_LIST][--check_proxies CHECK_PROXY]
    
                       [--print-found]
    
                       USERNAMES [USERNAMES ...]
    
     
    
    Sherlock:Find Usernames Across Social Networks (Version 0.7.5)
    
     
    
    positional arguments:
    
      USERNAMES             One or more usernames to checkwith social networks.
    
     
    
    optionalarguments:
    
      -h, --help            show this help message and exit
    
      --version             Display version information and dependencies.
    
      --verbose, -v, -d, --debug
    
                            Display extra debugginginformation and metrics.
    
      --rank, -r            Present websites ordered by theirAlexa.com global
    
                            rank in popularity.
    
      --folderoutput FOLDEROUTPUT, -fo FOLDEROUTPUT
    
                            If using multipleusernames, the output of the results
    
                            will be saved at thisfolder.
    
      --output OUTPUT, -o OUTPUT
    
                            If using singleusername, the output of the result
    
                            will be saved at thisfile.
    
      --tor, -t             Make requests over Tor; increasesruntime; requires
    
                            Tor to be installed andin system path.
    
      --unique-tor, -u      Make requests over Tor with new Torcircuit after each
    
                            request; increasesruntime; requires Tor to be
    
                            installed and in systempath.
    
      --csv                 Create Comma-Separated Values(CSV) File.
    
      --site SITE_NAME      Limit analysis to just the listed sites.Add multiple
    
                            options to specify morethan one site.
    
      --proxy PROXY_URL, -p PROXY_URL
    
                            Make requests over aproxy. e.g.
    
                            socks5://127.0.0.1:1080
    
      --json JSON_FILE, -j JSON_FILE
    
                            Load data from a JSONfile or an online, valid, JSON
    
                            file.
    
      --proxy_list PROXY_LIST, -pl PROXY_LIST
    
                            Make requests over aproxy randomly chosen from a list
    
                            generated from a .csvfile.
    
      --check_proxies CHECK_PROXY, -cp CHECK_PROXY
    
                            To be used with the'--proxy_list' parameter. The
    
                            script will check ifthe proxies supplied in the .csv
    
                            file are working andanonymous.Put 0 for no limit on
    
                            successfully checkedproxies, or another number to
    
                            institute a limit.
    
      --print-found         Do not output sites where the usernamewas not found.

比如说，我们可以使用下列命令来搜索特定用户名：

    
    
    python3 sherlock.py user123

同时搜索多个目标用户名：

    
    
    python3 sherlock.py user1 user2 user3

Sherlock搜索到的全部用户账号信息都会存储在一个单独的文本文件中，并以用户名作为文件名，例如user123.txt。

## Docker

如果你的设备已经安装了Docker，你就可以构建一个镜像，然后以容器的方式运行Sherlock了：

    
    
    docker build -t mysherlock-image .

镜像构建完毕之后，我们就可以利用下列命令调用Sherlock了：

    
    
    docker run --rm -t mysherlock-image user123

\--rm选项可以可以在完成任务之后移除容器文件系统，以防止冗余数据堆积。具体请参考：【[清除手册](https://docs.docker.com/engine/reference/run/#clean-up---rm)】。

-t选项可以分配一个伪TTY，并允许我们使用颜色方案高亮标记输出数据。具体请参考：【[前端手册](https://docs.docker.com/engine/reference/run/#foreground)】。

当然了，我们也可以使用下列命令来访问存储的结果：

    
    
    docker run --rm -t -v "$PWD/results:/opt/sherlock/results" mysherlock-image-o /opt/sherlock/results/text.txt user123

-v"$PWD/results:/opt/sherlock/results"选项可以让Docker创建或使用当前目录下的“result”文件夹，然后在Docker容器中加载/opt/sherlock/results。“-o/opt/sherlock/results/text.txt”选项可以让Sherlock输出分析结果。

或者，你也可以直接使用“Docker Hub”来运行Sherlock：

    
    
    docker run theyahya/sherlock user123

### Sherlock覆盖率测试

![3.png](https://image.3001.net/images/20190724/1563906764_5d3752cc3eadc.png!small)

## 许可证协议

本项目遵循MIT开源许可证协议。

### 项目地址

Sherlock：【[GitHub传送门](https://github.com/sherlock-project/sherlock)】

 ***参考来源：[sherlock-project](https://github.com/sherlock-project/sherlock)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

