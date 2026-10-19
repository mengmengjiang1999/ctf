![](https://image.3001.net/images/20200805/1596635737.jpg!small)

## Commit-Stream

Commit-Stream是一款针对GitHub的安全检测工具，该工具能够利用GitHub的事件API来从GitHub库的commit日志记录中实时提取出敏感信息。

换句话说，Commit-Stream也可以作为开源情报收集工具和网络侦察工具来使用，对于红队研究人员和Bug Hunter来说，该工具能够提供以下帮助：

  * 了解目标公司员工提交的代码以及目标代码库，该功能通过对邮件域名过滤来实现；
  * 识别属于用户个人的GitHub代码库，可按开发者姓名过滤筛选；
  * 与其他工具（例如trufflehog）整合使用，并从目标GitHub库中提取出敏感数据；

## 工具安装

如需获取针对Windows、macOS和Linux的64位预编译的可执行程序文件，可以直接点击【[
_这里_](https://github.com/x1sec/commit-stream/releases/)】访问该项目的GitHub
Release页面。

### Go get

如果你想要自行对项目代码进行构建，可以直接使用go get方法进行工具安装，但前提是本地主机已配置好了[
_Go环境_](https://golang.org/doc/install)：

    
    
    go get -u github.com/x1sec/commit-stream

### 源码构建

    
    
    go get && go build

## 工具使用

    
    
    Usage:
    
      commit-stream [OPTIONS]
    
     
    
    Options:
    
      -e, --email       需要匹配的电子邮件地址，多个地址通过逗号分隔，不填则匹配全部 
    
      -n, --name       需要匹配的开发者姓名，多个地址通过逗号分隔，不填则匹配全部   
    
      -t, --token       GitHub令牌，如果不指定则默认使用环境变量 'CSTREAM_TOKEN'
    
      -a  --all-commits  搜索之前的commit代码提交历史（默认为false）
    
      -i  --ignore-priv  忽略noreply.github.com私有邮件地址（默认为false）

Commit-Stream需要使用到一个GitHub个人访问令牌，你可以直接在GitHub中生成这个令牌：[设置/
开发者设置/个人访问令牌]，接下来，选择“生成一个新的令牌”。其他都不用选择，直接输入令牌名称并点击生成按钮即可。

令牌创建成功之后，我们建议广大研究人员通过环境变量“CSTREAM_TOKEN”来设置这个访问令牌：

    
    
    export CSTREAM_TOKEN=xxxxxxxxxx

或者，我们也可以在调用该工具时，通过“--token”参数来设置访问令牌：

    
    
    ./commit-stream --token xxxxxxxxxx

如果在运行Commit-Stream时没有提供任何运行参数的话，该工具将会立即导出目标GitHub库的开发者详细信息，并在终端中以CSV格式导出相关的代码库，在这里用户可以使用过滤选项来进行结果筛选。

### 通过电子邮件域名过滤：

    
    
    ./commit-stream --email '@company.com'

### 通过开发者姓名过滤：

    
    
    ./commit-stream --name 'John Smith'

### 多个关键词可以通过逗号“，”进行分隔，比如说：

    
    
    ./commit-stream --email '@telsa.com,@ford.com'

通过使用“--all-commits”参数，可以搜索目标代码库最多20条代码提交记录。电子邮件地址如果设置成了私有地址（@users.noreply.github.com），可以通过“--ignore-priv”选项来忽略该地址。如果长时间运行该工具，这个选项将有助于减少收集的数据量。

## 注意事项

GitHub能够防止电子邮件地址暴露，我们可以在GitHub的设置页面中，选择电子邮件选项中的“Keep my email addresses
private”和“Block command line pushes that expose my email”。

## 工具演示视频

视频地址：【[ _点我观看_](https://asciinema.org/a/317469)】

## 项目地址

Commit-Stream：【[ _GitHub传送门_](https://github.com/x1sec/commit-stream)】

