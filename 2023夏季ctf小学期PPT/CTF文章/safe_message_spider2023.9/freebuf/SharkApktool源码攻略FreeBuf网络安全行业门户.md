作者：[HAI_](https://bbs.ichunqiu.com/thread-43219-1-1.html?from=beef)

原文来自：[https://bbs.ichunqiu.com/thread-43219-1-1.html](https://bbs.ichunqiu.com/thread-43219-1-1.html?from=beef)

# 0x00 前言

网上的资料对于apktool的源码分析，来来回回就那么几个，而且还是不尽人意，所以只好自己动手试一试，于是乎拿着最新的SharkApkTool搞一下。

# 1.apktool.Main 第一部分

从Main出发，这个是整个工具的入口点

## 1.1 public static void main

先来一个main方法的合集，可能有点小。  
![image.png](https://image.3001.net/images/20180725/15325054706685.png!small)  

### 1.1.1 Verbosity verbosity = Verbosity.NORMAL;

我们先来看一下这个

    
    
     private static enum Verbosity
      {
        NORMAL,  VERBOSE,  QUIET;
    
        private Verbosity() {}
      }

很明显这是一个枚举类型，有三个成员  
NORMA:正常的  
VERBOSE:啰嗦的  
QUIET:安静的  
这里猜测可能是模式的选择。

### 1.1.2 CommandLineParser parser = new DefaultParser();

#### (1) CommandLineParser

    
    
    package org.apache.commons.cli;
    
    public abstract interface CommandLineParser
    {
      public abstract CommandLine parse(Options paramOptions, String[] paramArrayOfString, boolean paramBoolean)
        throws ParseException;
    }

CommandLineParser是一个接口，其中有一个抽象方法。返回了一个Commandline的类。

#### (2) DefaultParser()

  
然后来看看DefaultParser这里![image.png](https://image.3001.net/images/20180725/15325054945990.png!small)  

DefaultParser实现了CommandLineParser接口。

但是DefaultParser没有主动写构造方法，只实现系统默认的构造方法，相当于无操作

#### （3）

CommandLineParser parser = new DefaultParser();  
这里的写法是可以实现接口的多态的

### 1.1.5 _Options();

找到_Options()方法，很长的一大串，但是格式都是类似的。应该是在做什么配置一类的。我们来抓住一个看一下。

    
    
     Option versionOption = Option.builder("version").longOpt("version").desc("prints the version then exits").build();
    

这里使用了Builder设计模式  
先来看看Option.builder("version")。

    
    
    public static Builder builder(String opt)
      {
        return new Builder(opt, null);
      }

置换一下，相当于，我们现在拿到的是 new Builder("version",null)  
接着来看Builder类  
先找到对应的构造方法。

    
    
    private Builder(String opt)
          throws IllegalArgumentException
        {
          OptionValidator.validateOption(opt);
          this.opt = opt;
        }

这里置换一下就是  
传入了version，并且把当前的opt置换成了version。  
然后还把version传入了OptionValidator.validateOption  
继续了解一下

    
    
    static void validateOption(String opt)
        throws IllegalArgumentException
      {
        if (opt == null) {
          return;
        }
        char ch;
        if (opt.length() == 1)
        {
          ch = opt.charAt(0);
          if (!isValidOpt(ch)) {
            throw new IllegalArgumentException("Illegal option name '" + ch + "'");
          }
        }
        else
        {
          for (char ch : opt.toCharArray()) {
            if (!isValidChar(ch)) {
              throw new IllegalArgumentException("The option '" + opt + "' contains an illegal character : '" + ch + "'");
            }
          }
        }
      }

分了三种情况。  
第一种判空。  
第二种opt.length() == 1  
第三种其他情况  
第一种没有什么好说的，先来看看第二种。

    
    
    if (opt.length() == 1)
        {
          ch = opt.charAt(0);
          if (!isValidOpt(ch)) {
            throw new IllegalArgumentException("Illegal option name '" + ch + "'");
          }
        }

这里使用了

    
    
    ch = opt.charAt(0);

这一步就是为了获取char 类型的ch

    
    
     if (!isValidOpt(ch)) {
            throw new IllegalArgumentException("Illegal option name '" + ch + "'");
          }

又来一个判断。继续跟进

    
    
    private static boolean isValidOpt(char c)
      {
        return (isValidChar(c)) || (c == '?') || (c == '@');
      }

看到isValidChar，继续跟进

    
    
    private static boolean isValidChar(char c)
      {
        return Character.isJavaIdentifierPart(c);
      }

看到return就知道这个跟完了，来说说Character.isJavaIdentifierPart(c)这个是在干嘛把。这个是在判断是否为一个合法的java变量所包含的字符  
返回到isValidOpt，和(c == '?')，(c == '@')进行判断，然后return  
第二种情况结束，这里就是判断传入的字符判断是否为一个合法的java变量所包含的字符和字符等于？和@的情况。

第三种情况

    
    
    for (char ch : opt.toCharArray()) {
            if (!isValidChar(ch)) {
              throw new IllegalArgumentException("The option '" + opt + "' contains an illegal character : '" + ch + "'");
            }
          }

和第二种情况类似，对每一个字符进行判断。  
回到我们之前的OptionValidator.validateOption(opt);  
也就是说这句的作用就是进行一个字符串的检测。

是不是觉得有一点绕?

这个时候就该使用一个强大的工具了。来进行一个汇总。

  
![image.png](https://image.3001.net/images/20180725/15325055417801.png!small)有了这个可能就整齐一点了。最好的方式还是动手。  

剩下的内容都是在做初始化了。

整体来说那个_Options()就是再做一个清单配置，相当于搭建一个合适的环境。

### 1.1.4 commandLine = parser.parse(allOptions, args, false);

这条语句是被try包裹起来的。  
调用了parser.parse()方法，这里是三个参数，就是对应

    
    
     public CommandLine parse(Options options, String[] arguments, boolean stopAtNonOption)
        throws ParseException
      {
        return parse(options, arguments, null, stopAtNonOption);
      }

这个方法更改参数位置，又调用了

    
    
    public CommandLine parse(Options options, String[] arguments, Properties properties, boolean stopAtNonOption)
        throws ParseException
      {
        this.options = options;
        this.stopAtNonOption = stopAtNonOption;
        this.skipParsing = false;
        this.currentOption = null;
        this.expectedOpts = new ArrayList(options.getRequiredOptions());
        for (Object localObject = options.getOptionGroups().iterator(); ((Iterator)localObject).hasNext();)
        {
          group = (OptionGroup)((Iterator)localObject).next();
          group.setSelected(null);
        }
        OptionGroup group;
        this.cmd = new CommandLine();
        if (arguments != null)
        {
          localObject = arguments;group = localObject.length;
          for (OptionGroup localOptionGroup1 = 0; localOptionGroup1 < group; localOptionGroup1++)
          {
            String argument = localObject[localOptionGroup1];
    
            handleToken(argument);
          }
        }
        checkRequiredArgs();
    
        handleProperties(properties);
    
        checkRequiredOptions();
    
        return this.cmd;
      }
    

这个方法一大堆，看来又有我们要忙的了。

    
    
        this.options = options;
        this.stopAtNonOption = stopAtNonOption;
        this.skipParsing = false;
        this.currentOption = null;
        this.expectedOpts = new ArrayList(options.getRequiredOptions());

初始化当前成员变量。

    
    
    for (Object localObject = options.getOptionGroups().iterator(); ((Iterator)localObject).hasNext();)
        {
          group = (OptionGroup)((Iterator)localObject).next();
    
          group.setSelected(null);
        }

options.getOptionGroups().iterator() 返回一个迭代器用于遍历。

    
    
           group = (OptionGroup)((Iterator)localObject).next();
           group.setSelected(null);

将group的selected设为null

    
    
    this.cmd = new CommandLine();

new 了一个CommandLine()  
CommandLine()里也没有构造方法，所以只是单纯的new。

    
    
    if (arguments != null)
        {
          localObject = arguments;group = localObject.length;
          for (OptionGroup localOptionGroup1 = 0; localOptionGroup1 < group; localOptionGroup1++)
          {
            String argument = localObject[localOptionGroup1];
    
            handleToken(argument);
          }
        }

这个部分就是对参数进行一个处理，我们传入了的是args。  
然后就是对这个args进行遍历，把每一个值都传入handleToken这个方法里。  
所以我们接下来就是对handleToken进行追进。

    
    
     private void handleToken(String token)
        throws ParseException
      {
        this.currentToken = token;
        if (this.skipParsing) {
          this.cmd.addArg(token);
        } else if ("--".equals(token)) {
          this.skipParsing = true;
        } else if ((this.currentOption != null) && (this.currentOption.acceptsArg()) && (isArgument(token))) {
          this.currentOption.addValueForProcessing(Util.stripLeadingAndTrailingQuotes(token));
        } else if (token.startsWith("--")) {
          handleLongOption(token);
        } else if ((token.startsWith("-")) && (!"-".equals(token))) {
          handleShortAndLongOption(token);
        } else {
          handleUnknownToken(token);
        }
        if ((this.currentOption != null) && (!this.currentOption.acceptsArg())) {
          this.currentOption = null;
        }
      }

这个就是handleToken

    
    
    if (this.skipParsing) {
          this.cmd.addArg(token);
        } 

判断skipParsing，成立则cmd.addArg(token)  
这个addArg又是做什么的呢？  
在Commandline中找到

    
    
    protected void addArg(String arg)
      {
        this.args.add(arg);
      }
    

又跟进到args.add  
发现args是一个List。  
好了这里就是说把传入的arg加到list列表里。  
回到handleToken

    
    
    else if ("--".equals(token)) {
          this.skipParsing = true;
        } 

这里判断传入的参数是不是--如果是--就让skipParsing打开，也就是说会让之后的内容传入到我们的cmd list中去。

    
    
    else if ((this.currentOption != null) && (this.currentOption.acceptsArg()) && (isArgument(token))) {
          this.currentOption.addValueForProcessing(Util.stripLeadingAndTrailingQuotes(token));
        }

我们一点一点来看  
this.currentOption != null很容易理解  
this.currentOption.acceptsArg()，这里的acceptsArg()就是

    
    
    boolean acceptsArg()
      {
        return ((hasArg()) || (hasArgs()) || (hasOptionalArg())) && ((this.numberOfArgs <= 0) || (this.values.size() < this.numberOfArgs));
      }

这里的hasArg()

    
    
     public boolean hasArg()
      {
        return (this.numberOfArgs > 0) || (this.numberOfArgs == -2);
      }

在Option中numberOfArgs默认为-1

再来看hasArgs()

    
    
    public boolean hasArgs()
      {
        return (this.numberOfArgs > 1) || (this.numberOfArgs == -2);
      }

对numberOfArgs进行判断  
这里猜测这个numberOfArgs就是对参数进行一个判断，名字也是这样的意思

hasOptionalArg()

    
    
     public boolean hasOptionalArg()
      {
        return this.optionalArg;
      }

当前的一个开关

做到这里其实就已经了解到整个判断流程了，就是对参数进行处理，处理方式按照不同人的习惯处理起来不同，不过多分析一下还是会学到的很多东西的。

至此，我们的分析的第一部分就已经完成了。

  
![image.png](https://image.3001.net/images/20180725/15325055779845.png!small)  

# 2.Main 第二部分

还是一点点一点来

## 2.1 commandLine.hasOption("-v")||(commandLine.hasOption("--verbose")

    
    
    verbosity = Verbosity.VERBOSE;

选择工作状态

## 2.2 (commandLine.hasOption("-q")) || (commandLine.hasOption("--quiet"))

    
    
    verbosity = Verbosity.QUIET;

和上一个一样选择工作状态

## 2.3 setupLogging(verbosity)

又是一个比较长的方法

    
    
    private static void setupLogging(Verbosity verbosity)
      {
        Logger logger = Logger.getLogger("");
        for (Handler handler : logger.getHandlers()) {
          logger.removeHandler(handler);
        }
        LogManager.getLogManager().reset();
        if (verbosity == Verbosity.QUIET) {
          return;
        }
        Object handler = new Handler()
        {
          public void publish(LogRecord record)
          {
            if (getFormatter() == null) {
              setFormatter(new SimpleFormatter());
            }
            try
            {
              String message = getFormatter().format(record);
              if (record.getLevel().intValue() >= Level.WARNING.intValue()) {
                System.err.write(message.getBytes());
              } else if (record.getLevel().intValue() >= Level.INFO.intValue()) {
                System.out.write(message.getBytes());
              } else if (this.val$verbosity == Main.Verbosity.VERBOSE) {
                System.out.write(message.getBytes());
              }
            }
            catch (Exception exception)
            {
              reportError(null, exception, 5);
            }
          }
    
          public void close()
            throws SecurityException
          {}
    
          public void flush() {}
        };
        logger.addHandler((Handler)handler);
        if (verbosity == Verbosity.VERBOSE)
        {
          ((Handler)handler).setLevel(Level.ALL);
          logger.setLevel(Level.ALL);
        }
        else
        {
          ((Handler)handler).setFormatter(new Formatter()
          {
            public String format(LogRecord record)
            {
              return 
    
                record.getLevel().toString().charAt(0) + ": " + record.getMessage() + System.getProperty("line.separator");
            }
          });
        }
      }

读完这一段之后就可以彻底明白那三个状态是什么意思了，就是对log日志的不同的输出状态  
如果是QUIET

    
    
    if (verbosity == Verbosity.QUIET) {
          return;
        }

那么就打印少一点的日志或者不打印  
如果是VERBOSE

    
    
    if (verbosity == Verbosity.VERBOSE)
        {
          ((Handler)handler).setLevel(Level.ALL);
          logger.setLevel(Level.ALL);
        }

推测应该是打印所有的日志。至少会打印很多。

## 2.4 commandLine.hasOption("advance")) || (commandLine.hasOption("advanced")

    
    
    setAdvanceMode(true);

查看更多的参数。

## 2.6 for (String opt : commandLine.getArgs())

对传入的参数进行遍历

### 2.6.1 (opt.equalsIgnoreCase("d")) || (opt.equalsIgnoreCase("decode")

decode的英文意思是译码  
也就是我们说的反编译了。

    
    
    cmdBuild(commandLine);
    cmdFound = true;

我们接下来的重点那就是cmdBuild

#### 2.6.2 cmdBuild

这个方法的内容有点多，我们就来一部分一部分搞。

2.6.2.1 ApkDecoder decoder = new ApkDecoder();

这里首先是new了一个ApkDecoder()  
来看一下无参的构造方法

    
    
    public ApkDecoder()
      {
        this(new Androlib());
      }

这里又new了一个 Androlib()

    
    
    public Androlib()
      {
        this.apkOptions = new ApkOptions();
        this.mAndRes.apkOptions = this.apkOptions;
      }

这里的ApkOptions是空的，相当于是一个配置类。  
那这里的mAndRes是什么  
下Androlib中定义了一个变量

    
    
    private final AndrolibResources mAndRes = new AndrolibResources();

给apkOptions变量赋值

总结一下，ApkDecoder decoder = new ApkDecoder();这句相当于是在为之后的反编译建立一个反编译环境。

2.6.2.2 int paraCount = cli.getArgList().size();

返回一个ArgList的大小，值的结果给paraCount。

2.6.2.3 tring apkName = (String)cli.getArgList().get(paraCount - 1);

获取APKname

2.6.2.4 (cli.hasOption("s")) || (cli.hasOption("no-src")

这里如果有s的话，代表不解析源码

    
    
    decoder.setDecodeSources((short)0);

我们跟进serDecodeSources

    
    
    public void setDecodeSources(short mode)
        throws AndrolibException
      {
        if ((mode != 0) && (mode != 1)) {
          throw new AndrolibException("Invalid decode sources mode: " + mode);
        }
        this.mDecodeSources = mode;
      }

这里就是把decoder的mDecodeSources值从1变为0。

2.6.2.5 if ((cli.hasOption("d")) || (cli.hasOption("debug")))

这里的d功能已经被移除

2.6.2.6 (cli.hasOption("b")) || (cli.hasOption("no-debug-info")

关闭debug-info

2.6.2.7 File outDir;

配置部分我们就跳过了，根据以上的分析，自己应该是很容易的。我们直接来看反编译部分。

2.6.2.8 创建输出文件

    
    
    if ((cli.hasOption("o")) || (cli.hasOption("output")))
        {
          File outDir = new File(cli.getOptionValue("o"));
          decoder.setOutDir(outDir);
        }
        else
        {
          String outName = apkName;
    
          outName = outName + ".out";
    
          outName = new File(outName).getName();
          outDir = new File(outName);
          decoder.setOutDir(outDir);
        }

这里把文件命名为.out 然后设置ourdirfile

2.6.2.9 decoder.setApkFile(new File(apkName));

看到名字可以猜测到时拿到输入ApkFile  
跟进

    
    
    public void setApkFile(File apkFile)
      {
        if (this.mApkFile != null) {
          try
          {
            this.mApkFile.close();
          }
          catch (IOException localIOException) {}
        }
        this.mApkFile = new ExtFile(apkFile);
        this.mResTable = null;
      }

this.mApkFile = new ExtFile(apkFile);

这里确定mApkFile是ExtFil格式的，所以我们跟进ExtFile这个类

    
    
    public ExtFile(File file)
      {
        super(file.getPath());
      }

拿到地址。

最后把mResTable的值变更为null;

2.6.2.10 decoder.decode()

这个就是核心代码的地方

1\. OS.rmdir(outDir);

先删除文件

2.outDir.mkdirs();

创建

3.if (hasResources())

这里对hasResources()方法进行跟进查看

    
    
     public boolean hasResources()
        throws AndrolibException
      {
        try
        {
          return this.mApkFile.getDirectory().containsFile("resources.arsc");
        }
        catch (DirectoryException ex)
        {
          throw new AndrolibException(ex);
        }
      }

mApkFile.getDirectory()方法

    
    
    public Directory getDirectory()
        throws DirectoryException
      {
        if (this.mDirectory == null) {
          if (isDirectory()) {
            this.mDirectory = new FileDirectory(this);
          } else {
            this.mDirectory = new ZipRODirectory(this);
          }
        }
        return this.mDirectory;
      }

这里对FileDirectory(this)进行跟进

    
    
    public FileDirectory(File dir)
        throws DirectoryException
      {
        if (!dir.isDirectory()) {
          throw new DirectoryException("file must be a directory: " + dir);
        }
        this.mDir = dir;
      }

这里传进来的是一个目录，所以mDir=dir；

回到ExtFile

    
    
    this.mDirectory = new ZipRODirectory(this);

跟进到Zip

    
    
    public ZipRODirectory(File zipFile)
        throws DirectoryException
      {
        this(zipFile, "");
      }

这里构造方法转换

    
    
      public ZipRODirectory(File zipFile, String path)
        throws DirectoryException
      {
        try
        {
          this.mZipFile = new ZipFile(zipFile);
        }
        catch (IOException e)
        {
          throw new DirectoryException(e);
        }
        this.mPath = path;
      }

这里相当于是拿到了一个压缩包

返回到hasResources  
containsFile("resources.arsc");这里  
然后对这个进行检测。

简单的说这个hasResources就是对resources.arsc进行检测。

4.hasManifest()

名字类似，这里不需要分析都知道是对Manifest.xml进行判断是否进行解析

# 3.Main第三部分-核心部分

    
    
    this.mAndrolib.decodeResourcesFull(this.mApkFile, outDir, getResTable());

这个就是Resource反编译的核心语句  
首先来看看decodeResourcesFull方法

    
    
    public void decodeResourcesFull(ExtFile apkFile, File outDir, ResTable resTable)
        throws AndrolibException
      {
        this.mAndRes.decode(resTable, apkFile, outDir);
      }

这里调用了mAndRes的decode方法，我们继续跟进。  
这里先列出来几句

    
    
        Duo<ResFileDecoder, AXmlResourceParser> duo = getResFileDecoder();
        ResFileDecoder fileDecoder = (ResFileDecoder)duo.m1;
        ResAttrDecoder attrDecoder = ((AXmlResourceParser)duo.m2).getAttrDecoder();
    
        attrDecoder.setCurrentPackage((ResPackage)resTable.listMainPackages().iterator().next());

这里有一个Duo的类我们跟进去看看

    
    
     public Duo(T1 t1, T2 t2)
      {
        this.m1 = t1;
        this.m2 = t2;
      }

这里指Duo存放了两个类

这里存放的是ResFileDecoder和AXmlResourceParser

我们先跟进ResFileDecoder。

  
![image.png](https://image.3001.net/images/20180725/15325056264795.png!small)  

看到decode，估计就是对res进行解析的，这个之后会再次调用

然后跟进AXmlResourceParser![image.png](https://image.3001.net/images/20180725/15325056473918.png!small)

应该是对xml格式文件进行解析的类。  

接着往下看。  
ResFileDecoder fileDecoder = (ResFileDecoder)duo.m1;  
把duo.m1给fukeDecoder

    
    
     ResAttrDecoder attrDecoder = ((AXmlResourceParser)duo.m2).getAttrDecoder();

这里是把m2也就时拿到AXmlResourceParser.getAttrDecoder()  
我们跟进这个方法

    
    
    public ResAttrDecoder getAttrDecoder()
      {
        return this.mAttrDecoder;
      }

return了一个ResAttrDecoder对象

    
    
    attrDecoder.setCurrentPackage((ResPackage)resTable.listMainPackages().iterator().next());

  
接着attrDecoder调用了setCurrentPackage方法，拿到了一个ResPackage对象![image.png](https://image.3001.net/images/20180725/15325056978294.png!small)

    
    
    generatePublicXml(pkg, out, xmlSerializer);

最后解析的结果就是![image.png](https://image.3001.net/images/20180725/15325057214820.png!small)

## 总结

SharkApktool在进行编码的时候，对所有程序可能暂停的地方进行了规避，降低了通过软件来对apk进行保护的方式。

还有dex和Androidmanifist的解析模式是相同的。并且解析dex是调用了baksmali进行解析的，有兴趣也可以对baksmali进行解析。

# 4\. 简介版

代码可能看起来脑壳痛，所以这里用freeMind做了一个简洁版，当然不是完整版，有兴趣可以扩充

## 总览

  
![image.png](https://image.3001.net/images/20180725/15325057366468.png!small)  

## 细分

  
![image.png](https://image.3001.net/images/20180725/15325057415424.png!small)![image.png](https://image.3001.net/images/20180725/15325057456584.png!small)![image.png](https://image.3001.net/images/20180725/1532505749249.png!small)

  

[有问题大家可以留言哦~也欢迎大家到春秋论坛中来玩耍呢！
]()[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  

