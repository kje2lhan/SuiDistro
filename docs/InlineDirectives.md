# Sui Inline Directives

Inline directives are special non-SQL statements that can be embedded in a Sui
query script. They begin with `#` and are processed by the `nonSQL` class before
the surrounding SQL statements are executed. A directive occupies its own
statement slot, separated from other statements by the configured statement
delimiter (default `;`).

---

## `#URL=` — Per-statement Connection Override

### Purpose

Redirects subsequent SQL execution to a different database without changing the
active connection shown in the URL box. This lets a single script query or
modify multiple databases in sequence.

### Syntax

```
#URL= <jdbc-url>
```

| Part | Description |
|---|---|
| `#URL` | Keyword (case-insensitive). |
| `=` | Separator — the `=` is part of the parsing split, not optional. |
| `<jdbc-url>` | The full JDBC URL of the target database. Must be the first (and only) token after `=`. Any additional tokens are ignored. |

### Example

```sql
SELECT * FROM prod_db.orders WHERE status = 'OPEN';

#URL= jdbc:db2://prodserver:50000/PRODDB;

SELECT COUNT(*) FROM reporting.summary;
```

In this script the first `SELECT` runs against the active connection. After the
`#URL=` directive the connection switches to `jdbc:db2://prodserver:50000/PRODDB`
and the second `SELECT` runs there.

### Credential Resolution

Credentials for the target URL are resolved in the following order. No password
dialog is shown — the lookup is entirely from the current session's in-memory
store.

1. **Userid** — looked up by key `SUI.USERID.<jdbc-url>`.  
   This key is written when you connect to a URL during the current session.  
   Fallback: the userid currently shown in the Sui userid field.

2. **Password** — looked up by key `SUI.PW.<userid>.<jdbc-url>`,  
   where `<userid>` is the userid resolved in step 1.  
   This key is written when you connect to a URL during the current session.  
   Fallback: the password currently held for the active connection.

> **Requirement:** The target database must have been connected to at least once
> during the current Sui session so that its credentials are cached in-memory.
> If the connection fails, an error is shown and script execution stops.

### Scope

The URL override applies to all SQL statements that follow the `#URL=` directive
within the same script execution. It is **reset at the start of each Run**
(`TMPURL` is cleared before the statement array is iterated), so it does not
carry over between separate runs.

### Query Report Title

When a Query Report window is opened for a statement that ran under a `#URL=`
override, its title shows the overriding URL rather than the URL-box URL:

```
Query Report - jdbc:db2://prodserver:50000/PRODDB - 10:23:45/1
```

---

## `#SET=` — Session Symbol Assignment

### Purpose

Sets a named session property that can be referenced as a symbolic variable
elsewhere in the script (subject to the Symbolic Resolution setting).

### Syntax

Two equivalent forms are supported:

```
#SET= <KEY> <value>
```
```
#SET <KEY>=<value>
```

| Part | Description |
|---|---|
| `#SET` | Keyword (case-insensitive). |
| `<KEY>` | Property key. |
| `<value>` | Property value. |

### Example

```sql
#SET= MYSCHEMA REPORTING;

SELECT * FROM &MYSCHEMA..ORDERS;
```

```sql
#SET MYSCHEMA=REPORTING;

SELECT * FROM &MYSCHEMA..ORDERS;
```

The value is stored via `Sui.PutTmpProp(KEY, value)` and is available for the
lifetime of the session.

### Using `#SET=` to Suppress the Prompt — the `&&` Prefix

The symbolic variable character (default `&`) has two forms:

| Reference | Behaviour |
|---|---|
| `&VARNAME` | Always prompts the user for a value (single `&`). |
| `&&VARNAME` | Uses the value from `TmpProp` **without prompting** if it is set; falls back to a single-`&` prompted variable if not set. |

This means `#SET=` combined with `&&` lets you define a value once and have it
substituted silently throughout the rest of the script:

```sql
#SET= ENV PROD;

SELECT * FROM &&ENV..ORDERS;
SELECT * FROM &&ENV..CUSTOMERS;
```

Both `SELECT` statements run with `ENV` replaced by `PROD` and no dialog appears.

If `&&ENV` is used but `ENV` has not been set (e.g. via `#SET=` or a previous
run), the double `&&` is reduced to a single `&ENV` and the user **is** prompted.

> **Note:** The variable substitution character can be changed from `&` via the
> `SUI.VARSUBS.CHAR` application property.

---

## `BATCH=YES` — Suppress Row-Count Confirmation

### Purpose

Runs all DML statements in the script (INSERT, UPDATE, DELETE) without showing
the "N rows affected — commit?" confirmation dialog after each one.  
Useful for generated scripts that contain many statements (e.g. a full table
load or a diff-generated sync script).

### Syntax

```
BATCH=YES;
```

`BATCH=YES` must appear as the **first statement** in the script (before any
SQL). It is case-insensitive. The trailing delimiter (`;` by default) is
required.

### Behaviour

| Without `BATCH=YES` | With `BATCH=YES` |
|---|---|
| Each UPDATE/DELETE/INSERT shows a dialog — "N rows affected. Commit?" | All statements execute without confirmation. |
| Script pauses after every DML statement | Script runs to completion without interruption. |
| User can commit or roll back each statement individually | All changes are committed automatically. |

### Example

