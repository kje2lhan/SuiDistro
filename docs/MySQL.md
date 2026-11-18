# Using Sui with MySQL

Sui connects to MySQL through JDBC. You need a running MySQL server and the
MySQL Connector/J driver; installing the driver does not install or start the
database server.

## 1. Install or locate MySQL Server

Download MySQL Community Server from the
[official MySQL downloads page](https://dev.mysql.com/downloads/mysql/). If
MySQL is already running, ask your database administrator for the server
hostname, port, database name, and a user account that is allowed to connect
from your computer.

The usual MySQL port is `3306`. For a local installation, the host is usually
`localhost`. Create or obtain a database and a MySQL account with only the
permissions needed for your work. For a remote server, ensure that the server,
network firewall, and MySQL account allow connections from your client machine.

## 2. Download MySQL Connector/J

Download **Connector/J** (the MySQL JDBC driver) from the
[official Connector/J downloads page](https://dev.mysql.com/downloads/connector/j/).
The [Connector/J installation guide](https://dev.mysql.com/doc/connector-j/en/connector-j-installing.html)
has details for other installation methods and versions.

For a manual Sui setup, download the platform-independent archive, extract it,
and locate the `mysql-connector-j-<version>.jar` file. Sui does not bundle
Connector/J, so you must add this JAR to Sui's driver catalog.

## 3. Add the driver in Sui

1. Start Sui and open **File → Connection Manager…**.
2. Click **New**, enter an alias such as `MySQL-Dev`, and choose **MySQL** in
   the **Driver** list.
3. Open the **Driver / JAR** tab. Select the MySQL driver row, click
   **Browse JAR…**, choose the Connector/J JAR you extracted, then click
   **Reload JARs**. Confirm that the status is green.
4. Confirm the driver class is `com.mysql.cj.jdbc.Driver`. This is the class
   name used by current Connector/J releases. If an older Sui distribution
   shows `com.mysql.jdbc.Driver`, replace it with the current class name.

The Connector/J JAR must remain at the configured path whenever Sui is used.
The path is stored in Sui's connection properties and can be changed later in
the **Driver / JAR** tab.

## 4. Configure and test the connection

Return to the **Connection** tab and fill in:

| Field | Example |
|---|---|
| **Alias** | `MySQL-Dev` |
| **Driver** | `MySQL` |
| **Server** | `localhost` |
| **Port** | `3306` |
| **Database** | `sampledb` |
| **User** | Your MySQL user |
| **Password** | The password for that user |

The JDBC URL should have this form:

```text
jdbc:mysql://localhost:3306/sampledb
```

For a remote database, replace `localhost` with its hostname. The supported
Connector/J URL format is documented in the
[MySQL JDBC URL reference](https://dev.mysql.com/doc/connector-j/en/connector-j-reference-jdbc-url-format.html).
If your Sui installation has an older MySQL URL template, check that the URL
contains `jdbc:mysql://` (two slashes after the colon). Older Sui distributions
may need the MySQL template in the bundled `url.pro` updated to the format
shown above and Sui rebuilt.

Enter the database user and password, then click **Test Connection**. A green
message with the database product and version confirms that Sui reached MySQL.
Click **Save** to keep the profile. Passwords are not saved unless you
deliberately enable **Auto-login**; see
[Credential Handling](CredentialHandling.md) before enabling it.

## 5. Run a query

Select the saved `MySQL-Dev` connection in Sui's URL dropdown, then run a
simple query such as:

```sql
SELECT VERSION();
```

To check the selected database and user:

```sql
SELECT DATABASE(), CURRENT_USER();
```

Write and run additional SQL in the editor as usual. Sui sends the SQL to the
selected database; MySQL permissions determine which schemas and operations
the account can access.

## Troubleshooting

- **Driver not loaded / `No suitable driver`:** Confirm that the Connector/J
  JAR is selected in **Driver / JAR**, click **Reload JARs**, and verify the
  class is `com.mysql.cj.jdbc.Driver`.
- **Connection refused or timeout:** Check that MySQL is running, the hostname
  and port are correct, and remote access is allowed by the server and
  firewall.
- **Access denied:** Verify the username and password and that the MySQL
  account is permitted to connect from the client host.
- **Unknown database:** Confirm the database name exists and that the account
  can access it.
- **TLS/certificate error:** Follow your organization's TLS requirements and
  the Connector/J documentation. Avoid disabling certificate verification as
  a general fix, especially for remote or production databases.
