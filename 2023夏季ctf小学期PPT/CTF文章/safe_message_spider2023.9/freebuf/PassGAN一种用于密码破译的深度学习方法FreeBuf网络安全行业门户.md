III．GAN的构造和参数

利用GAN的能力有效的评估训练集包含的口令的概率分布。我们实验了一些参数。在这一部分，我们讲解GANs在具体构架和参数方面的选择。

我们通过Gulraiani团队的IWGAN（Improved training of Wasserstein
GANs）[27]把PassGAN实例化。本论文中贯彻实施的IWGAN通过 ADAM优化器[34]尽量介绍训练误差，即，减少模块输出和训练数据之间的不匹配。

我们的模块用下面的超参数作为特征：

l Batch size，代表训练集包含的密码的数量，优化器的每一步中，训练集所含的密码都是通过GAN传播的。

l Number of
iterations,它表示GAN调用前向传播和反向传播的次数[38],[37]。在每次迭代过程中，GAN运行一个生成器迭代器以及一个或多个鉴别器迭代器。

l Number of discriminator iterations per generator
iteration，它表示生成器在每一个GAN迭代器中的迭代次数。

l Model dimensionality，它代表每个卷积层的维数（权重）。

l Gradient penalty
coefficient（λ），它指定应用于鉴别器关于输入梯度的规范的惩罚[27]。添加这个参数会使GAN的训练更加稳定[27]。

l Output sequence length，它表示生成器生成的字符串的最大值（G以后）。

l Size of the input noise vector(seed)，它决定生成一个样例，需要多少随机比特位作为G的输入。

l Maximum number of examples，它表示训练项目负荷的最大数量（在PassGAN中的密码）

l Adam optimizer’shyper-parameters:

n Learning rate，即，如何快速调整模型的权重。

n Coefficient β1，它指明梯度运行的平均衰减速率。

n Coefficient β2，它表明表明梯度平方的平均衰减率。

我们实例化了我们的模型，batch的大小是64。我们用不同的迭代次数训练GAN，最终会解决了199,000次迭代。随着匹配次数的增加，进一步的迭代会提供逐渐缩小的返回（详见IV部分的分析）。每个生成迭代器会把鉴别器的迭代次数设定到10，这个值是IWGAN的默认值。我们的实验使用层生成器和鉴别器的5个剩余层，深度神经网络中的每一层有128个维度。

我们把gradient
penalty都设为10，还把GAN生成的序列长度从32个字符（IWGAN的默认长度）变为10个字符，从而可以匹配密码训练期间使用的的最大长度（详见IV-A部分）。GAN加载的最大实例的值被设定为整个训练数据集的大小。我们把噪声向量的大小设为128浮点数。

Adam优化器的系数β1和β2分别设为0.5和0.9，当学习率是10^-4时，这些参数就是Gulrajani团队的默认值[27]。

IV．评估

在这一部分，我们首先展示我们的训练和测试流程。然后，我们会对我们的实验结果进行报告，并把我们的实验中PassGAN的输出和通常用于JTR和HashCat的生成器规则进行比较。

我们的实验是利用IWGAN的TensorFlow实施的。我们用1.2.2版本的TensorFlow
GPU，和1.2.12版本Python。所有的实验都是运行Ubuntu16.04.2LTS的工作台上执行的，该工作台具有64G
RAM和12核2.0GHz英特尔Xeon CPU。以及NVIDA GeForce GTX 1080 Ti GPU。

A． GAN的训练和测试

要鉴定PassGAN的性能，并用它和最先进的密码生成规则做比较，首先，需要在RockYou泄露的一个大型密码集上对GAN,JTR和HashCat进行训练。进入这个数据集代表常见和复杂的密码的混合物，因为这些密码以明文形式存储在服务器上，因此他们都被恢复了。然后，我们会计算在两个独立的测试集中每一个工具生成的密码数量：一个RockYou的不同于训练集的子集，一个LinkedIn密码数据集[40]。

