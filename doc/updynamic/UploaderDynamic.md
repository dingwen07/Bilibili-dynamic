# Bilibili-dynamic - API Documentation

## UploaderDynamic (class)

### Field Summary

| Type                        | Field and Description               |
| --------------------------- | ----------------------------------- |
| `int`                       | [`uploader_uid`](#uploader_uid)     |
| `bool`                      | [`cache_resource`](#cache_resource) |
| `str`                       | [`resource_path`](#resource_path)   |
| `str`                       | [`dynamic_url`](#dynamic_url)       |
| `str`                       | [`uploader_name`](#uploader_name)   |
| `requests.sessions.Session` | [`session`](#session)               |
| `sqlite3.Connection`        | [`db`](#db)                         |
| `sqlite3.Cursor`            | [`db_cursor`](#db_cursor)           |

### Method Summary

| Return Type | Method and Description                                       |
| ----------- | ------------------------------------------------------------ |
| `int`       | [`fetch()`](#fetch)<br />Fetch all dynamics of the Uploader, insert them into database, return the number of dynamics fetched. |
| `dict`      | [`get_update()`](#get_update)<br />Get the first page of dynamics of the Uploader, insert them into database, return new dynamics. |
| `dict`      | [`get_all_dynamics()`](#get_all_dynamics)<br />Fetch all dynamics of the Uploader, return them. |
| `int`       | [`refresh_dynamic_status()`](#refresh_dynamic_status)<br />Refresh the dynamic status, return the number of dynamics whose status has been updated. |
| void        | [`close()`](#close)<br />Close the current object.           |
| void        | [`_save_data()`](#_save_data)<br />Save all data to database. |

### Field Detail

#### `uploader_uid`

`uploader_uid`: `int`

- The UID of the Uploader
- Populated by the constructor
- Should not be modified inside the class
- Should not be modified outside the class

#### `cache_resource`

`cache_resource`: `bool`

- Switch for caching resources
- Populated by the constructor, with default value `True`

#### `resource_path`

`resource_path`: `str`

- Path to store resource cache
- Populated by the constructor, with default value `'./resource_cache'`
- Path to store resource cache

#### `dynamic_url`

`dynamic_url`: `str`

  - Request URL of dynamic data
  - Populated by the constructor
  - Should not be modified inside the class
  - Should not be modified outside the class
  - Need to format with "dynamic offset"

#### `uploader_name`

`uploader_name`: `str`

  - The name of the Uploader
  - Populated by the constructor

#### `session`

`session`: `requests.sessions.Session`

  - A `requests` session, which will be used when requesting Internet data.
  - Populated by the constructor
  - Must point to a `requests.sessions.Session` object
  - The current class implementation will ensure that this instance variable points to the same object

#### `db`

`db`: `sqlite3.Connection`

- Database connector
- Populated by the constructor
- Must point to a `sqlite3.Connection` object
- The current class implementation will ensure that this instance variable points to the same object

#### `db_cursor`

`db_cursor`: `sqlite3.Cursor`

- Database cursor
- Populated by the constructor, by calling `self.db.cursor()`
- Must point to a `sqlite3.Cursor` object
- The current class implementation will ensure that this instance variable points to the same object

### Method Detail

#### `fetch`

`fetch()`: `int`

Fetch all dynamics of the Uploader, insert them into database, return the number of dynamics fetched.

**Returns:** number of dynamics fetched

#### `get_update`

`get_update()`: `dict`

Get the first page of dynamics of the Uploader, insert them into database, return new dynamics.

**Returns:** new dynamics

#### `get_all_dynamics`

`get_all_dynamics()`: `dict`

Fetch all dynamics of the Uploader, return them.

**Returns:** all dynamics of the Uploader fetched

#### `refresh_dynamic_status`

`refresh_dynamic_status()`: `int`

Refresh the dynamic status, return the number of dynamics whose status has been updated.

**Returns:** number of dynamics whose status has been updated

#### `close`

`close()`

Close the current object.

#### `_save_data`

`_save_data()`

Save all data to database.