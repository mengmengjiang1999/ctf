**今天给大家介绍的是一款名叫GitGot的半自动信息收集工具，在GitGot的帮助下，广大研究人员可以轻松从GitHub公开数据中搜索敏感信息。**  

![](https://image.3001.net/images/20190821/1566403095_5d5d6a17c5ecd.png!small)

## 工具运行机制

在搜索会话的过程中，用户可以给GitGot提供反馈信息，并设置需要忽略的搜索结果，GitGot将会对搜索结果集进行筛选。用户还可以根据通过文件名、存储库名称、用户名或文件内容的模糊匹配来设置黑名单。

用户可以将之前的会话所生成的黑名单保存下来，并针对类似的查询进行重复使用，会话也可以随时进行暂停或恢复。

## 工具安装

### 手动安装

首先安装ssdeep依赖，Ubuntu/Debian或其他Linux发行版请参考下列命令：

    
    
    apt-get install libfuzzy-dev ssdeep

macOS可以参考下列命令：

    
    
    brew install ssdeep

Windows用户的ssdeep安装方法，请参考这篇【[文档](https://ssdeep-project.github.io/ssdeep/index.html)】。

安装好ssdeep之后，可以使用pip命令来安装Python依赖：

    
    
    pip3 install -r requirements.txt

### Docker指令

运行gitgot-docker.sh文件来构建GitGot Docker镜像，并执行Docker化的GitGot版本工具。运行之后，gitgot-docker.sh文件将会在主机当前的工作目录下创建并加载logs和states目录。如果gitgot-docker.sh文件是直接从GitGot项目目录下运行的话，它将会更新Docker容器：

    
    
    ./gitgot-docker.sh -q example.com

## 工具使用

由于GitHub会限制访问频率，因此我们还需要一个令牌，我们可以直接创建一个无权限/无范围的GitHub
API令牌：【[传送门](https://github.com/settings/tokens)】，这个令牌可以直接拿来访问公共GitHub库。Gitgot.py文件的顶部需要添加下列代码：

    
    
    ACCESS_TOKEN= "<NO-PERMISSION-GITHUB-TOKEN-HERE>"

编辑好令牌之后，我们就可以开始动手了：

# 使用默认正则式列表和日志文件地址(/logs/<query>.log)查询字符串"example.com"

    
    
    ./gitgot.py -q example.com

#查询GitHub Gist

    
    
    ./gitgot.py --gist -q CompanyName

# 使用GitHub高级搜索语句

    
    
    ./gitgot.py -q "org:github cats"

# 自定义正则表达式和日志文件地址

    
    
    ./gitgot.py -q example.com -f checks/default.list -o example1.log

# 恢复之前退出的会话

    
    
    ./gitgot.py -q example.com -r example.com.state

# 使用现有的正则表达式进行新的查询

    
    
    ./gitgot.py -q "Example Org" -r example.com.state

## UI命令

    
    
    Ignore similar [c]ontent: 设置文件内容哈希黑名单来过滤搜索结果；
    
    Ignore [r]epo/[u]ser/[f]ilename: 通过字符串黑名单来忽略搜索结果；
    
    Search /(mykeyword)]: 提供自定义正则表达式进行实时搜索结果匹配；
    
    [a]dd to Log: 添加匹配日志文件的正则表达式；
    
    Next [<Enter>],[b]ack: 返回高级搜索结果；
    
    [s]ave state: 保存黑名单列表以及搜索结果；
    
    [q]uit:退出；

## 项目地址

GitGot：【[GitHub传送门](https://github.com/BishopFox/GitGot)】

 ***
参考来源：[BishopFox](https://github.com/BishopFox/GitGot)，Alpha_h4ck编译整理，转载请注明来自FreeBuf.COM**

