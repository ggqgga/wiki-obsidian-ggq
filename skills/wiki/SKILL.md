---
name: wiki
description: "LLM Wiki + QMD + Graphify 통합 위키 관리 스킬. llmwiki-cli로 위키 구조/건강/링크를 관리하고, qmd로 정밀 검색, graphify로 지식 그래프를 구축한다. 서브커맨드: init, read, list, add(인제스트), search, qsearch, vsearch, graph(그래프 빌드/질의/경로/설명), lint, links, backlinks, orphans, index, log, status, sync. 트리거: '/wiki', '위키', '위키 검색', '위키 점검', '위키 추가', '위키 동기화', '소스 입력', '인제스트', '그래프', '그래프에서', '그래프 업데이트', '그래프 확인' 등을 언급할 때."
---

# Wiki - LLM Wiki + QMD + Graphify 통합 위키 관리

llmwiki-cli(위키 구조/관리) + qmd(정밀 검색) + graphify(지식 그래프)를 하나로 통합한 스킬.

- **SCHEMA**: 활성 위키 루트의 `SCHEMA.md` 참조
- **Scripts**: `~/.claude/skills/wiki/scripts/` 에 헬퍼 스크립트
- **활성 위키 확인**: `wiki registry` (`*` = 활성), `wiki use <id>` 로 전환

## Subcommand Routing

| Pattern | Action |
|---------|--------|
| `/wiki init [dir]` or `setup` | `bash ~/.claude/skills/wiki/scripts/wiki-init.sh [dir] --name <name>` |
| `/wiki read <path>` or `r` | `wiki read <path>` |
| `/wiki list [dir]` or `ls`, `목록` | `wiki list [dir] [--tree] [--json]` |
| `/wiki add <source>` or `in`, `input`, `입력` | 대화형 인제스트 + 재색인 (요약 → 질문 → 반영) |
| `/wiki add <source> --quick` or `raw/*` | 빠른 인제스트 + 재색인 (대화 없이 일괄 처리) |
| `/wiki search <query>` or `s`, `찾아줘` | `wiki search "<query>" [--limit N] [--json]` |
| `/wiki qsearch <query>` or `qs`, `빨리찾아줘` | `qmd query "<query>" -c <wiki-id>` |
| `/wiki vsearch <query>` or `vs`, `벡터검색` | `qmd vsearch "<query>" -c <wiki-id>` |
| `/wiki graph` or `g`, `그래프`, `그래프 업데이트` | `graphify update .` — 지식 그래프 빌드/업데이트 |
| `/wiki graph <query>` or `그래프에서 ...`, `그래프 ... 확인` | `graphify query "<query>"` — 그래프 기반 관계 질의 |
| `/wiki graph path "A" "B"` or `그래프 경로`, `A와 B 관계` | `graphify path "A" "B"` — 두 노드 간 최단 경로 |
| `/wiki graph explain "X"` or `그래프 설명`, `X 설명` | `graphify explain "X"` — 노드와 이웃 관계 설명 |
| `/wiki graph add <url>` | `graphify add <url>` — URL에서 소스 추가 → 그래프 반영 |
| `/wiki graph export [--wiki/--svg/--neo4j]` or `그래프 내보내기` | 그래프 내보내기 |
| `/wiki lint` or `health`, `점검` | `wiki lint [--json]` |
| `/wiki links <path>` or `link`, `링크` | `wiki links <path>` |
| `/wiki backlinks <path>` or `backlink`, `백링크` | `wiki backlinks <path>` |
| `/wiki orphans` or `missing`, `고아` | `wiki orphans` |
| `/wiki index [show/add/remove]` | `wiki index <sub>` + reindex on add/remove |
| `/wiki log [show/append]` | `wiki log <sub>` |
| `/wiki status` or `stat` | `bash ~/.claude/skills/wiki/scripts/wiki-status.sh` |
| `/wiki sync` or `git`, `깃` | Git 동기화 — `gh-cli` 스킬 참조 (`gh repo sync`, `git push/pull`) |
| `/wiki help` or `?` | Help 텍스트 출력 |
| `/wiki <text>` (no match) | `qmd query "<text>" -c <wiki-id>` |
| `/wiki` (no args) | 사용자에게 검색어 요청 |

## Scripts

| 스크립트 | 용도 |
|---------|------|
| `scripts/wiki-init.sh` | wiki init + qmd collection setup 통합 |
| `scripts/wiki-status.sh` | wiki status + qmd status 통합 출력 |
| `scripts/wiki-reindex.sh` | qmd update + embed (검색 인덱스 갱신) |

## Ingest 워크플로우

### 대화형 (기본) — `/wiki add <source>`

1. 소스 읽기 (raw/는 절대 수정 금지)
2. 사용자에게 요약 제시:
   - 핵심 주장 (Key Claims)
   - 언급된 엔티티 (사람, 도구, 조직)
   - 다루는 개념 (Concepts)
