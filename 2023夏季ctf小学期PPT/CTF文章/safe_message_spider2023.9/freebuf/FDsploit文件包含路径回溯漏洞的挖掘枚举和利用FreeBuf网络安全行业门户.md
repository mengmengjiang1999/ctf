**FDsploit是一个件包含/路径回溯漏洞的挖掘枚举和利用工具。**

**![FDsploit.png](https://image.3001.net/images/20190322/1553211473_5c9420511e2eb.png!small)**

FDsploit可自动化的为我们发现和利用本地/远程文件包含及目录遍历漏洞。如果发现了LFI漏洞，可以使用--lfishell选项来进行利用。目前，支持以下3种不同类型的LFI shell：

> simple: 这种类型的shell允许用户轻松读取文件，而无需每次都输入URL。
> 此外，它只提供文件的输出，而不是页面的整个html源码，这使得它非常实用。
>
> expect: 这种类型的shell是一个半交互式shell，允许用户通过PHP的expect:// wrapper执行命令。
>
> input: 这种类型的shell是一个半交互式shell，允许用户通过PHP的php://input流执行命令。

到目前为止，只有两个lfi-shell内置命令：

> clear
>
> exit

## 特性

> LFI-shell接口仅提供已处理文件或发出命令的输出，而不是所有html代码。
>
> 可以指定3种不同类型的LFI shell。
>
> 支持GET/POST请求。
>
> 自动检测GET参数。
>
> 可以使用通配符（*）指定某些参数进行测试。
>
> 可以指定和使用可选的会话cookie。
>
> 可以使用PHP函数自动检查RCE。
>
> 使用sha-256 hash识别潜在的漏洞。
>
> 支持base64/urlencoding。

## 示例

 **1.目录遍历漏洞发现：**

从下面的输出来看，directory参数可能易受到目录遍历漏洞的影响，因为每个使用../作为payload的请求都会产生不同的sha-256哈希。每个请求的内容长度也不同：

    
    
    ./fdsploit.py -u 'http://127.0.0.1:8888/test/bWAPP/bWAPP/directory_traversal_2.php?directory=documents' -c 'PHPSESSID=7acf1c5311fee614d0eb40d7f3473087; security_level=0' -d 8

**![directory_traversal.png](https://image.3001.net/images/20190322/1553211502_5c94206e0c326.png!small)**

 **2\. LFI漏洞发现：**

同样，
language参数易受到LFI漏洞的影响，因为使用../etc/passwd等作为payload，每个绿色的请求都会产生不同的哈希，与初始值不同的内容长度，并且指定的关键字在响应中：

    
    
    ./fdsploit.py -u 'http://127.0.0.1:8888/test/bWAPP/bWAPP/rlfi.php?language=*&action=go' -c 'PHPSESSID=7acf1c5311fee614d0eb40d7f3473087; security_level=0' -d 7 -k root -p /etc/passwd

**![3lfi.png](https://image.3001.net/images/20190322/1553211521_5c942081d224b.png!small)**

 **3.使用simple shell进行LFI利用：**

使用simple shell利用上面的LFI：

![simpleshell.png](https://image.3001.net/images/20190322/1553211546_5c94209a5ca97.png!small)

##  **注意：**

> 使用POST时，还必须指定--params选项。
>
> 要测试目录遍历漏洞，必须将--payload选项保留为默认值（None）。
>
> 当--file选项用于多URL测试时，则仅支持GET请求。
>
> 如果同时设置了--file和--> cookie选项，那么每次url必须在同一个域上引用时才可以指定一个cookie，或者在没有cookie的情况下可以访问（这将在未来的更新中修复）。
>
> input shell与POST不兼容。

## 安装依赖

    
    
    pip install -r requirements.txt --upgrade --user

## 未来计划

> 修复以上第4条，让--file可以与POS参数和cookies工作，可能会使用json等文件作为输入。
>
> 向--lfishell添加更多内置命令，如history等。

## 贡献和反馈

如果你愿意为该项目贡献你的一份力或对该项目有任何意见或建议，那么欢迎你随时通过issue提交他们。我们会尽快的审核并解决它！谢谢！

***参考来源：[GitHub](https://github.com/chrispetrou/FDsploit)，FB小编secist编译，转载请注明来自FreeBuf.COM
**  

