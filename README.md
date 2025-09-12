
# PyWebWinUI3

PyWebWinUI3 is a project that helps you easily build WinUI3-style desktop UIs in Python using [pywebview](https://pywebview.flowrl.com/).

## Features
- Modern and intuitive **WinUI3-style** UI components
- Rapid desktop app development with Python
- Svelte-based FrontEnd integration
- Custom fonts and Fluent icon support

## Installation & Build
You can install PyWebWinUI3 directly from PyPI:
```bash
pip install PyWebWinUI3
```

## Usage
You can define your UI using XAML files and control the app with Python. See the `example/` folder for more details.

### Minimal Example
```python
from pywebwinui3 import MainWindow, loadPage

app = MainWindow("PyWebWinUI3", debug=True)
app.addSettings(loadPage("Settings.xaml"))
app.addPage(loadPage("Dashboard.xaml"))
app.addPage(loadPage("Test.xaml"))

# Set values for UI bindings
app.setValue("system.theme", "dark")

app.start("dashboard")
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

## Contributing
- PRs and issues are welcome!
- You can contribute Svelte components, Python modules, UI improvements, and more.

## License
Apache-2.0
---
> This README was generated using AI (GitHub Copilot).
