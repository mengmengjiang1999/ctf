  
  

## wfuzz教程

这个教程主要内容是来自[wfuzz官方文档](http://wfuzz.readthedocs.io)。之所以写这个，是因为大多数的国内文章并没有对这个工具进行详细的说明。个人英文还算可以，所以抖胆翻译一下，加上自己的一些操作，一方面加深下自己对这个工具的熟练程度，另一方面方便广大初学者学习。  
感觉这个工具比平时使用的御剑灵活很多（如果参数都弄明白的话），总之，作为渗透测试信息收集的一个环节，它还是有用武之地的。

这个教程本来想弄一篇文章，但是实在是太多了，所以借鉴了一下官方文档的分节，把这个教程做成了一个系列，一共四个部分，分别是：

  * 初识wfuzz：看完这个，你应该可以使用比较简单的命令来做一些任务了。

  * wfuzz 基本用法：看完这个的话，你应该可以从容使用wfuzz来做一些常用扫描器做不了的活，而且觉得wfuzz是个好东西。

  * wfuzz 高级用法：看完这个，你应该就可以玩弄wfuzz于手掌之中，各种小姿势让你在别人扫不成的时候装装X。

  * wfuzz 库：看完这个，不，能去仔细学习这个的同学，我就不说了，此类人圈内统称”大婊哥“，小弟在这只是抛砖引玉了。

* * *

## 简介

wfuzz 是一款Python开发的Web安全测试工具  
wfuzz不仅仅是一个web扫描器：

  * wfuzz能够通过发现并利用网站弱点/漏洞的方式帮助你使网站更加安全。wfuzz的漏洞扫描功能由插件支持。

  * wfuzz是一个完全模块化的框架，这使得即使是Python初学者也能够进行开发和贡献代码。开发一个wfuzz插件是一件非常简单的事，通常只需几分钟。

  * wfuzz提供了简洁的编程语言接口来处理wfuzz或Burpsuite获取到的HTTP请求和响应。这使得你能够在一个良好的上下文环境中进行手工测试或半自动化的测试，而不需要依赖web形式的扫描器。

* * *

### 初识wfuzz

* * *

#### 最简单命令

一个典型的wfuzz命令只需要指定一个字典和一个要测试的URL即可，如下：

  1. `┌─[michael@parrot]─[/usr/share/wfuzz/src/wfuzz]`
  2. `└──╼ $wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt http://testphp.vulnweb.com/FUZZ`
  3. `********************************************************`
  4. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  5. `********************************************************`
  6.   

  7. `Target: http://testphp.vulnweb.com/FUZZ`
  8. `Total requests: 950`
  9.   

  10. `==================================================================`
  11. `ID Response Lines Word Chars Payload `
  12. `==================================================================`
  13.   

  14. `000223: C=404 7 L 12 W 168 Ch "constants"`
  15. `000224: C=404 7 L 12 W 168 Ch "contact"`
  16. `000225: C=404 7 L 12 W 168 Ch "contacts"`
  17. `000230: C=404 7 L 12 W 168 Ch "controlpanel"`
  18. `000226: C=404 7 L 12 W 168 Ch "content"`
  19. `000227: C=404 7 L 12 W 168 Ch "contents"`
  20. `000228: C=404 7 L 12 W 168 Ch "control"`
  21. `...`
  22. `000008: C=404 7 L 12 W 168 Ch "100"`
  23.   

  24. `Total time: 5.193345`
  25. `Processed Requests: 950`
  26. `Filtered Requests: 0`
  27. `Requests/sec.: 182.9264`

wfuzz的输出使我们能够分析web server的响应，还可根据获得的HTTP响应信息过滤出我们想要的结果，比如过滤响应码/响应长度等等。

每一行输出给我们提供了以下信息：

  * ID：测试时的请求序号
  * Response：HTTP响应吗
  * Lines：响应信息中的行数
  * Word：响应信息中的字数
  * Chars：响应信息中的字符数
  * Payload：当前使用的payload

* * *

#### 获取帮助信息

使用`-h`和`--help`参数来获取基本帮助信息和详细帮助信息。  
wfuzz是一个完全模块化的模式，你可以使用`-e <<category>>`参数查看其中可用的模块，例如：

  1. `┌─[michael@parrot]─[/usr/share/wfuzz/src/wfuzz]`
  2. `└──╼ $wfuzz -e iterators`
  3.   

  4. `Available iterators:`
  5.   

  6. ` Name | Summary `
  7. `----------------------------------------------------------------------------------------------`
  8. ` product | Returns an iterator cartesian product of input iterables. `
  9. ` zip | Returns an iterator that aggregates elements from each of the iterables. `
  10. ` chain | Returns an iterator returns elements from the first iterable until it is exhaust `
  11. ` | ed, then proceeds to the next iterable, until all of the iterables are exhausted `
  12. ` | .`

可用的categories包括：`payloads`,`encoders`,`iterators`,`printers`和`scripts`。

* * *

#### Payloads

wfuzz基于一个非常简单的概念：它用一个给定的payload来替换相应的FUZZ关键词的值，我们称FUZZ这样的关键词为`占位符`，这样更容易理解。一个wfuzz中的payload就是一个输入的源。

要想得到所有可用的payload列表，可以执行如下命令：  
`$ wfuzz -e payloads`

关于payloads的更详细的信息可以通过以下命令获取：  
`$ wfuzz -z help`

上面这个命令还可以使用`--slice`参数来对输出结果进行过滤：

  1. `┌─[michael@parrot]─[/usr/share/wfuzz/src/wfuzz]`
  2. `└──╼ $wfuzz -z help --slice "dirwalk"`
  3. `Name: dirwalk 0.1`
  4. `Categories: default`
  5. `Summary: Returns filename's recursively from a local directory.`
  6. `Author: Xavi Mendez (@xmendez)`
  7. `Description:`
  8. ` Returns all the file paths found in the specified directory.`
  9. ` Handy if you want to check a directory structure against a webserver,`
  10. ` for example, because you have previously downloaded a specific version`
  11. ` of what is supposed to be on-line.`
  12. `Parameters:`
  13. ` + dir: Directory path to walk and generate payload from.`

* * *

#### 指定一个payload

每个FUZZ占位符都必须为它指定相应的payload。指定一个payload时有几种方法：

  * 命令比较长的方式是显式的定义payload的参数:  
`$ wfuzz -z file --zP fn=/usr/share/wfuzz/wordlist/general/common.txt
http://testphp.vulnweb.com/FUZZ`

  * 另一个不太长的方式是只提供payload所需的默认参数：  
`$ wfuzz -z file,/usr/share/wfuzz/wordlist/general/common.txt
http://testphp.vulnweb.com/FUZZ`

  * 最后，短的方式是使用别名：  
`$ wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt
http://testphp.vulnweb.com/FUZZ`

`stdin`这个payload可以在使用一些外部字典生成工具时很方便：

  1. `┌─[michael@parrot]─[/usr/share/wfuzz/src/wfuzz]`
  2. `└──╼ $crunch 2 2 ab | wfuzz -z stdin http://testphp.vulnweb.com/FUZZ`
  3. `Crunch will now generate the following amount of data: 12 bytes`
  4. `0 MB`
  5. `0 GB`
  6. `0 TB`
  7. `0 PB`
  8. `Crunch will now generate the following number of lines: 4 `
  9. `********************************************************`
  10. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  11. `********************************************************`
  12.   

  13. `Target: http://testphp.vulnweb.com/FUZZ`
  14. `Total requests: <<unknown>>`
  15.   

  16. `==================================================================`
  17. `ID Response Lines Word Chars Payload `
  18. `==================================================================`
  19.   

  20. `000002: C=404 7 L 12 W 168 Ch "ab"`
  21. `000001: C=404 7 L 12 W 168 Ch "aa"`
  22. `000003: C=404 7 L 12 W 168 Ch "ba"`
  23. `000004: C=404 7 L 12 W 168 Ch "bb"`
  24.   

  25. `Total time: 3.827355`
  26. `Processed Requests: 4`
  27. `Filtered Requests: 0`
  28. `Requests/sec.: 1.045107`

* * *

#### 使用多个payloads

使用`-z` 或`-w` 参数可以同时指定多个payloads，这时相应的占位符应设置为 FUZZ, … , FUZnZ,
其中`n`代表了payload的序号。比如下面的例子，我们同时暴破文件，后缀和目录：  
`$ wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt -w
/usr/share/wfuzz/wordlist/general/common.txt -w
/usr/share/wfuzz/wordlist/general/extensions_common.txt --hc 404
http://testphp.vulnweb.com/FUZZ/FUZ2ZFUZ3Z`

* * *

#### 过滤器

对wfuzz的结果时行过滤是非常重要的：

  * 非常大的字典文件可以生成非常庞大的输出，并且把我们想要的结果淹没
  * 对HTTP响应的一些分类在实际攻击时是非常重要的，例如，为了查检一个SQLi的漏洞是否存在，我们必须能够将合理的响应和错误/不同的响应区分开。

wfuzz可根据HTTP响应码和收到的响应的长度（字数，字符数或行数）来过滤。还可以用正则表达式。  
过滤的方法有两种：隐藏或显示符合过滤条件的结果。

* * *

隐藏响应结果

通过`--hc`，`--hl`，`--hw`，`--hh`参数可以隐藏某些HTTP响应。  
隐藏无法找到的页面的响应如下：  
`$ wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt --hc 404
http://testphp.vulnweb.com/FUZZ`

可指定多个需要隐藏的条件，如，想要加上隐藏禁止访问的响应：  
`$ wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt --hc 404,403
http://testphp.vulnweb.com/FUZZ`

用行数，字数，字符数来指定过滤规则，在当HTTP返回码相同的时候比较方便。比如，网站一般会指定一个自定义的错误页面，返回码是200，但实际上起到了一个404页面的作用，我们称之为软404。  
下面是一个例子：

  1. `┌─[michael@parrot]─[~]`
  2. `└──╼ $wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt --hc 404 http://datalayer.io/FUZZ`
  3. `********************************************************`
  4. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  5. `********************************************************`
  6.   

  7. `Target: http://datalayer.io/FUZZ`
  8. `Total requests: 950`
  9.   

  10. `==================================================================`
  11. `ID Response Lines Word Chars Payload `
  12. `==================================================================`
  13.   

  14. `000083: C=200 51 L 138 W 962 Ch "apache"`
  15. `000008: C=200 51 L 138 W 962 Ch "100"`
  16. `000009: C=200 51 L 138 W 962 Ch "1000"`
  17. `000011: C=200 51 L 138 W 962 Ch "2"`
  18. `000012: C=200 51 L 138 W 962 Ch "20"`
  19. `000013: C=200 51 L 138 W 962 Ch "200"`
  20. `...`

仔细观察上面的结果，我们很容易推断出所有”not found”的返回信息中都有
51个行，138个字，962个字符。因此，我们需要改进一下我们的过滤条件（增加多个过滤条件）：

  1. `┌─[michael@parrot]─[~]`
  2. `└──╼ $wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt --hc 404 --hh 962 http://datalayer.io/FUZZ`
  3. `********************************************************`
  4. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  5. `********************************************************`
  6.   

  7. `Target: http://datalayer.io/FUZZ`
  8. `Total requests: 950`
  9.   

  10. `==================================================================`
  11. `ID Response Lines Word Chars Payload `
  12. `==================================================================`
  13.   

  14. `000430: C=302 0 L 0 W 0 Ch "img"`
  15. `000689: C=500 2 L 1 W 9 Ch "register"`
  16. `000135: C=302 0 L 0 W 0 Ch "blog"`
  17. `000438: C=200 1677 L 5416 W 90077 Ch "index"`
  18.   

  19. `Total time: 8.323663`
  20. `Processed Requests: 950`
  21. `Filtered Requests: 946`
  22. `Requests/sec.: 114.1324`

* * *

显示响应结果

显示响应结果的使用方法跟隐藏时的原理一样，只不过参数变为了：`--sc`，`--sl`，`--sw`，`--sh`。

* * *

使用Baseline

习惯上称Baseline为”基准线“。过滤器可以是某个HTTP响应的引用，这样的引用我们称为Baseline。  
之前的使用`--hh`进行过滤的例子中，还可以使用下面的命令代替：

  1. `┌─[michael@parrot]─[~]`
  2. `└──╼ $wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt --hh BBB http://datalayer.io/FUZZ{notthere}`
  3. `********************************************************`
  4. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  5. `********************************************************`
  6.   

  7. `Target: http://datalayer.io/FUZZ`
  8. `Total requests: 951`
  9.   

  10. `==================================================================`
  11. `ID Response Lines Word Chars Payload `
  12. `==================================================================`
  13.   

  14. `000002: C=200 51 L 138 W 962 Ch "notthere"`
  15. `000432: C=302 0 L 0 W 0 Ch "img"`
  16. `000086: C=404 0 L 0 W 0 Ch "api"`
  17. `000691: C=500 2 L 1 W 9 Ch "register"`
  18. `000137: C=302 0 L 0 W 0 Ch "blog"`
  19. `000045: C=404 0 L 0 W 0 Ch "WEB-INF"`
  20. `000440: C=200 1677 L 5416 W 90077 Ch "index"`
  21.   

  22. `Total time: 21.76636`
  23. `Processed Requests: 951`
  24. `Filtered Requests: 944`
  25. `Requests/sec.: 43.69125`

这里，`{ }`来指定`第一次`HTTP请求时用来替换`FUZZ占位符`的值，其响应将被标记为`BBB`，并用于过滤条件中。

* * *

使用正则表达式过滤

在命令行中，参数`--ss`和`--hs`可以接受正则表达式来对返回的结果时行过滤。  
详细例子请参考<http://edge-security.blogspot.co.uk/2014/10/scan-for-shellshock-with-wfuzz.html>  
`$ wfuzz -H "User-Agent: () { :;}; echo; echo vulnerable" --ss vulnerable -w
cgis.txt http://localhost:8000/FUZZ`

* * *

### 重要关键词

* * *

#### payload

payload为wfuzz生成的用于测试的特定字符串，一般情况下，会替代被测试URL中的FUZZ占位符。  
当前版本中的wfuzz中可用payloads列表如下：

  1. `┌─[michael@parrot]─[~]`
  2. `└──╼ $wfuzz -e payloads`
  3.   

  4. `Available payloads:`
  5.   

  6. ` Name | Summary `
  7. `------------------------------------------------------------------------------------------------------`
  8. ` guitab | 从可视化的标签栏中读取请求 `
  9. ` dirwalk | 递归获得本地某个文件夹中的文件名 `
  10. ` file | 获取一个文件当中的每个词 `
  11. ` autorize | 获取autorize的测试结果Returns fuzz results' from autororize. `
  12. ` wfuzzp | 从之前保存的wfuzz会话中获取测试结果的URL `
  13. ` ipnet | 获得一个指定网络的IP地址列表 `
  14. ` bing | 获得一个使用bing API搜索的URL列表 (需要 api key). `
  15. ` stdin | 获得从标准输入中的条目 `
  16. ` list | 获得一个列表中的每一个元素，列表用以 - 符号分格 `
  17. ` hexrand | 从一个指定的范围中随机获取一个hex值 `
  18. ` range | 获得指定范围内的每一个数值 `
  19. ` names | 从一个以 - 分隔的列表中，获取以组合方式生成的所有usernames值`
  20. ` burplog | 从BurpSuite的记录中获得测试结果 `
  21. ` permutation | 获得一个在指定charset和length时的字符组合 `
  22. ` buffer_overflow | 获得一个包含指定个数个A的字符串. `
  23. ` hexrange | 获得指定范围内的每一个hex值 `
  24. ` iprange | 获得指定IP范围内的IP地址列表 `
  25. ` burpstate | 从BurpSuite的状态下获得测试结果`

* * *

#### encoder

encoder的作用是将payload进行编码或加密。  
wfuzz的encoder列表如下：

  1. `┌─[michael@parrot]─[~]`
  2. `└──╼ $wfuzz -e encoders`
  3.   

  4. `Available encoders:`
  5.   

  6. ` Category | Name | Summary `
  7. `------------------------------------------------------------------------------------------------------------------------`
  8. ` url_safe, url | urlencode | 用`%xx`的方式替换特殊字符， 字母/数字/下划线/半角点/减号不替换`
  9. ` url_safe, url | double urlencode | 用`%25xx`的方式替换特殊字符， 字母/数字/下划线/半角点/减号不替换`
  10. ` url | uri_double_hex | 用`%25xx`的方式将所有字符进行编码`
  11. ` html | html_escape | 将`&`，`<`，`>`转换为HTML安全的字符`
  12. ` html | html_hexadecimal | 用 `&#xx;` 的方式替换所有字符`
  13. ` hashes | base64 | 将给定的字符串中的所有字符进行base64编码`
  14. ` url | doble_nibble_hex | 将所有字符以`%%dd%dd`格式进行编码`
  15. ` db | mssql_char | 将所有字符转换为MsSQL语法的`char(xx)`形式`
  16. ` url | utf8 | 将所有字符以`\u00xx` 格式进行编码`
  17. ` hashes | md5 | 将给定的字符串进行md5加密`
  18. ` default | random_upper | 将字符串中随机字符变为大写`
  19. ` url | first_nibble_hex | 将所有字符以`%%dd?` 格式进行编码`
  20. ` default | hexlify | 每个数据的单个比特转换为两个比特表示的hex表示`
  21. ` url | second_nibble_hex | 将所有字符以`%?%dd` 格式进行编码`
  22. ` url | uri_hex | 将所有字符以`%xx` 格式进行编码`
  23. ` default | none | 不进行任何编码`
  24. ` hashes | sha1 | 将字符串进行sha1加密`
  25. ` url | utf8_binary | 将字符串中的所有字符以 `\uxx` 形式进行编码`
  26. ` url | uri_triple_hex | 将所有字符以`%25%xx%xx` 格式进行编码`
  27. ` url | uri_unicode | 将所有字符以`%u00xx` 格式进行编码`
  28. ` html | html_decimal | 将所有字符以 `&#dd; ` 格式进行编码`
  29. ` db | oracle_char | 将所有字符转换为Oracle语法的`chr(xx)`形式`
  30. ` db | mysql_char | 将所有字符转换为MySQL语法的`char(xx)`形式`

* * *

#### iterator

wfuzz的iterator提供了针对多个payload的处理方式。  
itorators的列表如下：

  1. `┌─[michael@parrot]─[~]`
  2. `└──╼ $wfuzz -e iterators`
  3.   

  4. `Available iterators:`
  5.   

  6. ` Name | Summary `
  7. `----------------------------------------------------------------------------------------------`
  8. ` product | 返回输入条目的笛卡尔积`
  9. ` zip | Retns an iterator that aggregates elements from each of the iterables.（翻译不好，请自行理解）`
  10. ` chain | Returns an iterator returns elements from the first iterable until it is exhaust `
  11. ` | ed, then proceeds to the next iterable, until all of the iterables are exhausted `
  12. ` | （翻译不好，请自行理解）`

* * *

#### printer

wfuzz的printers用于控制输出打印。  
printers列表如下：

  1. `┌─[michael@parrot]─[~]`
  2. `└──╼ $wfuzz -e printers`
  3.   

  4. `Available printers:`
  5.   

  6. ` Name | Summary `
  7. `--------------------------------------------------`
  8. ` raw | `Raw` output format`
  9. ` json | Results in `json` format`
  10. ` csv | `CSV` printer ftw`
  11. ` magictree | Prints results in `magictree` format`
  12. ` html | Prints results in `html` format`
  13. `（比较好懂，不再翻译）`

* * *

#### scripts

暂时不知道怎么使用  
scripts列表如下：

  1. `┌─[michael@parrot]─[~]`
  2. `└──╼ $wfuzz -e scripts`
  3.   

  4. `Available scripts:`
  5.   

  6. ` Category | Name | Summary`
  7. `----------------------------------------------------------------------------------------------------`
  8. ` default, passive | cookies | 查找新的cookies`
  9. ` default, passive | errors | 查找错误信息`
  10. ` passive | grep | HTTP response grep`
  11. ` active | screenshot | 用linux cutycapt tool 进行屏幕抓取 `
  12. ` default, active, discovery | links | 解析HTML并查找新的内容`
  13. ` default, active, discovery | wc_extractor | 解析subversion的wc.db文件`
  14. ` default, passive | listing | 查找列目录漏洞`
  15. ` default, passive | title | 解析HTML页面的title`
  16. ` default, active, discovery | robots | 解析robots.txt文件来查找新内容`
  17. ` default, passive | headers | 查找服务器的返回头`
  18. ` default, active, discovery | cvs_extractor | 解析 CVS/Entries 文件`
  19. ` default, active, discovery | svn_extractor | 解析 .svn/entries 文件`
  20. ` active, discovery | backups | 查找已知的备份文件名`
  21. ` default, active, discovery | sitemap | 解析 sitemap.xml 文件`

* * *

### 内置工具

* * *

#### wfencode 工具

这是wfuzz自带的一个加密/解密（编码/反编码）工具，目前支持内建的encoders的加/解密。

  1. `┌─[michael@parrot]─[~/.wfuzz]`
  2. `└──╼ $wfencode -e base64 123456`
  3. `MTIzNDU2`
  4. `┌─[michael@parrot]─[~/.wfuzz]`
  5. `└──╼ $wfencode -d base64 MTIzNDU2`
  6. `123456`

* * *

#### wfpayload工具

wfpayload是payload生成工具

  1. `┌─[michael@parrot]─[~/.wfuzz]`
  2. `└──╼ $wfpayload -z range,0-10`
  3. `0`
  4. `1`
  5. `2`
  6. `3`
  7. `4`
  8. `5`
  9. `6`
  10. `7`
  11. `8`
  12. `9`
  13. `10`

* * *

#### wxfuzz 工具

这个看源码是一个wxPython化的wfuzz，也就是GUI图形界面的wfuzz。目前需要wxPython最新版本才能使用，但是在ParrotOS和Kali上都无法正常安装成功，问题已在GitHub提交Issue，期待开发者的回复中…

* * *

### wfuzz命令中文帮助

这是wfuzz的主工具，我们平时使用的时候就是用这个。  
先来看看帮助文档：

  1. `┌─[✗]─[michael@parrot]─[~]`
  2. `└──╼ $wfuzz --help`
  3. `********************************************************`
  4. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  5. `* *`
  6. `* Version up to 1.4c coded by: *`
  7. `* Christian Martorella (cmartorella@edge-security.com) *`
  8. `* Carlos del ojo (deepbit@gmail.com) *`
  9. `* *`
  10. `* Version 1.4d to 2.2.9 coded by: *`
  11. `* Xavier Mendez (xmendez@edge-security.com) *`
  12. `********************************************************`
  13.   

  14. ` Usage: wfuzz [options] -z payload,params <url>`
  15.   

  16. ` FUZZ, ..., FUZnZ payload占位符，wfuzz会用指定的payload代替相应的占位符，n代表数字. `
  17. ` FUZZ{baseline_value} FUZZ 会被 baseline_value替换，并将此作为测试过程中第一个请求来测试，可用来作为过滤的一个基础。`
  18.   

  19.   

  20. ` Options:`
  21. ` -h/--help : 帮助文档`
  22. ` --help : 高级帮助文档`
  23. ` --version : Wfuzz详细版本信息`
  24. ` -e <type> : 显示可用的encoders/payloads/iterators/printers/scripts列表`
  25.   

  26. ` --recipe <filename> : 从文件中读取参数`
  27. ` --dump-recipe <filename> : 打印当前的参数并保存成文档`
  28. ` --oF <filename> : 将测试结果保存到文件，这些结果可被wfuzz payload 处理`
  29.   

  30. ` -c : 彩色化输出`
  31. ` -v : 详细输出`
  32. ` -f filename,printer : 将结果以printer的方式保存到filename (默认为raw printer).`
  33. ` -o printer : 输出特定printer的输出结果`
  34. ` --interact : (测试功能) 如果启用，所有的按键将会被捕获，这使得你能够与程序交互`
  35. ` --dry-run : 打印测试结果，而并不发送HTTP请求`
  36. ` --prev : 打印之前的HTTP请求（仅当使用payloads来生成测试结果时使用）`
  37.   

  38. ` -p addr : 使用代理，格式 ip:port:type. 可设置多个代理，type可取的值为SOCKS4,SOCKS5 or HTTP（默认）`
  39.   

  40. ` -t N : 指定连接的并发数，默认为10`
  41. ` -s N : 指定请求的间隔时间，默认为0`
  42. ` -R depth : 递归路径探测，depth指定最大递归数量`
  43. ` -L,--follow : 跟随HTTP重定向`
  44. ` -Z : 扫描模式 (连接错误将被忽视).`
  45. ` --req-delay N : 设置发送请求允许的最大时间，默认为 90，单位为秒.`
  46. ` --conn-delay N : 设置连接等待的最大时间，默认为 90，单位为秒.`
  47.   

  48. ` -A : 是 --script=default -v -c 的简写`
  49. ` --script= : 与 --script=default 等价`
  50. ` --script=<plugins> : 进行脚本扫描， <plugins> 是一个以逗号分开的插件或插件分类列表`
  51. ` --script-help=<plugins> : 显示脚本的帮助`
  52. ` --script-args n1=v1,... : 给脚本传递参数. ie. --script-args grep.regex="<A href=\"(.*?)\">"`
  53.   

  54. ` -u url : 指定请求的URL`
  55. ` -m iterator : 指定一个处理payloads的迭代器 (默认为product)`
  56. ` -z payload : 为每一个占位符指定一个payload，格式为 name[,parameter][,encoder].`
  57. ` 编码可以是一个列表, 如 md5-sha1. 还可以串联起来, 如. md5@sha1.`
  58. ` 还可使用编码各类名，如 url`
  59. ` 使用help作为payload来显示payload的详细帮助信息，还可使用--slice进行过滤`
  60. ` --zP <params> : 给指定的payload设置参数。必须跟在 -z 或-w 参数后面`
  61. ` --slice <filter> : 以指定的表达式过滤payload的信息，必须跟在-z 参数后面`
  62. ` -w wordlist : 指定一个wordlist文件，等同于 -z file,wordlist`
  63. ` -V alltype : 暴力测试所有GET/POST参数，无需指定占位符`
  64. ` -X method : 指定一个发送请求的HTTP方法，如HEAD或FUZZ`
  65.   

  66. ` -b cookie : 指定请求的cookie参数，可指定多个cookie`
  67. ` -d postdata : 设置用于测试的POST data (ex: "id=FUZZ&catalogue=1")`
  68. ` -H header : 设置用于测试请求的HEADER (ex:"Cookie:id=1312321&user=FUZZ"). 可指定多个HEADER.`
  69. ` --basic/ntlm/digest auth : 格式为 "user:pass" or "FUZZ:FUZZ" or "domain\FUZ2Z:FUZZ"`
  70.   

  71. ` --hc/hl/hw/hh N[,N]+ : 以指定的返回码/行数/字数/字符数作为判断条件隐藏返回结果 (用 BBB 来接收 baseline)`
  72. ` --sc/sl/sw/sh N[,N]+ : 以指定的返回码/行数/字数/字符数作为判断条件显示返回结果 (用 BBB 来接收 baseline)`
  73. ` --ss/hs regex : 显示或隐藏返回结果中符合指定正则表达式的返回结果`
  74. ` --filter <filter> : 显示或隐藏符合指定filter表达式的返回结果 (用 BBB 来接收 baseline)`
  75. ` --prefilter <filter> : 用指定的filter表达式在测试之前过滤某些测试条目`

  

