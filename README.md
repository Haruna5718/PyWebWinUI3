
# PyWebWinUI3

PyWebWinUI3 is a project that helps you easily build WinUI3-style desktop UIs in Python using PySide6, QtWebEngine, and Svelte.

## Features
- Modern and intuitive **WinUI3-style** UI components
- Rapid desktop app development with Python
- Frameless desktop window powered by Qt
- Svelte-based frontend integration through `QWebChannel`
- Custom fonts and Fluent icon support
- Static frontend bundle loading without a local HTTP server

## Installation & Build
You can install PyWebWinUI3 directly from PyPI:
```bash
pip install PyWebWinUI3
```

## Usage
You can define your UI using XAML files and control the app with Python. See the `example/` folder for more details.

### Minimal Example
```python
from pywebwinui3.core import MainWindow

app = MainWindow("PyWebWinUI3", "./app.ico")
app.addSettings("Settings.xaml")
app.addPage("Dashboard.xaml")
app.addPage("Test.xaml")

# Set values for UI bindings
app.values["system.theme"] = "dark"

app.start()
```

### XAML Example (Settings.xaml)
```xml
<Page path="settings" icon="\ue713" name="Settings" title="Settings">
	<Box>
		<Horizontal>
			<Text>App theme</Text>
			<Space />
			<Select value="system.theme">
				<Option value="dark">Dark</Option>
				<Option value="light">Light</Option>
				<Option value="system">Use system setting</Option>
			</Select>
		</Horizontal>
	</Box>
	<!-- ...more UI elements... -->
</Page>
```

### More
- See `example/example.py` and the XAML files in `example/` for advanced usage.
- The desktop shell is now based on PySide6 + QtWebEngine, so `PySide6` must be available in your environment.

## Contributing
- PRs and issues are welcome!
- You can contribute Svelte components, Python modules, UI improvements, and more.

## License
Apache-2.0

> This README was generated using AI (GitHub Copilot).
