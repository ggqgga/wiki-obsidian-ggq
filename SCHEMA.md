# my-wiki — personal knowledge base Knowledge Base

## Wiki Structure

```
raw/                  # Immutable source documents (paste originals here)
  my_folder/               # 사용자가 직접 쓴 글 (메모, 아이디어, 일지)
  sources/            # 외부 텍스트 소스 (articles, books, papers, youtube 등)
  assets/             # Downloaded images and files
wiki/                 # LLM-generated pages (all knowledge lives here)
  index.md            # Master index of all pages
  log.md              # Chronological activity log
  entities/           # People, orgs, products
  concepts/           # Ideas, frameworks, theories
  sources/            # One summary per ingested source
  insights/           # Cross-cutting analysis, insights
Output/               # Final deliverables (AI + user)
```

## Page Format

Every wiki page should use YAML frontmatter:

```markdown
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
source: URL or description
---

Page content here. Use [[wikilinks]] to connect pages.
```

## Wikilink Syntax

- `[[page-name]]` — links to a page (resolved by filename across all wiki directories)
- `[[page-name|Display Text]]` — link with custom display text

## CLI Commands

### Wiki Management
```bash
wiki init [dir] --name <name> --domain <domain>   # Create new wiki
wiki registry                                       # List all wikis
wiki use [wiki-id]                                  # Set active wiki
## GitHub auth는 `gh auth login` 사용 (llmwiki-cli에 auth 없음)
```

### Reading & Writing
```bash
wiki read <path>                                    # Print page to stdout
wiki write <path> <<'EOF'                           # Write page (create/overwrite)
content here
EOF
wiki append <path> <<'EOF'                          # Append to page
additional content
EOF
wiki list [dir] [--tree] [--json]                   # List pages
wiki search <query> [--limit N] [--all] [--json]    # Search pages (grep)
```

### Index & Log
```bash
wiki index show                                     # Print master index
wiki index add <path> <summary>                     # Add entry to index
wiki index remove <path>                            # Remove entry from index
wiki log show [--last N] [--type T]                 # Print log entries
wiki log append <type> <message>                    # Append log entry
```

### Git Operations (위키 루트에서 직접 실행)

llmwiki-cli에 git 명령은 포함되어 있지 않다. 위키 루트 디렉토리에서 직접 git을 실행한다.

```bash
cd <wiki-root> && git add -A && git commit -m "<message>"   # Commit
cd <wiki-root> && git log --oneline -N                       # History
cd <wiki-root> && git diff [ref]                             # Diff
cd <wiki-root> && git push                                   # Push
cd <wiki-root> && git pull                                   # Pull
cd <wiki-root> && git pull --rebase && git push              # Sync (pull → push)
```

### Health & Links
```bash
wiki lint [--json]                                  # Health check
wiki links <path>                                   # Outbound + inbound links
wiki backlinks <path>                               # Inbound links only
wiki orphans                                        # Pages with no inbound links
wiki status [--json]                                # Wiki overview stats
```

## Search (qmd integration)

llmwiki-cli의 `wiki search`는 경량 grep 검색이다. 고품질 검색이 필요할 때는 [qmd](https://github.com/tobi/qmd)를 사용한다.

### Setup (최초 1회)
```bash
# qmd 설치
npm install -g @tobilu/qmd

# 컬렉션 등록
qmd collection add <wiki-path>/wiki --name <wiki-id>
qmd context add qmd://<wiki-id> "<wiki description>"
qmd embed
```

### Hybrid Search (권장)
BM25 + 벡터 + Query Expansion + Re-ranking. 가장 높은 품질.
```bash
qmd query "<query>" -c <wiki-id> [-n <limit>] [--json] [--explain]
```

### Vector Search
시맨틱 유사도 기반. 정확한 키워드를 모를 때 유용.
```bash
qmd vsearch "<query>" -c <wiki-id> [-n <limit>] [--json]
```

### Index Refresh
위키 페이지 변경 후 검색 인덱스 갱신:
```bash
qmd update && qmd embed
```

## Ingest Workflow

When ingesting a new source:

1. Save the raw source to `raw/` (paste full text, keep immutable)
2. Create a source summary page in `wiki/sources/`
3. Extract entities → create/update pages in `wiki/entities/`
4. Extract concepts → create/update pages in `wiki/concepts/`
5. If cross-cutting insights emerge → create `wiki/insights/` pages
6. Update `wiki/index.md` with new entries
7. Append to `wiki/log.md` with ingest activity
8. Refresh search index: `qmd update && qmd embed`
9. Commit: `wiki commit "ingest: <source description>"`

## Query Workflow

When answering a question using the wiki:

1. `wiki search "<query terms>"` or `qmd query "<query>"` to find relevant pages
2. `wiki read <path>` to read promising results
3. Follow [[wikilinks]] to gather connected knowledge
4. Synthesize answer from wiki content
5. Log the query: `wiki log append query "<question summary>"`

## Lint Workflow

Periodically check wiki health:

1. `wiki lint` to find issues (broken links, orphans, missing frontmatter)
2. Fix broken links by creating missing pages or updating references
3. Connect orphan pages by adding wikilinks from related pages
4. Add frontmatter to pages missing it
5. Commit fixes: `wiki commit "maintenance: fix lint issues"`

## Conventions

1. File names use kebab-case: `my-topic-name.md`
2. One topic per file. Split large topics into sub-topics.
3. Always update index.md when adding/removing pages.
4. Always append to log.md when making changes.
5. Use [[wikilinks]] to connect related pages.
6. Prefer updating existing pages over creating new ones — avoid duplicates.
7. Include the source of knowledge when possible.
8. Prefer concrete examples over abstract descriptions.
9. Sources (`wiki/sources/`) contain facts only; interpretation goes in concepts (`wiki/concepts/`).
10. Use callouts for important notes:
    - `> [!NOTE]` for general notes
    - `> [!WARNING]` for contradictions or caveats — cite both sources
    - `> [!TIP]` for best practices