RockYou数据集包含332,603,388个密码。我们从大约3亿密码中选择所有长度小于等于10个字符的密码（29,599,680个密码，这些占据数据集得90.8%），并使用这些密码中的80%训练工具（总共23,679,744个密码，9,925,896个独特的密码）。我们用剩余的20%做测试（共5,919,936个密码，3,094,199个独特的密码）。

我们也会在LinkedIn数据集中所有的长度小于10
个字符的密码上测试每一个工具。这个数据集是由60,065,486个不同的密码组成的，因此，有43,354,871个不同的长度小于10个字节的密码（LinkedLn数据集中没有可用的频率计数）。LinkedIn的数据集中的密码可以作为哈希值，而不是明文。因此，LinkedIn数据集中只包含明文密码的工具，例如JTR和HashCat能够恢复。我们呈现在IV-B中的结果，表明用于恢复LinkecIn密码的规则和数据集基本上覆盖了用于这项工作的规则和数据集。

我们的研究和测试流程允许我们进行决定和相关测试：（1）在同样的密码分布中，PassGAN预测密码研究和测试工作做得有多好（如，把RockYou数据集用于训练和测试）；（2）PassGAN能否概括整个密码的数据集。即，当PassGAN在RockYou数据集研究以及在LinkedIn数据集测试时，会观测它是如何表现的。

GAN的训练过程对输出的影响。训练GAN是一个迭代过程，由大量的迭代次数组成。随着迭代次数的增加，GAN从数据分布中学习到更多的信息。然而，增加步数也增加了过度拟合的可能性[23],[76].要评估密码数据的权衡，我们存储中间训练检查点并在每一个检查点生成10^8个密码。