3. **사용자에게 질문** (동시에):
   - "이 글을 왜 수집하셨나요?"
   - "지금 하고 계신 일과 어떻게 연결되나요?"
4. 사용자 답변을 반영하여 wiki/ 페이지 생성:
   - `wiki write wiki/sources/<name>.md` — 소스 요약 + 사용자 맥락
   - 엔티티 → `wiki/entities/`, 개념 → `wiki/concepts/`, 인사이트 → `wiki/insights/`
5. `wiki index add <path> <summary>` — 인덱스 등록
6. `wiki log append ingest "<description>"` — 로그 기록
7. `bash ~/.claude/skills/wiki/scripts/wiki-reindex.sh` — 검색 인덱스 갱신

### 빠른 모드 — `/wiki add <source> --quick` 또는 `/wiki add raw/*`

대화 없이 바로 처리. 복수 파일 일괄 인제스트 시 사용.

1. 소스 읽기
2. `wiki write raw/<name>.md <<'EOF' ... EOF` — 원본 저장 (아직 raw/에 없는 경우)
3. `wiki write wiki/sources/<name>.md <<'EOF' ... EOF` — 요약 페이지 (frontmatter + [[wikilinks]])
4. 엔티티 → `wiki/entities/`, 개념 → `wiki/concepts/`, 인사이트 → `wiki/insights/`
5. `wiki index add <path> <summary>` — 인덱스 등록
6. `wiki log append ingest "<description>"` — 로그 기록
7. `bash ~/.claude/skills/wiki/scripts/wiki-reindex.sh` — 검색 인덱스 갱신

> **경로**: 위키 루트 기준 상대 경로 사용. `wiki read wiki/concepts/ai.md` (O)
> **heredoc**: `<<'EOF'` (single-quoted) 필수 — shell expansion 방지

## Graph (Graphify 지식 그래프)

코드 + 문서 + 논문 + 이미지를 지식 그래프로 압축. 구조 기반 추론 가능.

- **출력**: `graphify-out/graph.json`, `GRAPH_REPORT.md`, `graph.html`
- **자동 업데이트**: git hook(post-commit)으로 커밋 시 자동 리빌드
- **검색과의 차이**: qmd는 "이 내용 어디 있지?" → Graphify는 "이것들이 어떻게 연결되지?"

### 주요 명령

```bash
graphify update .                    # 그래프 빌드/업데이트
graphify query "<query>"             # 그래프 기반 관계 질의
graphify path "A" "B"                # 두 노드 간 최단 경로
graphify explain "X"                 # 노드와 이웃 관계 설명
graphify add <url>                   # URL에서 소스 추가 → 그래프 반영
graphify update . --wiki             # 커뮤니티별 위키 마크다운 내보내기
graphify update . --svg              # SVG 그래프 내보내기
```

### GRAPH_REPORT.md 핵심 정보

- **God nodes**: 가장 많이 연결된 핵심 노드
- **Surprising connections**: 의외의 중요 연결
- **Communities**: Leiden 알고리즘으로 탐지된 커뮤니티
- **Knowledge gaps**: 보강이 필요한 영역

## Index 후처리

`wiki index add` / `wiki index remove` 후 검색 인덱스도 갱신:
```bash
wiki index add "<path>" "<summary>" && bash ~/.claude/skills/wiki/scripts/wiki-reindex.sh
```

## Conventions

1. 파일명 **kebab-case**: `my-topic.md`
2. **한 파일 한 주제**, 중복 페이지 방지
3. **index.md 필수 업데이트** — 페이지 추가/삭제 시
4. **log.md 필수 기록** — 모든 오퍼레이션마다
5. **`[[wikilinks]]`** 로 페이지 연결
6. **출처 명시** — frontmatter `source:` 또는 본문
7. **기존 페이지 업데이트 우선** — 새 페이지보다
8. `sources/` = 사실, `concepts/` = 분석/해석
9. 모순 시 `> [!WARNING]` + 양쪽 소스 인용
10. 모든 wiki 페이지에 **YAML frontmatter** 필수:
    ```yaml
    title: / created: / updated: / tags: [] / source:
    ```

## Help

`/wiki help` 또는 `/wiki ?` 시 출력:

```
Wiki - LLM Wiki + QMD + Graphify 통합 위키 관리

사용법: /wiki [command] [args]

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
  /wiki graph query "<query>" 그래프 기반 관계 질의
  /wiki graph path "A" "B"    두 노드 간 최단 경로
  /wiki graph explain "X"     노드 설명 + 이웃 관계
  /wiki graph add <url>       URL에서 소스 추가 → 그래프 반영
  /wiki graph export --wiki   커뮤니티별 위키 내보내기 [--svg/--neo4j]

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
  /wiki help                  이 도움말 (별칭: ?)
```
