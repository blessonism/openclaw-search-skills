# GitHub Explorer（OpenClaw Skill）

有些项目的 README 写得像发布会 PPT：

- “🚀 Next-gen / SOTA / blabla…”
- badge 一排，图很炫
- 但你真正想知道的：**活不活跃、坑多不多、作者回不回 Issue、到底适不适合你** —— README 基本不告诉你。

`github-explorer` 这个 skill 做的事很简单：

> 让 OpenClaw 帮你把“评估一个 GitHub 项目”这件事做得更像一个认真看过源码/社区的人，而不是只读了 README。

---

## 你会得到什么

当你对 OpenClaw 说：

- “帮我看看这个 GitHub 项目 raganything”
- “分析一下 HKUDS/LightRAG”

它会输出一份结构化报告（带链接、可追溯）：

- 一句话定位（它到底解决什么问题）
- 核心机制（不是复制 README，用人话讲架构/流程）
- 项目健康度（Stars/Forks/License、作者背景、commit 近况）
- 精选 Issues（按评论/价值挑 3–5 条，指出真实风险点）
- 适用场景 & 局限（什么时候该用/别碰）
- 竞品对比（同赛道项目 + 链接）
- 论文 / Demo / DeepWiki / Zread 等“知识图谱入口”
- 社区声量（X/Twitter、知乎/V2EX 等，**引用具体内容** + 原链接）
- 最后一段：它自己的判断（值不值得投入时间）

---

## 依赖（很重要）

`github-explorer` 本身只是“总控流程”，真正干活要靠同仓库的几个 plumbing skills：

- `search-layer`：Exa + Tavily 多源搜索 + 去重（Brave `web_search` 由 OpenClaw 内置提供）
- `content-extract`：网页抓取失败/反爬时，自动走 MinerU 做高保真解析
- `mineru-extract`：MinerU 官方 API 包装层（给 content-extract 用）

所以如果你要推广 `github-explorer`，建议**四个目录一起安装**。

---

## 安装（推荐：symlink 方式）

把这个仓库 clone 到任意位置，然后把 4 个 skill 目录链接到你的 skill 目录里。

> OpenClaw 的 skill 目录在不同安装方式下可能不同；常见的是：
> - `~/.openclaw/skills/`
> - `~/.openclaw/workspace/skills/`
>
> 你只要保证：OpenClaw 能加载到这些目录里的 `SKILL.md` 即可。

示例（把它们放到 workspace/skills）：

```bash
mkdir -p ~/.openclaw/workspace/skills
cd ~/.openclaw/workspace/skills

# 先 clone 仓库
# git clone https://github.com/blessonism/openclaw-search-skills.git /path/to/openclaw-skills

ln -s /path/to/openclaw-skills/github-explorer github-explorer
ln -s /path/to/openclaw-skills/search-layer search-layer
ln -s /path/to/openclaw-skills/content-extract content-extract
ln -s /path/to/openclaw-skills/mineru-extract mineru-extract
```

---

## 配置

### 1) search-layer 的 API keys（建议配）

两种方式任选其一：

- 环境变量：

```bash
export EXA_API_KEY="..."
export TAVILY_API_KEY="..."
```

- 或者写到 OpenClaw workspace 的 `TOOLS.md` 里（search-layer 会去读）：

```md
### Search
- **Exa**: `your-exa-key`
- **Tavily**: `your-tavily-key`
```

### 2) MinerU Token（可选，但强烈建议）

当你要抓微信/知乎/小红书这种经常 403 的站点时，`content-extract` 会用 MinerU 兜底。

```bash
cp mineru-extract/.env.example mineru-extract/.env
# 然后在 mineru-extract/.env 里填 MINERU_TOKEN
```

---

## 使用方式

直接在对话里说就行：

- “帮我看看这个 GitHub 项目 xxx”
- “这个 repo 怎么样”

你不需要指定 mode；skill 会自动：

- 项目调研 → 默认走 `search-layer --mode deep`
- 单源失败 → 自动降级，不会因为一个 API 挂了就中断
- 反爬站点 → 自动升级到 MinerU

---

## 常见问题

### Q: 为什么我搜中文社区时结果少？

Brave 免费额度/速率有时会触发 429（你刚才也遇到了）。这个 skill 的策略是：

- Brave 限流时，依然会继续用 Exa/Tavily（如果你配了 key）
- 所以 **Exa/Tavily 的 key 很关键**

### Q: 为什么图像分析/文档解析效果不稳定？

多模态链路牵涉：解析器（MinerU/Docling）→ VLM（OpenAI/Azure）→ 你的 prompt/配置。

从项目自身的 Issues（例如 [#70](https://github.com/HKUDS/RAG-Anything/issues/70)）来看，这类问题不算少。

建议：先用少量样本跑通，再逐步扩大规模。

---

## 维护者建议（给想二次开发的人）

- `SKILL.md` 是给 agent 看的“行为规范”；`README.md` 是给人看的“使用说明”。
- 如果你要把报告发到 Telegram/Discord，注意空行和列表渲染（`github-explorer/SKILL.md` 里有专门的 Telegram 空行规则）。

---

## License

MIT
