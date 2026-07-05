# Mainframe Explorer

The **Mainframe Explorer** is an ISPF 3.4-style dataset list. You enter a
dataset-name *level* (a high-level-qualifier pattern), get back a table of the
matching datasets, drill a PDS into its members, and **Browse** or **Edit** any
sequential dataset or member — all over z/OSMF, with no 3270 terminal.

It builds on the same Zowe connection profiles and credential handling as
**Open Mainframe Dataset** and **Save Query to Mainframe**; set those up first in
the [Zowe Connection Manager](#prerequisites).

> **Requires Java 11 or later.** Mainframe integration features are hidden when running on Java < 11.

```
┌── Mainframe Explorer ─────────────────────────────────────────┐
│ Alias     [ PROD ▾ ] [⚙]                                       │
│ User      [ KJE2          ]                                    │
│ Password  [ ********       ] [Show]                            │
│ Dsname Level [ KJE2.**            ▾ ]            [ List ]      │
├───────────────────────────────────────────────────────────────┤
│ Level: KJE2.**                                                 │
│ ┌───────────────────┬─────┬────────┬───────┬───────┐          │
│ │ Name              │ Org │ Volume │ RECFM │ LRECL │          │
│ ├───────────────────┼─────┼────────┼───────┼───────┤          │
│ │ KJE2.JCL.CNTL     │ PO  │ WRK001 │ FB    │ 80    │          │
│ │ KJE2.SOURCE.DATA  │ PS  │ WRK002 │ VB    │ 255   │          │
│ │ ...                                              │          │
│ └───────────────────┴─────┴────────┴───────┴───────┘          │
│ 12 dataset(s) for KJE2.**                          [ Close ]  │
└───────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

The Explorer is only useful when the optional mainframe-integration JAR is on
Sui's classpath (`SUI.CLASSPATH.N` in `SuiCPProp.pro`) **and** at least one Zowe
connection is configured.

1. **Java 11 or later** is required for all mainframe features.
2. **File → Zowe Connection Manager…** — create a connection *alias* with:
   - z/OSMF server hostname and port (default 443)
   - Mainframe code page (e.g., IBM-1047)
   - Default user ID
   - **TLS certificate validation** — toggle to accept self-signed certificates
   - **Certificate Source** — strategy for TLS validation (see [Certificate Handling](#certificate-handling) below)
   - **Custom Truststore** — path to truststore file if using CUSTOM certificate source

3. The integration JAR must expose the dataset-list methods described under
   [Integration contract](#integration-contract).

If the JAR is missing, no alias exists, or you're running Java < 11, the menu item
explains what to fix instead of opening.

---

## Opening it

**File → Mainframe Explorer…**

The window is **modeless** — leave it open while you browse results in separate
windows or edit a loaded dataset in the main query editor.

| Field | Meaning |
|-------|---------|
| **Alias** | The configured Zowe connection to use. The ⚙ button opens the Zowe Connection Manager and refreshes the list on return. |
| **User** | Defaults to the alias's configured user; override per session. |
| **Password** | Held in memory for this session only — never written to disk. **Show** reveals it. |
| **Dsname Level** | The z/OSMF *dslevel* pattern to list (see below). Remembers recently-used levels per alias. |

### Dsname level patterns

The **Dsname Level** uses z/OSMF `dslevel` matching:

| Pattern | Matches |
|---------|---------|
| `KJE2`        | Everything under the `KJE2` high-level qualifier |
| `KJE2.*`      | One more qualifier, e.g. `KJE2.JCL` (not `KJE2.JCL.CNTL`) |
| `KJE2.**`     | Any number of further qualifiers |
| `KJE2.*.CNTL` | A middle wildcard, e.g. `KJE2.JCL.CNTL` |

`*` matches exactly one qualifier; `**` matches any number. 

**Validation:** Pattern must contain alphanumeric characters, dots (.), and asterisks (*) only; and must contain at least one dot to separate qualifiers. Click **List** (or press Enter) to run the query.

**Error examples:**
- `MY-HLQ.**` — hyphens not allowed ❌
- `SYS1` — missing dot separator ❌

---

## Working with the list

```
                  double-click PO ─▶ member list ─▶ double-click ─▶ Browse
   dataset list ──┤
                  double-click PS ─────────────────────────────▶ Browse
```

| Action | Result |
|--------|--------|
| **Double-click a PDS/PDSE** (`Org` = `PO…`) | Drills into its **member list** |
| **Double-click a sequential dataset** (`Org` = `PS`) | **Browses** it |
| **Double-click a member** | **Browses** that member |
| **◀ Back** | Returns from a member list to the dataset list |
| **Right-click a row** | Opens the line-command menu (below) |

### Right-click line commands

| Command | Available on | Effect |
|---------|--------------|--------|
| **Browse** | sequential dataset / member | Opens the content in a read-only result grid (one row per record), exactly like *Open Mainframe Dataset*. |
| **Edit (load into editor)** | sequential dataset / member | Loads the content into the main SQL editor and records the dataset in history, so **File → Save Query to Mainframe** has it ready to write back. |
| **Open Members** | PDS / PDSE | Drills into the member list (same as double-click). |

### Columns

| Column | Source (z/OSMF) | Notes |
|--------|-----------------|-------|
| **Name** | `dsname` / `member` | Dataset name, or member name when inside a PDS |
| **Org** | `dsorg` | `PS` sequential, `PO`/`PO-E` partitioned |
| **Volume** | `vol` | Remapped to the `volser` row key |
| **RECFM** | `recfm` | Record format, e.g. `FB`, `VB` |
| **LRECL** | `lrecl` | Logical record length |

Attribute columns are blank for datasets where z/OSMF does not return the value
(e.g. migrated datasets). Members show only the **Member** column in the MVP.

---

## Browse vs. Edit

- **Browse** is read-only and opens a separate
  [Result Window](QueryRepWindow.md) — handy for scanning many datasets without
  disturbing your current query.
- **Edit** replaces the main editor's content with the dataset text. After
  editing, write it back with **File → Save Query to Mainframe** (the dataset is
  pre-listed in that dialog's dropdown because the Explorer records every opened
  dataset in the shared per-alias history). Saving only ever writes to an
  **existing** dataset/member — see the safety rules in that dialog.

---

## Certificate Handling

Sui supports three strategies for TLS certificate validation when connecting to Zowe:

### WINDOWS-ROOT (Windows only; default on Windows)
Uses the Windows certificate store via Java's `SunMSCAPI` provider.
- **Best for:** Windows enterprise environments with GPO-deployed certificates
- **Setup:** Add certificates to Windows **Trusted Root Certification Authorities** store via Windows Certificate Manager
- **Advantages:** No Java truststore needed; certificates follow Windows profile to different machines

### JAVA (default on macOS/Linux)
Uses the standard Java truststore (system default).
- **Best for:** Systems with standard CA certificates
- **No configuration required** — uses platform default truststore
- **Advantages:** Corporate certificates in system truststore are automatically recognized

### CUSTOM
Uses a custom truststore file (`.jks` or `.p12` format).
- **Best for:** Isolated environments or custom certificate chains
- **Setup:** Select "CUSTOM" in Zowe Connection Manager, click "Browse", choose your truststore file
- **Advantages:** Full control over trusted certificates

### TLS Validation Toggle
Additionally, a separate **"Validate TLS Certificate"** checkbox controls whether certificate validity is enforced:
- **Checked (default):** Validates certificate against configured truststore
- **Unchecked:** Accepts any certificate, including self-signed (less secure; **dev/test only**)

---

## Input Validation

### Dataset Names
Validated before reading/writing to prevent runtime errors.
- **Sequential:** `MY.DATASET.NAME` ✓
- **PDS Member:** `MY.PDS.LIB(MEMBER)` ✓
- **Error:** Unclosed parenthesis: `MY.PDS(MEMBER` ❌

### User Credentials
- **User ID** is required (defaults to alias's configured user; can override per session)
- **Password** is required; kept in-memory only (never written to disk)

### Port Number
- Must be a valid integer between 1 and 65535
- **Error:** `"Port must be a number between 1 and 65535"`

### Dataset Level Patterns
- Characters: Alphanumeric (A-Z, 0-9), dots (.), asterisks (*) only
- Must contain at least one dot to separate qualifiers
- `*` = one qualifier, `**` = multiple qualifiers

---

## Errors

**Validation errors:**
- `"Invalid dsname level \"MY-HLQ.*\"...Use alphanumeric, dots (.), asterisks (*) only."` — Pattern contains invalid characters
- `"Dsname level must contain at least one dot (.)"` — Pattern missing dot separator
- `"Enter a user id."` — User field is empty
- `"Enter a password."` — Password field is empty
- `"Port must be a number between 1 and 65535"` — Port configuration is invalid

**Network and z/OSMF errors** (bad pattern, `HTTP 404`, authentication failures)
appear in red in the status line and in a dialog, carrying the full diagnosis
the integration layer reports (HTTP status plus the z/OSMF response body).

---

## Related properties

The Explorer reuses the Zowe connection profiles and history mechanisms.

| Key (file) | Purpose |
|------------|---------|
| `SUI.ZOWE.ALIAS.N` … (`zoweconfig.pro`) | Connection profiles (server, port, user, codepage) |
| `SUI.ZOWE.<alias>.REJECTUNAUTHORIZED` (`zoweconfig.pro`) | TLS validation toggle (true/false; default: true) |
| `SUI.ZOWE.<alias>.CERTSOURCE` (`zoweconfig.pro`) | Certificate strategy: WINDOWS-ROOT \| JAVA \| CUSTOM (default: WINDOWS-ROOT on Windows, JAVA otherwise) |
| `SUI.ZOWE.<alias>.CUSTOMTRUSTSTORE` (`zoweconfig.pro`) | Path to custom truststore file (.jks or .p12); used only when CERTSOURCE=CUSTOM |
| `<alias>.pw` (in-memory `TmpProp2`) | Session-only password, shared with Open/Save |
| `<alias>.DSHIST.<n>` (`TmpProp.pro`) | Recently-opened datasets, shared with Open/Save |
| `<alias>.LVLHIST.<n>` (`TmpProp.pro`) | Recently-used dsname levels for the Explorer (up to 100 per alias) |

---

## Integration contract

Sui has no compile-time dependency on the mainframe JAR; everything is called by
reflection through Sui's extended class loader, centralised in `ZoweService`.
The Explorer requires two list methods on
`com.sui.mainframe.datasets.ZoweDatasetService` in addition to the read/write
methods used by Open/Save:

```java
// dslevel pattern, e.g. "KJE2.**"   (* = one qualifier, ** = any number)
List<Map<String,String>> listDatasets(String level) throws ... ;

// members of a PDS / PDSE
List<Map<String,String>> listMembers(String pds) throws ... ;
```

Each row is a `Map<String,String>` (only `java.util.*` types cross the
reflection boundary, so they cast cleanly regardless of class loader).
Recognised keys — all optional except the name; missing keys render as a blank
cell:

| Map key | z/OSMF field | Used for |
|---------|--------------|----------|
| `dsname` | `dsname` | dataset name |
| `dsorg`  | `dsorg`  | `PS` / `PO` detection (drill-down) |
| `volser` | `vol`    | Volume column *(note the field rename)* |
| `recfm`  | `recfm`  | RECFM column |
| `lrecl`  | `lrecl`  | LRECL column |
| `member` | `member` | member name (from `listMembers`) |

Implementation notes for the JAR side:

- Endpoints: `GET /zosmf/restfiles/ds?dslevel={level}` (add header
  `X-IBM-Attributes: base` for the attribute fields) and
  `GET /zosmf/restfiles/ds/{pds}/member`.
- Send `X-CSRF-ZOSMF-HEADER` on GETs (z/OSMF rejects requests without it).
- Cap large results with `X-IBM-Max-Items`.
- Return empty strings (not `null`) for absent attributes.

`ZoweService` tolerates a plain `String` element in place of a map (treated as
the name), so a minimal first cut of the JAR can return just names.

---

## See also

- [Connection Manager](ConnManager.md)
- [Credential handling](CredentialHandling.md)
- [Result window](QueryRepWindow.md)
- [Query sheets and tabs](QuerySheetsAndTabs.md)
