# Apple Developer Program（组织号）注册攻略模板

## 为什么不卷国内开发平台

为什么不把工具类 App 先押在国内开发平台上？因为“某米”“某车”“某遥遥领先”再热，也替代不了稳定的跨平台生态。另一个原因是生态过于封闭：接口、工具链、分发和设备覆盖一旦被单一平台锁住，迁移成本和不确定性都由开发者与用户承担。最近做的工具类 App，会明确写出：暂不支持鸿蒙 OS——不是唱衰国产，而是不拿用户的可用性和团队的维护成本做实验。

更新日期：2026-10-11

## 适用场景

这篇适用于准备以公司或组织名义发布 Apple 生态应用的开发者，例如 iOS、iPadOS、macOS、visionOS 应用，或需要使用 TestFlight 做外部测试的团队。

组织号的核心不是“注册一个 Apple ID”，而是让 Apple 确认三件事：申请主体是真实可签约的法人，D-U-N-S 与法人信息一致，申请人有权代表公司签署 Apple Developer Program 协议。

Apple Developer Program 的标准会员费目前是 99 美元/年；实际注册页面可能按所在地区显示本地货币并叠加适用税费。组织号通过后，App Store 上显示的 Seller 通常是公司法定名称，而不是 Account Holder 的个人姓名。

## 入口

- 注册入口：https://developer.apple.com/programs/enroll/
- 账号管理与状态查看：https://developer.apple.com/account/
- 应用、协议、税务、收款管理：https://appstoreconnect.apple.com/

## 注册前提

| 项目 | 要求 | 准备方式 |
| --- | --- | --- |
| Apple Account | 开启双重认证；申请人需达到当地法定成年年龄 | 建议使用长期可控的公司用途 Apple Account |
| 法人主体 | 必须是能与 Apple 签约的 legal entity；Apple 不接受 DBA、虚拟商号、trade name、分支机构作为组织主体 | 使用公司注册文件上的法定全名，例如 `[Company Legal Name, LLC]` |
| D-U-N-S | 9 位 D-U-N-S 编码；D&B 档案里的公司名、地址、法律状态要匹配 | 先核对 D&B 档案，再开始 Apple 注册 |
| 工作邮箱 | 邮箱域名必须与公司域名关联 | 准备 `dev@[company-domain]`、`legal@[company-domain]` 或申请人个人企业邮箱 |
| 官网 | 公开可访问、功能正常，域名要能关联到公司 | 首页、产品介绍、联系方式、Privacy Policy、Terms of Service 先上线 |
| 授权人 | 申请人必须有权代表公司签署法律协议 | owner / founder / executive / senior project lead / 被授权员工均可，关键是能解释授权关系 |

## 官网最低配置

Apple 官方注册要求强调“公开可访问、功能正常、域名与组织关联”。Privacy Policy 和 Terms of Service 并不是组织号注册页逐字列出的必填字段，但它们会影响 App Review、支付、企业可信度和其他平台审核，所以建议申请前一起补齐。

建议官网至少包含：

- 首页：说明公司或产品做什么、服务对象是谁。
- Privacy Policy：说明收集哪些数据、用途、第三方服务、用户权利、联系方式。
- Terms of Service：说明服务范围、账号、付费、限制、免责声明、适用法律。
- Contact / Support：公司邮箱、支持邮箱、可接听电话。
- Footer：公司法定名称、主域名、政策链接。


## 官网与工作邮箱标准

详细标准见 `website_email_standard_guide.md`。Apple 组织号最看重官网是否公开可访问、功能正常、域名是否能关联组织，以及工作邮箱是否属于公司域名。

推荐使用 Google Workspace 管理公司邮箱。主申请人建议用真人企业邮箱，例如 `firstname@[company-domain]`；公开支持邮箱用 `support@[company-domain]`；隐私和服务条款里使用 `legal@[company-domain]`。不要用个人 Gmail、QQ、Outlook 免费邮箱作为组织号主联系邮箱。

官网设计上，至少准备 Home、Privacy Policy、Terms of Service、Contact / Support。页脚写公司法定名称、政策链接和同域名联系邮箱。

## 中国大陆开发者的注册地区与全球上架

中国大陆公司可以直接按中国大陆所在地区注册 Apple Developer Program，不需要为了面向海外用户而专门注册美国账号。注册地区应与申请主体、联系地址、税务和收款资料保持一致；不要借用其他国家或地区的信息规避审核。

Apple Developer Program 的会员资格支持面向全球用户分发 App。组织号审核通过后，在 App Store Connect 的 App 可用性设置中选择目标国家或地区即可提交全球发行，最终范围取决于 Apple 审核、当地法律、出口管制、支付能力和内容政策。

