# Xposed入门及免重启系统和免重启App探索

Xposed和Frida相比，Frida更加灵活还可以支持native所以目前我在使用Hook的时候也会优先选择Frida，但是根据实际使用体验来看的话，会存在一些Xposed能用frida却Hook失败或者反过来Frida能用Xposed失败的情况，所以二者目前也是结合使用。

之前使用Xposed或者EDXposed的时候Xposed模块每次修改都需要修改代码编译和重启设备，比较繁琐，对于逆向过程中定位一些函数啥的不是很方便，所以就萌生了一些研究的小想法，就考虑做一个免重启的模块方便定位一些方法。

其实之前也有很多大佬做过类似的功能更多更强大的项目，如免重启的Xposed框架，还有一些直接就可以枚举方法动态hook的模块。但是生命在于折腾，随便玩玩也是可以的嘛。

这个思路的核心在于`getDeclaredMethods`和`XposedBridge.hookMethod()`，通过`getDeclaredMethods`遍历方法，然后用`XposedBridge.hookMethod()`进行Hook和打印参数操作。在配置文件中配置需要Hook的包名、方法名。

# 1\. 编写入门

目前关于Xposed的入门教程不计其数，在此就简单写一下，重点会放在免重启

### 新建一个Android Project

### 修改AndroidManifest.xml文件

    
    
    <!-- xposed识别用，表示此app是个xposed模块 -->
    <meta-data
        android:name="xposedmodule"
        android:value="true" />
    <!-- 模块描述 -->
    <meta-data
        android:name="xposeddescription"
        android:value="劫持样例"/>
    <!--最低版本号 -->
    <meta-data
        android:name="xposedminversion"
        android:value="30"/>
    

### 修改app/build.gradle导入xposed依赖

`在android {}的同级别添加如下内容，表示从jcenter仓库中找包，也可以换成其他的镜像站`

    
    
    repositories {
        jcenter()
    }
    

`在dependencies中添加如下内容（必须是compileOnly ）`

    
    
    compileOnly 'de.robv.android.xposed:api:82'
    compileOnly 'de.robv.android.xposed:api:82:sources'
    

### 增加xposed_init

  * 在main目录下新增assets文件夹

  * 在assets文件夹下新增文件xposed_init  
最后的目录结构为：app\src\main\assets\xposed_init  
xposed_init的作用为存放Xpose Hook代码的入口类,格式大致如下，存放自己写的Hook代码的包名.类名即可

    
    
    com.example.androidhookdemo.Main_JG
    

# 2\. 代码实现

### 新建一个类，实现接口IXposedHookLoadPackage的方法handleLoadPackage

一个简单的算是固定写法吧，一般开头这么写就可以满足需求了

    
    
    import de.robv.android.xposed.IXposedHookLoadPackage;
    import de.robv.android.xposed.XC_MethodHook;
    import de.robv.android.xposed.XposedBridge;
    import de.robv.android.xposed.callbacks.XC_LoadPackage;
    
    import static de.robv.android.xposed.XposedHelpers.findAndHookMethod;
    
    
    //新建一个类，实现接口IXposedHookLoadPackage
    public class Main_JG implements IXposedHookLoadPackage {
        @Override
        //实现接口定义的方法handleLoadPackage
        public void handleLoadPackage(final XC_LoadPackage.
                LoadPackageParam lpparam) throws Throwable {
            .......//这里是具体的Hook代码，下面写
        }
    

### 使用findAndHookMethod来Hook目标方法

先导入：import static de.robv.android.xposed.XposedHelpers.findAndHookMethod;

  * 使用findAndHookMethod方法Hook目标方法，findAndHookMethod(目标class名，lpparam.classLoader，方法名，参数1，参数2....，

  * new XC_MethodHook(){实现beforeHookedMethod和afterHookedMethod方法})  
`XC_MethodHook:在目标方法执行前/后运行相应的替换函数；`  
`beforeHookedMethod 主要用来读取和修改参数`  
`afterHookedMethod 主要用来修改返回值以及查看修改是否生效`

  * `XC_MethodHook可以替换为XC_MethodReplace:完全替换目标方法，执行用户自定义方法。`

    
    
    //过滤掉不符合要求的类，可以打一下日志，看看是否正常
    if (lpparam.packageName.equals("com.example.xiaoming")){
      XposedBridge.log("Loaded app: " + lpparam.packageName);
      findAndHookMethod("com.example.xiaoming.myapplication.MainActivity", lpparam.classLoader, "getString", String.class,new XC_MethodHook(){
        @Override
        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
          XposedBridge.log("开始~~~~~");
          XposedBridge.log("参数1 = " + param.args[0]);
          //修改被hook方法的参数
          param.args[0] = "XXX";
        }
    
        @Override
        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
          XposedBridge.log("参数1 = " + param.args[0]);
          XposedBridge.log("结束~~~");
        }
      });
    }
    

# 3.Xposed模块免重启系统

现在进入正题，介绍一下当前的模块实现免重启系统的方案，流程大体如下：

  * 修改配置文件

  * 重启App（强行停止并再次启动）

  * 读取配置

  * 根据配置中配置的类名遍历其中的方法

  * 根据配置选择是Hook所有方法还是Hook方法列表中的方法

  * 打印参数和返回值

### 配置文件

    
    
    {
        "packageName":{
          "className1":["encrypt","decrypt"],
          "className2":["encryptCBC","decryptCBC"],
          "isHookAll":false,
          "isShelld":false,
          "shellClass":"s.h.e.l.l.S",
          "shellMethod":"attachBaseContext"
        },
    
        "com.xxx.xxx":{
            "className":["b","a"],
            "isHookAll":false,
            "isShelld":true,
            "shellClass":"com.secneo.apkwrapper.AW",
            "shellMethod":"attachBaseContext"
        }
    }
    

