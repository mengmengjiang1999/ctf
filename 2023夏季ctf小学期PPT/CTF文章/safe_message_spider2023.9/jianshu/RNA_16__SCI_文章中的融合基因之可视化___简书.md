RNA 16. SCI 文章中的融合基因之可视化

[ 桓峰基因](https://www.jianshu.com/u/90066456ace6)关注赞赏支持

# RNA 16. SCI 文章中的融合基因之可视化

## 前言

上期我们聊了一下数据库，可以直接使用，但是有的时候我们还是需要对新数据进行融合基因的检测，一般来说 RNA 和 DNA
都可以做融合的检测，但是为什么官方更倾向基于 RNA 进行融合检测呢？

## 一、 融合基因检测

我们先看融合基因示意图，例子选择的是血液病的融合基因 BCR-ABL，该融合是由于 9，22号染色体的易位，导致疾病的发生。

基因融合常见的三种发生机制：

1）Chromosomal
Translocation，染色体易位。如下图A中1号和2号染色体上的两片段发生交叉互换，导致1号染色体上的浅绿色基因与2号染色体上的橘黄色基因融合到一起；

2）Interstitial
deletion，中间缺失。如下图中，3号染色体上的橘黄色基因和浅绿色基因之间的区段发生缺失（deletion），最终导致这两个基因融合到了一起；

3）Chromosomal
Inversion，染色体倒位。如下图4号染色体上的橘黄色基因到墨绿色基因之间的片段发生倒位，最终导致橘黄色基因和浅绿色基因融合到了一起。

## 二、 融合基因检测

基于高通量测序的融合基因检测主要包括以下三步：

* 先将reads通过STAR比对到参考基因组，筛选出split和discordant reads作为候选的融合基因序列；

* 将候选融合基因序列与参考基因序列进行比对，根据overlaps预测出融合基因；

* 对预测结果做过滤，去除假阳性结果。

我们这里选择 Aviv Regev 实验室开发的 STAR-Fusion 软件，主要是因为这款软件后续也开发了一些可视化的软件，方便我们讲解。

**1\. 下载测试的数据**

我们首先下次测试数据，这个 STAR-Fusion 检测融合基因从原始的paried-end Reads 开始分析，

    
    
    https://codeload.github.com/STAR-Fusion/STAR-Fusion-Tutorial/zip/refs/tags/v0.0.1

下载后，看下压缩包里面的文件，包括原始数据，测试的shell脚本以及基因组文件（.fa）和基因注释文件 (.gtf)

 **2\. 软件安装**

软件包安装两种方式，一种 git 之间安装，但是这种需要考虑网速，另一种就是下载本地自己安装，make一下既可以。

* #### Installing from GitHub Clone:
    
    
    %  git clone --recursive https://github.com/STAR-Fusion/STAR-Fusion.git

#### b. Downloading a STAR-Fusion Release (Preferred)

    
    
    Visit https://github.com/STAR-Fusion/STAR-Fusion/releases

下载之后解压 .tar.gz 文件, 进入目录，在 'make'，即可以完成安装。

####  **3\. 建立reference lib**

首先需要建立参考基因组对应的reference lib, 至少需要参考基因组对应的`fasta`文件和`gtf`文件，另外还可以提供已有的融合基因的注释等。

对于`human`和`mouse`而言，提供了已经构建好的文件，链接如下：

  * 

    
    
    https://data.broadinstitute.org/Trinity/CTAT_RESOURCE_LIB/

文件目录如下：

建库如下：

    
    
    FusionFilter/prep_genome_lib.pl \  --genome_fa ref_genome.fa \  --gtf ref_annot.gtf \  --fusion_annot_lib CTAT_HumanFusionLib.dat.gz \  --annot_filter_rule AnnotFilterRule.pm \  --pfam_db PFAM.domtblout.dat.gz

 **4\. 软件检测过程**

利用建好库，以及下载的fastq 文件既可以运行 STAR-Fusion，如下：

    
    
    cd testing/STAR-Fusion --left_fq reads_1.fq.gz --right_fq reads_2.fq.gz \               -O star_fusion_outdir \               --genome_lib_dir  /path/to/your/CTAT_resource_lib \               --verbose_level 2

 **5\. 结果输出**

    
    
    #FusionName           JunctionReadCount  SpanningFragCount  SpliceType           LeftGene                        LeftBreakpoint    RightGene                        RightBreakpoint   LargeAnchorSupport  FFPM        LeftBreakDinuc  LeftBreakEntropy  RightBreakDinuc  RightBreakEntropy  annotsTHRA--AC090627.1      27                 93                 ONLY_REF_SPLICE      THRA^ENSG00000126351.8          chr17:38243106:+  AC090627.1^ENSG00000235300.3     chr17:46371709:+  YES_LDAS            23875.8456  GT              1.8892            AG               1.9656             ["CCLE","FA_CancerSupp","INTRACHROMOSOMAL[chr17:8.12Mb]"]THRA--AC090627.1      5                  93                 ONLY_REF_SPLICE      THRA^ENSG00000126351.8          chr17:38243106:+  AC090627.1^ENSG00000235300.3     chr17:46384693:+  YES_LDAS            19498.6072  GT              1.8892            AG               1.4295             ["CCLE","FA_CancerSupp","INTRACHROMOSOMAL[chr17:8.12Mb]"]ACACA--STAC2          12                 52                 ONLY_REF_SPLICE      ACACA^ENSG00000132142.15        chr17:35479453:-  STAC2^ENSG00000141750.6          chr17:37374426:-  YES_LDAS            12733.7844  GT              1.9656            AG               1.9656             ["ChimerSeq","CCLE","Klijn_CellLines","FA_CancerSupp","INTRACHROMOSOMAL[chr17:1.60Mb]"]RPS6KB1--SNF8         10                 43                 ONLY_REF_SPLICE      RPS6KB1^ENSG00000108443.9       chr17:57970686:+  SNF8^ENSG00000159210.5           chr17:47021337:-  YES_LDAS            10545.1651  GT              1.3753            AG               1.8323             ["Klijn_CellLines","FA_CancerSupp","ChimerSeq","CCLE","INTRACHROMOSOMAL[chr17:10.95Mb]"]TOB1--SYNRG           8                  30                 ONLY_REF_SPLICE      TOB1^ENSG00000141232.4          chr17:48943419:-  SYNRG^ENSG00000006114.11         chr17:35880751:-  YES_LDAS            7560.6844   GT              1.4566            AG               1.8892             ["FA_CancerSupp","CCLE","INTRACHROMOSOMAL[chr17:12.97Mb]"]VAPB--IKZF3           4                  46                 ONLY_REF_SPLICE      VAPB^ENSG00000124164.11         chr20:56964573:+  IKZF3^ENSG00000161405.12         chr17:37934020:-  YES_LDAS            9948.269    GT              1.9656            AG               1.7819             ["FA_CancerSupp","Klijn_CellLines","CCLE","ChimerSeq","ChimerPub","INTERCHROMOSOMAL[chr20--chr17]"]ZMYND8--CEP250        2                  44                 ONLY_REF_SPLICE      ZMYND8^ENSG00000101040.15       chr20:45852970:-  CEP250^ENSG00000126001.11        chr20:34078463:+  NO_LDAS             9152.4075   GT              1.8295            AG               1.8062             ["FA_CancerSupp","CCLE","ChimerSeq","INTRACHROMOSOMAL[chr20:11.74Mb]"]AHCTF1--NAAA          3                  38                 ONLY_REF_SPLICE      AHCTF1^ENSG00000153207.10       chr1:247094880:-  NAAA^ENSG00000138744.10          chr4:76846964:-   YES_LDAS            8157.5805   GT              1.7232            AG               1.8062             ["FA_CancerSupp","CCLE","INTERCHROMOSOMAL[chr1--chr4]"]VAPB--IKZF3           1                  46                 ONLY_REF_SPLICE      VAPB^ENSG00000124164.11         chr20:56964573:+  IKZF3^ENSG00000161405.12         chr17:37922746:-  NO_LDAS             9351.3729   GT              1.9656            AG               1.9329             ["FA_CancerSupp","Klijn_CellLines","CCLE","ChimerSeq","ChimerPub","INTERCHROMOSOMAL[chr20--chr17]"]VAPB--IKZF3           1                  46                 ONLY_REF_SPLICE      VAPB^ENSG00000124164.11         chr20:56964573:+  IKZF3^ENSG00000161405.12         chr17:37944627:-  NO_LDAS             9351.3729   GT              1.9656            AG               1.8892             ["FA_CancerSupp","Klijn_CellLines","CCLE","ChimerSeq","ChimerPub","INTERCHROMOSOMAL[chr20--chr17]"]STX16--RAE1           4                  33                 ONLY_REF_SPLICE      STX16^ENSG00000124222.17        chr20:57227143:+  RAE1^ENSG00000101146.8           chr20:55929088:+  YES_LDAS            7361.719    GT              1.9899            AG               1.9656             ["FA_CancerSupp","CCLE","INTRACHROMOSOMAL[chr20:1.27Mb]"]AHCTF1--NAAA          1                  38                 ONLY_REF_SPLICE      AHCTF1^ENSG00000153207.10       chr1:247094431:-  NAAA^ENSG00000138744.10          chr4:76846964:-   NO_LDAS             7759.6498   GT              1.9086            AG               1.8062             ["FA_CancerSupp","CCLE","INTERCHROMOSOMAL[chr1--chr4]"]STX16-NPEPL1--RAE1    4                  24                 INCL_NON_REF_SPLICE  STX16-NPEPL1^ENSG00000254995.4  chr20:57227143:+  RAE1^ENSG00000101146.8           chr20:55929088:+  YES_LDAS            5571.0306   GT              1.9899            AG               1.9656             INTRACHROMOSOMAL[chr20:1.27Mb]RAB22A--MYO9B         6                  11                 ONLY_REF_SPLICE      RAB22A^ENSG00000124209.3        chr20:56886178:+  MYO9B^ENSG00000099331.9          chr19:17256207:+  YES_LDAS            3382.4115   GT              1.6895            AG               1.9656             ["FA_CancerSupp","ChimerSeq","CCLE","INTERCHROMOSOMAL[chr20--chr19]"]MED1--ACSF2           4                  11                 ONLY_REF_SPLICE      MED1^ENSG00000125686.7          chr17:37595418:-  ACSF2^ENSG00000167107.8          chr17:48548389:+  YES_LDAS            2984.4807   GT              1.9656            AG               1.9656             ["FA_CancerSupp","CCLE","INTRACHROMOSOMAL[chr17:10.90Mb]"]MED13--BCAS3          2                  12                 ONLY_REF_SPLICE      MED13^ENSG00000108510.5         chr17:60129898:-  BCAS3^ENSG00000141376.16         chr17:59469338:+  YES_LDAS            2785.5154   GT              1.5546            AG               1.9086             ["FA_CancerSupp","CCLE","INTRACHROMOSOMAL[chr17:0.55Mb]"]MED1--STXBP4          1                  15                 ONLY_REF_SPLICE      MED1^ENSG00000125686.7          chr17:37607291:-  STXBP4^ENSG00000166263.9         chr17:53218671:+  NO_LDAS             3183.4461   GT              1.3996            AG               1.7968             ["CCLE","FA_CancerSupp","Klijn_CellLines","INTRACHROMOSOMAL[chr17:15.44Mb]"]MED13--BCAS3          1                  12                 ONLY_REF_SPLICE      MED13^ENSG00000108510.5         chr17:60129898:-  BCAS3^ENSG00000141376.16         chr17:59465979:+  NO_LDAS             2586.55     GT              1.5546            AG               0.8366             ["FA_CancerSupp","CCLE","INTRACHROMOSOMAL[chr17:0.55Mb]"]STARD3--DOK5          2                  7                  ONLY_REF_SPLICE      STARD3^ENSG00000131748.11       chr17:37793484:+  DOK5^ENSG00000101134.7           chr20:53259997:+  NO_LDAS             1790.6885   GT              1.8892            AG               1.9656             ["FA_CancerSupp","CCLE","INTERCHROMOSOMAL[chr17--chr20]"]DIDO1--TTI1           1                  10                 ONLY_REF_SPLICE      DIDO1^ENSG00000101191.12        chr20:61569148:-  TTI1^ENSG00000101407.8           chr20:36642259:-  NO_LDAS             2188.6192   GT              1.6402            AG               1.9329             ["FA_CancerSupp","ChimerSeq","CCLE","INTRACHROMOSOMAL[chr20:24.85Mb]"]DIDO1--TTI1           1                  10                 ONLY_REF_SPLICE      DIDO1^ENSG00000101191.12        chr20:61569148:-  TTI1^ENSG00000101407.8           chr20:36634799:-  NO_LDAS             2188.6192   GT              1.6402            AG               1.8892             ["FA_CancerSupp","ChimerSeq","CCLE","INTRACHROMOSOMAL[chr20:24.85Mb]"]BRD4--RFX1            1                  8                  ONLY_REF_SPLICE      BRD4^ENSG00000141867.13         chr19:15443101:-  RFX1^ENSG00000132005.4           chr19:14109129:-  NO_LDAS             1790.6884   GT              1.9086            AG               1.8892             ["CCLE","FA_CancerSupp","INTRACHROMOSOMAL[chr19:1.23Mb]"]BRD4--RFX1            1                  8                  ONLY_REF_SPLICE      BRD4^ENSG00000141867.13         chr19:15443101:-  RFX1^ENSG00000132005.4           chr19:14094407:-  NO_LDAS             1790.6884   GT              1.9086            AG               1.8295             ["CCLE","FA_CancerSupp","INTRACHROMOSOMAL[chr19:1.23Mb]"]TRPC4AP--MRPL45       1                  8                  ONLY_REF_SPLICE      TRPC4AP^ENSG00000100991.7       chr20:33665849:-  MRPL45^ENSG00000174100.5         chr17:36478009:+  NO_LDAS             1790.6884   GT              1.6895            AG               1.9086             ["CCLE","Klijn_CellLines","FA_CancerSupp","INTERCHROMOSOMAL[chr20--chr17]"]

## 三、 可视化

基于STAR-Fusion结果，通过配套的FusionInspector进行过滤及整合；

    
    
    FusionInspector  --fusions Sam_fusionList.txt \-O Sample  --genome_lib genome/genome \--left_fq clean/Sam.R1.fq.gz   --right_fq  clean/Sam.R2.fq.gz \--out_prefix finspector test --vis #输出可视化文件

获得输出文件：

    
    
    finspector.fa : the candidate fusion-gene contigsfinspector.bed : the reference gene structure annotations for fusion partnersfinspector.junction_reads.bam : alignments of the breakpoint-junction supporting reads.finspector.spanning_reads.bam : alignments of the breakpoint-spanning paired-end reads.

## 1、 IGV

IGV的使用网上有很多说明，有机会再给大家分享，IGV 输入文件包括：

* reference file (.fa)：也就是参考基因组文件;
* bed file (.bed)：参考基因结构注释文件; 
* bam file (.bam)：过滤后的比对文件。

如下官网说明：

    
    
    finspector.fa : the candidate fusion-gene contigsfinspector.bed : the reference gene structure annotations for fusion partnersfinspector.junction_reads.bam : alignments of the breakpoint-junction supporting reads.finspector.spanning_reads.bam : alignments of the breakpoint-spanning paired-end reads.

##

IGV 显示出来结果还是很特别的效果，但是可以看到是两个基因的融合，如下：

## 2、 chimeraviz

Bioconductor 包 chimeraviz 嵌合RNA可视化，一个自动整合RNA数据和已知基因组特征的可视化框架对于结果的检验是有帮助的。

2017年发布的一个 bioconductor 包，chimeraviz 就可以做到自动创建嵌合RNA 可视化。官网教程，直接在 bioconductor
可以看到详细说明，下载安装好该R包后，自带一系列的融合基因可视化的测试数据。

    
    
    https://bioconductor.org/packages/release/bioc/html/chimeraviz.html | HTML | R Script |

可以看到，所支持的9种融合基因检测工具的示例结果都在这里了，比如我最喜欢的 star-fusion 的结果节选如下：

    
    
    [1] "5267readsAligned.bam"                                                [2] "5267readsAligned.bam.bai"                                            [3] "aeron_fusion_support.txt"                                            [4] "aeron_fusion_transcripts.fa"                                         [5] "chimericJunctions_MCF-7.txt"                                         [6] "defuse_833ke_results.filtered.tsv"                                   [7] "ericscript_SRR1657556.results.total.tsv"                             [8] "fusion5267and11759reads.bam"                                         [9] "fusion5267and11759reads.bam.bai"                                    [10] "fusion5267and11759reads.bedGraph"                                   [11] "fusioncatcher_833ke_final-list-candidate-fusion-genes.txt"          [12] "FusionMap_01_TestDataset_InputFastq.FusionReport.txt"               [13] "Homo_sapiens.GRCh37.74.sqlite"                                      [14] "Homo_sapiens.GRCh37.74_subset.gtf"                                  [15] "infusion_fusions.txt"                                               [16] "jaffa_results.csv"                                                  [17] "oncofuse.outfile"                                                   [18] "PRADA.acc.fusion.fq.TAF.tsv"                                        [19] "protein_domains_5267.bed"                                           [20] "reads.1.fq"                                                         [21] "reads.2.fq"                                                         [22] "reads_supporting_defuse_fusion_5267.1.fq"                           [23] "reads_supporting_defuse_fusion_5267.2.fq"                           [24] "soapfuse_833ke_final.Fusion.specific.for.genes"                     [25] "squid_hcc1954_sv.txt"                                               [26] "star-fusion.fusion_candidates.final.abridged.txt"                   [27] "star-fusion.fusion_predictions.abridged.annotated.coding_effect.tsv"[28] "UCSC.HG19.Human.CytoBandIdeogram.txt"                               [29] "UCSC.HG38.Human.CytoBandIdeogram.txt"                               [30] "UCSC.MM10.Mus.musculus.CytoBandIdeogram.txt"

## 3、 Circos

经典的Circos,可以清晰的展示染色体间和染色体内的基因的融合，我们这里同样使用 star-fusion 软件的结果，如下：

    
    
    starFusion <- system.file(  "extdata",  "star-fusion.fusion_candidates.final.abridged.txt",  package = "chimeraviz")fusions <- import_starfusion(starFusion, "hg38", 10)plot_circle(fusions)

红色条带-染色体内融合，蓝色条带-染色体间融合，如下：

## 融合基因绘制

软件包 chimeraviz 自带绘图函数 plot_fusion，可以多角度的实现绘制融合基因，如下：

    
    
    defuse833ke <- system.file("extdata", "defuse_833ke_results.filtered.tsv",  package = "chimeraviz")fusion5267and11759reads  <- system.file("extdata",  "fusion5267and11759reads.bam",  package = "chimeraviz")fusions <- import_defuse(defuse833ke, "hg38")fusion <- get_fusion_by_gene_name(fusions,"RCC1")fusion <- get_fusion_by_id(fusions, 5267)edbSqliteFile <- system.file("extdata",  "Homo_sapiens.GRCh37.74.sqlite",  package="chimeraviz")count <- system.file("extdata","fusion5267and11759reads.bedGraph", package="chimeraviz")edb <- ensembldb::EnsDb(edbSqliteFile)plot_fusion(fusion,#bamfile = fusion5267and11759reads ,            edb = edb,non_ucsc = T,            reduce_transcripts = T,bedgraphfile = count)

我们看到每种展示方式各有利弊，

1.IGV+FusionInspector：步骤繁琐，文件冗余较多；展示结果清晰明了；

2.chimeraviz ：自定义创建数据库文件有限制；支持多种融合分析内容输入，结果可视化类型丰富；

3.Circos：文件整理和conf比较繁琐；可视化结果自定义化程度高，较为美观。

利用了两期内容来阐述基于 RNA-seq 检测融合基因以及 SCI
文章中的一般展示方法，所以转录组的数据出来表达大家很熟悉之外，融合基因的分析也可以考虑分析一下，也许有意外的收获！

关注公众号桓峰基因，每日更新，扫码进群交流不停歇，马上就出视频版，关注我，您最佳的选择！

 **References:**

* Haas B J , Dobin A , Li B , et al. Accuracy assessment of fusion transcript detection via read-mapping and de novo fusion transcript assembly-based methods[J]. Genome Biology, 2019, 20(1):1-16.

* Lågstad S, Zhao S, Hoff AM, Johannessen B, Lingjærde OC, Skotheim RI. chimeraviz: a tool for visualizing chimeric RNA. Bioinformatics. 2017;33(18):2954-2956.

> 本文使用 [文章同步助手](https://www.jianshu.com/p/5709df6fb58d) 同步

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [RNA 15. SCI 文章中的融合基因之 FusionGDB2](https://www.jianshu.com/p/398c83306b98)

基于 RNA 数据分析1-13期基本介绍完成，而基因融合同样也是转录组测序中能够获得的对于临床上非常有意义的数据，...

[桓峰基因](https://www.jianshu.com/u/90066456ace6)阅读 574评论 0赞 5

  * [结构变异SV分析(WGS/WES)和融合基因检测（RNA）](https://www.jianshu.com/p/9fe9e89246b7)

69种工具检测SV对比 https://www.jianshu.com/p/85ff211b4b4e[https...

[wo_monic](https://www.jianshu.com/u/64dfb67befe7)阅读 3,333评论 0赞 7

  * [融合基因学习笔记](https://www.jianshu.com/p/63b18075aa18)

概述 融合基因是指两个基因的全部或部分序列融合而成的嵌合基因，一般由染色体易位、缺失等原因所致。融合基因首次发现于...

[shannonnana](https://www.jianshu.com/u/aaf52d96013d)阅读 19,550评论 7赞 25

  * [RNA-seq融合检测软件](https://www.jianshu.com/p/6b9854459428)

STAR-Fusion 地址：Home · STAR-Fusion/STAR-Fusion Wiki · GitH...

[能坚持更新吗](https://www.jianshu.com/u/cca08dd16151)阅读 2,100评论 0赞 5

  * [最全的RNA-seq工具比较文章，以及RNACocktail分析流程](https://www.jianshu.com/p/15876147919a)

Sahraeian, Sayed Mohammad Ebrahim, et al. "Gaining compre...

[小白要变大神](https://www.jianshu.com/u/00f46fc128ce)阅读 1,869评论 1赞 9

 