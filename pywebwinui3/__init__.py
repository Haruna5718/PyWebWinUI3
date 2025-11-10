from .core import *
from .event import *

__version__ = '1.0.0-beta.31'

class Notice:
	Accent = 0
	Information = 0
	Attention = 0
	Green = 1
	Success = 1
	Online = 1
	Yellow = 2
	Warning = 2
	Caution = 2
	Red = 3
	Error = 3
	Critical = 3
	Gray = 4
	Offline = 4

class Color:
	class Accent:
		Default = "var(--AccentFillColorDefaultBrush)"
		Secondary = "var(--AccentFillColorSecondaryBrush)"
		Tertiary = "var(--AccentFillColorTertiaryBrush)"
		Background = "var(--AccentFillColorBackgroundBrush)"
	class Text:
		Primary = "var(--TextFillColorPrimaryBrush)"
		Secondary = "var(--TextFillColorSecondaryBrush)"
		Tertiary = "var(--TextFillColorTertiaryBrush)"
		Disabled = "var(--TextFillColorDisabledBrush)"
		class OnAccent:
			Primary = "var(--TextOnAccentFillColorPrimaryBrush)"
			Secondary = "var(--TextOnAccentFillColorSecondaryBrush)"
			Disabled = "var(--TextOnAccentFillColorDisabledBrush)"
			Selected = "var(--TextOnAccentFillColorSelectedTextBrush)"
	class Signal:
		Success = "var(--SystemFillColorSuccessBrush)"
		Caution = "var(--SystemFillColorCautionBrush)"
		Critical = "var(--SystemFillColorCriticalBrush)"
		Attention = "var(--AccentFillColorSecondaryBrush)" # Accent.Secondary
		Neutral = "var(--TextFillColorTertiaryBrush)" # Text.Tertiary
		class Background:
			Success = "var(--SystemFillColorSuccessBackgroundBrush)"
			Caution = "var(--SystemFillColorCautionBackgroundBrush)"
			Critical = "var(--SystemFillColorCriticalBackgroundBrush)"
			Attention = "var(--AccentFillColorBackgroundBrush)" # Accent.Background
			Neutral = "var(--AccentFillColorBackgroundBrush)" # Accent.Background
