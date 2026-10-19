![](https://image.3001.net/images/20230419/1681915082_643ffccacbfa4242fb69c.gif)

## 关于MegPlus

MegPlus是一款功能强大的自动化网络侦查任务执行框架，该工具可以帮助广大研究人员以自动化的形式执行多种网络侦查任务。该工具支持针对某个目标执行常见问题扫描并生成详细的分析报告。除此之外，该工具还具备一定的渗透测试功能。

值得一提的是，该工具还允许我们一次性扫描HackerOne上的所有范围内目标，而这个过程MegPlus仅使用GraphQL即可实现。

## 支持扫描的内容

MegPlus支持扫描下列内容：

> 1、使用Sublist3r扫描子域名；
>
> 2、配置文件；
>
> 3、其他有价值的数据；
>
> 4、开放重定向；
>
> 5、CRLF注入；
>
> 6、CORS错误配置；
>
> 7、基于路径的XSS；
>
> 8、（子）域名接管；

## 工具环境

> [ _Golang_](https://golang.org/doc/)
>
> Python 2或3
>
> [ _PHP_ _7_ _._ _0_](https://user-> images.githubusercontent.com/18099289/35768719-daaaf30c-0900-11e8-92ab-> bdc2498c80bf.png)

## 工具依赖组件

> [ _meg_](https://github.com/tomnomnom/meg)
>
> [ _waybackurls_](https://github.com/tomnomnom/waybackurls)
>
> [ _Sublist_ _3_ _r_](https://github.com/aboul3la/Sublist3r)
>
> [ _gio_](http://manpages.ubuntu.com/manpages/artful/man1/gio.1.html)

## 工具安装

配置完该工具的运行环境之后，广大研究人员就可以使用下列命令将该项目克隆至本地：

    
    
    git clone https://github.com/EdOverflow/megplus.git

然后切换到项目所在目录中，安装该工具所需的相关依赖组件：

    
    
    cd megplus
    
    go get github.com/tomnomnom/meg
    
    go get github.com/tomnomnom/waybackurls
    
    git clone https://github.com/aboul3la/Sublist3r.git

注意事项：如果你不想使用gio或者没有安装gio的话，可以直接将工具代码中和gio有关的代码行注释掉。

## 工具使用

我们可以直接对大量主机执行扫描，或者使用HackerOne的X-Auth-Token令牌来扫描所有你参与的漏洞奖励计划项目。

### 本地使用

    
    
    $ ./megplus.sh
    
    1) Usage - 扫描目标域名列表:        ./megplus.sh <目标域名列表>
    
    2) Usage - 扫描所有HackerOne项目: ./megplus.sh -x <H1 X-Auth-Token>
    
    3) Usage - 首先执行sublist3r扫描:           ./megplus.sh -s <single host>
    
     
    
    1) 样例一: ./megplus.sh domains
    
    2) 样例二: ./megplus.sh -x XXXXXXXXXXXXXXXX
    
    3) 样例三: ./megplus.sh -s example.com

### Docker使用

如果你不想安装前文提到的那些依赖组件的话，你也可以直接运行该工具提供的Docker镜像“abhartiya/tools_megplus”，容器提供了一个test.txt文件，这是一个包含了大量测试目标URL的列表文件，你可以直接运行下列命令来进行测试：

    
    
    docker run -v $(pwd):/megplus abhartiya/tools_megplus test.txt

上述命令将以一个容器来运行Docker镜像“abhartiya/tools_megplus”，并在容器中挂载pwd来托管test.txt文件。执行完成后，工具会在pwd路径下的out目录中存储所有的扫描结果。

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/EdOverflow/megplus/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **MegPlus** ：【[ _GitHub传送门_](https://github.com/EdOverflow/megplus)】

## 参考资料

> [
> _https://www.youtube.com/watch?v=DvS_ew77GXA_](https://www.youtube.com/watch?v=DvS_ew77GXA)
>
> [ _https://golang.org/doc/_](https://golang.org/doc/)
>
> [
> _http://manpages.ubuntu.com/manpages/artful/man1/gio.1.html_](http://manpages.ubuntu.com/manpages/artful/man1/gio.1.html)
>
> [ _https://github.com/tomnomnom/meg_](https://github.com/tomnomnom/meg)
>
> [ _https://user-> images.githubusercontent.com/18099289/35768719-daaaf30c-0900-11e8-92ab-> bdc2498c80bf.png_](https://user-> images.githubusercontent.com/18099289/35768719-daaaf30c-0900-11e8-92ab-> bdc2498c80bf.png)
>
> [
> _https://github.com/tomnomnom/waybackurls_](https://github.com/tomnomnom/waybackurls)
>
> [
> _https://github.com/aboul3la/Sublist3r_](https://github.com/aboul3la/Sublist3r)

