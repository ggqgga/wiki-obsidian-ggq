---
name: notebooklm
description: NotebookLM API를 통해 노트북 생성, 소스 추가, 콘텐츠 생성(팟캐스트, 비디오, 슬라이드, 퀴즈 등), 다운로드를 자동화합니다. 사용자가 notebooklm, 팟캐스트 만들어, 슬라이드 생성, 리서치 등을 언급할 때 활성화됩니다.
argument-hint: "[create|source|generate|download|ask] [대상/옵션]"
---

# NotebookLM Automation

Google NotebookLM의 완전한 프로그래매틱 접근. 노트북 생성, 소스 추가(URL, YouTube, PDF, 오디오, 비디오, 이미지), 챗, 아티팩트 생성 및 다운로드.

> 기반: [notebooklm-py](https://github.com/teng-lin/notebooklm-py) (비공식 라이브러리)

---

## Prerequisites (최초 1회 셋업)

```bash
# 1) 설치 — notebooklm-py 및 Playwright 브라우저
uv pip install notebooklm-py
playwright install chromium

# 2) 인증 — 브라우저 OAuth 창이 열립니다. Google 계정으로 로그인
notebooklm login

# 3) 인증 확인
notebooklm list

# 4) 언어 기본값 설정 (원하는 경우)
notebooklm language set ko   # 한국어
# notebooklm language set en # 영어
```

**인증 실패 시** `notebooklm auth check --test`로 진단 → `notebooklm login` 재실행.

### 팁

- 노트북 네이밍: `Wiki-<주제>-<YYMMDD>` 같이 일관된 규칙 권장 (검색·관리 편의)
- 쿠키가 만료되면 `notebooklm login`으로 재인증 필요 (보통 몇 주~몇 달마다)

---

## Autonomy Rules

**자동 실행 (확인 불필요):**
- `status`, `auth check`, `list`, `source list`, `artifact list` — 읽기 전용
- `language list/get/set` — 설정 조회/변경
- `use <id>` — 컨텍스트 설정
- `create` — 노트북 생성
- `ask "..."` — 챗 (save-as-note 제외)
- `history` — 대화 이력 조회
- `source add` — 소스 추가
- `profile list/create/switch` — 프로필 관리
- `doctor` — 환경 점검

**확인 필요:**
- `delete` — 파괴적
- `generate *` — 장시간 소요, 실패 가능
- `download *` — 파일시스템 쓰기
- `ask "..." --save-as-note` — 노트 저장
- `history --save` — 노트 저장

---

## Quick Reference

| Task | Command |
|------|---------|
| 인증 | `notebooklm login` |
| 인증 진단 | `notebooklm auth check --test` |
| 노트북 목록 | `notebooklm list` |
| 노트북 생성 | `notebooklm create "Title"` |
| 컨텍스트 설정 | `notebooklm use <notebook_id>` |
| 상태 확인 | `notebooklm status` |
| URL 소스 추가 | `notebooklm source add "https://..."` |
| 파일 소스 추가 | `notebooklm source add ./file.pdf` |
| YouTube 소스 추가 | `notebooklm source add "https://youtube.com/..."` |
| 소스 목록 | `notebooklm source list` |
| 소스 삭제 | `notebooklm source delete <source_id>` |
| 소스 대기 | `notebooklm source wait <source_id>` |
| 웹 리서치 (빠름) | `notebooklm source add-research "query"` |
| 웹 리서치 (깊이) | `notebooklm source add-research "query" --mode deep --no-wait` |
| 챗 | `notebooklm ask "question"` |
| 챗 (참조 포함) | `notebooklm ask "question" --json` |
| 챗 → 노트 저장 | `notebooklm ask "question" --save-as-note` |
| 대화 이력 | `notebooklm history` |
| 소스 전문 | `notebooklm source fulltext <source_id>` |
| 팟캐스트 생성 | `notebooklm generate audio "instructions"` |
| 비디오 생성 | `notebooklm generate video "instructions"` |
| 슬라이드 생성 | `notebooklm generate slide-deck` |
| 리포트 생성 | `notebooklm generate report --format briefing-doc` |
| 퀴즈 생성 | `notebooklm generate quiz` |
| 마인드맵 생성 | `notebooklm generate mind-map` |
| 인포그래픽 생성 | `notebooklm generate infographic` |
| 데이터 테이블 생성 | `notebooklm generate data-table "description"` |
| 플래시카드 생성 | `notebooklm generate flashcards` |
| 아티팩트 상태 | `notebooklm artifact list` |
| 아티팩트 대기 | `notebooklm artifact wait <artifact_id>` |
| 오디오 다운로드 | `notebooklm download audio ./output.mp3` |
| 비디오 다운로드 | `notebooklm download video ./output.mp4` |
| 슬라이드 다운로드 (PDF) | `notebooklm download slide-deck ./slides.pdf` |
| 슬라이드 다운로드 (PPTX) | `notebooklm download slide-deck ./slides.pptx --format pptx` |
| 리포트 다운로드 | `notebooklm download report ./report.md` |
| 마인드맵 다운로드 | `notebooklm download mind-map ./map.json` |
| 퀴즈 다운로드 | `notebooklm download quiz quiz.json` |
| 플래시카드 다운로드 | `notebooklm download flashcards cards.json` |
| 노트북 삭제 | `notebooklm notebook delete <id>` |
| 언어 설정 | `notebooklm language set ko` |

---

## Generation Types

| Type | Command | Options | Download |
|------|---------|---------|----------|
| Podcast | `generate audio` | `--format [deep-dive\|brief\|critique\|debate]`, `--length [short\|default\|long]` | .mp3 |
| Video | `generate video` | `--format [explainer\|brief]`, `--style [auto\|classic\|whiteboard\|kawaii\|anime\|...]` | .mp4 |
| Slide Deck | `generate slide-deck` | `--format [detailed\|presenter]`, `--length [default\|short]` | .pdf / .pptx |
| Infographic | `generate infographic` | `--orientation [landscape\|portrait\|square]`, `--style [auto\|sketch-note\|professional\|...]` | .png |
| Report | `generate report` | `--format [briefing-doc\|study-guide\|blog-post\|custom]` | .md |
| Mind Map | `generate mind-map` | *(sync, instant)* | .json |
| Data Table | `generate data-table` | description required | .csv |
| Quiz | `generate quiz` | `--difficulty [easy\|medium\|hard]`, `--quantity [fewer\|standard\|more]` | .json/.md/.html |
| Flashcards | `generate flashcards` | `--difficulty [easy\|medium\|hard]` | .json/.md/.html |

모든 generate 명령은 `-s <source_id>`, `--language`, `--json`, `--retry N` 옵션 지원.

---

## Processing Times

| Operation | Typical time | Suggested timeout |
|-----------|--------------|-------------------|
| Source processing | 30s - 10 min | 600s |
| Research (fast) | 30s - 2 min | 180s |
| Research (deep) | 15 - 30+ min | 1800s |
| Mind-map | instant (sync) | n/a |
| Quiz, flashcards | 5 - 15 min | 900s |
| Report, data-table | 5 - 15 min | 900s |
| Audio generation | 10 - 20 min | 1200s |
| Video generation | 15 - 45 min | 2700s |

장시간 작업은 subagent 패턴 사용 권장: `generate --json` → artifact_id 파싱 → 백그라운드 에이전트에서 `artifact wait` + `download`.

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| Auth/cookie error | 세션 만료 | `notebooklm auth check` → `notebooklm login` |
| "No notebook context" | 컨텍스트 미설정 | `notebooklm use <id>` 또는 `-n <id>` |
| "No result found for RPC ID" | Rate limiting | 5-10분 대기 후 재시도 |
| `GENERATION_FAILED` | Google rate limit | 대기 후 재시도 |
| Download fails | 생성 미완료 | `artifact list`로 상태 확인 |

실패 시 사용자에게 선택지 제시: (1) 재시도, (2) 건너뛰기, (3) 에러 조사.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 성공 |
| 1 | 에러 (not found, processing failed) |
| 2 | 타임아웃 (wait 명령 전용) |

---

## Troubleshooting

```bash
notebooklm --help              # 전체 명령어
notebooklm auth check --test   # 인증 전체 검증
notebooklm doctor              # 환경 점검
notebooklm doctor --fix        # 자동 수정
notebooklm --version           # 버전 확인
```

---

## 참고: 위키와 연동

`/wiki add --nblm <source>` 또는 자연어 "노트북LM 가져와"로 호출하면 이 스킬을 경유해서 NotebookLM 리포트를 만들고 `raw/sources/YYYY-MM-DD-<slug>-nblm.md`로 저장됩니다. 상세는 wiki 스킬의 "NotebookLM 경유" 섹션 참조.
