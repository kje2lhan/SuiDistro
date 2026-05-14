# Sui — Credential Handling (User ID and Password)

## Overview

By default, Sui keeps credentials in memory only for the duration of the session.
The password is **never written to disk unless the user explicitly chooses to save it**.
This is intentional and is the recommended mode of operation for all corporate and
security-sensitive environments.

Credentials are sourced from two places — the **Connection Manager** (per-URL profiles)
and the **Startup Preferences** (generic defaults) — with a clear priority order.

---

## Credential sources

### Source A — Connection Manager profiles (`SuiConnProp.pro`)

The Connection Manager stores named connection profiles under:

```
SUI.CONN.<alias>.USERID     — user ID for this connection
SUI.CONN.<alias>.PW         — password (only written when Auto-login = Y)
SUI.CONN.<alias>.AUTOLOGIN  — Y / N
```

- `USERID` is always written to disk when saved (if non-empty).
- `PW` is written **only when Auto-login is ticked**. Without Auto-login the sentinel
  value `null` is stored in its place and the password field is blank on startup.
- **BigQuery profiles**: the Auto-login checkbox and password field are disabled in
  ConnManager because BigQuery uses OAuth web-login and does not accept a stored password.

### Source B — Startup Preferences (`SuiSys.pro`)

The generic preferences panel stores:

```
SUI.USERID   — default user ID (applies when no per-URL profile exists)
SUI.PW       — default password (applies when no per-URL profile exists)
SUI.AUTOC    — Y / N: auto-connect at startup using the generic credentials
```

Special values for `SUI.USERID`:

| Value | Behaviour |
|-------|-----------|
| `?`   | Replaced at startup with the OS-logged-on username (`user.name`). |
| `?L`  | Same as `?` but also makes the userid field non-editable. |

### Source C — Session cache (`TmpProp2`, memory only)

Once the user connects, the credentials are cached in the in-memory `TmpProp2` map:

```
SUI.PW.<userid>.<url>  →  password used for this userid + URL combination
```

`TmpProp2` is **never written to disk** and is cleared on JVM exit. It is used to
restore credentials silently when switching back to a URL that was already connected
during the current session.

> **Note on `TmpProp`:** The `TmpProp` map is persisted to `TmpProp.pro` between
> sessions. It previously stored `SUI.USERID.<url>` entries from prior sessions.
> At startup these are now **purged before the URL list is populated** so that stale
> values from a previous session cannot override the credential priority rules below.

---

## Credential priority at startup and on URL selection

The same three-level priority applies both when Sui starts (first URL in the combo)
and whenever the user selects a different URL:

### Level 1 — ConnManager profile for the selected URL

If the selected URL matches a saved alias in `SuiConnProp.pro` **and** that alias has
a non-empty `USERID`:

- The profile userid is placed in the `Uid` field.
- If `AUTOLOGIN=Y` **and** a password is stored: the password is pre-filled and
  (at startup only) an automatic connect is attempted.
- If `AUTOLOGIN=N` (or no password stored): the password field is left blank.

### Level 2 — Generic startup preferences (fallback)

If the selected URL has no matching profile, or the profile has no userid:

- `SUI.USERID` from preferences is used (with `?` / `?L` expansion).
- `SUI.PW` from preferences is used as the password.
- At startup: if `SUI.AUTOC=Y` and the password is non-empty, an automatic connect
  is attempted.

### Level 3 — Neither source has credentials

Both `Uid` and `Pw` fields are set to blank. No auto-connect is attempted.

### Override: `SUI.SETPWBLANK=Y`

When the preference **Set PW blank if not connected** (`SUI.SETPWBLANK=Y`) is enabled
it takes precedence over Levels 1 and 2:

- The password field is always cleared on startup and on every URL selection.
- Auto-login is suppressed regardless of the profile's `AUTOLOGIN` setting.
- The user must type the password manually before connecting.

---

## Manual connect — `Sui.ConnDB()`

When the user clicks **Connect** (or presses `Ctrl+D`):

