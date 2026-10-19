## 0x00 前言

对于Log4J的修复方法现在已经很多了，大部分是在程序未运行情况的修复方法，比如在JVM参数中添加`-Dlog4j2.formatMsgNoLookups=true`或者
添加系统环境变量 或者
修改配置文件。而本次是一种基于`javaagent`机制进行RASP防护，通过Patch`org.apache.logging.log4j.core.net.JndiManager`的`lookup`方法，能够在程序运行时修复漏洞。

本次环境：<https://github.com/chaitin/log4j2-vaccine>

## 0x01 代码分析

  

![](https://image.3001.net/images/20220414/1649921855_6257cf3f2d768a9187d86.png!small)

### agent.jar

    
    
    import com.chaitin.vaccine.agent.transform.JndiManagerTransformer;  
    ​  
    import java.io.UnsupportedEncodingException;  
    import java.lang.instrument.Instrumentation;  
    import java.net.URLDecoder;  
    ​  
    public class Agent {  
    /**  
    * 解码传递参数  
    * @param arg  
    * @return  
    * @throws UnsupportedEncodingException  
    */  
    protected static String decodeArg(String arg) throws UnsupportedEncodingException {  
    try {  
    return URLDecoder.decode(arg, "UTF-16");  
    } catch (UnsupportedEncodingException e) {  
    return URLDecoder.decode(arg, "UTF-8");  
    }  
    }  
    ​  
    /**  
    * 启动时加载的agent入口方法  
    *  
    * @param agentArg 启动参数  
    * @param inst     {@link Instrumentation}  
    */  
    public static void premain(String agentArg, Instrumentation inst) {  
    try {  
    System.out.println("[Vaccine] Premain Agent");  
    JndiManagerTransformer jndiManagerTransformer = new JndiManagerTransformer(inst);  
    inst.addTransformer(jndiManagerTransformer, true);  
    jndiManagerTransformer.retransform();  
    }catch (Throwable e){  
    e.printStackTrace();  
    }  
    }  
    ​  
    /**  
    * attach 机制加载 agent  
    *  
    * @param agentArg 启动参数  
    * @param inst     {@link Instrumentation}  
    */  
    public static void agentmain(String agentArg, Instrumentation inst) {  
    try {  
    System.out.println("[Vaccine] Attach Agent");  
    JndiManagerTransformer jndiManagerTransformer = new JndiManagerTransformer(inst);  
    //添加  
    inst.addTransformer(jndiManagerTransformer, true);  
    jndiManagerTransformer.retransform();  
    }catch (Throwable e){  
    System.out.println("[Vaccine] Error "+ e.getMessage());  
    e.printStackTrace();  
    }  
    }  
    }

提供了permain和agentmain两种启动方式，我们这里实验环境是类加载后，所以分析agentmain即可

注册转换器jndiManagerTransformer，而当类加载的时候，会先进入我们的jndiManagerTransformer

 **进去jndiManagerTransformer.retransform()**

    
    
    public void retransform() {  
    //获得所有加载的类  
    Class<?>[] loadedClasses = inst.getAllLoadedClasses();  
    for (Class<?> clazz : loadedClasses) {  
    //匹配加载的类是否有JndiManagerClassName  
    if (clazz.getName().replace("/", ".").equals(JndiManagerClassName)) {  
    System.out.println("[Vaccine] Find Loaded JndiManager Lookup Method!");  
    try {  
    //重加载  
    inst.retransformClasses(clazz);  
    } catch (Throwable t) {  
    System.out.println("failed to retransform class " + clazz.getName() + ": " + t.getMessage());  
    }  
    }  
    }  
    }

作用是将已加载的JndiManagerClassName进行重加载，这里涉及一个知识：已加载的类要进行修改时，需要先进行重加载，然后才可以修改

 **进去JndiManagerTransformer.transform()**

    
    
    @Override  
    public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {  
    //匹配class对象是否有JndiManagerClassName  
    if(className.replace("/",".").equals(JndiManagerClassName)){  
    System.out.println("[Vaccine] Start Patch JndiManager Lookup Method!");  
    CtClass ctClass = null;  
    CtMethod ctMethod = null;  
    try{  
    // 初始化classPool  
    ClassPool classPool = new ClassPool();  
    classPool.appendSystemPath();  
    if (loader != null) {  
    classPool.appendClassPath(new LoaderClassPath(loader));  
    }  
    ​  
    // 构造CtClass  
    ctClass = classPool.makeClass(new ByteArrayInputStream(classfileBuffer));  
    ​  
    // 获取lookup方法  
    for(CtMethod method:ctClass.getMethods()){  
    if(method.getName().equals(JndiManagerLookupMethodName)){  
    ctMethod = method;  
    break;  
    }  
    }  
    ​  
    // 修改lookup方法  
    assert ctMethod != null;  
    //ctMethod.insertBefore("if(name.startsWith(\"ldap://\") || name.startsWith(\"rmi://\")){return null;}");  
    //使得提前退出方法  
    ctMethod.insertBefore("return null;");  
    ​  
    // 返回字节码  
    System.out.println("[Vaccine] Patch JndiManager Lookup Success!");  
    return ctClass.toBytecode();  
    }catch (Exception e){  
    e.printStackTrace();  
    }finally {  
    if (ctClass != null) {  
    ctClass.detach();  
    }  
    }  
    }else{  
    return classfileBuffer;  
    }  
    ​  
    return classfileBuffer;  
    }

使用 **javassist** 对拦截的类 **org.apache.logging.log4j.core.net.JndiManager** 中
**lookup** 方法进行修改，在类的最前面直接添加 **return null** ，使得直接跳出类，不进行接下来的恶意操作

总结：拦截恶意类，重加载，然后进行修改。到这里我们还需要根据程序在JVM中的线程pid，才能进行拦截恶意类等操作

### load.jar

 **VirtualMachine** 和 **VirtualMachineDescriptor**

存在于`com.sun.tools.attach`里面有两个重要的类，通过这两个类可以根据线程pid，远程连接到JVM

`VirtualMachine`可以来实现获取系统信息，内存dump、现成dump、类信息统计（例如JVM加载的类）。里面配备有几个方法LoadAgent，Attach
和 Detach 。下面来看看这几个方法的作用

  *  **Attach** ：从 JVM 上面解除一个代理等方法，可以实现的功能可以说非常之强大 。该类允许我们通过给attach方法传入一个jvm的pid(进程id)，远程连接到jvm上

  *  **loadAgent** ：向jvm注册一个代理程序agent，在该agent的代理程序中会得到一个Instrumentation实例，该实例可以 在class加载前改变class的字节码，也可以在class加载后重新加载。在调用Instrumentation实例的方法时，这些方法会使用ClassFileTransformer接口中提供的方法进行处理。

  *  **Detach** ：从 JVM 上面解除一个代理(agent)

`VirtualMachineDescriptor`是用于描述 Java
虚拟机的容器类。它封装了一个标识目标虚拟机的标识符，以及一个`AttachProvider`在尝试连接到虚拟机时应该使用的引用。标识符依赖于实现，但通常是进程标识符（或
pid）环境，其中每个 Java 虚拟机在其自己的操作系统进程中运行。

`VirtualMachineDescriptor`实例通常是通过调用`VirtualMachine.list()`方法创建的。这将返回描述所有已安装
Java 虚拟机的完整描述符列表`attach providers`。

 **启动类Command.main**

    
    
    public static void main(String[] args) {  
    new Command().app(args);  
    }

 **跟进Command().app**

    
    
    public void app(String[] args) {  
    try {  
    //在解析阶段，我们在创建解析器实例后解析使用命令行参数传递的选项。  
    CommandLineParser parser = new DefaultParser();  
    CommandLine cmd = parser.parse(options, args);  
    //输出的参数  
    List<String> arguments = cmd.getArgList();  
    ​  
    //返回agent的值  
    File agent = new File(cmd.getOptionValue("agent")).getAbsoluteFile();  
    //获得uninstall参数  
    String action = cmd.hasOption("uninstall") ? "uninstall":"install";  
    ​  
    long pid = -1;  
    boolean injectAll = false;  
    ​  
    if (arguments.size() != 1) {  
    // select jvm process pid  
    try {  
    pid = ProcessUtils.select(false, -1, null);  
    } catch (InputMismatchException e) {  
    throw new UsageException("Please input an integer to select pid.");  
    }  
    if (pid < 0) {  
    throw new UsageException("Please select an available pid.");  
    }  
    }else{  
    // "all" means inject all porcess  
    if(arguments.get(0).equals("all")){  
    injectAll = true;  
    }else{  
    //获得pid  
    pid = Integer.parseInt(arguments.get(0));  
    ​  
    }  
    }  
    ​  
    if(injectAll){  
    Map<Long, String> processMap = ProcessUtils.listProcessByJps(false);  
    for(Long processPid : processMap.keySet()){  
    Application application = new Application(processPid, agent.getAbsolutePath(), action);  
    application.load();  
    }  
    }else{  
    ​  
    Application app = new Application(pid, agent.getAbsolutePath(),action);  
    app.load();  
    }  
    } catch (IOException e) {  
    LogUtils.error("Error: attach io error, " + e.getMessage());  
    }  
    catch (ParseException e) {  
    printHelp();  
    } catch (NumberFormatException e) {  
    ps.println("Error: pid must be a number");  
    printHelp();  
    } catch (UsageException e) {  
    ps.println("Error: " + e.getMessage());  
    printHelp();  
    }  
    }

主要作用是处理命令行提交的参数，这里要求提交一个pid，对提交的pid进行处理。获得pid后调用 **Application.load**
进行加载agent.jar到JVM中，从而修改目标class的字节码

跟进 **Application.load**

    
    
    public void load() throws IOException  
    {  
    VirtualMachine virtualMachine = null;  
    String pid = Long.toString(this.pid);  
    ​  
    //TODO jdk version > 9 will throw java.util.ServiceConfigurationError:  
    try {  
    System.out.println("[Vaccine] Agent Patch Pid: " + pid + " Start");  
    virtualMachine = VirtualMachine.attach(pid);  
    Thread.sleep(1000);  
    if (virtualMachine != null) {  
    String arg = formatArg();  
    virtualMachine.loadAgent(this.agent,arg);  
    }  
    } catch (AttachNotSupportedException e) {  
    System.err.println("[Vaccine] Error: attach api is not supported, " + e.getMessage());  
    } catch (ServiceConfigurationError e){//jdk 9+ 由于attach api 整合在jdk中会报错，实际上可以忽略  
    ​  
    } catch (Exception e) {  
    System.err.println("[Vaccine] Error: vaccine loaded failed, " + e.getMessage());  
    } finally {  
    if (virtualMachine != null) {  
    virtualMachine.detach();  
    System.out.println("[Vaccine] Agent Patch Finished");  
    }  
    }  
    ​  
    }

线程pid，远程连接到JVM，然后通过 **virtualMachine.loadAgent(this.agent,arg**
)向jvm注册一个代理程序agent，在该agent的代理程序中会得到一个Instrumentation实例，该实例可以
在class加载前改变class的字节码

## 0x02 复现

 **启动环境**

java -jar log4j2vuln3-0.0.2-SNAPSHOT.jar

![image-20220412103552384](https://image.3001.net/images/20220414/1649922279_6257d0e7bf917930581aa.png!small)

 **修复前**

漏洞触发url:

    
    
    curl http://127.0.0.1:8080/input?msg=xxx.dnslog.cn

![image-20220412103756273](https://image.3001.net/images/20220414/1649922282_6257d0eab3ef8a4b95de8.png!small)

 **修复后**

命令：

    
    
    java -jar loader.jar --agent agent.jar

![image-20220412103847824](https://image.3001.net/images/20220414/1649922284_6257d0ec6d0a078121f45.png!small)

已经无法进行攻击

![image-20220412103942485](https://image.3001.net/images/20220414/1649922286_6257d0eeadcb071e7bf77.png!small)

## 0x03 思考

基于javaagent的插桩技术，对于修复漏洞和程序运行时修改代码，提供了很便携的方法。不仅仅是修复log4j。它能够解决的是任何需要再程序运行时去修改代码的，都可以通过javaagent动态的通过JVM去修改程序的字节码。

