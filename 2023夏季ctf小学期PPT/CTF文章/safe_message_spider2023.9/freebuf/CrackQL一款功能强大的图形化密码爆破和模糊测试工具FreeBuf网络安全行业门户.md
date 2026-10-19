![](https://image.3001.net/images/20220709/1657304318_62c874fee3c856c9b8094.png!small)

## 关于CrackQL

CrackQL是一款功能强大的图形化密码爆破和模糊测试工具，在该工具的帮助下，广大研究人员可以针对密码安全和应用程序安全进行渗透测试。

除此之外，CrackQL同时也是一款通用的GraphQL渗透测试工具，它可以控制速率限制和其他分析控制技术来对目标系统进行凭证爆破和模糊测试等操作，以测试程序的安全性。

## 工具运行机制

CrackQL的工作原理是将单个GraphQL查询或变异自动批量处理为多个别名操作，该工具可以根据CSV输入变量确定要使用的别名数。在以编程方式生成分批GraphQL文档后，CrackQL然后会分批并将Payload发送到目标GraphQL
API，并解析结果和错误信息。

## 工具依赖组件

> Python3
>
> Requests
>
> GraphQL
>
> Jinja

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone git@github.com:nichola*saleks/CrackQL.git

接下来，利用项目提供的requirements.txt文件安装该工具所需的依赖组件：

    
    
    pip install -r requirements.txt

## 工具运行

### 查看帮助信息

    
    
    python3 CrackQL.py -h
    
     
    
    Options:
    
      -h, --help             显示工具帮助信息和退出
    
      -t URL, --target=URL   目标GraphQL节点的URL路径
    
      -q QUERY, --query=QUERY
    
                            指定输入查询或编译操作
    
      -i INPUT_CSV, --input-csv=INPUT_CSV
    
                            输入CSV列表的文件路径
    
      -d DELIMITER, --delimiter=DELIMITER
    
                            CSV输入分隔符，默认：“，”
    
      -o OUTPUT_DIRECTORY, --output-directory=OUTPUT_DIRECTORY
    
                            存储结果的输出目录，默认：./results/[domain]_[uuid]/
    
      -b BATCH_SIZE, --batch-size=BATCH_SIZE
    
                            每次GraphQL文档请求的批量操作数量，默认：100
    
      -D DELAY, --delay=DELAY
    
                            批量请求发送的时间间隔，默认：0
    
      --verbose           启用工具Verbose模式
    
      -v, --version         输出工具当前版本和退出

### 使用样例

    
    
    python3 CrackQL.py -t http://example.com/graphql -q sample-queries/login.graphql -i sample-inputs/usernames_and_passwords.csv

## 工具使用演示

### 密码喷射爆破

 **sample-queries/login.graphql**

    
    
    mutation {
    
      login(username: {{username|str}}, password: {{password|str}}) {
    
        accessToken
    
      }
    
    }

### 双因素身份验证OTP绕过

 **sample-queries/otp-bypass.graphql**

    
    
    mutation {
    
      twoFactor(otp: {{otp|int}}) {
    
        accessToken
    
      }
    
    }

### 用户账号枚举

 **sample-queries/enumeration.graphql**

    
    
    query {
    
      signup(email: {{email|str}}, password: {{password|str}}) {
    
        user {
    
          email
    
        }
    
      }
    
    }

### 不安全的直接对象引用

 **sample-queries/idor.graphql**

    
    
    query {
    
      profile(uuid: {{uuid|int}}) {
    
        name
    
        email
    
        picture
    
      }
    
    }

### 字典Payload

 **sample-inputs/usernames_and_passwords.csv**

    
    
    username, password
    
    admin, admin
    
    admin, password
    
    admin, pass
    
    admin, pass123
    
    admin, password123
    
    operator, operator
    
    operator, password
    
    operator, pass
    
    operator, pass123
    
    operator, password123

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-3-Clause_](https://github.com/nicholasaleks/CrackQL/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **CrackQL** ：【[ _GitHub传送门_](https://github.com/nicholasaleks/CrackQL)】

## 参考资料

> [
> _https://portswigger.net/burp/documentation/desktop/tools/intruder_](https://portswigger.net/burp/documentation/desktop/tools/intruder)
>
> [ _https://www.graphql-modules.com/docs#authentication-> module_](https://www.graphql-modules.com/docs#authentication-module)
>
> [ _https://github.com/dolevf/Damn-Vulnerable-GraphQL-> Application_](https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application)
>
> [ _https://github.com/nichola*saleks_](https://github.com/nicholasaleks)
>
> [ _https://github.com/dolevf_](https://github.com/dolevf)

