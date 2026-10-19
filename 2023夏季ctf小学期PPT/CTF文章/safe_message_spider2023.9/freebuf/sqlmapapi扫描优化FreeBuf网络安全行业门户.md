**市面上的开源sqli扫描，其中有不少是基于sqlmapapi做自动化的。当然，已经有不少脚本进行了利用，但是细节做好的不是特别多。**

为了保证扫描效率和降低漏报、误报，这里会针对脚本做一些优化。

##### sqlmapapi中基础方法

在sqlmap/lib/utils/api.py中:

###### 用户方法

    
    
    @get("/task/new") Create new task ID. 
    
    @get("/task/<taskid>/delete") Delete own task ID.
    

###### 管理函数

    
    
    @get("/admin/<taskid>/list") List task pull. 
    
    @get("/admin/<taskid>/flush") Flush task spool (delete all tasks).
    

###### 核心交互函数

    
    
    @get("/option/<taskid>/list") List options for a certain task ID
    
    @post("/option/<taskid>/get") Get the value of an option (command line switch) for a certain task ID
    
    @post("/option/<taskid>/set") Set an option (command line switch) for a certain task ID
    
    @post("/scan/<taskid>/start") Launch a scan
    
    @get("/scan/<taskid>/stop") Kill a scan
    
    @get("/scan/<taskid>/status") Return status of a scan
    
    @get("/scan/<taskid>/data") Retrieve the data of a scan
    
    @get("/scan/<taskid>/log/<start>/<end>") Retrieve a subset of log messages
    
    @get("/scan/<taskid>/log") Retrieve the log messages
    
    @get("/download/<taskid>/<target>/<filename:path>") Download a certain file from the file system
    

##### 细节优化

###### post("/option/<taskid>/set")

在这个地方，我们可以操作sqlmap的预置参数。在配置好后，能很明显的提升我们批量扫描的检测效率。

这里先放一个定制化的配置，仅供大家参考：

    
    
    option = {
    
            "options": {
    
            "smart": True, #智能模式，sqlmap会进行智能选择
    
            "randomAgent": True,
    
            "safeUrl": self.target,
    
            "safeFreq": 1,
    
            "level": 3,
    
            "risk": 3,
    
            "threads": 6,
    
            "timeSec": 10,
    
            "tamper": self.tamper,
    
            "freshQueries": True,  #忽略存储在会话文件中的查询结果
    
            "flushSession": True,   #刷新本地Session
    
            "technique":"BT",
    
            "dbms":"mysql"
    
                }
    
             }
    

下面会介绍一部分option参数，所对应的sqlmap命令行参数。

在sqlmap/lib/core/option.py中：

参数：--technique（technique）

    
    
    
    
    
    这个参数可以指定sqlmap使用的探测技术，默认情况下会测试所有的方式。
    
    
    
    
    支持的探测方式如下：
    
    
    
    
    B: Boolean-based blind SQL injection（布尔型注入）
    
    E: Error-based SQL injection（报错型注入）
    
    U: UNION query SQL injection（可联合查询注入）
    
    S: Stacked queries SQL injection（可多语句查询注入）
    
    T: Time-based blind SQL injection（基于时间延迟注入）
    

参数：--dbms（dbms）

    
    
    如果是企业内部扫描，一般使用的数据有限，加上这个参数可以减少扫描时间。
    

参数：--time-sec（timeSec）

    
    
    防止超时阻断，一般用于waf和网站响应过慢和网络延迟的情况。
    

参数：参数：--smart（smart），--batch（batch）

    
    
    smart为智能选择sqlmap中的决断，batch为统一选择默认情况。
    

参数：--random-agent（randomAgent）

    
    
    使用随机ua，一定程度上绕过老版waf。
    

参数：--safe-url（safeUrl）,--safe-freq（safeFreq）

    
    
    有的web应用程序会在你多次访问错误的请求时屏蔽掉你以后的所有请求，这样在sqlmap进行探测或者注入的时候可能造成错误请求而触发这个策略，导致以后无法进行。
    
    
    
    
    绕过这个策略有两种方式：
    
    
    
    
    1、--safe-url：提供一个安全不错误的连接，每隔一段时间都会去访问一下。
    
    2、--safe-freq：提供一个安全不错误的连接，每次测试请求之后都会再访问一边安全连接。
    

参数：--tamper（tamper）

    
    
    这里的tammper建议使用定制化脚本，不仅仅是绕waf，更多的是一些策略型判断。
    

参数：--level（level），--risk（risk）

    
    
    设置参数和风险等级，简单讲下level[1-5]越高，可测试的point越多；risk[0-3]越高，可添加的payload越多。
    
    这两个参数会造成测试时间的增加，具体设置的级别，需要根据使用场景而，譬如：
    
    
    
    
    - 企业内部例检
    
    - 外部SRC挖洞
    
    - 乙方给甲方做规模扫描
    
    - 项目渗透比赛
    

