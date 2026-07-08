# Caller Index (generated — do not edit)

Regenerate: `python hooks/build_index.py`
Who references each function (crude name match). Read this to state blast radius before editing.

- `attempt` — defined at hooks/keepalive.py:26 — called by: hooks/keepalive.py:46
- `beads_snapshot` — defined at hooks/session_start.py:17 — called by: hooks/session_start.py:45
- `body_fingerprint` — defined at hooks/check_duplicates.py:18 — called by: hooks/check_duplicates.py:45
- `caller_lines` — defined at hooks/build_index.py:46 — called by: hooks/build_index.py:83
- `collect` — defined at hooks/check_duplicates.py:24 — called by: hooks/check_duplicates.py:51
- `dangling_beads` — defined at hooks/stop_gate.py:39 — called by: hooks/stop_gate.py:99
- `deny` — defined at hooks/pre_tool.py:54 — called by: hooks/pre_tool.py:74, hooks/pre_tool.py:85, hooks/pre_tool.py:91
- `duplicate_defs` — defined at hooks/pre_tool.py:35 — called by: hooks/pre_tool.py:89, hooks/test_pre_tool.py:32, hooks/test_pre_tool.py:34, hooks/test_pre_tool.py:36, hooks/test_pre_tool.py:38
- `first_line` — defined at hooks/build_index.py:18 — called by: hooks/build_index.py:40, hooks/build_index.py:42
- `index_lines` — defined at hooks/build_index.py:34 — called by: hooks/build_index.py:77
- `is_dep_install` — defined at hooks/pre_tool.py:28 — called by: hooks/pre_tool.py:73, hooks/test_pre_tool.py:12, hooks/test_pre_tool.py:13, hooks/test_pre_tool.py:14, hooks/test_pre_tool.py:15, hooks/test_pre_tool.py:16, hooks/test_pre_tool.py:17, hooks/test_pre_tool.py:18, hooks/test_pre_tool.py:19
- `llm_review` — defined at hooks/stop_gate.py:56 — called by: hooks/stop_gate.py:105
- `load_files` — defined at hooks/audit.py:242 — called by: hooks/audit.py:276
- `main` — defined at hooks/audit.py:256 — called by: hooks/audit.py:293, hooks/build_index.py:93, hooks/check_duplicates.py:67, hooks/keepalive.py:61, hooks/launch.py:45, hooks/post_edit.py:45, hooks/pre_tool.py:96, hooks/session_start.py:50, hooks/stop_gate.py:113
- `r_abstraction` — defined at hooks/audit.py:105 — called by: no references found
- `r_bare_except` — defined at hooks/audit.py:84 — called by: no references found
- `r_dead` — defined at hooks/audit.py:179 — called by: no references found
- `r_duplicates` — defined at hooks/audit.py:59 — called by: no references found
- `r_long` — defined at hooks/audit.py:122 — called by: no references found
- `r_missing_docstring` — defined at hooks/audit.py:225 — called by: no references found
- `r_print` — defined at hooks/audit.py:132 — called by: no references found
- `r_stale_index` — defined at hooks/audit.py:72 — called by: no references found
- `r_stale_worktree` — defined at hooks/audit.py:217 — called by: no references found
- `r_test_gaming` — defined at hooks/audit.py:142 — called by: no references found
- `r_todo` — defined at hooks/audit.py:95 — called by: no references found
- `r_wrapper` — defined at hooks/audit.py:161 — called by: no references found
- `rule` — defined at hooks/audit.py:48 — called by: hooks/audit.py:58, hooks/audit.py:71, hooks/audit.py:83, hooks/audit.py:94, hooks/audit.py:104, hooks/audit.py:121, hooks/audit.py:131, hooks/audit.py:141, hooks/audit.py:160, hooks/audit.py:178, hooks/audit.py:216, hooks/audit.py:224
- `source_files` — defined at hooks/build_index.py:23 — called by: hooks/build_index.py:76
- `test_dep_install_detection` — defined at hooks/test_pre_tool.py:11 — called by: hooks/test_pre_tool.py:42
- `test_duplicate_def_detection` — defined at hooks/test_pre_tool.py:22 — called by: hooks/test_pre_tool.py:43
