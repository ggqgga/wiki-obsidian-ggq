---
name: wiki
description: "LLM Wiki + QMD + Graphify 통합 위키 관리 스킬. llmwiki-cli로 위키 구조/건강/링크를 관리하고, qmd로 정밀 검색, graphify로 지식 그래프를 구축한다. 서브커맨드: init, read, list, add(인제스트), search, qsearch, vsearch, graph(그래프 빌드/질의/경로/설명), lint, links, backlinks, orphans, index, log, status, sync. 트리거: '/wiki', '위키', '위키 검색', '위키 점검', '위키 추가', '위키 동기화', '소스 입력', '인제스트', '그래프', '그래프에서', '그래프 업데이트', '그래프 확인', '노트북LM 가져와', 'notebooklm 데이터 인제스트', 'nblm 요약 넣어줘', 'PDF 가져와', 'PDF 인제스트', 'pdf ingest' 등을 언급할 때."
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
| `/wiki add --nblm <source>` or `노트북LM 가져와`, `nblm 데이터`, `notebooklm 요약 넣어줘` | NotebookLM 경유 인제스트 — `notebooklm` 스킬로 report 생성·다운로드 → `raw/sources/YYYY-MM-DD-<slug>-nblm.md` 배치 → 빠른 인제스트 흐름. 상세 규칙은 [[wiki/concepts/notebooklm-workflow]] |
| `/wiki add <path>.pdf` or `PDF 가져와`, `PDF 인제스트` | PDF 경유 인제스트 — `tools/odl/ingest.py` (OpenDataLoader PDF) 호출 → `raw/assets/<slug>.pdf` + `raw/sources/YYYY-MM-DD-<slug>.md` + `raw/assets/json/<slug>.json` 생성 → index/log/reindex. 상세는 아래 "PDF 경유" 섹션 |
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

### NotebookLM 경유 — `/wiki add --nblm <source>` 또는 자연어 "노트북LM에서 가져와줘"

**트리거**: "노트북LM 데이터", "nblm 요약 가져와", "notebooklm 노트북 <title> 인제스트해줘", "NotebookLM에서 뽑아서 위키에 넣어줘" 등.
**전제**: `notebooklm` 스킬 인증 완료 (없으면 `notebooklm login` 안내).

1. **소스 판별**: URL(웹/유튜브) / 파일 / 이미 존재하는 notebook_id 중 무엇인지 확인
2. **노트북 준비** (`notebooklm` 스킬 사용):
   - 기존 노트북에 추가: `notebooklm use <id>` + `notebooklm source add <src>`
   - 새 노트북: `notebooklm create "Wiki-<slug>-<YYMMDD>"` + `source add`
   - `notebooklm source wait <source_id>` 로 처리 완료 대기
3. **리포트 생성 및 다운로드** (확인 필요):
   - `notebooklm generate report --format briefing-doc`
   - `notebooklm download report raw/sources/YYYY-MM-DD-<slug>-nblm.md`
4. **원본 쌍 배치 권장**: 원본 트랜스크립트·기사 본문이 있으면 `raw/sources/YYYY-MM-DD-<slug>.md`로 **함께** 저장 (fact/파생 분리)
5. **빠른 모드 ingest 흐름 적용** (위 절차):
   - sources 페이지 frontmatter `source:` 에 원본 URL + "NotebookLM 파생" 병기
   - 원본과 파생 둘 다 `[[raw/...]]`로 역링크, `> [!NOTE]` 로 우선순위 선언 (원본 = fact)
6. **로그**: `wiki log append ingest "<description> (NotebookLM 경유)"`

**규칙·판정 기준 상세**: [[wiki/concepts/notebooklm-workflow]] — Claude Code 직접 요약 vs NotebookLM 판정, 산출물별 흡수 규칙(report만 sources/, audio/slide/mindmap은 Output·raw/podcasts), `-nblm` 네이밍.

> [!WARNING]
> NotebookLM 요약은 hallucination 위험이 0이 아님. 결정·주장 근거로 쓰기 전 원본 대조 필수. 원본이 없이 파생물만 있는 경우 sources 페이지에 `> [!WARNING]` 로 명시.

### PDF 경유 — `/wiki add <path>.pdf` 또는 자연어 "PDF 가져와"

**트리거**: `.pdf` 확장자 감지, 또는 "PDF 가져와", "이 PDF 위키에", "PDF 인제스트" 등.
**도구**: `tools/odl/ingest.py` (OpenDataLoader PDF 래퍼). 활성 위키 루트에 없으면 설치 안내.

1. **PDF 원본 보관**: 사용자 제공 경로가 `raw/assets/` 외부면 → `raw/assets/<slug>.pdf`로 복사 (slug는 PDF 내용 기반 title 미리보기 후 사용자 확인)
2. **변환 실행**:
   ```bash
   cd <wiki-root>
   uv run --directory tools/odl python ingest.py [--tag <t>]... <raw/assets/*.pdf>
   ```
   - 내부: OpenJDK 17 PATH 주입 → `opendataloader-pdf -o $TMPDIR -f json,markdown --image-output off -q` 호출 → page-1 max font-size heading으로 title 추출 → 점선·과잉 빈줄 정리 → frontmatter 주입 후 `raw/sources/YYYY-MM-DD-<slug>.md` 저장 → `raw/assets/json/<slug>.json` 백업
3. **frontmatter 확인**: title이 잘못 추출됐으면 사용자에게 확인 후 수정. 태그는 `pdf` 자동 + 주제 태그(`manual`, `policy`, `paper` 등) 수동 추가 권장
4. **index.md 등록**: `### PDF 문서 (외부 매뉴얼·레퍼런스)` 섹션 사용. 없으면 Sources 하위에 생성
5. **log.md 기록**: `wiki log append ingest "<title> PDF — <page수>p, tools/odl/ingest.py 경유"`
6. **재인덱스**: `bash ~/.claude/skills/wiki/scripts/wiki-reindex.sh`

**Fast 모드 한계**: 스캔 PDF·복잡한 표·수식은 품질 저하. 이 경우 hybrid 모드 검토 (별도 백엔드 서버 `opendataloader-pdf-hybrid --port 5002` 기동 필요).

**민감 정보 PDF**: `--sanitize` 플래그 명시. URL/이메일/전화/IP를 placeholder로 치환 — 공개 API 매뉴얼엔 쓰지 말 것 (endpoint 소실).

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
  /wiki add --nblm <source>   NotebookLM 경유 인제스트 (자연어: "노트북LM 가져와")
  /wiki add <path>.pdf        PDF 경유 인제스트 — OpenDataLoader (자연어: "PDF 가져와")

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
