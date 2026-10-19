![](https://image.3001.net/images/20200806/1596644651.jpg!small)

## Sitedorks

Sitedorks是一款针对多个搜索引擎的统一搜索工具，Sitedorks可以帮助广大研究人员仅使用一个搜索关键词便能够同时搜索包括Google、Bing、Yahoo和Yandex在内的多个不同站点。除此之外，该工具默认以提供了一套默认列表，其中也包括GitHub、Gitlab、Surveymonkey和Trello等等。目前，默认列表中已包含了241个可Docker化的网站，文件中的当前类别包括：

  * analysis(10)
  * cloud(35)
  * code(38)
  * comm(27)
  * companies(3)
  * docs(36)
  * edu(3)
  * forms(11)
  * orgs(13)
  * other(4)
  * remote(1)
  * shortener(15)
  * social(42)
  * storage(3)

## 工具特性

  * 该工具可以帮助用户轻松查询不同的搜索引擎；
  * 可以针对1个或多个类别执行Docker；
  * 可轻松针对不同使用场景创建输入文件；
  * 将新网站添加到您的搜索查询中，只需将它们添加到输入文件即可；
  * 默认已包含大量可Docker化的网站，并且该列表会定期更新；
  * 有些搜索引擎在一个查询中会忽略了大量关键字/字符，此时可以使用参数-count来将Dork划分成更多的查询。
  * 该工具提供了一个包含了Bugcrowd、HackerOne、Intigrity和YesWeHack的列表，只需一个命令，就可以同时在多个漏洞奖励平台搜索程序域名了。

## 工具安装

Sitedorks可以直接在默认Kali Linux环境中直接安装、运行和使用，而且无需安装额外的Python包。工具的安装命令如下：

    
    
    git clone https://github.com/Zarcolio/sitedorks
    
    cd sitedorks
    
    bash install.sh

## 工具使用

    
    
    usage: sitedorks [-h] [-cat <category>] [-cats] [-count <count>] [-engine <engine>] [-file <file>]
    
    [-query <query>] [-site <on|off|inurl>] [-excl <domains>] [-echo]
    
     
    
    Use your favorite search engine to search for a search term with different websites. Use single quotes around a
    
    query with double quotes. Be sure to enclose a query with single quotes it contains shell control characters like
    
    space, ';', '>', '|', etc.
    
     
    
    optional arguments:
    
      -h, --help            Show this help message, print categories on file (add -file to check other CSV file) and exit.
    
      -cat <category>       Choose from 1 or more categories, use ',' (comma) as delimiter. Defaults to all categories.
    
      -cats                 Show all categories on file, use with or without -file.
    
      -count <count>        How many websites are searched per query. Google has a maximum length for queries.
    
      -engine <engine>      Search with 'google', 'baidu', 'bing', 'bing-ecosia', 'duckduckgo' 'yahoo' or 'yandex', defaults to
    
                            'google'.
    
      -file <file>          Enter a custom website list.
    
      -query <query>        Enter a mandatory search term.
    
      -site <on|off|inurl>  Turn the 'site:' operator 'on' or 'off', or replace it with 'inurl:' (only for Google), defaults to
    
                            'on'.
    
      -excl <domains>       Excluded these domains from the search query.
    
      -echo                 Prints the search query URLs, for further use like piping or bookmarking.

## 工具使用样例

想要使用Google来查询包含“uber.com”相关的所有类型内容，可以直接使用下列命令：

    
    
    sitedorks -query '"uber.com"'

想要查询“uber website”，可以直接使用下列命令：

    
    
    sitedorks -query '"uber website"'

想要查询Yandex中的通信邀请，但是不想使用“site:”查询关键词，可以使用下列命令：

    
    
    sitedorks -cat comm -site disable -engine yandex -query uber

如果想要查看文件中的类型，可以使用下列命令：

    
    
    sitedorks -file sitedorks-hackerone.csv -cats

## 项目地址

Sitedorks：【[ _GitHub传送门_](https://github.com/Zarcolio/sitedorks)】

