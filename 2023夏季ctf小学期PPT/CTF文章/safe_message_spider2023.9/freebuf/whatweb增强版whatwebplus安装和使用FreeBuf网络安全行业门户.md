# ****whatweb增强版**** ** **whatweb-plus****

安装和使用

kali下的安装:

首先卸载原版whatweb:

apt-get remove WhatWeb

安装:

上传WhatWeb增强版到kali /opt 文件夹

添加可执行权限

cd /opt/WhatWeb/

chmod +x whatweb

使得WhatWeb可以直接被调用运行

ln -s /opt/WhatWeb/whatweb /usr/bin

然后先将/opt/WhatWeb/my-plugins目录清空再将下载的插件解压缩放到/opt/WhatWeb/my-plugins目录下面

![1632057999_61473a8f579eb28e22800.png!small](https://image.3001.net/images/20210919/1632057999_61473a8f579eb28e22800.png!small)

![1632058012_61473a9c9d0e663fbf904.png!small](https://image.3001.net/images/20210919/1632058012_61473a9c9d0e663fbf904.png!small)

执行whatweb -l查看插件是否加载:

![1632058019_61473aa3c9a1b36a9797e.png!small](https://image.3001.net/images/20210919/1632058019_61473aa3c9a1b36a9797e.png!small)

简单扫描一个目标

Whatweb [_http://xxxx.com_](http://xxxx.com)

比如如下爆出的一些指纹

![1632058026_61473aaa439d52b8719fe.png!small](https://image.3001.net/images/20210919/1632058026_61473aaa439d52b8719fe.png!small)

可以在plugins目录搜索一下看到指纹规则

![1632058031_61473aafde1cfdc75b41e.png!small](https://image.3001.net/images/20210919/1632058031_61473aafde1cfdc75b41e.png!small)

规则的帮助文件在这里:

https://mp.weixin.qq.com/s/TaYHrzw5Yb6jxj046nR_DA

比如这样:

![1632058043_61473abb6cf204ed37cda.png!small](https://image.3001.net/images/20210919/1632058043_61473abb6cf204ed37cda.png!small)

插件规则修改小示例:

比如我某个网站有个ewebeditor.编辑器,whatweb默认规则如下:

![1632058052_61473ac40a27b64d9942a.png!small](https://image.3001.net/images/20210919/1632058052_61473ac40a27b64d9942a.png!small)

实际测试中发现匹配不到,然后通过大概收集，我把matches修改如下

![1632058064_61473ad09c61e2a873cd3.png!small](https://image.3001.net/images/20210919/1632058064_61473ad09c61e2a873cd3.png!small)

规则解释:

通过:text指定搜索/ewebeditor.htm?和eWebSoft和www.ewebsoft.com这几个关键字

通过:url 指定默认去访问/admin/eWebEditor/admin_login.asp

和/eWebEditor/admin_login.asp来触发网站返回关键字

通过如下参数:

whatweb -p ewebeditor http://www.xxxxx.com/admin/eWebEditor/admin_login.asp -a
4

就会让whatweb主动去访问规则里的:url后面的链接,-p参数是指定单独使用某个规则,

-a 4参数指定让whatweb主动访问规则里:url后面的链接也可以直接用如下参数:

whatweb -p ewebeditor http://www.xxxxx.com -a 4

如下是扫描结果,可以看到已经识别出来了ewebeditor

![1632058087_61473ae79d707cad6da2c.png!small](https://image.3001.net/images/20210919/1632058087_61473ae79d707cad6da2c.png!small)

如果不使用-p参数指定插件规则，直接开启所有插件里的:url可以用如下参数:

Whatweb [_http://www.xxxx.com_](http://www.xxxx.com)-a 4 --log-json
/home/123.txt

\--log-json是保存json输出结果到文件

插件下载地址:

https://github.com/winezer0/whatweb-plus

如下是详细命令参数:

    
    
    WhatWeb - Next generation web scanner version 0.5.5.12.用法: whatweb [选项] 目标目标选择:URL     URL,主机名,IP地址,文件名, CIDR IP段格式（支持多目标逗号分隔）--input-file=文件名, -i  从文件中读取目标，可以使用-i /dev/stdin管道。目标修改:--url-prefix   为目标url添加前缀。（PS：支持单字符串）--url-suffix   为目标url添加后缀。（PS：支持单字符串）--url-pattern  替换目标url中的%insert%串（PS：支持单字符串,源版本BUG已修复）举例：whatweb http://www.baidu.com/%insert%/robots.txt --url-pattern=1111111111 -Z新增功能请求控制:--no-max-match, -X   新增，忽略匹配:url要求，默认True。--no-min-urls, -Y    新增，关闭最小化访问插件:url，默认True。--no-base-path, -Z   新增，关闭自动访问高频指纹路径，默认True。新增请求控制功能是为了实现尽可能少的访问插件中的URL，对于多个相同的URL只访问一次，并且不影响匹配效果。max-match 开启该功能会忽略对指纹中:url的匹配，并且对同一个指纹中的多个:url进行去重访问，同时不影响匹配效果，（Passive和Aggressive可能不受影响）。min-urls 开启该功能会把插件中的url请求调用到whatweb主流程中，由于主程序做了URL去重，实现所有插件中的URL都不会重复访问，缺陷是多次调用所有插件,会变慢。（Passive和Aggressive可能不受影响）base-path 内置添加高频的指纹路径,如/favicon.ico, /robots.txt，在访问时会只能追加到目标URL后，便于发现指纹问题。对于高频指纹路径可以关闭[-Z]，其他两个选项[-X -Y]不建议同时关闭。入侵级别：通过攻击级别进行速度/隐身和可靠性之间的权衡控制。--aggression, -a=级别              设置攻击级别。默认值:1。1.隐形 匹配被动规则，为每个目标创建一个HTTP请求，并遵循重定向。3.入侵 促进匹配被动+主动规则，当插件中的有被动规则被匹配，将额外发送主动规则的请求进一步匹配。4.重击 强行匹配被动+主动规则，对每个目标进行大量HTTP请求，所有插件的url会被请求主动规则：matches数组中有:url开头的规则 和 aggressive do函数。被动规则：matches数组中没有:url开头的规则 和 passive do函数。HTTP选项:--user-agent, -U=AGENT       替换请求user-agen,源版本特征是WhatWeb/0.5.5，增强版已修改。--header, -H                     指定默认头将替换它,指定空值将删除它。增强版增加了动态Host头。--follow-redirect=WHEN       控制是否跟随302重定向,可选`never', `http-only', `meta-only', `same-site', or `always'. 默认是总是跟随302跳转--max-redirects=NUM              最大重定向次数. 默认值:10。认证选项：--user, -u=       HTTP基本认证--cookie, -c=COOKIES              使用Cookie ,格式'name=value; name2=value2'.--cookie-jar=FILE              从文件读取一个Cookie.代理配置：--proxy, -P      设置HTTP代理服务器和端口 默认端口8080.--proxy-user      设置代理服务器账号密码插件选项:--list-plugins, -l       列出所有插件。(如果有-p指定插件文件夹会列出文件夹的插件信息(新增))--info-plugins, -I=[SEARCH]       列出所有插件信息. 可选多个关键字搜索（逗号分隔）。(如果有-p指定插件文件夹会列出文件夹的插件信息(新增))--search-plugins=STRING       通过规则里的关键字搜索。(如果有-p指定插件文件夹会列出文件夹的插件信息(新增))，实际上与--info-plugins是同一个选择，只不过支持参数。--plugins, -p=LIST  选择多个插件文件或文件夹中的插件（以逗号分隔），默认选择所有my-plugins和plugins目录的所有插件（注意：代码逻辑导致这个两个文件夹不能删除） 每个元素可以是一个目录、文件或插件名，并且可以有一个[+/-]修饰符 例如: ( +/tmp/moo.rb,+/tmp/foo.rb )  ( title,md5,+./plugins-disabled/ )  ( ./plugins-disabled,-md5 )  ( -p + 是-p +plugins-disabled.的快捷方式,基本没什么用)--grep, -g=STRING|REGEXP  搜索字符串或正则表达式。只显示匹配的结果，例如--grep "hello" --grep "/he[l]*o/" （实际使用时，本参数会先使用正则匹配选择合适的插件，再过滤输出结果）--custom-plugin=DEFINITION       定义一个名为custom-plugin的自定义插件,（原理是生成一个临时插件,然后将规则存放进去,没有什么用途）。例如: ":text=>'powered by abc'"":version=>/powered[ ]?by ab[0-9]/"":ghdb=>'intitle:abc \"powered by abc\"'"":md5=>'8666257030b94d3bdb46e05945f60b42'""{:text=>'powered by abc'}"--dorks=PLUGIN              列出所选插件的谷歌搜索语法，要求插件里面有dorks这一项。输出: --verbose, -v                     详细输出包括插件描述。调试时使用两次--colour,--color=WHEN       控制是否使用颜色。`never', `always', or `auto'.（已修改为总是显示颜色）--quiet, -q                     不要显示简要日志。--no-errors                     禁用错误消息提示日志输出:--log-brief=FILE              日志单行摘要输出。--log-verbose=FILE       日志详细输出。--log-errors=FILE              输出错误日志。--log-xml=FILE              输出XML格式日志。--log-json=FILE              输出JSON格式日志。--log-sql=FILE              输出数据库插入语句格式日志。--log-sql-create=FILE              创建SQL数据库表。--log-json-verbose=FILE       输出JSON详细格式。--log-magictree=FILE              输出MagicTree XML 格式.--log-object=FILE              输出Ruby对象检查格式。--log-mongo-database       MongoDB数据库的名称。--log-mongo-collection       MongoDB集合的名称,默认: whatweb.--log-mongo-host              MongoDB主机名或IP地址。默认值:0.0.0.0。--log-mongo-username              MongoDB用户名。默认值: nil。--log-mongo-password              MongoDB 密码. 默认值: nil.--log-elastic-index              用于elastic存储结果的索引的名称。默认值:whatweb --log-elastic-host              指明elastic http接口的主机:端口. 默认: 127.0.0.1:9200性能和稳定性选项：PERFORMANCE & STABILITY:--max-threads, -t              并发线程数。默认值:25。--open-timeout              打开时间(秒)。默认值:15。--read-timeout              读取时间(秒)。默认值: 30.--wait=SECONDS              连接之间的等待(秒)。这在使用单个线程时非常有用。帮助和杂项:--short-help                     短的使用帮助。--help, -h                     完整的使用帮助--debug                            在插件中引发错误。--version, -V                     显示详细的版本信息（已修改版本号为0.5.5.12）

