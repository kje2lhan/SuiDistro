# SuiHome — How the Sui Home Directory Is Resolved

## Purpose

`SuiHome` is a static field in the `Sui` class that holds the path to the directory where Sui stores its configuration and property files (e.g. `SuiSys.pro`, `SuiSheetProp.pro`, `SuiConnPref.pro`). It is resolved once at startup and never changes during the lifetime of the application.

---

## `HomeDrive` — Prerequisite

Before `SuiHome` is resolved, the drive letter (`HomeDrive`) is determined in `main()`:

```
main(args)
  ├─ args[0] present?  → HomeDrive = first character of args[0]  (e.g. "C")
  └─ otherwise         → HomeDrive = System.getenv("HOMEDRIVE")  (e.g. "C")
```

`HomeDrive` is used as a symbolic token (`&homedrive`) inside `Sui.ini` and is also available via `Sui.GetHomeDrive()`.

---

## Resolution Order

`SuiHome` is determined by working through four candidates in order, stopping at the first one that succeeds:

```
1. Sui.ini  →  SuiHome=<folder>;  (if the folder exists)
2. <user.home>\AppData\Sui\        (if the folder exists)
3. <user.dir>\                     (current directory, if Sui can write to it)
4. <user.home>\AppData\Sui\        (fallback — folder is created if missing)
```

---

## Step 1 — `Sui.ini` (explicit override)

Sui reads `Sui.ini` from the current working directory. The file is scanned line by line for a `SuiHome=...;` statement.

**Syntax:**
```
SuiHome=<folder>;
```

**Symbolic tokens** that can be embedded in `<folder>`:

| Token | Resolved to |
|---|---|
| `&homedrive` | `HomeDrive` (drive letter, e.g. `C`) |
| `&user.name` | Java system property `user.name` |
| `&user.home` | Java system property `user.home` |

**Examples:**
```
SuiHome=C:\SuiData;
SuiHome=&homedrive:\Users\&user.name\SuiData;
SuiHome=&user.home\AppData\Sui;
```

After token substitution the path is tested with `File.isDirectory()`. If the folder exists, `Folder` is set to that path and steps 2–4 are skipped. If the folder does not exist, `Folder` remains `null` and the next step is tried.

If `Sui.ini` is missing or cannot be read, the whole block is caught and `Folder` stays `null`.

**Other settings parsed from `Sui.ini`** (processed in the same loop):

| Key | Effect |
|---|---|
| `Font=<name>,<size>;` | Sets the global Swing UI font |
| `LookandFeel=<class>;` | Records the Look & Feel class name to apply (see below) |
| `Pyjamas=true\|false;` | Enables/disables Pyjamas report formatting |

---

## Step 2 — `user.home\AppData\Sui\`

If no valid `SuiHome` was found in `Sui.ini`, Sui checks whether the folder `<user.home>\AppData\Sui\` exists:

```java
SuiHome = userHome + "\\AppData\\Sui\\";
f = new File(SuiHome);
if (f.isDirectory()) → use it
```

This is the standard Windows per-user application data location.

---

## Step 3 — Current directory (`user.dir`)

If the `AppData\Sui` folder does not exist either, Sui falls back to the current working directory:

```java
SuiHome = userDir + "\\";
```

---

## Write-access check

After steps 1–3 have selected a candidate, Sui verifies it can actually write there by attempting to create and immediately delete a temporary file:

```java
File f = new File(SuiHome + "\\test.fil");
f.createNewFile();  // succeeds → delete and proceed
```

If the write test fails (`IOException`), Sui falls back to step 4.

---

## Step 4 — Fallback: create `user.home\AppData\Sui\`

If the write test throws (or if `user.home` was empty and none of the earlier steps succeeded), Sui attempts to create the `AppData\Sui` folder under the user home directory:

```java
SuiHome = userHome + "\\AppData\\Sui\\";
new File(SuiHome).mkdir();
```

A second `catch` block handles the case where even `mkdir()` fails (e.g. restricted environment), printing a stack trace but continuing.

---

## Final value

Once resolved, `SuiHome` always ends with a backslash (`\`), so file references can be built by simple concatenation:

```java
String propsFile = SuiHome + "SuiSys.pro";
```

The final path is logged to the console along with `user.dir` and `user.home`:

```
Final: C:\Users\kjell\AppData\Sui\
****************************************************************
User Directory     = C:\SuiVsCode\suidev080
Home Directory     = C:\Users\kjell
Sui Home Directory = C:\Users\kjell\AppData\Sui\
****************************************************************
```

---

## Summary Flow

```
main()
  └─ HomeDrive = args[0][0]  OR  HOMEDRIVE env var

