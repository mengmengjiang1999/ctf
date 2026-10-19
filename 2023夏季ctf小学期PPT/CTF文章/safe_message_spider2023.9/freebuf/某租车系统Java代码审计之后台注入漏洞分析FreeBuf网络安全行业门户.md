## CMS简介

 **系统基于租车业务场景而搭建的O2O服务平台，可为用户提供商务租车、接送机、旅游租车、企业租车、自驾租车、婚庆用车等自助租车服务。**

系统包含车辆库管理、门店管理、员工管理、司机管理、订单管理、活动管理、评价管理、财务管理、统计等。

> cms的下载地址：<http://down.admin5.com/jsp/135501.html>

## 部署简介

1、下载代码文件，可以本机调试或上传到自己服务器运行。

2、安装运行程序：

> （1）将解压文件夹中的opencarrun安装包复制到tomcat-->webapps--> 下；
>
> （2）将sql导入mysql；
>
> （3）启动tomcat；
>
> （4）启动完毕后，前台访问地址：<http://localhost:8080/opencarrun/>

后台访问地址：<http://localhost:8080/opencarrun/admin/login> (默认账号：adimin
默认密码：zft3285497)

3、开发包安装

打开MyEclipse-->File-->Import-->选择Existing Porjects into
Workspace-->Next-->Select root directory 选择刚才解压的开发包文件中的opencar-->Finish

## sql审计过程

漏洞位置：

> WebRoot\WEB-INF\lib\car-> weishang-1.0.jar!\com\weishang\my\admin\DeleteAunt.class

功能模块：删除外聘员工

 ****

    
    
     **public void** doGet(HttpServletRequest request,HttpServletResponse response) **throws** ServletException, IOException {  
        response.setContentType( **"text/html;charset=UTF-8"** );  
        PrintWriter out =response.getWriter();  
        ShopService ss = **new** ShopService();  
       HttpSession session = request.getSession( **true** );  
        Object user = session.getAttribute( **"user"** );  
        Locale loc = **new** Locale( **"zh"** , **"CN"** );  
        ResourceBundle rb =ResourceBundle.getBundle( **"messages"** , loc);  
        String adminTip = rb.getString( **"adminTip"** );  
       String json = **""** ;  
        **if** (user== **null** ) {  
            RequestDispatcher rd =request.getRequestDispatcher( **"/WEB-INF/jsp/login.jsp"** );  
            request.setAttribute( **"tip"** , adminTip);  
            rd.forward(request, response);  
        } **else** {  
           String[] auntIds = request.getParameterValues( **"aunt_id"** );  
           String ids = **""** ;  
      
            **for** ( **int** i = 0; i < auntIds.length; ++i) {  
                ids = ids + auntIds[i] + **","** ;  
            }  
      
            ids = ids.substring(0, ids.length() - 1);  
            String flag = ss.deleteAunt(ids);  
            **if** (flag.equals( **"ok"** )) {  
                json = **"{** **\"** **tip** **\"** **:** **\"** **"** + rb.getString( **"delete"** ) + rb.getString( **"success"** ) + **"** **\"** **}"** ;  
            } **else** {  
                json = **"{** **\"** **tip** **\"** **:** **\"** **"** + rb.getString( **"delete"** ) + rb.getString( **"failure"** ) + **"** **\"** **}"** ;  
            }  
      
            out.print(json);  
        }  
      
    }

request.getParameterValues("aunt_id") 获取获取用户值，赋值给字符串数组变量 aunt_id,
aunt_id经过处理交给ids变量,而ids变量进入deleteAunt方法，这里通过flag变量判断执行是否成功，这样只可能存在盲注了，跟进去：

deleteAunt方法位于

> /WebRoot/WEB-INF/lib/car-> weishang-1.0.jar!/com/weishang/my/service/ShopService.class
    
    
     **public** String deleteAunt(String ids) {  
    
        String sql = **"delete from aunt where aunt_id in ("** + ids + **")"** ;  
    
        **int** flag = **this**.jdbc.executeUpdate(sql);  
    
        **this**.jdbc.close();  
    
        **return** flag > 0 ? **"ok"** : **"bad"** ;  
    
    }

从这个方法看是一个执行删除操作，变量ids， 也就是我们问题参数直接被拼接到sql语句中，未做编译，未做任何过滤，从而造成注入漏洞，

##  **修复建议**

做全局过滤，或使用参数绑定

 ***本文作者：qq1654985095，转载请注明来自FreeBuf.COM**

