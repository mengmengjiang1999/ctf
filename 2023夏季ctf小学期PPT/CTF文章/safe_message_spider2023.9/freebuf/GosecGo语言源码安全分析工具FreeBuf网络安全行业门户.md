****

**gosec是一个Go语言源码安全分析工具，其通过扫描Go AST（抽象语法树）来检查源代码是否存在安全问题。**

##  **许可证**

根据Apache
2.0版本的License；除非符合许可，否则你将不能使用该文件。你可以[在这里](http://www.apache.org/licenses/LICENSE-2.0)获取到一个许可证的副本。

##  **安装**

    
    
    $ go get github.com/securego/gosec/cmd/gosec/...

##  **使用**

我们可以将Gosec配置为仅运行某个规则子集，如排除某些文件路径，生成不同格式的报告等。在默认情况下，Gosec将对提供的输入文件运行所有规则。要从当前目录递归扫描，你可以提供'./...'
作为输入参数。

###  **选择规则**

默认情况下，gosec将针对提供的文件路径运行所有规则。但如果你要指定运行某个规则，则可以使用 '-include=' 参数，或者你也可以使用
'-exclude='来排除那些你不想运行的规则。

 **可用规则**

> G101：查找硬编码凭证
>
> G102：绑定到所有接口
>
> G103：审计不安全区块的使用
>
> G104：审计错误未检查
>
> G105：审计math/big.Int.Exp的使用
>
> G106：审计ssh.InsecureIgnoreHostKey的使用
>
> G201：SQL查询构造使用格式字符串
>
> G202：SQL查询构造使用字符串连接
>
> G203：在HTML模板中使用未转义的数据
>
> G204：审计命令执行情况
>
> G301：创建目录时文件权限分配不合理
>
> G302：chmod文件权限分配不合理
>
> G303：使用可预测的路径创建临时文件
>
> G304：作为污点输入提供的文件路径
>
> G305：提取zip存档时遍历文件
>
> G401：检测DES，RC4或MD5的使用情况
>
> G402：查找错误的TLS连接设置
>
> G403：确保最小RSA密钥长度为2048位
>
> G404：不安全的随机数源（rand）
>
> G501：导入黑名单列表：crypto/md5
>
> G502：导入黑名单列表：crypto/des
>
> G503：导入黑名单列表：crypto/rc4
>
> G504：导入黑名单列表：net/http/cgi
    
    
    # Run a specific set of rules
    $ gosec -include=G101,G203,G401 ./...
    
    # Run everything except for rule G303
    $ gosec -exclude=G303 ./...

###  **注释代码**

与所有自动检测工具一样，gosec也会出现误报的情况。如果gosec报告已手动验证为安全的，则可以使用“#nosec”来注释代码。

注释将导致gosec停止处理AST中的任何其他节点，因此可以应用于整个块或应用于单个表达式中。

    
    
    import "md5" // #nosec
    
    
    func main(){
    
        /* #nosec */
        if x > y {
            h := md5.New() // this will also be ignored
        }
    
    }

在某些情况下，你可能还需要重新访问已使用#nosec注释的位置。那么你可以执行以下命令来运行扫描程序以及忽略#nosec注释：

    
    
    $ gosec -nosec=true ./...

###  **build标签**

gosec能够将Go构建标签传递给分析器。它们可以以逗号分隔的列表提供，如下所示：

    
    
    $ gosec -tag debug,ignore ./...

###  **输出格式**

gosec目前支持text，json，yaml，csv和JUnit XML的输出格式。默认情况下，结果将以stdout（标准输出）。但我们也可以使用
'-fmt'参数指定输出格式，以及'-out'来指定输出文件。

    
    
    # Write output in json format to results.json
    $ gosec -fmt=json -out=results.json *.go

###  **开发**

按照此处的说明安装dep：[https://github.com/golang/dep ](https://github.com/golang/dep)

安装最新版本的golint：<https://github.com/golang/lint>

 **Build**

    
    
    make

 **Tests**

    
    
    make test

###  **发布版本**

确保你已安装了[goreleaser](https://github.com/goreleaser/goreleaser)，然后你可以按以下方式发布gosec：git
tag 1.0.0 export GITHUB_TOKEN= make release

dist文件夹中提供了该工具的已发布版本。build信息应该会被展示在usage文本中。

    
    
    ./dist/darwin_amd64/gosec -h
    gosec  - Golang security checker
    
    gosec analyzes Go source code to look for common programming mistakes that
    can lead to security problems.
    
    VERSION: 1.0.0
    GIT TAG: 1.0.0
    BUILD DATE: 2018-04-27T12:41:38Z

注意，所有已发布的存档也会被同步到GitHub上。

 **Docker image**

你可以执行一个发布版本并build docker镜像：

    
    
    git tag <VERSION>
    export GITHUB_TOKEN=<Your GitHub token>
    make image

在容器中运行gosec：

    
    
    docker run -it -v <YOUR LOCAL WORKSPACE>:/workspace gosec /workspace

###  **生成TLS规则**

可以从Mozilla的[TLS ciphers](https://statics.tls.security.mozilla.org/server-side-tls-conf.json)建议生成TLS规则配置。

首先，你需要安装generator工具：

    
    
    go get github.com/securego/gosec/cmd/tlsconfig/...

现在你可以在项目的根目录中调用go generate：

    
    
    go generate ./...

这将生成一个rules/tls_config.go文件，其中包含来自Mozilla的当前ciphers建议。

 ** *参考来源：[github](https://github.com/securego/gosec)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

