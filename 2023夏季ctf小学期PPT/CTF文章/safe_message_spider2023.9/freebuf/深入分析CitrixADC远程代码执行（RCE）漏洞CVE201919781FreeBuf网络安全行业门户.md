![](https://image.3001.net/images/20200215/1581759908_5e47bda41b197.png!small)

**2019年年底，Citrix ADC和Citrix
Gateway被曝出存在远程代码执行的高危漏洞CVE-2019-19781，该漏洞最吸引人的地方在于，未授权的攻击者可以利用它入侵控制Citrix设备，并实现进一步的内网资源访问获取。漏洞由安全团队Positive
Technologies 和 Paddy Power Betfair发现上报，但在漏洞公告中却未给出过多的漏洞利用方式，因此，这是值得来深入研究的地方。**

## 漏洞分析

虽然在Citrix官方的漏洞公告中未透露出漏洞利用细节，但从[其中的漏洞缓解措施](https://support.citrix.com/article/CTX267679)中，却侧面揭露了该漏洞的相关类型：

![](https://image.3001.net/images/20200215/1581759047_5e47ba479c4d0.png!small)

从上述缓解措施信息中，我们判断漏洞可能存在的路径为/vpns/，且有可能是一个目录遍历漏洞。有了这些线索，我们开始在httpd.conf文件中去寻找路径/vpns的定义方法，之后发现NetScaler::Portal::Handler
Perl Module (Handler.pm)模块在/vpn/portal/scripts/目录下负责生成了一些方法定义。

![](https://image.3001.net/images/20200215/1581759352_5e47bb7853a15.png!small)

/vpn/portal/scripts/下包含了一些脚本文件，由于前期我们判断漏洞起因是目录遍历，因此我们把分析重点放到了那些具备文件写操作的代码路径上。之后，我们在perl模块中的UsersPrefs脚本中发现了以下代码：

    
    
    sub csd {
    
    my $self = shift;
    
    my $skip_read = shift || "";
    
    # Santity Check
    
    my $cgi = new CGI;
    
    print "Content-type: text/html\n\n";
    
    // Username variable initialized by the NSC_USER HTTP Header
    
    my $username = Encode::decode('utf8', $ENV{'HTTP_NSC_USER'}) || errorpage("Missing NSC_USER header.”); <- MARK THIS
    
    $self->{username} = $username;
    
    ...
    
    $self->{session} = %session;
    
    // Constructing the path from the username.
    
    $self->{filename} = NetScaler::Portal::Config::c->{bookmark_dir} . Encode::encode('utf8', $username) . '.xml’;
    
    if($skip_read eq 1) {
    
    return;
    
    }

简言之，上述代码用于从用户相关的NSC_USER
HTTP头中构建一条路径，但是在过程中却缺乏任何安全校验措施，结果导致可用任意调用csd方法的脚本去触发目录遍历漏洞。经分析发现，/vpn/portal/scripts/下的所有脚本都会调用csd方法函数，但其中一个脚本文件newbm.pl比较特别：

    
    
    my $cgi = new CGI;
    
    print "Content-type: text/html\n\n";
    
    my $user = NetScaler::Portal::UserPrefs->new();
    
    my $doc = $user->csd();
    
    ...
    
    my $newurl = Encode::decode('utf8', $cgi->param('url'));
    
    my $newtitle = Encode::decode('utf8', $cgi->param('title'));
    
    my $newdesc = Encode::decode('utf8', $cgi->param('desc'));
    
    my $UI_inuse = Encode::decode('utf8', $cgi->param('UI_inuse'));
    
    ...
    
    my $newBM = { url => $newurl,
    
    title => $newtitle,
    
    descr => $newdesc,
    
    UI_inuse => $UI_inuse,
    
    };
    
    ...

newbm.pl会首先创建一个包含各种参数信息的数组，之后，又会调用filewrite方法把数组中的信息写入到一个XML文件中：

    
    
    if ($newBM->{url} =~ /^\/){
    
    push @{$doc->{filesystems}->{filesystem}}, $newBM;
    
    } else { # bookmark
    
    push @{$doc->{bookmarks}->{bookmark}}, $newBM;
    
    }
    
    // Writing XML file to disk
    
    $user->filewrite($doc);

按理来说，我们可以通过构造一些写入命令去控制文件路径或XML中内容，但是，在这里一切都不管用。之后，我们看了安全研究者Craig
Yong写的《关于CVE-2019-19781你需要知道的》，其中特别提到了可用Perl Template Toolkit模板工具实现漏洞利用。

深入研究后，我们发现可以在XML文件中插入一些特定的指令，如果这些指令被模板引擎解析，就能触发命令执行。以下就是模板引擎解析test.xml后发生命令执行的一个例子：

![](https://image.3001.net/images/20200215/1581759513_5e47bc19d64a9.png!small)

综上所述，现在我们有了Perl Template
Toolkit这种插入指令的文件写操作方法，但还需要一种方法让某个脚本去强制模板发生解析操作。之后，我们在模板的引用代码中发现Handler.pm可以被用来实现模板解析：

![](https://image.3001.net/images/20200215/1581759541_5e47bc35ed902.png!small)

其中的变量 $tmplfile是从HTTP Request
Path中构建的，而且之后为了处理这个$tmplfile变量文件，还会生成一个新的模板。现在，将我们之前创建的test.xml测试文件放到模板目录下，触发模板解析行为看看：

![](https://image.3001.net/images/20200215/1581759552_5e47bc40f0413.png!small)

总结来看，为了成功漏洞利用需要进行以下步骤：

> 1、通过模板机制发现执行Perl代码的方式（需要绕过）；
>
> 2、利用目录遍历方式，在模板目录下放入一个经过构造的XML文件；
>
> 3、浏览放入的XML文件，触发模板解析，实现XML中的代码执行。

重点在于最后一步的任意代码执行，在原本默认的Citrix配置中，是不能实现代码执行的，只有经过一个特性配置才能实现Perl代码执行。先前考虑到受漏洞影响的Citrix设备数量，且已有多个团队已经把该漏洞武器化，因此我们没有提供针对该漏洞的利用代码，但后续随着漏洞的披露以及多个安全研究者的exploit公开，我们也选择了公布具体的漏洞利用方法。

## 第一种方法：模板注入可导致的远程代码执行

这里有两种方法可以实现代码执行，第一种也就是目前大多数公开exploit中使用的BLOCK模板注入方法。我们通过在Perl Template
Toolkit的GitHub中，发现了这个被其他用户提交的bug，而正是这个bug可被在此进行利用：

![](https://image.3001.net/images/20200215/1581759596_5e47bc6c43a18.png!small)

bug问题中介绍执行任意perl代码的方法，目前看似所有公开的exploit中都使用了这种方法，实现了上述漏洞中的任意命令执行，我们再来深入看看这种利用方法在漏洞中的具体实现。

根据Perl Template
Toolkit的文档描述可知，模板变量是一个特殊变量，且在调用处理过程中会包含一个指向主模板的对象引用，这里的对象类型可以通过print方法打印显示，为Template::Document：

![](https://image.3001.net/images/20200215/1581759626_5e47bc8a14023.png!small)

有了这个对象引用之后，就可以用受控参数去调用方法。通过研究其中的类class代码，我们发现可以综合上述特性成功去调用new方法：

    
    
    # new(\%document)
    
    #
    
    # Creates a new self-contained Template::Document object which
    
    # encapsulates a compiled Perl sub-routine, $block, any additional
    
    # BLOCKs defined within the document ($defblocks, also Perl sub-routines)
    
    # and additional $metadata about the document.
    
    #------------------------------------------------------------------------    
    sub new {
    
    my ($class, $doc) = @_;
    
    my ($block, $defblocks, $variables, $metadata) = @$doc{ qw( BLOCK DEFBLOCKS VARIABLES METADATA ) };
    
    $defblocks ||= { };
    
    $metadata ||= { };
    
    # evaluate Perl code in $block to create sub-routine reference if necessary
    
    unless (ref $block) {
    
    local $SIG{__WARN__} = \&catch_warnings;
    
    $COMPERR = '';
    
    # DON'T LOOK NOW! - blindly untainting can make you go blind!
    
    $block = each %{ { $block => undef } } if ${^TAINT}; #untaint
    
    $block = eval $block;
    
    return $class->error($@)
    
    unless defined $block;
    
    }

该new方法可以获取BLOCK模板中的参数并调用eval方法，由此实现任意的perl代码执行。此外，我们还发现用另一个方法component
，也可以实现同样的攻击效果。

![](https://image.3001.net/images/20200215/1581759703_5e47bcd731e01.png!small)

## 第二种方法：DATAFILE插件中的命令注入

在对源代码的方法调用安全分析中，我们发现了DATAFILE插件中的以下代码：

    
    
    sub new {
    
    my ($class, $context, $filename, $params) = @_;
    
    my ($delim, $line, @fields, @data, @results);
    
    my $self = [ ];
    
    local *FD;
    
    local $/ = "\n";
    
    $params ||= { };
    
    $delim = $params->{'delim'} || ':';
    
    $delim = quotemeta($delim);
    
    return $class->fail("No filename specified")
    
    unless $filename;
    
    open(FD, $filename)
    
    || return $class->fail("$filename: $!");
    
    # first line of file should contain field definitions
    
    while (! $line || $line =~ /^#/) {
    
    $line = <FD>;
    
    chomp $line;
    
    $line =~ s/\r$//;
    
    }sub new {
    
    my ($class, $context, $filename, $params) = @_;
    
    my ($delim, $line, @fields, @data, @results);
    
    my $self = [ ];
    
    local *FD;
    
    local $/ = "\n";
    
    $params ||= { };
    
    $delim = $params->{'delim'} || ':';
    
    $delim = quotemeta($delim);
    
    return $class->fail("No filename specified")
    
    unless $filename;
    
    open(FD, $filename)
    
    || return $class->fail("$filename: $!");
    
    # first line of file should contain field definitions
    
    while (! $line || $line =~ /^#/) {
    
    $line = <FD>;
    
    chomp $line;
    
    $line =~ s/\r$//;
    
    }

如果你具备perl代码审计经验，就会了解使用上述只有两个参数的open函数来打开文件进行操作是不安全的。如果加上管道命令 |
后，open函数将会把它的其余部分解释为命令调用，加之由于我们可以控制文件名变量$filename，所以可以用这种方法来实现命令执行。

通过构造一个模板文件，在调用了 DATAFILE 插件后，就可导致任意命令执行，如下：

![](https://image.3001.net/images/20200215/1581759760_5e47bd108456c.png!small)

可以看到构造文件中的命令成功创建了预想的/tmp/COMMAND_INJECTION/目录：

![](https://image.3001.net/images/20200215/1581759772_5e47bd1ce3083.png!small)

该漏洞被相继发现披露后出现了各种exploit，但如Craig Yong在文章中说到的“需要注意的是，某些Payload会导致Citrix
NetScaler过度记录错误，直到它填满/var分区”。大家可[点此获取](https://gist.github.com/0x09AL/48c759855b2213a57acafe8c517bc788)Exploit漏洞利用代码。

## 漏洞修复

目前，Citrix公布了[详细的漏洞缓解措施](https://support.citrix.com/article/CTX267679)，其中包含了具体的执行步骤，我们建议Citrix
ADC用户及时参照该项措施进行修复。

此外，在针对设备发起的外界POST请求中，如果其中涉及到“/vpns/” and
“/../”样式的字符串，且之后跟着一个对xml文件的GET请求，那么就可以直接把它判断为漏洞利用的攻击行为了。

 ***参考来源：[mdsec](https://www.mdsec.co.uk/2020/01/deep-dive-to-citrix-adc-remote-code-execution-cve-2019-19781/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