![1.png](https://image.3001.net/images/20180313/15209112252529.png!small)

图1：GAN生成的不重复的密码的个数，以及匹配到RockYou测试集的密码数量。X轴代表PassGAN的训练流程迭代次数的数量（检查点）。PassGAN在每一个检查点生成一个总量大约为10^8的密码。

图1表明在GAN的每一个检查点生成的唯一密码数，以及能与RockYou测试集中的内容匹配的密码数量。GAN生成的唯一样本数和迭代次数（检查点编号）几乎没有变化。然而，和测试集匹配的密码数量随着迭代数量稳步增长。这种增加会逐步减少至175.000~199,000次迭代，其中唯一密码的数量略有下降。该图指明迭代次数的进一步增加很可能导致过度拟合，从而降低GAN生成大量疑似密码的能力。因此，我们认为这种迭代范围对于我们的RockYou训练集而言是合适的。

REFERENCES

[1] M. Abadi, A. Chu, I. Goodfellow, H. B. McMahan, I.Mironov,K. Talwar, and
L. Zhang, “Deep learning with differential privacy,” in Proceedingsof the 2016
ACM SIGSAC Conference on Computer and Communications Security. ACM,2016, pp.
308–318.

[2] A. Abdulkader, A. Lakshmiratan, and J. Zhang. (2016)Introducing deeptext:
Facebook’s text understanding engine.
[Online].Available:https://tinyurl.com/jj359dv

[3]M.Arjovsky,S.Chintala,andL.Bottou,“Wasserstein
gan,”CoRR,vol.abs/1701.07875,2017.

[4] G. Ateniese, L. V. Mancini, A. Spognardi, A. Villani,D. Vitali, and G.
Felici, “Hacking smart machines with smarter ones: How toextract meaningful
data from machine learning classifiers,”International Journalof Security and
Networks, vol. 10, no. 3, pp. 137–150, 2015.

[5] D. Berthelot, T. Schumm, and L. Metz, “Began:Boundary
equilibriumgenerative adversarial networks,”arXiv preprint
arXiv:1703.10717,2017.

[6] H. Bidgoli, “Handbook of information
securitythreats,vulnerabilities,prevention, detection, and management
volume3,” 2006.

[7] L. Breiman, “Random forests,”Machine learning, vol.45, no. 1, pp.5–32,
2001.

[8] N. Carlini and D. Wagner, “Defensive distillation isnot robust to
adversarial examples,”arXiv preprint arXiv:1607.04311,2016.

[9] ——, “Adversarial examples are not easily detected:Bypassing tendetection
methods,”arXiv preprint arXiv:1705.07263, 2017.

[10] C. Castelluccia, M. D̈urmuth,and D. Perito, “Adaptive password-strength
meters from markov models.” In NDSS,2012.

[11] X. Chen, Y. Duan, R. Houthooft, J. Schulman, I.Sutskever, and P. Abbeel,
“Infogan: Interpretable representationlearning by information maximizing
generative adversarial nets,” in Advancesin Neural Information Processing
Systems, 2016, pp. 2172–2180.

[12] R. Collobert, J. Weston, L. Bottou, M. Karlen, K.Kavukcuoglu, and P.
Kuksa, “Natural language processing (almost) from scratch,”Journal of Machine
Learning Research, vol. 12, no. Aug,pp. 2493–2537, 2011.

[13] A. A. Cruz-Roa, J. E. A. Ovalle, A. Madabhushi, andF. A. G.Osorio, “A
deep learning architecture for imagerepresentation, visual interpretability
and automated basal-cell carcinomacancer detection,” in International
Conference on Medical Image Computing and Computer-AssistedIntervention.
Springer Berlin Heidelberg, 2013, pp. 403–410.

[14] M. Dell’Amico, P. Michiardi, and Y. Roudier,“Password strength: An
empirical analysis,” in INFOCOM, 2010 ProceedingsIEEE.IEEE,2010, pp. 1–9.

[15] E. L. Denton, S. Chintala, R. Fergus et al., “Deepgenerative image models
using a? laplacian pyramid of adversarial networks,” in Advances in neural
information processing systems, 2015,pp. 1486–1494.

[16] J. Donahue, L. A. Hendricks, S. Guadarrama, M.Rohrbach, S. Venugopalan,
K. Saenko, and T. Darrell, “Long-term recurrent convolutionalnetworks for
visual recognition and description,”2015 IEEE Conference onComputer Vision and
Pattern Recognition (CVPR), pp. 2625–2634,2015.

[17] B. Duc, S. Fischer, and J. Bigun, “Face authenticationwith gabor
information on deformable graphs,”IEEE Transactions on ImageProcessing,vol. 8,
no. 4, pp. 504–516, 1999.

[18] M. D̈urmuth, F.Angelstorf, C. Castelluccia, D. Perito, and C.
Abdelberi,“Omen: Faster passwordguessing using an ordered markov enumerator.”
In ESSoS. Springer, 2015, pp.119–132.

[19] R. Fakoor, F. Ladhak, A. Nazi, and M. Huber, “Usingdeep learning to
enhance cancer diagnosis and classification,” in The 30th International
Conference on Machine Learning(ICML 2013),WHEALTH workshop,2013.

[20] S. Fiegerman. (2017) Yahoo says 500 million
accountsstolen.[Online].Available:http://money.cnn.com/2016/09/22/technology/yahoo-data-breach/index.html

[21] M. Frank, R. Biedert, E. Ma, I. Martinovic, and D.Song, “Touchalytics:On
the applicability of touchscreen input as a behavioralbiometric for continuous
authentication,”IEEE transactions on informationforensics and security, vol.
8, no. 1, pp. 136–148, 2013.

[22] M. Fredrikson, S. Jha, and T. Ristenpart, “Modelinversion attacks that
exploit confidence information and basiccountermeasures,” in Proceedings of
the 22nd ACM SIGSAC Conference on Computerand Communications Security. ACM,
2015, pp. 1322–1333.

[23] I. Goodfellow, J. Pouget-Abadie, M. Mirza, B. Xu, D.Warde-Farley,S.
Ozair, A. Courville, and Y. Bengio, “Generativeadversarial nets,” in Advances
in neural information processing systems, 2014, pp. 2672–2680.

[24] Google DeepMind. (2016) Alphago, the first computerprogram to ever beat a
professional player at the game
ofGO.[Online].Available:https://deepmind.com/alpha-go

[25] A. Graves, “Generating sequences with recurrentneural networks,”arXiv
preprint arXiv:1308.0850, 2013.

[26] A. Graves, A.-r. Mohamed, and G. Hinton, “Speechrecognition with deep
recurrent neural networks,” in 2013 IEEE internationalconference on acoustics,
speech and signal processing.IEEE, 2013, pp.6645–6649.

[27] I. Gulrajani, F. Ahmed, M. Arjovsky, V. Dumoulin,and A. C.
Courville,“Improved training of wasserstein gans,”CoRR, vol.
abs/1704.00028,2017.

[28] HashCat. (2017). [Online]. Available:https://hashcat.net

[29] J. Hayes, L. Melis, G. Danezis, and E. D.Cristofaro, “LOGAN: Evaluating
privacy leakage of generative models usinggenerative adversarial
networks,”CoRR, vol. abs/1705.07663, 2017.

[30] W. He, J. Wei, X. Chen, N. Carlini, and D. Song,“Adversarial example
defenses: Ensembles of weak defenses are not strong,”arXivpreprint
arXiv:1706.04701, 2017.

[31] B. Hitaj, G. Ateniese, and F. Perez-Cruz, “Deepmodels under the
GAN:Information leakage from collaborative deeplearning,”CCS’17, 2017.

[32] P. G. Kelley, S. Komanduri, M. L. Mazurek, R. Shay,T. Vidas, L. Bauer,N.
Christin, L. F. Cranor, and J. Lopez, “Guess again (andagain and again):
Measuring password strength by simulating password-cracking algorithms,”in
Security and Privacy (SP), 2012 IEEE Symposium on.IEEE, 2012, pp. 523–537.

[33] T. Kim, M. Cha, H. Kim, J. Lee, and J. Kim,“Learning to discover cross-domain relations with generative adversarialnetworks,”arXiv preprint
arXiv:1703.05192, 2017.

[34] D. Kingma and J. Ba, “Adam: A method for stochastic
optimization,”arXivpreprint arXiv:1412.6980, 2014.

[35] J. Kos and D. Song, “Delving into adversarialattacks on deep
policies,”arXiv preprint arXiv:1705.06452, 2017.

[36] M. Lai, “Giraffe: Using deep reinforcement learningto play chess,”arXiv
preprint arXiv:1509.01549, 2015.

[37] Y. LeCun, B. Boser, J. Denker, D. Henderson, R.Howard, W. Hubbard,and L.
Jackel, “Handwritten digit recognition with aback-propagation network,” in
Advances in neural information processing systems2, NIPS 1989. Morgan Kaufmann
Publishers, 1990, pp. 396–404.

[38] Y. LeCun, B. Boser, J. S. Denker, D. Henderson, R.E. Howard,W. Hubbard,
and L. D. Jackel, “Backpropagation applied tohandwritten zip code
recognition,”Neural computation, vol. 1, no. 4, pp.541–551,1989.

[39] Y. LeCun, K. Kavukcuoglu, C. Farabet et al.,“Convolutional networks and
applications in vision.” In ISCAS, 2010, pp.253–256.

[40]LinkedIn.Linkedin.[Online].Available:https://hashes.org/public.php

[41] Y. Liu, X. Chen, C. Liu, and D. Song, “Delving intotransfer-
able adversarial examples and black-box attacks,”arXivpreprint
arXiv:1611.02770, 2016.

[42] J. Ma, W. Yang, M. Luo, and N. Li, “A study ofprobabilistic password
models,” in Security and Privacy (SP), 2014 IEEESymposium on.IEEE, 2014, pp.
689–704.

[43] P. McDaniel, N. Papernot, and Z. B. Celik, “Machinelearning in

adversarial settings,”IEEE Security & Privacy, vol.14, no. 3, pp. 68-72, 2016.

[44] W. Melicher, B. Ur, S. M. Segreti, S. Komanduri, L.Bauer,N. Christin, and
L. F. Cranor, “Fast, lean, and accurate:Modeling password guessability using
neural networks,” in 25thUSENIX Security Symposium (USENIX Security 16).
Austin, TX: USENIXAssociation,2016, pp. 175–191. [Online].
Available:https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/melicher

[45] C. Metz. (2016) Google’s GO victory is just aglimpse of how powerful ai
will be. [Online]. Available:https://tinyurl.com/l6ddhg9

[46] M. Mirza and S. Osindero, “Conditional generativeadversarial nets,”arXiv
preprint arXiv:1411.1784, 2014.

[47] V. Mnih, K. Kavukcuoglu, D. Silver, A. Graves, I.Antonoglou, D. Wierstra,
and M. A. Riedmiller, “Playing atari with deepreinforcement learning,”CoRR,
vol. abs/1312.5602, 2013.

[48] R. Morris and K. Thompson, “Password security: Acase
history,”Communications of the ACM, vol. 22, no. 11, pp. 594–597,1979.

[49] A. Narayanan and V. Shmatikov, “Fast dictionaryattacks on passwords using
time-space tradeoff,” in Proceedings of the 12th ACMconference on Computer and
communications security. ACM, 2005, pp. 364–372.

[50] Y. Pan, T. Mei, T. Yao, H. Li, and Y. Rui, “Jointlymodeling embedding and
translation to bridge video and language,”2016 IEEEConference on Computer
Vision and Pattern Recognition (CVPR), pp.4594–4602,2016.

[51] N.Papernot,P. McDaniel,and I.Goodfellow, “Transferabilityin machine
learning: from phenomena to black-box attacks using adversarial
samples,”arXivpreprint arXiv:1605.07277, 2016.

[52] N.Papernot,P.McDaniel,S. Jha,M.Fredrikson,Z.B.Celik, and A. Swami, “The
limitations of deep learning in adversarial settings,”InProceedings of the 1st
IEEE European Symposium on Security andPrivacy, 2015.

[53] N. Papernot, P. McDaniel, X. Wu, S. Jha, and A.Swami, “Distillation as a
defense to adversarial perturbations against deepneural networks,” in
Proceedings of the 37th IEEE Symposium on Security andPrivacy,2015.

[54] C. Percival and S. Josefsson, “The scryptpassword-based keyderivation
function,” Tech. Rep., 2016.

[55] S.Perez.(2017)Google plans to bring password-freelogins to android apps
by year-end.

[Online].Available:https://techcrunch.com/2016/05/23/google-plans-to-bring-password-free-logins-to-android-apps-by-year-end/

[56] H.P.Position Markov
Chains.(2017).[Online].Available:https://www.trustwave.com/Resources/SpiderLabs-Blog/Hashcat-Per-Position-Markov-Chains/

[57]T.P.Project.(2017).[Online].Available:http://thepasswordproject.com/leakedpasswordlists
and dictionaries

[58] N. Provos and D. Mazieres, “Bcrypt algorithm,” inUSENIX, 1999.

[59] A. Radford, L. Metz, and S. Chintala, “Unsupervisedrepresentation
learning with deepconvolutional generative adversarial networks,” in 4th
International Conferenceon Learning Representations, 2016.

[60] C. E. Rasmussen and C. K. Williams,Gaussianprocesses for machine
learning.MIT press Cambridge, 2006, vol. 1.

[61]RockYou.(2010)Rockyou.[Online]. Available:
http://downloads.skullsecurity.org/passwords/rockyou.txt.bz2

[62]H.Rules.(2017).[Online].Available:https://github.com/hashcat/hashcat/tree/master/rules

[63] J. T. R. K. Rules. (2017). [Online].
Available:http://contest-2010.korelogic.com/rules.html

[64] B. Sch ̈olkopf andA. J. Smola,Learning with kernels: support vector
machines, regularization,optimization, and beyond. MIT press, 2002.

[65] R. Shokri and V. Shmatikov, “Privacy-preserving deeplearning,” in
Proceedings of the 22nd ACM SIGSAC conference on computer andcommunications
security. ACM, 2015, pp. 1310–1321.

[66] R. Shokri, M. Stronati, C. Song, and V. Shmatikov,“Membership inference
attacks against machine learning models,” in Security andPrivacy (SP), 2017
IEEE Symposium on. IEEE, 2017, pp. 3–18.

[67] Z. Sitov ́a, J.ˇSedˇenka, Q. Yang, G. Peng, G. Zhou,P. Gasti, and K.
S.Balagani, “Hmog: New behavioral biometric features forcontinuous
authentication of smartphone users,”IEEE Transactions on InformationForensics
and Security, vol. 11, no. 5, pp. 877–892, 2016.

[68] T. SPIDERLABS. (2012) Korelogic-rules.
[Online].Available:https://github.com/SpiderLabs/KoreLogic-Rules

[69] I. Sutskever, J. Martens, and G. E. Hinton,“Generating text with
recurrent neural networks,” inProceedings of the 28th InternationalConference
on Machine Learning (ICML-11), 2011, pp. 1017–1024.

[70] Y. Taigman, M. Yang, M. Ranzato,and L. Wolf,“Deepface:Closing the gap to
human-level performance in face verification,”InProceedings of the 2014 IEEE
Conference on Computer Vision and Pattern Recognition, ser. CVPR
’14.Washington, DC, USA:IEEEComputer Society, 2014, pp. 1701–1708.[Online].
Available:http://dx.doi.org/10.1109/CVPR.2014.220

[71] J. the Ripper. (2017). [Online].Available:http://www.openwall.com/john/

[72] J. the Ripper Markov Generator.(2017).
[Online].Available:http://openwall.info/wiki/john/markov

[73] I. Tolstikhin, S. Gelly, O. Bousquet, C.-J.Simon-Gabriel, andB. Sch
̈olkopf,“Adagan: Boosting generative models,”arXiv preprint arXiv:1701.02386,
2017.

[74] F. Tram`er, F. Zhang, A. Juels, M. K. Reiter, and T.Ristenpart,
“Stealingmachine learning models via prediction apis.” In USENIX,2016.

[75] M. Weir, S. Aggarwal, B. De Medeiros, and B. Glodek,“Password cracking
using probabilistic context-free grammars,” in Security andPrivacy, 2009 30th
IEEESymposium on. IEEE, 2009, pp. 391–405.

[76] Y. Wu, Y. Burda, R. Salakhutdinov, and R. Grosse,“On the quantitative
analysis ofdecoder-based generative models,”arXiv preprint arXiv:1611.04273,
2016.

[77] V. Zantedeschi, M.-I. Nicolae, and A. Rawat,“Efficient defenses against
adversarial attacks,”arXiv preprintarXiv:1707.06728, 2017.

[78] H. Zhang, T. Xu, H. Li, S. Zhang, X. Huang, X. Wang,and D. Metaxas,

“Stackgan: Text to photo-realistic image synthesis withstacked generative
adversarial networks,”arXiv preprint arXiv:1612.03242, 2016.

[79] X. Zhang and Y. A. LeCun, “Text understanding fromscratch,”arXiv preprint
arXiv:1502.01710v5, 2016.

[80] Y. Zhong, Y. Deng, and A. K. Jain, “Keystrokedynamics for ser
uthentication,”in Computer Vision and Pattern RecognitionWorkshops (CVPRW),
2012 IEEE Computer Society Conference on. IEEE, 2012,pp.117–123.

*本文参考：PassGAN: A Deep Learning Approach for Password Guessing，丁牛网安实验室小编EVA编辑，如需转载请标明出处。  

