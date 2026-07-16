# 中文技术文档风格画像（手册／教程／参考文档）

**速览**：称读者「你」（或「您」，全文禁止混用），动词开头的指令式短句，一句一意，客观礼貌不推销。
结构走「概述→前提条件→任务步骤→示例→提示」；标题之间必有引导句，步骤前先说目的，Warning 留给不可逆操作。
模糊程度词换具体数字，方位词换标题指认；主引号一律直角引号「」，界面元素名称也用「」标注。

## 一、语气与称呼

- 对话式基调：平易近人、直截了当，推荐「你可以……」。对话式不等于口语化——口语的冗长啰嗦、缺乏逻辑要极力避免。
- 人称纪律：读者称「您」或「你」皆可，禁止混用；作者用「作者」「文档作者」等第三人称，不用「我」；「我们」可代称公司但少用。
- 指令式：每句尽量以动词开头，删掉多余的「你可以」；避免「there is/are」式弱说法。为什么：读者在照做，动词就是任务本身。
  > Replace「You can access Office apps across your devices, and you get online file storage and sharing.」With「Store files online, access them from all your devices, and share them with coworkers.」
- 客观礼貌：不用反问句（读者感觉被质疑和挑战）；不轻易用感叹句（仅用于可能永久性删除数据等强警示）；不轻易用「请」「抱歉」，除非真的对读者造成了困扰；不用「亲爱的」等过分亲切的称呼。
- 建议句式给直接主语：写「X 推荐……」，不写无主语的「建议进行……」「It is recommended…」。为什么：读者需要知道这是谁的立场、找谁负责。
  > （incorrect）…it is recommended to create multiple service accounts… →（correct）…Red Hat recommends creating multiple service accounts…
- 规范强度三档：「应／不应」＝规范性要求，须遵守；「宜」＝推荐，无充分理由须采纳；「可以」＝选择性。写规范类内容时用这三档表达强制力，不留模糊地带。
- 主动语态优先，阐述清楚主语和宾语；被动仅用于把关键词前置到标题或句首。
- 不拟人：软件没有情感与动作。
  > 「The tool complains when you try to build the output.」→「The tool produces errors when you try to build the output.」
- 模糊程度词换具体数据：
  > 「很好地提升了性能。」→「性能提升了 50% 或者延迟从 10ms 降为 1ms。」
- 报错文案给出路而非宣判：
  > Replace「Invalid ID」With「You need an ID that looks like this: someone@example.com」

## 二、结构惯例

- 首段概述：第一个标题之前的段落必须概述本页覆盖范围与读者读完能做到什么，让读者三十秒内判断「这页与我是否相关」。
- 教程/指南引言四件套：主题＋前置知识＋涉及的技术与 API（带链接）＋适用场景。
- 摘要用 What／How／Why(Who) 三问组织：这份文档是什么、怎么讲、为谁而写。
- 前提条件先行：把前置知识、环境要求、权限要求集中放在步骤之前，不让读者做到一半才发现缺东西。
- 标题之间必有引导句：一级与二级标题之间有引言内容，二级与三级之间有正文内容，禁止「标题接标题」的空壳结构。
- 任务步骤：带标题的有序列表；步骤建议 ≤7 个、最多不超过 9 个，过多则拆分任务；描述步骤前先说明这组步骤要达成的目的；界面切换处以切换时点为界拆分步骤。
- 用户导向补全：需要输入的信息给输入格式要求；报错信息给解决操作；提供错误码速查；改变系统状态的命令同时给功能、潜在风险及避免方式、撤销方法。
- 示例三明治：每个示例前有「做什么」概述，示例后（或穿插其中）有「怎么运作」解说；多示例页给每个示例一个短标题点明场景。
- 代码块纪律：注释置于被注释片段之前、克制精简，不以注释代替正文解释；执行结果另起一个代码块；命令输入/输出框内不混入说明文字（会被误当输出，翻译时也易漏）。
- note/warning 使用时机：Note＝补充信息；Important＝不可忽视的信息；Warning＝潜在破坏性后果（如文件被删除），告知后果并提醒充分了解后再执行。提示要简短、少用（多则失效）、不自造标题；中文提示 ≤4 行、不含表格和图形。
- 引用块与提示框只留给上面三类告示。项目定位、适用范围、成熟度声明这类叙述性信息不单独开引用块——它们是概述的一部分，有机融进概述段落的行文里；把陈述句装进引用块只会打断阅读流，并稀释真正警示信息的显著性。
- 段落：一段只有一个主题，中心句放段首统领全段，长度 50～200 字，避免单句成段；技术描述类主题先图表、后句子。
- 可用性测试：操作型文档写完后，让一位无技术背景的人照着做一遍；走不通，改的是文档不是读者。

