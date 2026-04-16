# wiki-obsidian

AI가 구축하고 유지하는 개인 지식 베이스 (LLM Wiki) 템플릿.

[Karpathy의 LLM Wiki 패턴](https://github.com/karpathy/llm-wiki)을 기반으로, LLM이 원본 자료를 읽고 위키를 점진적으로 컴파일하는 구조입니다. RAG처럼 매번 지식을 재발견하는 것이 아니라, **한번 컴파일된 지식이 계속 축적**됩니다.

> **`raw/my_folder/`** 는 사용자 개인 메모 폴더입니다. 클론 후 자신에게 맞는 이름으로 변경하세요. (예: `raw/john/`, `raw/notes/`)

## 시작하기 전에 — 맥락 설정

위키를 셋업하기 전에 **나의 맥락**을 먼저 정리해야 합니다. 이게 없으면 AI가 목적 없이 정리만 합니다.

> Gold In, Gold Out — 목적 있는 수집만이 골드 데이터가 됩니다.

### Step 1. 위키가 될 폴더를 만든다

이 저장소를 클론하거나, 빈 폴더를 하나 만들어 Obsidian vault로 엽니다.

```bash
git clone https://github.com/ggqgga/wiki-obsidian-ggq.git my-wiki
cd my-wiki
```

### Step 2. 3가지 질문에 대한 답을 마크다운 파일로 작성한다

`raw/my_folder/나의-핵심-맥락.md` 파일을 만들고, 아래 3가지 질문에 **한 줄씩이면 충분**합니다.

```markdown
# 나의 핵심 맥락

## 나는 누구인가
- (이름, 하는 일, 역할을 적어주세요)

## 왜 기록하고 싶은가
- (지금 뭐가 안 되는지, 기록이 되면 뭐가 달라지는지 적어주세요)

## 어떤 아웃풋을 만들고 싶은가
- (누구를 위해, 어떤 형태로 만들고 싶은지 적어주세요)
```

### Step 3. Claude Code에서 맥락 인터뷰를 실행한다

Step 2에서 작성한 파일을 바탕으로, AI가 더 깊은 맥락을 뽑아냅니다. Claude Code를 이 폴더에서 열고 아래 프롬프트를 실행하세요:

```
우리는 지금 "AI를 위한 세컨드 브레인"을 만들고 있어.
raw/my_folder/나의-핵심-맥락.md 를 읽고, 나의 맥락을 더 깊이 이해하기 위해 인터뷰해줘.

아래 순서로 한 번에 하나씩 질문해줘:
1. "나는 누구인가"를 더 깊이 — 역할, 강점, 가치관
2. "왜 기록하고 싶은가"를 더 깊이 — 지금 안 되는 것, 비전
3. "어떤 아웃풋을 만들고 싶은가"를 더 깊이 — 대상, 형태, 1년 후 이상적인 모습

각 질문에 대한 내 답변을 받으면 깔끔하게 요약하고 다음 질문으로 넘어가줘.
3개 질문이 끝나면 전체를 종합해서 "나의 맥락 요약"을 raw/my_folder/나의-맥락-요약.md 에 저장해줘.
```

이 과정이 끝나면 `raw/my_folder/나의-맥락-요약.md`가 생성됩니다. AI가 당신의 맥락을 이해하고, 이후 모든 인제스트와 질의에서 **당신에게 맞는 방식으로** 지식을 정리합니다.

> `my_folder`는 자신에게 맞는 이름으로 변경하세요. (예: `raw/john/`, `raw/notes/`)

## 셋업 가이드

> "시작하기 전에" 의 Step 1~3을 먼저 완료한 후 아래를 진행하세요.

### 1. CLI 도구 설치

```bash
brew install gh               # GitHub CLI (git 동기화에 필요)
npm install -g llmwiki-cli
npm install -g @tobilu/qmd    # 선택: 고급 검색
```

### 2. 위키 초기화

```bash
wiki init . --name my-wiki --domain "my knowledge base"
```

### 3. qmd 검색엔진 setup (선택)

```bash
qmd collection add ./wiki --name my-wiki
qmd context add qmd://my-wiki "My knowledge base"
qmd embed
```

### 4. Graphify 설치 (선택)

```bash
uv tool install graphifyy
graphify claude install
graphify hook install
```

### 5. Claude Code 스킬 설치

```bash
mkdir -p ~/.claude/skills/wiki/scripts
cp skills/wiki/SKILL.md ~/.claude/skills/wiki/SKILL.md
cp skills/wiki/scripts/*.sh ~/.claude/skills/wiki/scripts/
chmod +x ~/.claude/skills/wiki/scripts/*.sh
```

### 6. Obsidian Web Clipper 설정

[Obsidian Web Clipper](https://chromewebstore.google.com/detail/cnjifjpddelmedmihgijeibhnjfabmlf?utm_source=item-share-cb) 설치 후, 설정 → Templates에서 `scripts/wiki-template-*.json` 파일들을 import하세요.

### 7. 첫 소스 인제스트

```bash
# 브라우저에서 Web Clipper로 클리핑 → raw/sources/ 에 자동 저장

# Claude Code에서 대화형 인제스트
/wiki add raw/sources/클리핑파일.md
```

## 사용 흐름 (Quick Start)

```
1. 수집    브라우저에서 Web Clipper로 클리핑 → raw/sources/ 에 자동 저장
2. 인제스트  /wiki add raw/sources/클리핑파일.md → 요약 → 질문 → 위키 반영
3. 검색    /wiki 검색어 → 하이브리드 검색으로 관련 페이지 찾기
4. 탐색    /wiki read wiki/concepts/주제.md → 페이지 읽기, [[wikilinks]] 따라가기
5. 점검    /wiki lint → 깨진 링크, 고아 페이지 발견 및 수정
6. 동기화   /wiki sync → GitHub에 push
```

### 일상적인 사용 예시

```bash
# 아티클을 읽다가 Web Clipper로 클리핑 (브라우저에서)
# → raw/sources/2026-04-17-interesting-article.md 자동 생성

# Claude Code에서 인제스트 (대화형)
/wiki add raw/sources/2026-04-17-interesting-article.md
# → AI가 요약을 보여주고, "왜 수집하셨나요?" 질문
# → 답변하면 내 맥락이 반영된 위키 페이지 생성

# 나중에 관련 내용 검색
/wiki AI 아키텍처

# 그래프에서 관계 확인
/wiki graph query "LLM Wiki와 세컨드 브레인 관계"

# 위키 건강 점검
/wiki lint

# GitHub 동기화
/wiki sync
```

## 3계층 구조

```
raw/                  # 불변 원본 자료 (사용자 소유)
  my_folder/          #   직접 쓴 글, 메모 ← 이름을 변경하세요!
  sources/            #   외부 텍스트 소스 (articles, books, papers, youtube 등)
  assets/             #   이미지, PDF, 첨부 파일
wiki/                 # LLM이 컴파일하는 지식 베이스 (AI 소유)
  index.md            #   마스터 인덱스
  log.md              #   활동 로그
  entities/           #   인물, 조직, 제품
  concepts/           #   아이디어, 프레임워크
  sources/            #   소스별 요약 페이지
  insights/           #   교차 분석, 인사이트
Output/               # 최종 결과물 (AI + 사용자)
```

세부 소스 분류(article, youtube, paper 등)는 폴더가 아닌 frontmatter `tags`로 구분합니다.

## 도구

### llmwiki-cli

위키 구조, 건강, 링크를 관리하는 CLI 도구.

```bash
npm install -g llmwiki-cli
```

주요 명령:
```bash
wiki init [dir] --name <name>       # 새 위키 생성
wiki read <path>                     # 페이지 읽기
wiki write <path> <<'EOF' ... EOF    # 페이지 작성
wiki list [dir] [--tree]             # 페이지 목록
wiki search <query>                  # grep 검색
wiki index show/add/remove           # 인덱스 관리
wiki log show/append                 # 로그 관리
wiki lint                            # 건강 점검
wiki links <path>                    # 링크 분석
wiki orphans                         # 고아 페이지 탐지
wiki status                          # 상태 요약
```

### qmd (선택)

마크다운 파일용 로컬 검색 엔진. BM25 + 벡터 + Re-ranking 하이브리드 검색 지원.

```bash
npm install -g @tobilu/qmd

# 컬렉션 등록
qmd collection add ./wiki --name my-wiki
qmd embed

# 검색
qmd query "검색어" -c my-wiki          # 하이브리드 (권장)
qmd vsearch "검색어" -c my-wiki        # 벡터 시맨틱
```

### Graphify (선택)

코드 + 문서 + 논문 + 이미지를 지식 그래프로 압축. 임베딩 없이 그래프 토폴로지(Leiden)로 커뮤니티를 탐지하고, 구조 기반 추론을 가능하게 합니다.

```bash
uv tool install graphifyy       # 설치
graphify claude install          # Claude Code 통합 (CLAUDE.md + PreToolUse hook)
graphify hook install            # git hook (커밋 시 자동 그래프 업데이트)
```

주요 명령:
```bash
graphify update .                # 그래프 빌드/업데이트
graphify query "검색어"           # 그래프 기반 관계 질의
graphify path "A" "B"            # 두 노드 간 최단 경로
graphify explain "X"             # 노드와 이웃 관계 설명
graphify add <url>               # URL에서 소스 추가 → 그래프 반영
graphify update . --wiki         # 커뮤니티별 위키 마크다운 내보내기
```

qmd(텍스트 검색)와 Graphify(구조/관계 추론)는 상호 보완적입니다:
- **qmd**: "이 내용 어디 있지?" — 키워드/의미 기반 검색
- **Graphify**: "이것들이 어떻게 연결되지?" — 구조/관계 기반 추론

## Claude Code 스킬

이 프로젝트에는 Claude Code용 위키 관리 스킬이 포함되어 있습니다. llmwiki-cli + qmd + graphify를 하나의 `/wiki` 명령으로 통합합니다.

### 설치

```bash
mkdir -p ~/.claude/skills/wiki/scripts
cp skills/wiki/SKILL.md ~/.claude/skills/wiki/SKILL.md
cp skills/wiki/scripts/*.sh ~/.claude/skills/wiki/scripts/
chmod +x ~/.claude/skills/wiki/scripts/*.sh
```

### 명령어

```
/wiki <검색어>              하이브리드 검색 (기본값)

--- 읽기 & 탐색 ---
/wiki read <path>           페이지 읽기 (별칭: r)
/wiki list [dir]            목록 (별칭: ls, 목록) [--tree] [--json]

--- 검색 ---
/wiki search <query>        grep 검색 (별칭: s, 찾아줘)
/wiki qsearch <query>       하이브리드 검색 (별칭: qs)
/wiki vsearch <query>       벡터 검색 (별칭: vs)

--- 소스 ---
/wiki add <source>          대화형 인제스트 (별칭: in, input, 입력)
/wiki add <source> --quick  빠른 인제스트 (대화 없이)
/wiki add raw/*             일괄 인제스트

--- 그래프 (Graphify) ---
/wiki graph                 지식 그래프 빌드/업데이트 (별칭: g, 그래프)
/wiki graph <query>         그래프 기반 관계 질의 ("그래프에서 XX 확인해줘")
/wiki graph path "A" "B"    두 노드 간 최단 경로
/wiki graph explain "X"     노드 설명 + 이웃 관계
/wiki graph add <url>       URL에서 소스 추가 → 그래프 반영
/wiki graph export          그래프 내보내기 [--wiki/--svg/--neo4j]

--- 건강 ---
/wiki lint                  건강 점검 (별칭: health, 점검)
/wiki links <path>          링크 분석
/wiki backlinks <path>      인바운드 링크
/wiki orphans               고아 페이지

--- 인덱스 & 로그 ---
/wiki index [show|add|remove]
/wiki log [show|append]

--- 관리 ---
/wiki init [dir]            새 위키 + qmd setup (별칭: setup)
/wiki status                통합 상태 (별칭: stat)
/wiki sync                  Git 동기화 (별칭: git, 깃)
/wiki help                  도움말 (별칭: ?)
```

전체 서브커맨드 목록은 [skills/wiki/SKILL.md](skills/wiki/SKILL.md)를 참조하세요.

## Obsidian Web Clipper

웹 페이지를 위키에 클리핑하기 위해 [Obsidian Web Clipper](https://chromewebstore.google.com/detail/cnjifjpddelmedmihgijeibhnjfabmlf?utm_source=item-share-cb) Chrome 확장을 사용합니다.

### 설치

1. [Chrome 웹스토어](https://chromewebstore.google.com/detail/cnjifjpddelmedmihgijeibhnjfabmlf?utm_source=item-share-cb)에서 확장 설치
2. Obsidian Web Clipper 설정 → Vault를 이 프로젝트 폴더로 지정
3. 설정 → Templates에서 `scripts/wiki-template-*.json` 파일들을 import

### 템플릿 목록

| 템플릿 | Tag | 자동 트리거 |
|--------|-----|-----------|
| `wiki-template-clipper.json` | `clip` | 없음 (기본, 수동 선택) |
| `wiki-template-article.json` | `article` | medium, substack, 브런치, velog, 티스토리, 네이버블로그 등 |
| `wiki-template-youtube.json` | `youtube` | youtube.com, youtu.be |
| `wiki-template-paper.json` | `paper` | arxiv, DBpia, RISS, KCI, nature, IEEE 등 |
| `wiki-template-book.json` | `book` | 교보, YES24, 알라딘, 밀리, 리디, goodreads 등 |
| `wiki-template-github.json` | `github` | github.com, gitlab, bitbucket |
| `wiki-template-sns.json` | `sns` | X, LinkedIn, Reddit, Threads, Bluesky 등 |
| `wiki-template-news.json` | `news` | 네이버뉴스, 조선, 중앙, 한경, BBC, NYT 등 |

URL 패턴에 매칭되면 자동으로 해당 템플릿이 선택됩니다. 매칭 안 되면 기본 `clip` 템플릿을 수동 선택하세요.

모든 클리핑은 `raw/sources/`에 `YYYY-MM-DD-title.md` 형식으로 저장됩니다.

## 위키 작성 규칙

1. 파일명은 **kebab-case**: `my-topic-name.md`
2. **한 파일 한 주제**. 커지면 하위 주제로 분리
3. 페이지 추가/삭제 시 **index.md 필수 업데이트**
4. 모든 오퍼레이션마다 **log.md에 기록**
5. 페이지 간 연결은 **`[[wikilinks]]`** 사용
6. 지식의 **출처 명시** (frontmatter `source:` 또는 본문)
7. **새 페이지보다 기존 페이지 업데이트 우선**
8. `sources/`는 **사실만**, `concepts/`는 **분석/해석**
9. 모순 발견 시 **양쪽 소스 모두 인용** (`> [!WARNING]`)
10. 모든 wiki 페이지에 **YAML frontmatter** 필수

```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
source: URL or description
---
```

## 참고

- [LLM Wiki 패턴 (Karpathy)](https://github.com/karpathy/llm-wiki) — 이 프로젝트의 기반 아이디어
- [llmwiki-cli](https://github.com/nickarora/llmwiki-cli) — 위키 구조 관리 CLI
- [qmd](https://github.com/tobi/qmd) — 마크다운 하이브리드 검색 엔진
- [Graphify](https://graphify.net/) ([한국어](https://graphify.net/kr/index.html)) — 지식 그래프 빌드 도구 (Leiden 커뮤니티 탐지)

## 라이선스

MIT
