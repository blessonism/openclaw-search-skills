# OpenClaw Search Skills

一组 [OpenClaw](https://github.com/openclaw/openclaw) 技能（Skills），提供 **多源搜索** 和 **内容提取** 能力。

主要为 [github-explorer](https://github.com/blessonism/github-explorer-skill) 提供底层支撑，也可以独立使用。

## 包含什么

| Skill | 干什么的 |
|-------|---------|
| **[search-layer](./search-layer/)** | 多源搜索（Exa + Tavily）+ 自动去重。Brave 由 OpenClaw 内置的 `web_search` 提供。 |
| **[content-extract](./content-extract/)** | URL → 干净的 Markdown。遇到反爬站点（微信、知乎）自动降级到 MinerU 解析。 |
| **[mineru-extract](./mineru-extract/)** | [MinerU](https://mineru.net) 官方 API 的封装层。把 PDF、Office 文档、HTML 页面转成 Markdown。 |

## 它们之间的关系

```
github-explorer（独立 repo）
├── search-layer ──── Exa + Tavily 并行搜索        ← 本仓库
├── content-extract ── 智能 URL → Markdown           ← 本仓库
│   └── mineru-extract ── MinerU API（重活）         ← 本仓库
└── OpenClaw 内置工具 ── web_search, web_fetch, browser
```

## 安装

### 方式一：让 OpenClaw 帮你装（推荐 🚀）

直接在对话里告诉你的 OpenClaw agent：

> 帮我安装这个 skill：https://github.com/blessonism/openclaw-search-skills

### 方式二：用 ClawHub CLI

```bash
npx clawhub install search-layer
npx clawhub install content-extract
npx clawhub install mineru-extract
```

### 方式三：手动安装

```bash
# 1. Clone 到任意位置
mkdir -p ~/.openclaw/workspace/_repos
git clone https://github.com/blessonism/openclaw-search-skills.git \
  ~/.openclaw/workspace/_repos/openclaw-search-skills

# 2. 链接到你的 skills 目录
cd ~/.openclaw/workspace/skills

ln -s ~/.openclaw/workspace/_repos/openclaw-search-skills/search-layer search-layer
ln -s ~/.openclaw/workspace/_repos/openclaw-search-skills/content-extract content-extract
ln -s ~/.openclaw/workspace/_repos/openclaw-search-skills/mineru-extract mineru-extract
```

> 💡 skills 目录因安装方式不同可能不同，常见的是 `~/.openclaw/workspace/skills/` 或 `~/.openclaw/skills/`。

## 配置

### 搜索 API Keys（search-layer 需要）

**环境变量：**

```bash
export EXA_API_KEY="your-exa-key"        # https://exa.ai
export TAVILY_API_KEY="your-tavily-key"  # https://tavily.com
```

**或写到 TOOLS.md（OpenClaw workspace 根目录）：**

```markdown
### Search
- **Exa**: `your-exa-key`
- **Tavily**: `your-tavily-key`
```

### MinerU Token（可选，content-extract 需要）

只有当你需要抓取微信/知乎/小红书等反爬站点时才需要：

```bash
cp mineru-extract/.env.example mineru-extract/.env
# 编辑 .env，填入你的 MinerU token（从 https://mineru.net/apiManage 获取）
```

### Python 依赖

```bash
pip install requests  # 唯一的外部依赖
```

## 单独使用

### search-layer

```bash
python3 search-layer/scripts/search.py "RAG framework comparison" --mode deep --num 5
```

模式：`fast`（仅 Exa）、`deep`（Exa + Tavily 并行）、`answer`（Tavily 带 AI 摘要）

### content-extract

```bash
python3 content-extract/scripts/content_extract.py --url "https://mp.weixin.qq.com/s/some-article"
```

### mineru-extract

```bash
python3 mineru-extract/scripts/mineru_extract.py "https://example.com/paper.pdf" --model pipeline --print
```

## 环境要求

- [OpenClaw](https://github.com/openclaw/openclaw)（agent 运行时）
- Python 3.10+
- `requests`（pip install）
- API Keys：Exa 和/或 Tavily（用于 search-layer），MinerU token（可选，用于 content-extract）

## License

MIT
