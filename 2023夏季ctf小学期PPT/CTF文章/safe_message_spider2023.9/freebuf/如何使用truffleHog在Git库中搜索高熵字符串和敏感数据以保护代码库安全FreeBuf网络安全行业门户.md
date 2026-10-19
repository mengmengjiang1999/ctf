## 关于truffleHog

truffleHog是一款功能强大的数据挖掘工具，该工具可以帮助广大研究人员轻松从目标Git库中搜索出搜索高熵字符串和敏感数据，我们就可以根据这些信息来提升自己代码库的安全性了。该工具可以通过深入分析目标Git库的提交历史和代码分支，来搜索出潜在的敏感信息。

## 运行机制

该工具将遍历目标Git库的每个分支的整个提交历史，检查每个提交的每个Diff，并检查可能存在的敏感数据。这是由正则表达式和熵得出的，对于熵检查，truffleHog将评估每个Diff中超过20个字符的文本块的base64字符集和十六进制字符集的香农熵。如果在任何时候检测到大于20个字符的高熵字符串，它便会将相关数据打印到屏幕上。

## 工具安装

该工具基于Python开发，因此广大研究人员可以使用pip命令来完成工具的安装：

    
    
    pip install truffleHog

## 自定义配置

我们可以通过“--rules /path/to/rules”添加自定义正则表达式，添加方式为JSON文件，内容格式如下：

    
    
    {
    
        "RSA private key": "-----BEGIN EC PRIVATE KEY-----"
    
    }
    
    
    {
    
        "local self signed test key": "-----BEGIN EC PRIVATE KEY-----\nfoobar123\n-----END EC PRIVATE KEY-----",
    
        "git cherry pick SHAs": "regex:Cherry picked from .*",
    
    }

注意，之前版本的truffleHog是在git Diff上运行熵检查。该功能当前版本仍然存在，但增加了高信号正则表达式检查，并且还增加了抑制熵检查的功能：

    
    
    trufflehog --regex --entropy=False https://github.com/dxa4481/truffleHog.git

或者

    
    
    trufflehog file:///user/dxa4481/codeprojects/truffleHog/

在“--include_paths”和“--exclude_paths”选项的帮助下，我们还可以通过在文件中定义正则表达式（每行一个）来匹配目标对象路径，从而将扫描限制为Git历史中对象的子集。下面给出的是可供参考的正则文件样例：

    
    
    include-patterns.txt：
    
    src/
    
    # lines beginning with "#" are treated as comments and are ignored
    
    gradle/
    
    # regexes must match the entire path, but can use python's regex syntax for
    
    # case-insensitive matching and other advanced options
    
    (?i).*\.(properties|conf|ini|txt|y(a)?ml)$
    
    (.*/)?id_[rd]sa$
    
    exclude-patterns.txt：
    
    (.*/)?\.classpath$
    
    .*\.jmx$
    
    (.*/)?test/(.*/)?resources/

这些过滤器文件接下来可以通过下列命令部署使用：

    
    
    trufflehog --include_paths include-patterns.txt --exclude_paths exclude-patterns.txt file://path/to/my/repo.git

在这些过滤器的帮助下，工具可以发现并报告目标Git库中根目录下的问题。与此同时，我们还可以使用“-h”和“--help”命令来查看更多有用的信息。

## 工具帮助信息

    
    
    usage: trufflehog [-h] [--json] [--regex] [--rules RULES] [--allow ALLOW]
    
                      [--entropy DO_ENTROPY] [--since_commit SINCE_COMMIT]
    
                      [--max_depth MAX_DEPTH]
    
                      git_url
    
     
    
    Find secrets hidden in the depths of git.
    
     
    
    positional arguments:
    
      git_url               URL for secret searching
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      --json                Output in JSON
    
      --regex               Enable high signal regex checks
    
      --rules RULES         Ignore default regexes and source from json list file
    
      --allow ALLOW         Explicitly allow regexes from json list file
    
      --entropy DO_ENTROPY  Enable entropy checks
    
      --since_commit SINCE_COMMIT
    
                            Only scan from a given commit hash
    
      --branch BRANCH       Scans only the selected branch
    
      --max_depth MAX_DEPTH
    
                            The max commit depth to go back when searching for
    
                            secrets
    
      -i INCLUDE_PATHS_FILE, --include_paths INCLUDE_PATHS_FILE
    
                            File with regular expressions (one per line), at least
    
                            one of which must match a Git object path in order for
    
                            it to be scanned; lines starting with "#" are treated
    
                            as comments and are ignored. If empty or not provided
    
                            (default), all Git object paths are included unless
    
                            otherwise excluded via the --exclude_paths option.
    
      -x EXCLUDE_PATHS_FILE, --exclude_paths EXCLUDE_PATHS_FILE
    
                            File with regular expressions (one per line), none of
    
                            which may match a Git object path in order for it to
    
                            be scanned; lines starting with "#" are treated as
    
                            comments and are ignored. If empty or not provided
    
                            (default), no Git object paths are excluded unless
    
                            effectively excluded via the --include_paths option.

## 结合Docker使用

首先，我们要进入包含目标Git库的目录：

    
    
    cd /path/to/git

然后通过Docker镜像启动truffleHog，并运行下列命令：

    
    
    docker run --rm -v "$(pwd):/proj" dxa4481/trufflehog file:///proj

“-v”选项将把当前工作目录（pwd）加载到Docker容器中的/proj目录中。

“file:///proj”包含了容器中“/proj”目录的引用。

## 工具使用样例

![](https://image.3001.net/images/20220228/1646027247_621c61efa0c726a464eec.png!small)

## 项目地址

 **truffleHog：** 【[
_GitHub传送门_](https://github.com/trufflesecurity/truffleHog)】

## 参考资料

[ _https://join.slack.com/t/trufflehog-community/shared_invite/zt-pw2qbi43-Aa86hkiimstfdKH9UCpPzQ_](https://join.slack.com/t/trufflehog-community/shared_invite/zt-pw2qbi43-Aa86hkiimstfdKH9UCpPzQ)