### 读取配置

    
    
    public static String readJsonFile(String fileName) {
            String jsonStr = "";
            try {
                File jsonFile = new File(fileName);
                FileReader fileReader = new FileReader(jsonFile);
                Reader reader = new InputStreamReader(new FileInputStream(jsonFile),"utf-8");
                int ch = 0;
                StringBuffer sb = new StringBuffer();
                while ((ch = reader.read()) != -1) {
                    sb.append((char) ch);
                }
                fileReader.close();
                reader.close();
                jsonStr = sb.toString();
                return jsonStr;
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }
    

### 关键方法

    
    
    // 获取所需的类对象
    clazz = Class.forName(className, false, classLoader);
    
    // 遍历目标类的方法
    for (final Method method: clazz.getDeclaredMethods()) {
      // 处理逻辑
    }
    
    // Hook目标方法
    try {
      Class clazz = Class.forName(className, false, classLoader);
      // 遍历方法
      for (final Method method : clazz.getDeclaredMethods()) {
        StringBuffer s = new StringBuffer();
        int num = 0;
        for (Class c : method.getParameterTypes()) {
          s.append(c.getName()).append(",");
          num = num + 1;
        }
        // Hook目标方法
        if (hookMethods.contains(method.getName())) {// Hook符合条件的方法
          XposedBridge.log("进入" + className + "\\" + method + "分支");
          XposedBridge.hookMethod(method, new XC_MethodHook() {
            @Override
            protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
              super.beforeHookedMethod(param);
            }
    
            @Override
            protected void afterHookedMethod(MethodHookParam param) throws Throwable {
              int a = method.getParameterTypes().length;
              if (a > 0) {
                for (int i = 0; i < a; i++) {
                  XposedBridge.log(methodName + "，参数 [" + i + "] = " + param.args[i]);
                }
                XposedBridge.log( methodName + "，返回值" + param.getResult().toString());
              } else {
                XposedBridge.log( methodName + "，返回值" + param.getResult().toString());
              }
            }
          });
        }
      }
    } catch (ClassNotFoundException e) {
      e.printStackTrace();
    }
    

# 4.Xposed模块免重启App替换参数和返回值

解决了每次都要编写模块、编译、安装、重启这样繁琐的流程后，在后续的逆向中又遇到了另一个问题：有时需要修改一些方法的参数和返回值，但是如果使用Xposed每次重启App也是个很麻烦的事（有时候Frida修改脚本后也会出现无法生效的情况），所以又搞了一下免重启App来实现替换参数的Xposed模块，方便在分析阶段替换报文。

这个模块目前实现比较简单，即在Hook过程中每次执行到被Hook的方法时都读取配置文件进行判断

目前仅能替换一些字符串，如果需要替换复杂参数还需要做对应的修改，后续如果遇到复杂变量的替换再增加和更新

### 配置文件

    
    
    { 
      "Encrypt.decrypt":{ 
        // oldString根据需要匹配的字符串
        "\"STATUS\":\"B6047\"":{
          "isReplaceAll":false,
          "newString":"\"STATUS\":\"1\""
        }
      },
      "Encrypt.decrypt999":{
        "\"STATUS\":\"00002\"":{
          "isReplaceAll":false,
          "newString":"\"STATUS\":\"1\""
        },
        "\"STATUS\":\"00003\"":{
          "isReplaceAll":false,
          "newString":"\"STATUS\":\"1\""
        }
      }
    }
    

### 关键方法

    
    
    //读取json文件
        public static JSONObject readJsonFile(String fileName) {
            String jsonStr = "";
            try {
                File jsonFile = new File(fileName);
                FileReader fileReader = new FileReader(jsonFile);
                Reader reader = new InputStreamReader(new FileInputStream(jsonFile),"utf-8");
                int ch = 0;
                StringBuffer sb = new StringBuffer();
                while ((ch = reader.read()) != -1) {
                    sb.append((char) ch);
                }
                fileReader.close();
                reader.close();
                jsonStr = sb.toString();
                return JSONObject.parseObject(jsonStr);
    //            return jsonStr;
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }
    // 替换
    public static String MyReplace(String value,String methodName){
            final JSONObject jsonObject = JsonUtil.readJsonFile("/data/local/tmp/replace.json");
            if(jsonObject != null && jsonObject.containsKey(methodName)){
                JSONObject jso = jsonObject.getJSONObject(methodName);
                for (Map.Entry<String, Object> entry : jso.entrySet()) {
                    String oldStr = entry.getKey(); 
                    JSONObject jsobj = jso.getJSONObject(oldStr); // 目标json的key对应的值为新字符串和替换模式
                    String newStr = jsobj.getString("newString");
                    if(value.contains(oldStr)){ 
                        if(jsobj.getBoolean("isReplaceAll")){ // 判断替换模式
                            MLogUtil.d("Ming-HookED","新数据:" + newStr +"替代包含目标字符串:" + oldStr +"的数据" );
                            value = newStr;
                        }else{
                            MLogUtil.d("Ming-HookED","使用新字符串:" + newStr + "替换目标字符串:" + oldStr);
                            value = value.replace(oldStr,newStr);
                        }
                    }
                }
            }
            // 返回处理后的字符串
            return value;
        }
    

### 使用以上方法的返回的值替换目标

    
    
    String value = JsonUtil.MyReplace((String) param.getResult(),methodName);
    param.setResult(value);
    

免重启系统的Xposed模块关键代码都贴出来了，内容很少复制之后改改就可以用或者大佬们也可以自己写

免重启App的如果有需要使用的直接复制文章中的代码编译到自己的模块即可