如果选择在中国大陆 App Store 提供服务，还要单独检查应用备案、许可证、加密、医疗、金融、出版等行业要求。能否在某个国家或地区上架，不等于该地区的合规手续自动完成；涉及受监管业务时，先完成相应备案或许可，再提交审核。

组织号通过后，App Store 的 Seller 通常显示公司法定名称，而不是 Account Holder 的个人姓名。公司法定名称必须与注册文件、D-U-N-S、税务和银行资料一致；品牌名、DBA 或产品名应放在 App 名称、开发者网站或产品介绍中，不要替代 Seller 法定名称。

## 推荐办理顺序

1. 先确定主域名，例如 `[company-domain.com]`。Apple、Google、Microsoft、官网、邮箱尽量使用同一个主域名。
2. 配置公司邮箱，例如 `dev@[company-domain]`、`support@[company-domain]`、`legal@[company-domain]`。
3. 完成官网基础内容，至少上线首页、隐私政策、服务条款和联系方式。
4. 核对 D-U-N-S：公司法定名称、注册地址、邮寄地址、法律实体状态是否和注册文件一致。
5. 如果刚申请或刚更新 D-U-N-S，等 D&B 同步给 Apple 后再提交。Apple 通常提示 D&B 更新后最多需要 2 个工作日同步。
6. 准备公司文件：成立文件、注册证书或良好存续证明、税号文件、D&B 资料截图或确认邮件。
7. 用长期可控的 Apple Account 进入注册入口，选择 Organization。
8. 填写 legal entity name、D-U-N-S、官网、工作邮箱、申请人身份和电话。
9. 等 Apple 核验。Apple 可能通过邮件或电话确认申请人是否有签署开发者协议的授权，也可能要求补充经过公证的业务文件副本。
10. 通过后支付年费，进入 App Store Connect。
11. 如果要销售付费 App、IAP 或订阅，再签 Paid Apps Agreement，填写税务和银行资料。

## 会卡在哪里

| 卡点 | 典型原因 | 处理方式 |
| --- | --- | --- |
| D-U-N-S 查不到 | D&B 尚未生成，或公司名/地址不一致 | 先在 D&B 更新，再等 Apple 同步后重试 |
| 公司名不匹配 | 注册文件、D&B、税务、银行、官网写法不同 | 选一个法定全名作为唯一写法，不要随意省略 LLC、Inc.、标点或后缀 |
| 官网不被接受 | 域名停放、内容太少、无法体现公司关联 | 补首页、政策页、联系方式、公司主体信息 |
| 工作邮箱不通过 | 使用个人邮箱，或邮箱域名与官网/公司域名不一致 | 使用公司域名邮箱，确认能正常收信 |
| 电话核验错过 | Apple 给企业代表打电话没人接 | 申请期保持电话可接，语音信箱和邮件也要可用 |
| 文件补件 | 区域或审核人员要求公证业务文件 | 准备清晰 PDF，必要时做 notarized copy |

## 收款与税务

组织号通过后，如果只是免费 App，可以先不急着配置完整收款。只要销售付费 App、IAP 或订阅，就要在 App Store Connect 的 Business 区域签 Paid Apps Agreement，并提交税务和银行信息。

Apple 官方要求：收款前需要填写银行信息并提交所需税表；美国公司通常走 W-9，并填写 EIN；非美国主体可能走 W-8BEN、W-8BEN-E 或 W-8ECI，系统会按问答引导。银行账号必须是注册开发者法律实体或个人名下的账号。

示例：如果主体是美国 LLC，建议准备 EIN confirmation letter、公司法定名称、公司地址、美元银行账户信息、路由号和账号。银行账户名要与开发者主体匹配。

## 风控建议

- 注册期间不要频繁改公司名、地址、域名、邮箱。
- Apple Account、公司邮箱、D&B、官网、银行、税务文件的主体名称尽量完全一致。
- 注册与日常管理使用稳定设备和稳定网络，避免频繁切换地区、代理和浏览器指纹。
- Apple 给出的补件要求优先级最高，补件时只提交清晰、官方、可核验文件。
- 建议设置至少两个可信团队成员，但 Account Holder 要由最稳定、最长期可控的人持有。

## 官方资料

- Apple Developer Program：https://developer.apple.com/programs/
- Program enrollment：https://developer.apple.com/help/account/membership/program-enrollment
- D-U-N-S Number：https://developer.apple.com/help/account/membership/D-U-N-S/
- Identity verification：https://developer.apple.com/help/account/membership/identity-verification/
- Provide tax information：https://developer.apple.com/help/app-store-connect/manage-tax-information/provide-tax-information
- Enter banking information：https://developer.apple.com/help/app-store-connect/manage-banking-information/enter-banking-information/
