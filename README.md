# PyWebWinUI3

PyWebWinUI3 is a Windows desktop UI framework that combines:

- a Python backend
- a frameless PySide6 / Qt shell
- a Svelte frontend rendered inside Qt WebEngine
- an XAML-like page format for declaring UI

The goal is to make desktop apps feel like WinUI3-style apps while still being driven from Python.

## What It Does

PyWebWinUI3 lets you:

- declare pages in XAML-like markup
- bind controls to Python values
- react to value changes and lifecycle events from Python
- use a static bundled frontend without running a local web server
- keep a modern Windows-style shell with theme and accent synchronization

At runtime, Python owns the application state, Qt hosts the window and WebEngine, and the Svelte app renders the page tree received from Python.

## Platform

PyWebWinUI3 is currently aimed at Windows.

Runtime dependencies:

- `PySide6`
- `pywin32`

## Installation

```bash
pip install PyWebWinUI3
```

## Quick Start

```python
from pywebwinui3.core import MainWindow
from pywebwinui3.type import Status

app = MainWindow("PyWebWinUI3")

app.addSettings("Settings.xaml")
app.addPage("Dashboard.xaml")
app.addPage("test.xaml")

app.values["test_input"] = "Hello, world"
app.values["test_switch"] = False

@app.onValueChange("test_noticeSample")
def show_notice(*_):
    app.notice(Status.Attention, "Title", "This is a sample notice")

app.start()
```

## Minimal Page Example

```xml
<Page path="settings" icon="&#xE713;" name="Settings" title="Settings">
	<Box>
		<Horizontal>
			<Text>App theme</Text>
			<Space />
			<Select value="system_theme">
				<Option value="dark">Dark</Option>
				<Option value="light">Light</Option>
				<Option value="system">Use system setting</Option>
			</Select>
		</Horizontal>
	</Box>
</Page>
```

## Core Concepts

### `MainWindow`

`pywebwinui3.core.MainWindow` is the main entry point.

Important methods:

- `addPage(...)`
- `addSettings(...)`
- `start(debug=False, min_width=900, min_height=600)`
- `notice(level, title, description, item=None)`
- `pin(state)`
- `syncValue(key, value)`

### `values`

`app.values` is the shared state dictionary between Python and the frontend.

Typical usage:

```python
app.values["user_name"] = "Haruna"
app.values["is_enabled"] = True
app.values["progress"] = 50
```

The frontend reads these values directly, and user input writes back into the same store.

Built-in system values include keys such as:

- `system_title`
- `system_icon`
- `system_theme`
- `system_theme_resolved`
- `system_accent`
- `system_pages`
- `system_settings`
- `system_nofication`
- `system_pin`
- `system_window_width`
- `system_window_height`

### Events

`MainWindow` exposes decorator-style event hooks:

- `@app.onValueChange(key)`
- `@app.onAccentColorChange()`
- `@app.onThemeChange()`
- `@app.onSetup()`
- `@app.onExit()`

Example:

```python
@app.onValueChange("user_name")
def on_user_name_change(*_):
    print(app.values["user_name"])
```

### Notifications

Use `app.notice(...)` to push InfoBar-style messages into the frontend.

```python
from pywebwinui3.type import Status

app.notice(Status.Success, "Saved", "Settings were saved successfully")
```

Status values:

- `Status.Attention`
- `Status.Success`
- `Status.Caution`
- `Status.Critical`
- `Status.Neutral`

## Markup Model

Pages are loaded into a JSON tree and rendered by the frontend.

Common tags currently implemented:

- `Page`
- `Box`
- `Horizontal`
- `Vertical`
- `Text`
- `Button`
- `Input`
- `Slider`
- `Switch`
- `Check`
- `Radio`
- `Select`
- `Option`
- `Image`
- `Webview`
- `Progressbar`
- `Line`
- `Space`
- `Expender`
- `If`
- `Match`
- `Repeat`

## Binding Model

PyWebWinUI3 supports two main binding styles:

- direct value binding through attributes like `value="test_input"`
- formatted text / expressions inside strings such as `{user_name}`

The frontend compiles and caches formatted expressions, while Python remains the source of truth for state.

Path-like targets such as nested array access are also handled by the runtime value system when used by supported controls.

## Resource Resolution

Relative resource paths are resolved from the Python caller's directory first, then from the packaged frontend bundle directory.

This lets you write things like:

- local XAML files via `addPage("Dashboard.xaml")`
- local images in markup
- bundled web assets shipped with the package

External URLs such as `https://...` and `file://...` are passed through as-is.

## Window / Shell Behavior

The desktop shell is implemented in Qt and provides:

- frameless custom window chrome
- theme and accent synchronization with Windows
- always-on-top pinning
- WebChannel bridge between Python and the frontend
- external link handling through the desktop layer

## Project Structure

```text
PyWebWinUI3/
├─ pywebwinui3/
│  ├─ core.py        # public Python API
│  ├─ qt.py          # Qt shell and bridge
│  ├─ util.py        # XAML loader, sync dict, accent watcher
│  ├─ event.py       # event system
│  ├─ type.py        # status and theme resource constants
│  └─ web/           # built frontend bundle shipped to users
├─ frontend/         # Svelte source
├─ example/          # sample application and XAML pages
└─ setup.py
```

## Development Notes

If you are only using the package, you do not need to build the frontend manually.

If you are working on the framework itself:

- Python runtime code lives in `pywebwinui3/`
- Svelte source lives in `frontend/`
- the distributable frontend bundle lives in `pywebwinui3/web/`

## Example

See:

- `example/example.py`
- `example/Settings.xaml`
- `example/Dashboard.xaml`
- `example/Test.xaml`

## License

Apache-2.0