参数：--fresh-queries（freshQueries），--flushSession（flushSession）：

    
    
    这两个参数主要用于case复测，以及反复扫描的场景，就不多讲了。
    

参数：--fresh-queries（freshQueries）

    
    
    这两个参数主要用于case复测，以及反复扫描的场景，就不多讲了。
    

###### post("/scan/<taskid>/start")

在这一步，需要配置参数检测点，这里使用默认参数，可能会被部分waf和检测机制拦截。

因为正常的数据流量，是可能带有认证和ua、referer过滤的。

注意，这里检测cookie和referer，需要提升level等级，否则可能无法检测。

示例函数如下：

    
    
    def scan_start(self):
    
        headers = {'Content-Type': 'application/json'}
    
        payload = {
    
            'url': self.req_url,#目标url
    
            'data': self.data, #目标url的post参数
    
            'cookie': self.cookie, #目标的cookie
    
            'referer': self.referer #目标的referer
    
            
    
        }
    
        url = self.server + 'scan/' + self.taskid + '/start'
    
        t = json.loads(
    
            requests.post(url, data=json.dumps(payload), headers=headers).text)
    

###### json sqli注入

这里有个小tip，在检测json类型的post参数时，如果参数里包含中括号，需要去掉后sqlmap才能识别。

本身sqlmap想要支持指定点扫描，需要加*号，显然sqlmapapi这里不合适，需要单独处理参数。

譬如:

    
    
    POST /api/xxx
    
    
    
    
    ...
    
    ...
    
    
    
    
    {"test1":"123","test2":['para1','para2','para3']}
    

去掉后变成：

    
    
    POST /api/xxx
    
    
    
    
    ...
    
    ...
    
    
    
    
    {"test1":"123","test2":'para1','para2','para3'}
    

##### 分布式扫描

###### server模式

sqlmapapi对于分布式的支持还是挺友好的，可以把主机监听设置为全局：

    
    
    python sqlmapapi.py -s -H "0.0.0.0" -p 8775
    

###### 权限认证

但是，如果要作为公用服务，还是需要做好接口认证，以免被黑客连上，滥用扫描功能，溯源难度也会加大。

sqlmapapi本身自带有http basic认证，server端可以设置username和password。

非sqlmapapi客户端发送请求时，可以直接带上认证：

    
    
    if self.username or self.password:
    
        headers["Authorization"] = "Basic %s" % base64.b64encode(
    
    "%s:%s" % (self.username or "", self.password or "")
    
    )
    

但是这个功能是在头部传输的，不存在https，本身存在泄露的风险。

##### 某些特殊bug

###### 正常页面404

某些web网站，如果参数错误返回404，sqlmap在运行时会返回一个critical的错误，所以必须选择非默认的no选项，才能继续扫下去。

但是，sqlmapapi默认没有自动选择no的选项，所以是不能直接扫的。

解决办法，修改lib/request/connect.py中代码:

    
    
    elif ex.code == httplib.NOT_FOUND:
    
        if raise404:
    
            errMsg = "page not found (%d)" % code
    
            raise SqlmapConnectionException(errMsg)
    
        else:
    
            debugMsg = "page not found (%d)" % code
    
            singleTimeLogMessage(debugMsg, logging.DEBUG)
    

将其中的raise SqlmapConnectionException(errMsg)注释掉后，再重新用刚才的sqlmap语句可以继续扫。

解决问题的文章说，这个方案在2017年8月，已经pull到sqlmap：

    
    
    https://github.com/sqlmapproject/sqlmap/pull/2663
    

但是sqlmap项目的人表示，你这bug提的价值不高，改了没有价值，巴拉巴拉。

然后让人直接走通用过滤机制：

    
    
    --ignore-code=404
    

话糙理不糙，关于类似的异常，我们确实可以通过ignore的方式来忽略，只不过正常扫描的话，这种场景相对少罢了。

这里的对应的--ignore-code对应的option参数则是ignoreCode。

##### 文章参考

  * [sqlmap对状态码404处理的bug](http://3xp10it.cc/web/2017/08/20/sqlmap%E5%AF%B9%E7%8A%B6%E6%80%81%E7%A0%81404%E5%A4%84%E7%90%86%E7%9A%84bug/?nsukey=syoj6%2BmT1F29XBLUzPdZtrgVKG7ILM63uXCesGVFtdNpab1EDjgcRHqhywSvPlKI4LdXkl1EmryrtNSOlwdLhkclpJqdlB0v10AeSgaxR2fbe7zo6unhEK9ASqOWjWVJe%2FcN6jLgrqc3KYB%2Fiuy5B08MtVwSu%2BaMbuoSH%2Be2CNn7fO8ewl5ZVRlV**vuDv1oz9IX1vln6tRyTqqieiWE4g%3D%3D)

  

