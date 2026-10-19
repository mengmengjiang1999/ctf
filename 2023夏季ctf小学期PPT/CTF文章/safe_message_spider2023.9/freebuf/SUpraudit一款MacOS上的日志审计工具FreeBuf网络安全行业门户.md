## 背景

 **你可能对BSM审计有所了解，也可能完全没有听说过。这是Solaris
OS遗留下来的产物，它存在于FreeBSD，Linux，当然还包括MacOS上。在我的[*OS Internals::Security &
Insecurity](http://newosxbook.com/)的第二章中有审计的详细介绍。虽然它没有MAC框架那样强大（并且无法进行推理，只能对操作做出反应），但也不像其他框架将简单的现场监控与纯用户模式的优点相结合。内核仍然非常复杂，但是你不能也不应该修改它的默认审计逻辑。**

值得注意的是，praudit(1)，它用于打印来自/var/audit和/dev/auditpipe中的文件的审计记录，这是一个非常可怕的工具，即使在与-l（单行输出）一起使用时，它也不是grep(1)友好的工具。

## SUpraudit

经过25年左右的时间，现在是时候进行改造了。我已经将praudit paltry ~220行的汇编回源（assembly back to
source），然后我决定重建它：

    
    
    root@Zephr (~) # supraudit -h
    supraudit: illegal option -- -h
    usage: supraudit [-lnpx] [-r | -s] [-d del] [file ...]
             OR
           supraudit [-S [-C] |-J] [-F filter] [-O output]
           -S: SuperAudit records (much more readable)
           -C: Color (because everything looks better in color)
           -J: JSON
           -L: Relay to local syslog
           -F: Filter by predefined rules - files, net, proc
           -O: Log to specified outputfile
    
    This is J's supraudit, compiled on May 22 2018. 
    Latest version always free @http://NewOSXBook.com/tools/supraudit.html

使用模式与praudit几乎相同 - 即supraudit可以用作审计文件的pipe
(|)的接收端，或者运行在通常是/dev/auditpipe上，因为它提供了实时审计firehose。supraudit的新开关都是大写的，以避免与之前的开关产生冲突。这些开关允许各种输出格式或过滤器（如下“使用示例”中所述）。

与praudit(1)不同的是，我的工具 - 在/dev/auditpipe上运行时 -通过ioctl(2)代码配置管道，允许它在不影响本地审计策略的情况下设置自定义过滤器（或根本没有）。简而言之，你不需要再配置任何东西 -只需在管道上直接运行supraudit并查看每个BSD级别的操作即可！（请注意，由于内核不支持该Mach级别操作，因此无法对其进行审计）。

## 使用示例

最直接和有用的功能是-S，它使用我自己的记录格式，而不是Apple的默认格式。格式非常像Linux的strace（和[我自己的](http://newandroidbook.com/tools/jtrace.html)jtrace），并且非常友好。你可以使用-C或JCOLOR=1来切换颜色：

![supraudit-connect.png](https://image.3001.net/images/20180529/15275564716069.png!small)

你可以使用grep和cut -d'|'进行过滤。

.一些有用的grep过滤是'INET'（所有网络连接），'INET4'（IPv4）和'INET6'。

![supraudit-oc.png](https://image.3001.net/images/20180529/15275565258177.png!small)

作为grep的快速替代方案，你可以使用 -F files,
net或proc作为内置过滤器。这是推荐的，因为之后你可以随时应用grep(1)。此外，这样做会自动将未经过滤的审计日志保存到/tmp，以便你可以随时查看完整的图片。

## syslog/os_log集成

将-L与-S一起使用将记录到本地syslog/os_log：

![supraudit-L.png](https://image.3001.net/images/20180529/15275565495676.png!small)

## 远程日志主机（loghost）

审计机制最明显的遗漏之一是，与syslogd不同，它没有对中央服务器进行远程日志记录 -如果你想确保日志的完整性，那么这是非常必要的，如果你拥有超过5台机器（如在企业中），则至关重要。那么，这已被修复。将supraudit与-R一起使用将会转发给中央服务器，但这需要......

## Supraudit-PRO

Supraudit的“专业版”具有更多功能（PRO版目前正处于开发阶段），其中包括：

> 触发器：使用配置文件，可以用基本变量替换来执行超审计命令（例如：'on file access "/secret/*" kill
> subject'）。这对于安全敏感的防御是不适用的，因为审计机制是被动的。但是建立一个基本的主机入侵机制会很有用。
>
>
> 插件：SUpraudit为希望编写自己插件的开发人员提供了一个简单但功能强大的API。这可以用来与littlesnitch/bigbrother/twinsister/whatever结合使用。
>
> GUI（即将推出）：当你合并多个审计日志时，数据会复杂的让你眼花缭乱。SUpraudit
> pro有一个GUI，你可以使用它来过滤，排序，分析甚至构建timeline视图，以记录你的完成进度。

## 相关授权

supraudit免费供个人，和/或5个主机内使用。如果你打算在10个以上主机的商业环境中使用它，则需要与products@technologeeks.com联系取得授权
- 你可能想要获得PRO版本，其中包含服务器（用于-R
消息中继）以及方便快速的GUI操作。同时欢迎大家对我提出修复或改进的建议。supraudit下载请[点击这里](http://newosxbook.com/tools/supraudit.tgz)。

 ***参考来源：[newosxbook](http://newosxbook.com/tools/supraudit.html)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**  