```sql
BATCH=YES;

UPDATE orders SET status = 'CLOSED' WHERE order_date < '2024-01-01';
DELETE FROM audit_log WHERE created < '2023-01-01';
INSERT INTO archive SELECT * FROM old_orders;
```

> **Tip:** The Result Set Compare "Sync SQL" feature automatically prepends
> `BATCH=YES;` to the generated sync script so you can run it without
> clicking through a confirmation for every row.

---

## `PROFI=` — Profile-based Connection Switch

### Purpose

Switches the active JDBC connection to a named profile stored in `SuiConnProp.pro`
(the Connection Manager). This is an alternative to `#URL=` when you want to
reference a saved connection by its alias rather than spelling out the full URL.

### Syntax

```
PROFI= <alias>
```

| Part | Description |
|---|---|
| `PROFI` | Keyword (case-insensitive). |
| `=` | Separator. |
| `<alias>` | The connection alias exactly as defined in the Connection Manager. |

---

## `<include>` — SQL File Include

### Purpose

Replaces an `<include>...</include>` tag pair with the full contents of the
referenced file, before the statement is executed. Multiple include tags in a
single statement are resolved in order (iteratively), so included files can
themselves contain further `<include>` tags.

Unlike `#FILX=`, this uses an XML-style tag and can appear anywhere in a
statement, including mid-statement.

### Syntax

```sql
<include>filepath</include>
```

| Part | Description |
|---|---|
| `<include>` | Opening tag — literal, case-sensitive. |
| `filepath` | Absolute or relative path to the file to read. |
| `</include>` | Closing tag — literal, case-sensitive. |

The entire `<include>filepath</include>` span is replaced by the file's text
content. The tags themselves are removed.

### Example

```sql
SELECT department, employee, salary
FROM employees
WHERE
<include>C:\queries\filters\active_employees.sql</include>
ORDER BY department;
```

If `active_employees.sql` contains `status = 'ACTIVE' AND hire_date < CURRENT DATE`,
the executed statement becomes:

```sql
SELECT department, employee, salary
FROM employees
WHERE
status = 'ACTIVE' AND hire_date < CURRENT DATE
ORDER BY department;
```

### Nested Includes

Includes are resolved in a loop, so a file brought in by `<include>` may itself
contain further `<include>` tags. Resolution continues until no more tags remain
or a file cannot be found.

### Notes

- If the path does not point to an existing file, processing stops and a message
  is printed to stdout — the tag is **not** removed and execution will likely
  fail.
- File reading uses `FileUtils.readFileToString()` (Apache Commons IO) with the
  platform default encoding.
- Symbolic resolution (`Symb()`) is applied **before** include processing, so
  symbolic variables inside the surrounding SQL are expanded first.
- `<include>` is processed per statement before `#FILX=` checking occurs.

---

## `#FILX=` — Inline File Inclusion

### Purpose

Splices the contents of an external file into a SQL statement at the point where
the tag appears. Unlike `#URL=` and `#SET=`, this is not a standalone directive
statement — it is embedded *inside* a SQL statement and is processed as part of
that statement's text before execution.

### Syntax

```
<sql-before>#FILX=<filepath>;<sql-after>
```

| Part | Description |
|---|---|
| `<sql-before>` | Any SQL text preceding the tag (may be empty). |
| `#FILX=` | Trigger string — case-sensitive, no spaces around `=`. |
| `<filepath>` | Absolute or relative path to the file to include. Delimited by the next `;`. |
| `;` | Acts as the end-of-filepath delimiter, **not** the statement delimiter. |
| `<sql-after>` | Any SQL text following the `;` (the remainder of the statement). |

The tag and filepath are replaced in-place by the file's full text content. The
resulting concatenation (`sql-before + file-contents + sql-after`) is what gets
executed.

### Example

```sql
SELECT department, total
FROM (
#FILX=C:\queries\dept_totals_subquery.sql;
) t
ORDER BY total DESC;
```

The content of `dept_totals_subquery.sql` is read and inserted between the
`FROM (` and `) t ORDER BY ...` portions before the statement is sent to the
database.

### Notes

- If the file cannot be read, the content is `null` and execution will fail with
  a NullPointerException — ensure the path is correct and the file is readable.
- Symbolic resolution (`Symb()`) is applied to the statement **before** `#FILX=`
  is processed, so symbolic variables in the surrounding SQL are expanded first.
- The `;` that terminates the filepath is consumed by the parsing — it does not
  act as a statement delimiter.
- Only one `#FILX=` tag is supported per statement.

---

## Statement Delimiter

Directives are split from SQL statements using the same delimiter as regular SQL.
The default delimiter is `;` and can be changed in Sui preferences
(`SUI.ENDSQLSTMT`).

---

## Implementation Notes

| Class | Role |
|---|---|
| `nonSQL` | Parses `#SET=` / `#URL=` lines and stores values in `TmpProp`. |
| `QryInclude` | Resolves `<include>` tags by reading and splicing file content, iterating until no tags remain. |
| `RunIt` | Resets `TMPURL` before each run; reads it before each SQL statement and switches the `DatabaseManager` connection if non-empty. Also handles `#FILX=` file splicing per statement. |
| `Sui` | `PutTmpProp` / `GetTmpProp` — session-only in-memory store, never written to disk. `readFile()` — reads file content for `#FILX=`. |
