# Microsoft Partner Center / Microsoft Store（公司开发者号）注册攻略模板

## 为什么不卷国内开发平台

为什么不把工具类 App 先押在国内开发平台上？因为“某米”“某车”“某遥遥领先”再热，也替代不了稳定的跨平台生态。另一个原因是生态过于封闭：接口、工具链、分发和设备覆盖一旦被单一平台锁住，迁移成本和不确定性都由开发者与用户承担。最近做的工具类 App，会明确写出：暂不支持鸿蒙 OS——不是唱衰国产，而是不拿用户的可用性和团队的维护成本做实验。

更新日期：2026-10-11

## 适用场景

这篇适用于准备以公司主体发布 Windows 桌面客户端、Microsoft Store 应用、MSIX / MSI / EXE 安装包、Edge 扩展，或后续衔接 Microsoft Marketplace、Azure、Microsoft for Startups 的团队。

如果是商业主体发布，建议使用 Microsoft Store 的 Company developer account。不要误选 Individual，因为 Partner Center 不支持把 Individual developer account 直接改成 Company；选错通常要重新创建公司账号。

Microsoft Store 新注册流程下，Individual 和 Company 开发者账号都免注册费。公司账号必须从新入口进入，否则可能看到旧流程。

## 入口

- 新 Store 开发者注册入口：https://storedeveloper.microsoft.com/
- Partner Center：https://partner.microsoft.com/dashboard/
- Microsoft Store 应用提交区域：Partner Center → Apps & Games
- Microsoft for Startups：https://www.microsoft.com/startups

注意：发布 Windows 应用或 Store 应用，走 Store developer onboarding。Microsoft AI Cloud Partner Program / Microsoft for Startups 是另外的合作伙伴或创业扶持路径，不要和 Store 开发者账号混成同一个步骤。

## 注册前提

| 项目 | 要求 | 准备方式 |
| --- | --- | --- |
| 账号类型 | 选择 Company account | 商业发布、公司发布、团队发布都优先选 Company |
| 登录账号 | Company 可用个人 Microsoft Account，也可用 Microsoft Entra ID work account | 早期可用长期可控 MSA；成熟后再规划 Entra tenant 和团队权限 |
| D-U-N-S | 推荐使用 9 位 DUNS，验证最快 | 优先用 D-U-N-S，不用文件人工审 |
| 替代文件 | 如不用 DUNS，可上传公司成立、注册、政府登记、税务文件 | 准备 formation、registration、good standing、tax filing 等官方文件 |
| 工作邮箱 | 验证邮箱应匹配公司域名；Gmail / Yahoo 等个人邮箱不支持验证字段 | 使用个人归属的企业邮箱，避免 group alias、plus addressing |
| 域名证明 | 邮箱域名与公司域名不一致时，可能要求域名所有权或购买 / 续费发票 | 主域名、公司邮箱、官网、D-U-N-S 尽量统一 |
| 客户联系信息 | Store 页面可能公开电话、地址、邮箱 | 准备 support 邮箱、可接听电话、可公开地址或注册代理地址方案 |


## 官网与工作邮箱标准

详细标准见 `website_email_standard_guide.md`。Microsoft 对公司邮箱和域名一致性比较敏感，主验证邮箱建议用真人企业邮箱，例如 `firstname@[company-domain]`，不要用 group alias、generic email 或 plus addressing。

推荐用 Google Workspace 先把公司邮箱体系搭好；如果后续需要 Azure、Entra ID、Teams 或企业权限管理，再规划 Microsoft Entra tenant。早期不要频繁切换邮箱服务商、主域名或登录租户。

官网至少要有 Home、Product / Solutions、Privacy Policy、Terms of Service、Contact / Support。Store 客户联系信息可能公开，所以要提前规划 `support@[company-domain]`、联系电话和可公开地址。

## 推荐办理顺序

1. 从 `https://storedeveloper.microsoft.com/` 进入，不要从旧 Partner Center、Xbox 或 Visual Studio 入口开始。
2. 点击 Get started，选择 Company account（free）。
3. 登录 MSA 或 Microsoft Entra ID work account。个人 MSA 只是登录身份，不等于个人开发者账号；Company account 才是开发者主体类型。
4. 选择 D-U-N-S 验证，填入公司法定信息并核对自动带出的公司名和地址。
5. 填联系人信息和 Store 支持联系信息。验证邮箱要用企业域名邮箱，接收 OTP。
6. 接受协议，提交验证。
7. 在 Verification summary 里看 mandatory due diligence、business verification、employment verification 状态。
8. 如果进入人工审核，通常等 2–5 个工作日；文件审核可能 3–5 个工作日。期间等邮件，不要反复改主体信息。
9. 通过后选择 Publish to Store，进入 Partner Center 的 Apps & Games。
10. 如果应用提交入口短时间不可用，等待约 5–30 分钟再刷新。

