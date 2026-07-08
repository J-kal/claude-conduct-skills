# Caller Index (generated — do not edit)

Regenerate: `python hooks/build_index.py`
Who references each function (crude name match). Read this to state blast radius before editing.

- `attempt` — defined at hooks/keepalive.py:26 — called by: hooks/keepalive.py:46
- `audit_level` — defined at hooks/config.py:37 — called by: hooks/post_edit.py:37, hooks/session_start.py:43, hooks/stop_gate.py:86, hooks/test_pre_tool.py:19, hooks/test_pre_tool.py:21, hooks/test_pre_tool.py:23, hooks/test_pre_tool.py:26, hooks/test_pre_tool.py:27
- `beads_snapshot` — defined at hooks/session_start.py:20 — called by: hooks/session_start.py:51
- `body_fingerprint` — defined at hooks/check_duplicates.py:18 — called by: hooks/check_duplicates.py:45
- `caller_lines` — defined at hooks/build_index.py:46 — called by: hooks/build_index.py:83
- `collect` — defined at hooks/check_duplicates.py:24 — called by: hooks/check_duplicates.py:51
- `dangling_beads` — defined at hooks/stop_gate.py:42 — called by: hooks/stop_gate.py:104
- `deny` — defined at hooks/pre_tool.py:55 — called by: hooks/pre_tool.py:75, hooks/pre_tool.py:86, hooks/pre_tool.py:92
- `duplicate_defs` — defined at hooks/pre_tool.py:36 — called by: hooks/pre_tool.py:90, hooks/test_pre_tool.py:64, hooks/test_pre_tool.py:66, hooks/test_pre_tool.py:68, hooks/test_pre_tool.py:70
- `first_line` — defined at hooks/build_index.py:18 — called by: hooks/build_index.py:40, hooks/build_index.py:42
- `index_lines` — defined at hooks/build_index.py:34 — called by: hooks/build_index.py:77
- `is_dep_install` — defined at hooks/pre_tool.py:29 — called by: hooks/pre_tool.py:74, hooks/test_pre_tool.py:44, hooks/test_pre_tool.py:45, hooks/test_pre_tool.py:46, hooks/test_pre_tool.py:47, hooks/test_pre_tool.py:48, hooks/test_pre_tool.py:49, hooks/test_pre_tool.py:50, hooks/test_pre_tool.py:51
- `llm_review` — defined at hooks/stop_gate.py:59 — called by: hooks/stop_gate.py:106
- `load_config` — defined at hooks/config.py:26 — called by: hooks/post_edit.py:22, hooks/pre_tool.py:67, hooks/session_start.py:40, hooks/stop_gate.py:83, hooks/test_pre_tool.py:16, hooks/test_pre_tool.py:19, hooks/test_pre_tool.py:21, hooks/test_pre_tool.py:23
- `load_files` — defined at hooks/audit.py:242 — called by: hooks/audit.py:280
- `main` — defined at hooks/audit.py:256 — called by: hooks/audit.py:297, hooks/build_index.py:93, hooks/check_duplicates.py:67, hooks/keepalive.py:61, hooks/launch.py:54, hooks/post_edit.py:51, hooks/pre_tool.py:97, hooks/session_start.py:56, hooks/stop_gate.py:114
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
- `review_model` — defined at hooks/config.py:43 — called by: hooks/stop_gate.py:106, hooks/test_pre_tool.py:34, hooks/test_pre_tool.py:35, hooks/test_pre_tool.py:38
- `rule` — defined at hooks/audit.py:48 — called by: hooks/audit.py:58, hooks/audit.py:71, hooks/audit.py:83, hooks/audit.py:94, hooks/audit.py:104, hooks/audit.py:121, hooks/audit.py:131, hooks/audit.py:141, hooks/audit.py:160, hooks/audit.py:178, hooks/audit.py:216, hooks/audit.py:224
- `source_files` — defined at hooks/build_index.py:23 — called by: hooks/build_index.py:76
- `test_audit_level` — defined at hooks/test_pre_tool.py:12 — called by: hooks/test_pre_tool.py:76
- `test_dep_install_detection` — defined at hooks/test_pre_tool.py:43 — called by: hooks/test_pre_tool.py:74
- `test_duplicate_def_detection` — defined at hooks/test_pre_tool.py:54 — called by: hooks/test_pre_tool.py:75
- `test_review_model` — defined at hooks/test_pre_tool.py:32 — called by: hooks/test_pre_tool.py:77
