## 关于graphw00f

graphw00f是一款针对GQL节点的GraphQL指纹识别工具，该工具可以混合发送良性和恶意查询请求，以帮助广大研究人员识别和确定目标应用程序背后的GraphQL引擎。

graphw00f可以为广大研究人员提供关于每种技术所具备的即时安全防御策略，以及相关安全保护技术默认情况下是打开还是关闭的。精心构建的查询请求会导致不同的GraphQL服务器实现对查询、突变和订阅做出不同的响应，以实现我们对后端引擎进行指纹识别并区分不同的GraphQL实现。

## 安全检测

当前版本的graphw00f将尝试检测和发现下列GraphQL引擎：

> Graphene - Python
>
> Ariadne - Python
>
> Apollo - TypeScript
>
> graphql-go - Go
>
> gqlgen - Go
>
> WPGraphQL - PHP
>
> GraphQL API for Wordpress - PHP
>
> Ruby - GraphQL
>
> graphql-php - PHP
>
> Hasura - Haskell
>
> HyperGraphQL - Java
>
> graphql-java - Java
>
> Juniper - Rust
>
> Sangria - Scala
>
> Flutter - Dart
>
> Diana.jl - Julia
>
> Strawberry - Python
>
> Tartiflette - Python

## GraphQL技术防御矩阵

每个指纹技术（如Graphene、Ariadne等）都有一个相关文档（例如Graphene），其中涵盖了特定技术支持的安全防御机制，以便更好地了解如何攻击实现。

    
    
    | Field Suggestions | Query Depth Limit | Query Cost Analysis | Automatic Persisted Queries | Introspection      | Debug Mode | Batch Requests  |
    
    |-------------------|-------------------|---------------------|-----------------------------|--------------------|------------|-----------------|
    
    | On by Default     | No Support        | No Support          | No Support                  | Enabled by Default | N/A        | Off by Default  |

## 工具依赖

> python3
>
> requests

## 工具安装&运行

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone git@github.com:dolevf/graphw00f.git

接下来，使用下列命令运行graphw00f，并查看工具帮助信息：

    
    
    python3 main.py -h
    
    
    Usage: main.py -t http://example.com/graphql -f
    Options:
      -h, --help            show this help message and exit
      -r, --noredirect      Do not follow redirections given by 3xx responses
      -t URL, --target=URL  target url with the path
      -f, --fingerprint     fingerprint mode
      -d, --detect          detect mode
      -T TIMEOUT, --timeout=TIMEOUT
                           Request timeout in seconds
      -o OUTPUT_FILE, --output-file=OUTPUT_FILE
                            Output results to a file (CSV)
      -l, --list            List all GraphQL technologies graphw00f is able to
                            detect
      -v, --version         Print out the current version and exit.

## 工具使用

### 识别GraphQL指纹

在这个例子中，我们将识别一个GraphQL节点的具体位置：

    
    
    python3 main.py -f -t https://demo.hypergraphql.org:8484/graphql
                    +-------------------+                 
                    |     graphw00f                  
                    +-------------------+                 
                      ***            ***               
                    **                  ***         
                  **                       **        
    
        +--------------+              +--------------+       
        |    Node X    |              |    Node Y    |    
        +--------------+              +--------------+     
    
                      ***            ***                  
                       **        **                     
                           **    **                       
                        +------------+                    
                        |   Node Z   |                      
                       +------------+    
                    graphw00f - v1.0.4
              The fingerprinting tool for GraphQL
               Dolev Farhi <dolev@lethalbit.com>
    [*] Checking if GraphQL is available at https://demo.hypergraphql.org:8484/graphql...
    
    [*] Found GraphQL...
    
    [*] Attempting to fingerprint...
    
    [*] Discovered GraphQL Engine: (HyperGraphQL)
    
    [!] Attack Surface Matrix: https://github.com/dolevf/graphw00f/blob/main/docs/hypergraphql.md
    
    [!] Technologies: Java
    
    [!] Homepage: https://www.hypergraphql.org
    
    [*] Completed.

### 检测和识别GraphQL指纹

在这个例子中，graphw00f可以检测GraphQL的活动状态，并执行指纹识别进程：

    
    
    python3 main.py -f -d -t http://localhost:5000             
    
                    +-------------------+                 
    
                    |     graphw00f                     
                    +-------------------+                 
    
                      ***            ***                  
                    **                  ***               
                  **                       **             
        +--------------+              +--------------+       
    
        |    Node X    |              |    Node Y    |       
        +--------------+              +--------------+     
    
                      ***            ***                
    
                         **        **                  
                           **    **                       
                        +------------+                      
                        |   Node Z   |                      
                        +------------+    
    
                    graphw00f - v1.0.4
    
              The fingerprinting tool for GraphQL
             Dolev Farhi <dolev@lethalbit.com>
    [*] Checking http://dvga.example.local:5000/graphql
    [!] Found GraphQL at http://dvga.example.local:5000/graphql
    [*] Attempting to fingerprint...
    [*] Discovered GraphQL Engine: (Graphene)
    [!] Attack Surface Matrix: https://github.com/dolevf/graphw00f/blob/main/docs/graphene.md
    [!] Technologies: Python
    [!] Homepage: https://graphene-python.org
    
    [*] Completed.

## 项目地址

 **graphw00f：** 【[ _GitHub传送门_](https://github.com/dolevf/graphw00f)】

## 参考资料

> [ _https://github.com/dolevf/Damn-Vulnerable-GraphQL-> Application/_](https://github.com/dolevf/Damn-Vulnerable-GraphQL-> Application/)