## 税务、商户权限与收款

如果只是发布免费应用，不一定要立即设置 payout 和 tax profile。如果要卖付费应用、内购、订阅、Marketplace transactable offer 或其他可结算项目，需要在 Partner Center 配置 payout account 和 tax forms。

Microsoft 官方说明：完成账号、Publisher agreement 和 vetting 后，要发布 transactable offer，需要设置 payout account 并填写 tax forms。非美国发布者通常填写 IRS W-8 表，系统在线引导；美国主体通常按 W-9 处理。税务和 payout profile 提交后，验证通常最多 48 小时。

示例：如果主体是美国 LLC，建议准备 EIN confirmation letter、IRS legal business name、公司地址、美元银行账户的路由号、账号、账户名和地址信息。若平台询问 beneficial owner / authorized representative，如实填写法人或授权代表。

## Edge 扩展与 Windows 客户端

Microsoft Store / Partner Center 可以承接 Windows 应用发布。Edge 扩展通常通过 Microsoft Edge Add-ons 提交流程处理，账号和 Microsoft 生态资料会有关联，但不要假定 Store 应用和 Edge 扩展的所有材料完全共用。建议公司身份、域名、隐私政策、支持邮箱统一，这样后续 Store、Edge、Azure、Marketplace 都能复用。

Windows 桌面客户端如果要走 Store：

- 准备 MSI / EXE / MSIX 的安装、卸载、更新、权限说明。
- 隐私政策 URL 和支持 URL 提前上线。
- 客户联系信息要真实可用。
- 如果涉及后台服务、网络代理、设备控制、AI 功能、账号登录，要准备审核说明和测试账号。

## Azure 创始人补贴与 Partner Center 的关系

Microsoft for Startups / Founders Hub 与 Store 开发者账号不是同一个注册流程。Azure credits 走 Microsoft for Startups 的申请与 Azure Portal 管理。微软官方资料显示，新流程下初始可能有小额度 startup credits，并可随业务验证、使用情况和项目进展解锁更高额度。

实际策略：先把公司主体、官网、域名邮箱、D-U-N-S、税号、隐私政策、服务条款整理好；这些材料可以同时服务 Store 公司开发者号、Google / Apple 组织号和 Microsoft for Startups。

## 会卡在哪里

| 卡点 | 典型原因 | 处理方式 |
| --- | --- | --- |
| 走到旧流程或收费页 | 从旧 Partner Center / Visual Studio / Xbox 入口进入 | 退出后从 `storedeveloper.microsoft.com` 重新开始 |
| 误选 Individual | 以为 MSA 登录就是个人/公司无所谓 | 新建 Company developer account，Individual 不能直接改 Company |
| D-U-N-S 不匹配 | 公司名、地址、域名与 D&B 信息不同 | 先修 D&B 和官网信息，再重试 |
| 验证邮箱失败 | 使用 Gmail / Yahoo、group alias、plus addressing，或邮箱域名不匹配 | 使用个人归属的公司域名邮箱，确保 OTP 可收 |
| 域名验证失败 | 域名购买记录不能体现公司或联系人 | 准备域名注册或续费发票、WHOIS / 注册商记录、官网主体信息 |
| 文件审核慢 | 不用 DUNS，上传文件进入人工审 | 优先 DUNS；补件只上传官方、当前、清晰文件 |
| Vetting rejected | 五类审核中任一失败 | 在 Partner Center Account settings 里看拒绝原因，用 Fix now 补对应材料 |

## 风控建议

- 公司账号注册期，不要反复切换登录账号、租户、域名和邮箱。
- MSA、Entra、Partner Center、D-U-N-S、官网、税务、银行资料保持同一公司身份。
- 给 Partner Center 至少配置两个 Owner / 管理员，避免单账号丢失导致恢复困难。
- Store 客户联系信息可公开，提前规划 support 邮箱、电话和地址。
- 付费或可结算能力等到主体通过后再开，不要在公司验证未稳定时反复修改税务资料。

## 官方资料

- Open a Microsoft Store developer account：https://learn.microsoft.com/en-us/windows/apps/publish/partner-center/open-a-developer-account
- Company account verification requirements：https://learn.microsoft.com/en-us/windows/apps/publish/store-business-verification-reqs
- Set up payout and tax profiles：https://learn.microsoft.com/en-us/partner-center/account-settings/set-up-your-payout-account
- Microsoft for Startups FAQ：https://learn.microsoft.com/en-us/startups/microsoft-for-startups/mfs-faqs
- Getting started with Microsoft for Startups：https://learn.microsoft.com/en-us/startups/microsoft-for-startups/getting-started-mfs