Sui constructor
  ├─ Read Sui.ini
  │     └─ SuiHome=...;  → expand tokens → folder exists?  → Folder = path
  │
  ├─ Folder set?
  │     yes → SuiHome = Folder + "\"
  │     no  → userHome available?
  │               yes → SuiHome = userHome + "\AppData\Sui\"  (if dir exists)
  │                     else → SuiHome = userDir + "\"
  │               no  → SuiHome = userDir + "\"
  │
  └─ Write test (create/delete test.fil)
        success → done
        fail    → SuiHome = userHome + "\AppData\Sui\"  (mkdir if needed)
```

---

## Look and Feel

### How it is set

The `LookandFeel` key in `Sui.ini` is read during startup (same loop as `SuiHome`) and stored in the static field `LfToUse`. The value is the **fully-qualified class name** of the Look & Feel implementation.

`setLF()` is called later in the startup sequence, after drivers and jars have been loaded. It applies the Look & Feel in two passes:

**Pass 1 — `SUI.LF` property (runtime profile)**  
Reads the `SUI.LF` key from the application property store (`SuiSys.pro`). If set, it iterates `UIManager.getInstalledLookAndFeels()` to find a matching installed L&F by *name* and applies it. This allows the user to switch themes at runtime and have the choice remembered.

**Pass 2 — `LfToUse` from `Sui.ini`**  
If `LfToUse` is not `null`, it calls `UIManager.setLookAndFeel(LfToUse)` directly with the class name string. This path is used for third-party L&Fs (like FlatLaf) that are not pre-registered with `UIManager`. After applying, `SwingUtilities.updateComponentTreeUI(cont)` is called to repaint all existing components, and `JFrame.setDefaultLookAndFeelDecorated(true)` enables native window decoration from the L&F.

If `LfToUse` is `null` (no `LookandFeel` key in `Sui.ini`), the connection panel background is set to the system menu colour as a minimal default.

Any exception during L&F loading is caught and logged — Sui continues with whatever L&F was in effect before the failure.

---

### FlatLaf examples

[FlatLaf](https://www.formdev.com/flatlaf/) is a modern flat Look & Feel for Java Swing. Its jar must be on the classpath (or loaded via Sui's jar loader) for these to work.

**Built-in FlatLaf themes:**

```ini
# Light themes
LookandFeel=com.formdev.flatlaf.FlatLightLaf;
LookandFeel=com.formdev.flatlaf.FlatIntelliJLaf;

# Dark themes
LookandFeel=com.formdev.flatlaf.FlatDarkLaf;
LookandFeel=com.formdev.flatlaf.FlatDarculaLaf;
```

**FlatLaf IntelliJ Themes (requires `flatlaf-intellij-themes` jar):**

```ini
# Popular light IntelliJ themes
LookandFeel=com.formdev.flatlaf.intellijthemes.FlatArcOrangeIJTheme;
LookandFeel=com.formdev.flatlaf.intellijthemes.FlatGitHubIJTheme;
LookandFeel=com.formdev.flatlaf.intellijthemes.FlatSolarizedLightIJTheme;

# Popular dark IntelliJ themes
LookandFeel=com.formdev.flatlaf.intellijthemes.FlatOneDarkIJTheme;
LookandFeel=com.formdev.flatlaf.intellijthemes.FlatDraculaIJTheme;
LookandFeel=com.formdev.flatlaf.intellijthemes.FlatNordIJTheme;
LookandFeel=com.formdev.flatlaf.intellijthemes.FlatSolarizedDarkIJTheme;
LookandFeel=com.formdev.flatlaf.intellijthemes.FlatMaterialDesignDarkIJTheme;
```

**Combining with other `Sui.ini` settings:**

```ini
SuiHome=C:\Users\kjell\AppData\Sui;
Font=JetBrains Mono,13;
LookandFeel=com.formdev.flatlaf.FlatDarkLaf;
Pyjamas=false;
```

> **Note:** The FlatLaf jar must be present. If it is not on the classpath, `setLF()` will catch the `ClassNotFoundException` and log `"Loading look and feel failed, lf=: com.formdev.flatlaf.FlatDarkLaf"` to the console — Sui continues with the default Java L&F.
