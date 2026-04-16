# wiki-obsidian — AI를 위한 세컨드 브레인 (템플릿)

> 이 문서는 AI가 매 세션마다 읽고, 위키를 운영하기 위한 기준점입니다.
> 개인 맥락은 `raw/my_folder/`에 작성하세요.

---

## 위키 운영 규칙 (Karpathy LLM Wiki 기반)

### 핵심 10계명

1. **raw/는 절대 수정 금지** — 불변 원본. 수집한 자료 그대로 보존
2. **wiki 페이지 생성/삭제 시 index.md 필수 업데이트** — 인덱스 없는 페이지는 존재하지 않는 것
3. **모든 오퍼레이션마다 log.md에 기록** — ingest, query, maintenance, sync
4. **내부 참조는 `[[wikilink]]` 형식** — 페이지 간 연결의 유일한 방법
5. **모든 wiki 페이지에 YAML frontmatter** — title, created, updated, tags, source
6. **모순 발견 시 양쪽 소스 모두 인용** — `> [!WARNING]`으로 명시
7. **소스 요약은 사실만, 해석은 개념 페이지에서** — sources/는 팩트, concepts/는 분석
8. **질의 시 index.md 먼저, raw/는 마지막 수단** — wiki → index → search → raw 순서
9. **새 페이지보다 기존 페이지 업데이트 우선** — 중복 페이지 방지
10. **index 항목은 한 줄, 120자 이내** — 간결한 목차 유지

### 3계층 구조

| 계층 | 폴더 | 역할 | 소유자 |
|------|------|------|--------|
| Raw Sources | `raw/` | 불변 원본 자료 | 사용자 |
| Wiki | `wiki/` | 컴파일된 지식 베이스 | AI |
| Output | `Output/` | 최종 결과물 | AI + 사용자 |

### 운영 사이클

```
Ingest: 소스 수집 → raw/ 저장 → wiki/ 페이지 생성/업데이트 → index + log
Query:  index.md → wiki search → 관련 페이지 읽기 → 답변 종합 → log
Lint:   건강 점검 → 깨진 링크/고아/frontmatter 수정 → log
Sync:   git push/pull → GitHub 동기화
```

### 도구

- **llmwiki-cli**: 위키 구조/건강/링크 관리 (`wiki lint`, `wiki links`, `wiki orphans`)
- **qmd**: 정밀 검색 (`qmd query`, `qmd vsearch`)
- **graphify**: 지식 그래프 (`graphify query`, `graphify path`, `graphify explain`)
- **통합 스킬**: `/wiki` 명령으로 모두 접근

---

## 작업 규칙

- **언어**: 한국어 (기술 용어는 원문 유지)
- **톤**: 존댓말, 간결하고 핵심만
- **결과물 형태**: Markdown 기본, 필요시 다이어그램/인포그래픽
- **문서 연결**: `[[wikilink]]`와 태그를 적극 활용
- **기록 원칙**: 빈칸이 있어도 괜찮음 — 채워진 것만으로 시작하고, 점진적으로 보강
