# Sui — Credential Handling (User ID and Password)

## Overview

By default, Sui keeps credentials in memory only for the duration of the session.
The password is **never written to disk unless the user explicitly chooses to save it**
through the Login/Preferences dialog. This is intentional and is the recommended mode
of operation for all corporate and security-sensitive environments.

---

## How credentials flow through the application

### 1. Startup — loading from disk

`Sui.LoadProp()` reads `SuiSys.pro` into the `SysProp` property object.

- `SUI.USERID` is read and placed in the `Uid` text field.
- `SUI.PW` is read (if present) into the static `Passw` field and placed in the `Pw` password field.

If `SUI.PW` is absent from `SuiSys.pro` (the default), `Passw` is `null` and the password
field is left blank — the user must type the password at each session start.

The userid field also supports two special values:

| Value | Behaviour |
|-------|-----------|
| `?`   | Replaced at startup with the OS-logged-on username (`user.name`). |
| `?L`  | Same as `?` but also makes the userid field non-editable. |

---

### 2. Manual connect — `Sui.ConnDB()`

When the user clicks **Connect** (or presses `Ctrl+D`):

1. `Passw = Pw.getText()` — the current password field value is copied to the static `Passw` field.
2. `new ConnDB(url, Userid, Passw)` — a JDBC connection is established via `ConnDB`.
3. On success, the password is cached in the in-memory `TmpProp2` map:
   ```
   SUI.PW.<userid>.<url>  →  current password
   ```
   `TmpProp2` is **never written to disk**, so this cache exists only for the lifetime of the JVM.

---

### 3. Session-level in-memory cache

Several components re-use the per-session cache to avoid re-prompting:

| Component | Key written | Key read |
|-----------|-------------|----------|
| `Sui.ConnDB()` | `SUI.PW.<uid>.<url>` in `TmpProp2` | — |
| `ConnDB.getConn()` | `SUI.PW.<uid>.<url>` in `TmpProp2` | — |
| `TabbedPaneClassic` | `PW.<tabNo>` in `TmpProp2` | `PW.<tabNo>` in `TmpProp2` |
| `ProfProp` | — | `SUI.PW.<uid>.<url>` in `TmpProp` / `TmpProp2` |
| `AppendToTable`, `SQLSeqComp` | — | `SUI.PW.<uid>.<url>` in `TmpProp2` |

All reads fall back gracefully to an empty string if the key is not present, so nothing
breaks if the cache is cold (e.g. after an application restart).

---

### 4. Alt-key profiles (Alt+0 … Alt+9)

Up to ten named connection profiles can be configured, each storing a userid, password,
URL and desktop prefix under keys `SUI.USERID`, `SUI.PW`, `SUI.URLX`, `SUI.DRIVERX`,
`SUI.DESKTOP` at index `k` in `SysProp`.

Selecting `Alt+k` calls `setAltKey(k)`, which reads `SUI.PW` at index `k` from `SysProp`
and populates the `Pw` field. If the user saved a password for that profile (see section 5),
it will be pre-filled.

---

### 5. The only path to disk — user-initiated save

The password reaches disk via **one path only**:

```
Propm (Sui Preferences)  →  PutAppProp("SUI.PW", ...)  →  SysProp
PropmLogin (Login panel) →  PutAppProp("SUI.PW", ...)  →  SysProp
                                                               ↓
                                                 StoreProp() writes SuiSys.pro
```

Both `Propm` and `PropmLogin` contain a password field. If the user types a value there
and saves, `SUI.PW` is written to `SuiSys.pro` in plain text.

> **Warning:** `SuiSys.pro` is a plain-text Java Properties file. Any password stored
> there is readable by anyone with file-system access to the Sui home directory.
> **Do not save passwords to this file in corporate, shared, or security-sensitive
> environments.** Leave the password field blank in the preferences dialogs and type
> the password at each session start instead.

To remove a saved password: open **Sui Preferences → Login**, clear the password field,
and save. `SUI.PW` will be written as an empty string and the field will be blank on next
startup.

---

## Summary table — where the password lives

| Store | Object | File | Written to disk? | Cleared on exit? |
|-------|--------|------|-----------------|-----------------|
| `SysProp` | `Properties` | `SuiSys.pro` | Only if user saves in Preferences | No — persists across sessions |
| `TmpProp2` (session cache) | `Properties` | *(none)* | Never | Yes — JVM exit |
| `Pw` Swing field | `JPasswordField` | *(none)* | Never | Yes — JVM exit |
| `Passw` static field | `String` | *(none)* | Never | Yes — JVM exit |

---

## Recommendations

- **Do not save the password** in Sui Preferences for any database that holds sensitive
  or corporate data.
- Use `SUI.USERID=?` or `SUI.USERID=?L` to avoid storing the userid as well, taking it
  from the OS login instead.
- Protect the Sui home directory (`SuiHome`) with appropriate OS-level file permissions
  so that `SuiSys.pro` (and the other `.pro` files) are not world-readable.
- For high-security environments, consider using JDBC URL parameters that support
  external credential stores (e.g. Kerberos or IAM-based authentication), so that no
  password needs to be managed by Sui at all.