## 三、句型库（按功能取用）

### 引言句型
> The Red Hat Satellite 5.6 API Guide is a full reference for Satellite's XMRPC API.（What：是什么）
> The guide explains each API method and demonstrates examples of data models for input and output.（How：怎么讲）
> This publication provides a basis for administrators and developers to write custom scripts and to integrate Red Hat Satellite with third-party applications.（Why/Who：为谁而写）
> The Apple Style Guide provides editorial guidelines for text in Apple instructional materials … The intent of these guidelines is to help maintain a consistent voice in Apple materials.（「关于本文档」段）

中文骨架：「本文是……的完整参考」→「本文逐一说明……并演示……」→「本文帮助（角色）完成……」。三句连排即一段合格摘要。

### 步骤句型
> 选择「Apple 菜单」>「系统偏好设置」，点击「通用」，然后从窗口顶部的「外观选项」中选择「深色模式」。（菜单路径：界面元素用「」突出，`>` 连接）
> 使用 `cd` 切换到用户主目录，然后用 `ls -a` 显示全部文件的清单。（命令行叙述：命令名行内代码，动作动词开头）
> 描述具体操作步骤之前，宜首先介绍该系列步骤要达成的目的。（步骤导语的位置规则）

动词选择：桌面端用「点击／双击／右键单击」，移动端用「轻点／轻按」，跨平台统一用「选择」。

### 示例引入句型
> Non-privileged users can use the role to configure the following interfaces:（导语必须是完整句，不许以碎片收尾）
> 本项目依赖于 `moment.js`。／已知主机的列表位于 `~/.ssh/known_hosts`。／使用 `GET` 方法访问 `127.0.0.1:8080`，返回 `404`。（正文夹用技术标识符的标准措辞）
> `grep [OPTION...] -f PATTERN_FILE ... [FILE...]`，其中 `PATTERN_FILE` 为存放匹配规则的外部文件路径。（占位符：选填加方括号、必填不加，随后一句解释占位符含义）
> "Using offset printing"／"Reverting to style in previous layer"（示例标题：动名词短语点明演示场景）

### 警示句型
> Use a `Note` admonition to bring extra information to the user's attention. / Use an `Important` admonition to show the user a piece of information that should not be overlooked. … / Use a `Warning` admonition to alert the reader to potential changes, such as files being removed, and not to perform the operation unless fully aware of the consequences.（三级分工与 Warning 正文骨架：先说会发生什么，再说清后果，最后给执行条件）
> 根据提示内容的级别和分类使用不同的文字描述。例如，分类可以包括「危险」、「警告」、「小心」、「注意」、「说明」、「建议」、「举例」、「错误」等。（中文分级命名）
> 不要轻易使用感叹句。感叹语气可能会让读者感受到被责备，建议仅用于特别强调的场景，例如：读者执行某项操作后，可能永久性地删除数据，需要提供强烈警示。（感叹号的唯一合法场景）

### 过渡与交叉引用句型
> Correct「Refer to the [Accessibility] section later on this page.」/ Incorrect「Refer to the Accessibility section below.」（去方位词：按标题指认，above/below 在响应式布局与屏幕阅读器下失效）
> 错误「详情请点击 `[这里]`」；正确「详情参见 `[故障诊断文档]`」（链接文字要能概括所链内容；同一文档内「详情参见／详情参阅／具体见」不混用）
> 「需要将其 `image` 字段留空」→「需要将相应镜像的 `image` 字段留空」（「其／该／此／这」必须指代明确）
> Correct「[Top-level await](…) on v8.dev (2019)」（外链锚文本标注来源站点与年份）

引用纪律：交叉引用只指向附加信息，读者完成当前任务必需的核心信息就地写清；关键信息（安全提示、排障步骤）宁可重复也不靠链接。每段至多一两个链接；标题与图注中不放链接；更多信息用一句话收尾指路。

## 四、标题与列表拟法

