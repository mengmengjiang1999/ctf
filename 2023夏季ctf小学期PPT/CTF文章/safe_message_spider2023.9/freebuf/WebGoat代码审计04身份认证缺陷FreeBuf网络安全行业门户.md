博客地址 [芜风](https://drun1baby.github.io/)

## 0x01 写在前面

  * 换了一种思维，先看代码，从代码里面找漏洞，然后去做题，代码审计也应该是这样一个思路。

## 0x02 Authentication Bypasses

### 1\. Authentication Bypasses PageLesson2

> 讲的是 2FA 的密码重置方式

#### 源码部分

打开源代码，优先去找`return success`的代码模块  
![image](https://image.3001.net/images/20220407/1649318454_624e9a36096b49b8f199e.png!small)

说实话这一块看不懂，关键点应该是这一块代码，很明显是继承

    
    
    if (verificationHelper.verifyAccount(Integer.valueOf(userId), (HashMap) submittedAnswers))
    

而在第 60 行这里

    
    
    AccountVerificationHelper verificationHelper = new AccountVerificationHelper();
    

进入 AccoutVerificationHelper 看看，并移步到 AccoutVerificationHelper.verifyAccout 下。

![image](https://image.3001.net/images/20220407/1649318468_624e9a441c1211407f8d6.png!small)

return true 的条件：

  * ①：UserId 相同

  * ②：第一个密保问题，即 secQuestion0 和上文中的 “作弊” 答案不一致

  * ③：第二个密保问题，即 secQuestion1 和上文中的 “作弊” 答案不一致

![image](https://image.3001.net/images/20220407/1649318479_624e9a4fe3171f8719495.png!small)

上框为 “作弊” 答案，下框的意思是，密码问题的参数是 "secQuestion0" 与 "secQuestion1"。只需包含这个参数即可进行判断。

#### 靶场部分

于是想到绕过手段，构造 payload 成功绕过 ~

![image](https://image.3001.net/images/20220407/1649318488_624e9a5892f0664c25380.png!small)

## 0x03 JWT Tokens

### 1\. JWT Tokens PageLesson3

  * 打开源码，去找 JWT 那一块，代码很简单，简单判断了 "$user" 是否等于 user

![image](https://image.3001.net/images/20220407/1649318496_624e9a60bb15b9f0d475d.png!small)

对 JWT 进行 base64 编码解密，轻松过  
![image](https://image.3001.net/images/20220407/1649318506_624e9a6a09200f31ed594.png!small)

![image](https://image.3001.net/images/20220407/1649318511_624e9a6f80169780aff1b.png!small)

### 2\. JWT Tokens PageLesson5

  * 题意，通过 JWT Token 的问题，获得 admin 权限，从而修改这些 Vote 的内容/样子。

  * 如果只是普通的 Guest 或者其他人的用户，是无法删除或者对投票界面进行更改操作的。

#### 源码部分

  * 打开文件 "JWTVotesEndPoint.java"，首先第一个函数，构造 Vote 界面  
![image](https://image.3001.net/images/20220407/1649318580_624e9ab446caa2bdf6649.png!small)  
这里对应的就是四个投票界面，在前端界面如图所示

![image](https://image.3001.net/images/20220407/1649318586_624e9aba888ad3ac220a2.png!small)

这里有一段语句要单独拿出来讲一下，因为和 JWT 的代码原理密不可分。

![image](https://image.3001.net/images/20220407/1649318607_624e9acf9568e724af726.png!small)

    
    
    String token = Jwts.builder()   // 创建 JWT 对象
            .setClaims(claims)      //  设置主题(声明信息)
            .signWith(io.jsonwebtoken.SignatureAlgorithm.HS512, JWT_PASSWORD) // 设置安全密钥(生成签名所需的密钥和算法)
            .compact(); // 生成token（1.编码 Header 和 Payload 2.生成签名 3.拼接字符串）
    

> 寻找一下何处可以绕过 admin 验证的，第 163 - 184 行

![image](https://image.3001.net/images/20220407/1649318614_624e9ad69608f58ae8d37.png!small)

#####  **逐行分析，代码审计**

前面的 166 - 168 行这里，判断 **"accessToken"**是否为空，若为空，则返回 failed；若不为空，则进入 else 语句

第 169 - 178 行，核心的判断语句。

![image](https://image.3001.net/images/20220407/1649318621_624e9add7f2b45be375fc.png!small)

170 行的语句，验证 token

    
    
    Jwt jwt = Jwt.paraser()     // 创建解析对象
    .setSigningKey(JWT_PASSWORD)// 设置安全密钥（生成签名所需的密钥和算法）
    .parse(accessToken)  // 解析token
    Claims claims = (Claims) jwt.getBody(); // 获取 payload 部分内容
    

第 172 行解读一下，中间是空格就可以了；`claims.get("admin")`这句语句得到的是 JWT 的 Payload 信息，数据类型是
String，通过 Boolean.valueOf(String)，将其转变为 Boolean 的数据类型；判断依据则是 Payload 的值是否等于
admin；若等于 admin，则为 True，反之为 False

    
    
    boolean isAdmin = Boolean.valueOf((String) claims.get("admin"));
    

  * 代码解读到这里，师傅们应该也能看懂原理了吧，我们加快分析进度~

第 173 - 178 行，判断 isAdmin 是否为 admin，若为 admin 时，将 vote 的值还原，并且返回 success 的消息。

    
    
    votes.values().forEach(vote -> vote.reset());  // 四个 vote 的值还原到最开始
    return success(this).build();
    

#### 靶场部分

  * 根据上面的代码审计分析，其实我们只需要抓一个 JWT 的包，并且将 JWT 当中的 Payload 修改为 "Admin"，再发包即可。

点击删除时抓包，如图所示  
![image](https://image.3001.net/images/20220407/1649318634_624e9aeaba63eaf3829f6.png!small)

将这一串 token 拿出来，base64 解码一下。

![image](https://image.3001.net/images/20220407/1649318645_624e9af5caf7cf8f2ff80.png!small)

那这里，我们发包的时候将`"admin":"false"`修改为`"admin":"true"`即可，再发包。

这里推荐一个 JWT 在线生成的工具，不要想着用 base64 去弄，我这里踩坑花了大概半个小时才解决，不信邪的小伙伴们可以试一试。  
工具网站：[JSON Web Tokens - jwt.io](https://jwt.io/)

JWT token 是

eyJhbGciOiJIUzUxMiJ9.eyJpYXQiOiIxNjQ5NzUwMzg1IiwiYWRtaW4iOiJ0cnVlIiwidXNlciI6IlRvbSJ9.

![image](https://image.3001.net/images/20220407/1649318660_624e9b042aea3a0cfdea8.png!small)

### 3\. JWT Tokens PageLesson7

这里虽然是两道选择题，但是还是有必要提一嘴

放进 Burpsuite 当中比较一下两段代码

![image](https://image.3001.net/images/20220407/1649318666_624e9b0ad9ae28816851b.png!small)

  * 对于 parseClaimsJws 来说，alg 为 none 则直接抛出异常

  * 对于 parse 来说，alg 为 none 则是判断是否为某个身份的依据。这里的 alg 如果被设置成 none，可以很好的绕过

综上，parseCliamsJws 的防御能力能强  
答案是 1，3

### 4\. JWT Tokens PageLesson8

  * 题意：让我们通过爆破的手段找出 JWT 当中的 Secert Key

一旦拥有了一个JWT token，我们可以尝试离线暴力破解或字典攻击。

#### 源码部分

![image](https://image.3001.net/images/20220407/1649318677_624e9b1526823d779aafe.png!small)

#####  **代码审计**

查看源码，第 85 行，返回成功的条件

    
    
    if (WEBGOAT_USER.equalsIgnoreCase(user))
    

再返回去看上面的判断条件

    
    
    if (!claims.keySet().containsAll(expectedClaims)) {
        return failed(this).feedback("jwt-secret-claims-missing").build();
    } else {
        String user = (String) claims.get("username");
    

呃，就是基本的判断，根据题意，需要爆破 " **Secret Key** "；这里借用一位师傅的
[exp](https://www.freebuf.com/articles/web/221947.html)。

    
    
    import termcolor
    import jwt
    if __name__ == "__main__":
        jwt_str = R'eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJXZWJHb2F0IFRva2VuIEJ1aWxkZXIiLCJhdWQiOiJ3ZWJnb2F0L**yZyIsImlhdCI6MTU3MjY4ODA3MSwiZXhwIjoxNTcyNjg4MTMxLCJzdWIiOiJ0b21Ad2ViZ29hdC5vcmciLCJ1c2VybmFtZSI6IlRvbSIsIkVtYWlsIjoidG9tQHdlYmdvYXQub3JnIiwiU**sZSI6WyJNYW5hZ2VyIiwiUHJvamVjdCBBZG1pbmlzdHJhdG9yIl19.2n1lN_F-Pk8GXxw7nAneMt1**ExfH7mVdtQF9nMKhVs'
        with open('/opt/burp/pass.txt') as f:
            for line in f:
                key_ = line.strip()
                try:
                    jwt.decode(jwt_str, verify=True, key=key_)
                    print('\r', '\bbingo! found key -->', termcolor.colored(key_, 'green'), '<--')
                    break
                except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.InvalidAudienceError, jwt.exceptions.InvalidIssuedAtError, jwt.exceptions.InvalidIssuedAtError, jwt.exceptions.ImmatureSignatureError):
                    print('\r', '\bbingo! found key -->', termcolor.colored(key_, 'green'), '<--')
                    break
                except jwt.exceptions.InvalidSignatureError:
                    print('\r', ' ' * 64, '\r\btry', key_, end='', flush=True)
                    continue
            else:
                print('\r', '\bsorry! no key be found.')
    

最后爆得 **"Secret Key"**的值为 shipping(做题时每个人是不一样的)

  * 也可以使用 hashcat

### 5\. JWT Tokens PageLesson10

题目是 Refreshing a token，那总归是要先探究为什么要 Refreshing a token。

token类型分为两种：access token 和 refreshing token

为什么需要refreshing token？

  * 为了避免多次验证access token(超时或是浪费资源)

  * refreshing token 由server生成并存储在server的数据库里，验证时对比即可。

个人感觉就是 session cookie 和 set-cookie 差不多

> 题目要求我们，让 Tom 付钱

#### 源码部分

源码部分如图所示，直接看如何才能成功的部分

![image](https://image.3001.net/images/20220407/1649318692_624e9b24349edc5bb249c.png!small)

第 106 行，这里比对了 Tom 是否为 user。但是一番抓包之后一无所获，甚至连 Tom 是谁，token 是啥全然不知。

回到题目界面，查看一下 logs.txt，发现了 Tom 的 token，丢到 jwt.io 中去验证一下。

![image](https://image.3001.net/images/20220407/1649318743_624e9b57465c411d08b81.png!small)

应该是没这么简单的，回到源代码中看一看其他的接口

![image](https://image.3001.net/images/20220407/1649318772_624e9b746476d920ac93b.png!small)

这里是关键点了，之前尝试了使用 logs.txt 中的 JWT 登录，最终失败了，个人的一点猜测是这样的：之前 Tom
购买时是很早之前的记录了，所以对于我们来说，这时候的 JWT 其实已经是失效了的，但如果我们需要让 Tom 来付款，必须要临时给 Tom 创建一个新的
JWT，或者把 Tom 的 access_token 找出来。

![image](https://image.3001.net/images/20220407/1649318793_624e9b891b161d8876cbb.png!small)

 **逐行代码审计又来了**

> 第 137 - 146 行，当 user 与 refreshToken 都存在，不为空的时候，JWT 成功被 Refresh。
    
    
    if (user == null || refreshToken == null) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
    } else if (validRefreshTokens.contains(refreshToken)) {
        validRefreshTokens.remove(refreshToken);
     return ok(createNewTokens(user));
    } else {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
    }
    

> 第 128 - 131 行，新构造出一个 JWT
    
    
    try {
        Jwt<Header, Claims> jwt = Jwts.parser().setSigningKey(JWT_PASSWORD).parse(token.replace("Bearer ", ""));
     user = (String) jwt.getBody().get("user");
     refreshToken = (String) json.get("refresh_token");
    

这里值得一提得是，最后解析 token 的参数，如果参数中存在 "Bearer" 就被替换为空格，这里感觉是有个双写绕过(?)，不清楚，一会儿试了就知道了。

再明确一下攻击的方式，通过构造 JWT 中的 Header 部分，也就是 Header = Authorization，把这一块放进 HTTP
Request 当中。代码如下

![image](https://image.3001.net/images/20220407/1649318902_624e9bf6f13ed498f1606.png!small)

#### 解题(巨坑，醉了)

首先是在 WebGoat 的界面下抓包，然后会抓到 /WebGoat/JWT/refresh/login
的这么一个包，接着添加`Authorization`的头，值为 Bearer null，目的是获取一个 access_token，再发包。

  * 发包完之后，注意！！！！！！！！这里巨坑！！！！！

这个 access_token 里面的最后一个字段是签名，不要拿进来！不要拿进来！不要拿进来！不要拿进来！

![image](https://image.3001.net/images/20220407/1649318915_624e9c03522c00e76971b.png!small)

在 JWTio 中编辑完毕后，去到 /checkout 接口，发送前两个字段。

![image](https://image.3001.net/images/20220407/1649318922_624e9c0a8bc401be5bd97.png!small)

### 6\. JWT Tokens PageLesson11

  * 题意： Jerry 想从 Twitter 上删除 Tom 的账号，算是越权吧。

#### 源码部分

![image](https://image.3001.net/images/20220407/1649318936_624e9c18cde976e9d9c68.png!small)

核心部分在 89- 103 行这里。

![image](https://image.3001.net/images/20220407/1649318943_624e9c1f2457937ca82c9.png!small)

  * 这里我把源代码贴出来再分析分析

    
    
    Jwt jwt = Jwts.parser().setSigningKeyResolver(new SigningKeyResolverAdapter() {
    	@Override
    	public byte[] resolveSigningKeyBytes(JwsHeader header, Claims claims) {
    		final String kid = (String) header.get("kid");
     		try (var connection = dataSource.getConnection()) { 
    			ResultSet rs = connection.createStatement().executeQuery("SELECT key FROM jwt_keys WHERE id = '" + kid + "'");
     			while (rs.next()) {
    				return TextCodec.BASE64.decode(rs.getString(1)); 
     }
            } catch (SQLException e) {
                errorMessage[0] = e.getMessage();
     }
            return null;
     }
    }).parseClaimsJws(token);
    

前面的代码都是之前差不多，新生成一个 JWT，引人注目的是第 94 行这里的 SQL 语句，感觉是存在 SQL 注入的。 **再好好审一审代码**

这次的 secret 是直接从数据库进行读取，而这个 SQL 语句查询的就是 JWT 的 secret。而因为之前使用了 parseClaimsJws
这个方法，于是无法构造`{"alg":"none"}`来绕过。因此确定思路通过 SQL 注入来绕过。

#### 题目部分

先点击 Delete 抓包，抓包的接口是 /JWT/final/delete?token=

![image](https://image.3001.net/images/20220407/1649318953_624e9c29db97556597dce.png!small)

我们看到 JWT header 当中多了一个 "kid"

修改包，将 "username" 修改为 Tom，再对 kid 进行 SQL 注入。这里使用 Union 联合查询注入。

  * 构造 payload，这里的 bmV3X2tleQ== 需要经过 base64 编码，因为 rs.next() 会执行一次 base64 的编码，所以我们要去 SELECT 的 secret key 需要先经过 base64 编码。

    
    
    "kid": "something_else' UNION SELECT 'bmV3X2tleQ==' FROM INFORMATION_SCHEMA.SYSTEM_USERS; --",
    

![image](https://image.3001.net/images/20220407/1649318963_624e9c33d67b9b2696ed4.png!small)

修改 kid 进行 SQL 注入，并修改 iat 以及其他需要修改的数据，如上图所示。并修改下面的 secret key

![image](https://image.3001.net/images/20220407/1649318980_624e9c4403ff32f540b41.png!small)

  * 不要点 secret base64 encoded ！不要点 secret base64 encoded ！不要点 secret base64 encoded ！不要点 secret base64 encoded ！不要点 secret base64 encoded ！不要点 secret base64 encoded ！

  * 这里踩坑卡了好久 …………

接着，发包即可。

![image](https://image.3001.net/images/20220407/1649318988_624e9c4c914a419a5191d.png!small)

## 0x04 Password Reset 密码重置

  * 密码重置这里主要也是以业务逻辑漏洞居多。

### 1\. Password Reset PageLesson2 使用 WebWolf

#### 源码部分

源码文件是 SimpleMailAssignment.Java

> 先看登录界面

  * 这里的第 56 - 67 行，简单的身份认证，当 username 和 password 都正确，则登录。

![image](https://image.3001.net/images/20220408/1649423075_625032e3211beb1dabcf9.png!small)

第 58 - 60 行，基础的 Java 语法讲解

    
    
    public AttackResult login(@RequestParam String email, @RequestParam String password) {
        String emailAddress = ofNullable(email).orElse("unknown@webgoat.org");  // emailAddress 等于 email，如果没有 email 这个值，则为 "unknown@webgoat.org"
     String username = extractUsername(emailAddress); // 拦截器的作用，判断传进来的参数是否为邮箱的格式
    

看了很久都感觉没有洞，后面查了才知道这题只是让我们感受一下 WebWolf，并不是直接挖洞哈哈哈哈哈

#### 题目部分

  * 发送一下忘记密码的邮件即可

![image](https://image.3001.net/images/20220408/1649423087_625032ef793a392e2e439.png!small)

再登录即可，只是让我们感受一下 WebGoat 而已，晕……

  * 解出题目之后是不会变色的，不必在意

### 2\. Password Reset PageLesson4 爆破密保

#### 源码部分

![image](https://image.3001.net/images/20220408/1649423095_625032f716fa241a99031.png!small)

  * 获取输入的第 56，57 行拉出来单独讲解一下 getOrDefault

 **参数说明：**

  * key - 键

  * defaultValue - 当指定的key并不存在映射关系中，则返回的该默认值

> 返回值

返回 key 相映射的的 value，如果给定的 key 在映射关系中找不到，则返回指定的默认值。

    
    
    String securityQuestion = (String) json.getOrDefault("securityQuestion", "");  // 获取当前参数的 "securityQuestion" 值，若没有 "securityQuestion"，则返回 ""
    String username = (String) json.getOrDefault("username", "");
    

分析完毕，看到上面的 static 中有一些字符，直接尝试爆破

#### 题目部分

抓包，并将颜色部分添加 dollar 符，进行爆破

![image](https://image.3001.net/images/20220408/1649423106_62503302d7f67b029f207.png!small)

再发包，成功。

![image](https://image.3001.net/images/20220408/1649423112_625033087c029a11db5ba.png!small)

  * 这也给我们的渗透攻击提供了一些思路，在实际的渗透测试当中，对于回答密保问题来验证身份，也可使用爆破。

  * 正确的防御手法应该是添加验证码。

### 3\. Password Reset PageLesson5 关于密保的小 tips

这里让我们写密保时，不要写真实的答案，不然会被社工。  
选 favorite color

### 4\. Password Reset PageLesson6 修改重置密码的链接 Creating the password reset link

  * 题意是让我们创建一个密码重置的链接，这种情景需要先行理解一下。

我们邮箱中收到重置密码的邮件时，通常都会发给我们另外一个 Web 地址，上面是去往密码重置的 Web 界面。

> 在此时，若我们修改了这个密码重置的 Web 链接。  
> 举个例子，Tom 的邮箱对应的地址是 10.48.244.196:8011，那么 8011 这个端口就是专门为了 Tom 设置的。
>
> 假设我的账户名叫 Jerry，邮箱的地址是 10.48.244.196:8022，那么我先请求一个 **"forget password"** ，名字是
> Tom 的邮箱，再将去到的 Host 修改为我自己的 "10.48.244.196:8022"；若后台不加以任何的限制，我们就可以越权修改 Tom
> 的密码。

本道靶场就演示了这么一个情况。当我们输入要找回密码的邮箱时，会将链接发送道我们邮箱，点开链接才是修改密码的。

![image](https://image.3001.net/images/20220408/1649423122_62503312041342f92a0bb.png!small)

  * 攻击思路已经比较清楚了，我们再看一看源码

#### 源码部分

  * 主要是看发送密码重置链接的源码

![image](https://image.3001.net/images/20220408/1649423129_6250331974860ffd8a2bb.png!small)

> 总体上比较好理解，为了帮助其他小伙伴理解，还是细讲一下吧

第 67 - 69 行，几个变量的定义及赋值

    
    
    String resetLink = UUID.randomUUID().toString();  // resetLink 变量的值是由 UUID 产生的，至于 UUID 是一串随机数序列
    ResetLinkAssignment.resetLinks.add(resetLink);  // 在接口中添加 resetLinks 这一段
    String host = request.getHeader("host");  // host 的值是 Request 包中的 host 值
    

后面的判断语句，判断 host 当中是否存在 WebWlof 服务对应的端口与 Host；之后再产生一个 Response 包中的 Session。

  * 很显然，就是这一句判断语句不够精确，所以才会导致漏洞，对应的攻击手段如下。

#### 题目部分

先到忘记密码的界面，输入`tom@webgoat-cloud.org`，并抓包。  
接着修改 Host 为 localhost:9090，也就是 WebWolf 的地址，这样子的话，原本是 Tom 忘记密码的操作就到了我们的邮箱上。

![image](https://image.3001.net/images/20220408/1649423140_62503324388fc0fe20ab6.png!small)

再到 WebWolf 下的一个`Incoming requests`下，查看请求。

![image](https://image.3001.net/images/20220408/1649423146_6250332a70bda435d40f4.png!small)

再访问 http://124.222.21.138:9000/WebGoat/PasswordReset/reset/change-password
即可，因为 Tom 的请求的 Host 就为此，输入密码重置即可。

#### 修复方式

固定我们的host就可以了，其实归根结底就是太相信用户的输入了，这也是很多安全问题存在的原因。

## 0x05 Secure Passwords

这里的和很多的业务逻辑漏洞是重复的，就简单过一遍靶场吧。

### 1.Secure Passwords PageLesson4 防爆破的密码

这里输入一传强密码即可，随意输入都可以 ~  
我这里的答案是`1!22@Misliq!39`

![image](https://image.3001.net/images/20220408/1649423252_625033944366c76b8a741.png!small)