1. The current `Uid` and `Pw` field values are used for the JDBC connection.
2. On success, credentials are written to the session cache:
   ```
   SUI.PW.<userid>.<url>   in TmpProp2   (memory only)
   SUI.USERID.<url>        in TmpProp    (persisted to TmpProp.pro)
   ```
3. These cache entries are consulted first on subsequent URL selections within
   the same session so the user is not re-prompted.

---

## Session-level in-memory cache

Several components re-use the per-session cache to avoid re-prompting:

| Component | Key written | Key read |
|-----------|-------------|----------|
| `Sui.ConnDB()` | `SUI.PW.<uid>.<url>` in `TmpProp2` | — |
| `ConnDB.getConn()` | `SUI.PW.<uid>.<url>` in `TmpProp2` | — |
| `TabbedPaneClassic` | `PW.<tabNo>` in `TmpProp2` | `PW.<tabNo>` in `TmpProp2` |
| `ProfProp` | — | `SUI.PW.<uid>.<url>` in `TmpProp2` |
| `AppendToTable`, `SQLSeqComp` | — | `SUI.PW.<uid>.<url>` in `TmpProp2` |

---

## Alt-key profiles (Alt+0 … Alt+9)

Up to ten named connection profiles can be configured, each storing a userid, password,
URL and desktop prefix under `SUI.USERID`, `SUI.PW`, `SUI.URLX` etc. at index `k` in
`SysProp`. Selecting `Alt+k` calls `setAltKey(k)`, which reads `SUI.PW` at index `k`
and populates the `Pw` field.

---

## Paths to disk — where passwords can be written

```
ConnManager (Auto-login=Y)  →  PutConnProp("SUI.CONN.<alias>.PW", ...)  →  ConnProp
                                                                                ↓
                                                               StoreConnProp() writes SuiConnProp.pro

Propm / PropmLogin           →  PutAppProp("SUI.PW", ...)               →  SysProp
                                                                                ↓
                                                               StoreProp()  writes SuiSys.pro
```

> **Warning:** Both `SuiConnProp.pro` and `SuiSys.pro` are plain-text Java Properties
> files in the Sui home directory. Any password stored there is readable by anyone with
> file-system access. **Do not save passwords in corporate, shared, or
> security-sensitive environments.** Leave Auto-login off and the password blank in the
> preferences dialogs; type the password at each session start instead.

---

## Summary table — where the password lives

| Store | Object | File | Written to disk? | Cleared on exit? |
|-------|--------|------|-----------------|-----------------|
| `ConnProp` | `Properties` | `SuiConnProp.pro` | Only when Auto-login=Y in ConnManager | No — persists across sessions |
| `SysProp` | `Properties` | `SuiSys.pro` | Only if user saves in Preferences | No — persists across sessions |
| `TmpProp2` (session cache) | `Properties` | *(none)* | Never | Yes — JVM exit |
| `TmpProp` (session/url uid cache) | `Properties` | `TmpProp.pro` | Yes, but purged at next startup | Purged at startup |
| `Pw` Swing field | `JPasswordField` | *(none)* | Never | Yes — JVM exit |
| `Passw` static field | `String` | *(none)* | Never | Yes — JVM exit |

---

## Recommendations

- **Prefer ConnManager profiles** over generic preferences for per-database credentials.
  Enable Auto-login only on machines where `SuiConnProp.pro` is adequately protected.
- Use `SUI.USERID=?` or `SUI.USERID=?L` in preferences so the OS login name is used
  automatically without storing anything.
- Enable **Set PW blank if not connected** (`SUI.SETPWBLANK=Y`) in environments where
  passwords must never be pre-filled from disk.
- Protect the Sui home directory with appropriate OS-level file permissions so that
  `SuiSys.pro` and `SuiConnProp.pro` are not world-readable.
- For high-security environments, prefer JDBC authentication mechanisms that do not
  require a password in Sui at all (e.g. Kerberos, IAM, OAuth web-login for BigQuery).