标题：
- 中文标题五种句式：名词词组（「…概述」）；主题词＋动词（「A 工具安装」）；动词＋主题词（「配置 MySQL 数据库」）；定语＋主题词（「A 工具的安装」）；介词＋定语＋主题词（「对机器配置的要求」）。
- 任务章节用「动词＋主题词」，概念章节用名词短语；避免「Understanding／Introducing」式空泛动词：Understanding OpenShift Users and Groups → OpenShift Users and Groups。
- 同级标题句式平行；层级由高到低不跳级；下级标题禁止重复上级内容；标题不以标点结尾；不在标题里解释缩略语、不塞文件名/命令名（文件名和命令在正文里引入）；标题不要只有一个词。
- 标题要能概括本章节中心内容，简洁扼要、涵义明确。

列表：
- 3 项或更多重要信息才用纵向列表；少于 3 项且无需强调，直接放进句子里效果更好。
- 顺序不重要用无序列表；步骤、排名、需引用第 N 项才用有序列表——除非顺序重要，否则不用有序列表。
- 列表项平行：句式相似、长度相近、开头不重复同一词，导语清晰。改写示范：
  > 错误「不支持外部身份验证方式。—不支持列级别权限设置。」改为「TiDB 不支持的功能有如下几种：—外部身份验证方式—列级别权限设置」
- 导语用完整句；不把列表插在一句话中间再续写；整句项以句号结尾，短语项不加标点，混排则统一加句号。
- 不列举过短的内容、不列举无并列关系的内容、不以列表代替标题。

## 五、包容性表达要点

- 泛指读者用「你」、复数或角色名（读者、用户、管理员），不用 he/she；英文可用单数 they，最佳解是改写掉代词。
- 描述发生了什么，而非读者看到/听到什么：写「A message appears, a light flashes, an alert sound plays」，不写「you see a message」。为什么：屏幕阅读器用户没有「看到」。
- 聚焦人而非残障：非必要不提及残障；不用怜悯词（suffering from）；不用蔑称，用「残疾人」「盲人」「聋人」「智力障碍者」等规范词。
- 避免暴力/残酷习语与不利本地化的成语：kill two birds with one stone → solve two problems at once；不用未普及流行语与谐音梗（「魔改」「墙裂」「童鞋们」），不用反语、讽刺、影射等易误解修辞。
- 举例用多元姓名与去刻板印象的职业角色；虚构内容避免与现实实体雷同：域名用 `example.com`，IP 用 `192.0.2.0/24`。
- 首次出现的术语先定义、缩略语先展开再使用：「XUL (XML User Interface Language) is …」；拿不准就展开。
- 不用绝对化评价词（「最佳」「最著名」「最先进水平」）；涉及多地域时正确使用领土主权表述，不将港澳台与中国并列提及。

## 六、反面特征清单（技术文档坏味道，命中即改）

- [ ] 「It is recommended…」「建议进行……」式无主语建议。
- [ ] 「该功能允许用户……」（allow 句式）——改为以用户动作为主语，或换用「使……能够」。
- [ ] 拟人：「工具会抱怨／拒绝／认为」。
- [ ] 方位词引用：「见下文」「如上所述」「点击这里」。
- [ ] 标题接标题，中间没有引导句（空壳结构）。
- [ ] 一逗到底的百字长句；一句塞多个意思（中文一句建议 ≤100 字）。
- [ ] 普通说明里出现反问句、感叹号。
- [ ] 「您」「你」混用；作者自称「我」；称读者「亲爱的」。
- [ ] 「很好地提升了性能」式空泛程度词，无具体数字。
- [ ] 提示框连用、超过 4 行、内含表格图形——提示一多就全部失效。
- [ ] 列表项不平行；导语是半句碎片；两项内容也硬列成表；列表代替标题。
- [ ] 步骤不先说目的；要求输入却不给格式；给危险命令却不给风险与撤销方式。
- [ ] 标题里塞命令名/文件名；「深入理解……」「浅谈……」式空泛标题。
- [ ] 营销腔：推销产品而非传达技术信息；「最佳」「最先进」等评价词。
- [ ] 行话黑话不解释：「CPU 打到 60%」「魔改」。
- [ ] 冗余填充词：「实际上」「真的」「非常」；同一文档重复表达同一事物。
- [ ] 「actually/simply/very」直译腔：「简单地运行」「事实上你可以」。

## 七、标点提醒

- 主引号一律直角引号「」，嵌套用『』；界面元素名称用「」突出（选择「通用」）。
- 连续界面操作用 `>` 连接各元素：「Apple 菜单」>「系统偏好设置」。
- 命令名、包名、文件路径、状态码用行内代码标注。
- 善用句号断句；断句后用「这」「其」等代词衔接前句，切分逻辑。
