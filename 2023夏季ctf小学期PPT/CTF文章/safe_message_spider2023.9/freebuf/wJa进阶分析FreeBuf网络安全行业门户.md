继上篇文章： https://www.freebuf.com/sectool/316916.html

## 优化

在上述的代码脚本中，其实还是有可优化的的地方的，当程序项目比较大时，类就无法通过手动输入进行测试，所以可以通过`GetAllClassName`类进行测试，所以可以进行如此优化。

    
    
    function SQLTrack(className){
    	an = GetClassAnnotation(className);
    	classPath = "http://127.0.0.1:8080".getSpringAnnotationValue(an);
    	methods = GetAllMethodName(className);
    	size = GetArrayNum(methods);
    	i = 0;
    	while(i < size){
    		if(methods[i] != "<init>"){track(className,methods[i],classPath);}
    		i = ToInt(i+1);
    	}
    	return 0;
    }
    function main(args){
    	allClass = GetAllClassName();
    	size = GetArrayNum(allClass);
    	i = 0;
    	while(i < size){
    		an = GetClassAnnotation(allClass[i]);
    		p = getSpringAnnotationValue(an);
    		if(p != ""){
    			SQLTrack(allClass[i]);
    		}
    		i = ToInt(i + 1);
    	}
    	
    }
    

而且也可以观察到，脚本已经非常的大了，所以有一点臃肿了，之后我会将Spring的常用函数全部编写成工具文件，直接使用`#include`就可以直接包含进来常用的方法。

## 更复杂的调用链

这里我们更换一个靶场，使用一个朋友的靶场，下面是Spring的项目结构：

![image](https://image.3001.net/images/20211223/1640229140_61c3e914ac4d53d49d155.png!small)

相同的，我们同样运行之前写好的SQL注入漏洞脚本，我们可以看到如下的结果：

![image](https://image.3001.net/images/20211223/1640229150_61c3e91e310fd15be5762.png!small)

仔细观察调用链你会发现一件很有意思的事情。

首先先手动分析一下这条路径的真正执行流：

    
    
    return this.sqliDao.addUser(name,age);
    

这里注意sqliDao这个属性变量，当你看这个变量类型时，你会发现他是一个接口：

    
    
    private final SQLIDao sqliDao;
    
    
    
    //_       ____                ____                                  _ __
    //| |     / / /_____  _____   / __ \___  _________  ____ ___  ____  (_) /__
    //| | /| / / //_/ _ \/ ___/  / / / / _ \/ ___/ __ \/ __ `__ \/ __ \/ / / _ \
    //| |/ |/ / ,< /  __/ /     / /_/ /  __/ /__/ /_/ / / / / / / /_/ / / /  __/
    //|__/|__/_/|_|\___/_/     /_____/\___/\___/\____/_/ /_/ /_/ .___/_/_/\___/ 
    //                                                        /_/
    package org.sec.cidemo.dao;
    public interface SQLIDao{
    	public abstract List selectUser(){
    	}
    	public abstract String addUser(){
    	}
    
    }
    

但最终为何我们还是可以跟踪出真正的调用链呢？

实际上wJa会帮我们进行特定于java的分析，并且可以自动分析子类对象和实现类是否进入危险函数。

看wJa的调用链第三条可以看到，当前处于：`SQLIDaoImpl.selectUser`

跳转到此方法：

    
    
    public class SQLIDaoImpl implements SQLIDao
    ...
    public List selectUser(String name){
    		String sql;
    		List users;
    		System.out.println(name);
    		sql = new StringBuilder().append("select * from t_user where name='").append(name).append("'").toString();
    		users = this.jdbcTemplate.query(sql,new BeanPropertyRowMapper(User.class));
    		return users;
    	}
    ...
    

发现正是这个实现类存在注入漏洞。

并且仔细观察可以看到，wJa还可以帮助我们进行变量转换跟踪。

其实实际上jdbc最终调用的是sql这个变量，并不是name，wJa可以自动追加追踪接受追踪变量的变量。

## SSRF漏洞分析

我们这里主要跟踪SSRF漏洞，相比于SQL注入漏洞，我们要对目标进入函数和黑盒测试代码进行修改。

    
    
    url = new URL(data);
    con = url.openConnection();
    con.setRequestMethod("GET");
    con.setRequestProperty("User-Agent","Mozilla/5.0");
    in = new BufferedReader(new InputStreamReader(con.getInputStream()));
    

这里可以通过进入BufferedReader的构造方法来判断是否是SSRF，但是更安全的是如果路径存在URL类，那么就可以基本判断是存在SSRF漏洞。

对于黑盒测试代码可以通过传递百度的地址进行关键字判断。

    
    
    function judgeSSRF(api){
    	res = HttpGet(api."http://www.baidu.com","");
    	if(StrFindStr(res[0],"//www.baidu.com/",0) != "-1"){
    		return 1;
    	}
    	return 0;
    }
    

其余的代码都是进行小幅度更改，但是需要注意的是，构造函数是`<init>`。

最终可以得到如下：

![image](https://image.3001.net/images/20211223/1640229167_61c3e92f71f54c31d2f67.png!small)

~工作顺利

