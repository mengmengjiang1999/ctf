**前言**
：在某些场景中不想进行目标的资产测绘只想确定一个URL是否存在某种漏洞，或者已经确定其存在某种漏洞，想进一步利用(反弹shell，代码执行)。本插件就是为了解决这种场景而生——通过直接调用Goby
API对指定的URL进行PoC的检测以及EXP的利用。

## 0x001 插件效果

### 1.1 插件使用

第一次使用需要先生成一个页面去呈现可能扫出的漏洞信息(插件中叫做`载体`)，之后扫描可以选择之前生成过的载体，或者重新生成载体。由于漏洞显示原因，所有生成的载体都会存在一个`Git
repository found`的漏洞。

![](https://image.3001.net/images/20210207/1612689735_601fb147979fe94695a61.gif!small)![](https://image.3001.net/images/20210207/1612687989_601faa7585aa2d269ede0.png!small)

###  **1.2 一瓢冷水**

设想很美好，但是还是有不少缺陷，以上面的GIF为例，首先就是看不到URL检测的进度，其次是还是需要一个Goby的资产测绘页面去呈现漏洞信息，以及大多数PoC的URL
path截断问题。最后一个问题直接导致了漏洞检出与否。

以下图的st045 PoC为例

![](https://image.3001.net/images/20210207/1612689808_601fb1903dfae483f40de.jpg!small)同理执行调用EXP
API时也有这种问题。不过听@帅帅的涛哥说后续PoC可能会解决这个问题。

## 0x002 插件开发

### 2.1 确定PoC检测的API

以下API使用均为臆测和遐想

    
    
    以下应该是Goby全部的API
    assetDetail
    assetDetailPage
    assetSearch
    startScan    //  开始检测模块，
    assetSearchPage
    assetTags
    check
    debugExp  //  exp验证模块
    debugPoc  //  用户POC验证模块
    deleteAssets  //  删除资产
    deleteTask    //  删除任务
    deleteTaskPage
    deleteTasks    //  批量删除任务
    exportAssets
    getChildrenCategory
    getComponents
    getCrawlerURLs    //  获取指定TaskID下的爬取到的url
    getEnvi      //  获取一些配置环境
    getHostLists
    getIPInfo
    getIPInfoPage
    getPOCInfo    //  获取POC详细详细
    getPOCInfoPage
    getPOCList    //  获取POC列表
    getPOCListPage
    getPOCs        //  获取POC列表
    getPocsPage
    getProgress
    getScanIPObjects
    getStatisticsData
    getStatisticsDataPage
    getTasks
    getValueCategory
    getVulAnalysis
    getVulStatistics
    getWebList
    getWebListPage
    hostSearch
    importAssets    //  导入任务
    ipSegment
    listAdapters
    listAdaptersPage
    listSupport
    listSupportPage
    live
    rescanVulnerability      //  poc检测
    resumeScan
    ruleVuls
    setEnvi
    stopScan    //  停止当前进行的任务
    tasks        //  获取所有的历史任务
    tasksPage
    verifyPoc    //  验证导入的poc
    version
    vulnerabilitySearch      //  可以获取存在漏洞的host信息
    vulnerabilitySearchPage
    vulnerabilityStatisticsData
    

这些API根据名字还是很好猜测其功能，比如`getEnvi`，就是获取一些系统配置环境。

![](https://image.3001.net/images/20210207/1612689858_601fb1c2e7d68622d7b5e.jpg!small)首先第一步获取PoC的列表，通过`/api/v1/getPOCList`或者`/api/v1/getPocs`都可以获得，我们的目的是获取filename。

![](https://image.3001.net/images/20210207/1612689874_601fb1d28a9b1e744f82f.jpg!small)获取了`filename`之后就可以进行下一步的操作了。

我们需要的是PoC检测功能，也就是下图红框中的按钮。

![](https://image.3001.net/images/20210207/1612688153_601fab19871cdf097de6c.jpg!small)抓包发现如下所示，使用了`/api/v1/rescanVulnerability`API

![](https://image.3001.net/images/20210207/1612689894_601fb1e65918a6b6546f1.png!small)

大胆猜测与尝试构造如下data后点击发送(只保留options字段也可以正常发包，但是不知道该如何呈现漏洞）：

![](https://image.3001.net/images/20210207/1612689915_601fb1fb5afdd5039c313.png!small)![](https://image.3001.net/images/20210207/1612689926_601fb2062bba429bb4d12.jpg!small)可以看到我们在`[]`中输入的URL都被检测了，与此同时也产生了上面说过的两个缺陷。

1\. 好像没有扫描检测进度的API供我们调用。（下图为正常流程下的漏洞检测，猜测是此检测进度条没有API实现）

![](https://image.3001.net/images/20210207/1612688191_601fab3f1a216fcb20816.jpg!small)

2\. 通过API调用实际上是通过`goby-cmd`检测漏洞，但是没有找到合适的API去单独呈现扫描到的漏洞，`/api/v1/rescanVulnerability`这个API也和大多数PoC检测一样，分为有回显检测和无回显检测。有回显不用多说，返回包匹配一下字符判断即可，无回显的这里用到了DNSLog的方式去判断，在Goby中有一个`godserver`就是用来判断这一类无回显的漏洞，以及反弹shell之类的操作，以上面的`shiro`检测为例，我们解密一下`rememberMe`可以发现：

![](https://image.3001.net/images/20210207/1612689956_601fb2242fb5f898922a5.jpg!small)所以在进行漏洞检测之后，goby-cmd会通过`https://gobygo.net/api/v1/pull?gid=3d358d3a2aaccaf4`进行DNSLog的查询，来判断是否存在漏洞，其中gid在Goby启动时就已经生成。

![](https://image.3001.net/images/20210207/1612689976_601fb2387e8971f4e0cee.jpg!small)

### 2.2 EXP用到的API

EXP用的到API为`/api/v1/debugExp`相比上面的PoC检测API，因为不用用到TaskId，感觉上更加独立。如下调用一个st2045的EXP执行命令：

![](https://image.3001.net/images/20210207/1612690020_601fb264b7afb07cd20ed.jpg!small)

但是这个EXP是有点问题的`whoami;echo
be4ea51d962be8308a0099ae1eb3ec63`，在wins下会报错，再大胆猜测一下，之所以要执行两句是因为想通过匹配这一串md5，来确定命令执行是否成功，如果匹配成功，回包中的output字段就会回显代码执行的结果，如果匹配失败，output将为空。于是发包->拦截->修改->放行，就可以得到上图的结果了：

![](https://image.3001.net/images/20210207/1612690034_601fb272e851e08b8065a.jpg!small)

AttackType除了cmd代码执行外，还有`goby_shell_linux`的反弹shell的方式，还以045为例：

![](https://image.3001.net/images/20210207/1612690056_601fb2880f959db75bbc7.png!small)会发现有一条这个请求`https://gobygo.net/api/v1/bind?magic=true&key=84e32117d16abdf8&type=reverse_linux`。

会去`GodServer`获取一个监听的端口，获取到端口后，将会对目标发送反弹的EXP，如果成功就会获得一个`session`。

![](https://image.3001.net/images/20210207/1612690090_601fb2aa57b7114b37005.png!small)

如果反弹成功，`/api/v1/debugExp`的回包中的output字段就会包含远程会话的地址，同时左侧导航页也会弹出一个会话提示，如下图：

![](https://image.3001.net/images/20210207/1612688284_601fab9c2b4df18990a13.png!small)

### 2.3 开发

通过上面的一大串话，我们可以知道，因为没办法呈现漏洞，所以我们得利用`/api/v1/importAssetsAPI`导入一个报告模板，其余用到的API也基本在上面讲到了，确定了要使用的API之后就是用node.js的request模块，或者ajax完成对API的调用即可。

例：

    
    
    this.request({
              url: `http://${this.host}:${this.port}/api/v1/getPOCInfo`,
              method: 'POST',
              auth: {
                'user': this.username,
                'pass': this.password,
              },
              proxy: proxystr,
              json: { "vulname": vulname }
            }, function (error, response, body) {
              if (!error && response.statusCode == 200) {
                //输出返回的内容
                // console.log(body);
                resolve(body);
              } else {
                reject(error)
              }
    });

## 0x003 小结

这次写这个插件也算是一次突发奇想，整个开发过程也没有什么难点。但是总体来说，插件还是存在一些不足，以及通过这次对Goby
API调用尝试发现的一些问题，相信后续会让插件更加完美哒~

插件开发文档及Goby开发版下载：  
<https://gobies.org/docs.html>

> 作者：go0p

