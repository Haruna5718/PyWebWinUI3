import enum

class Status(enum.IntEnum):
	Attention = 0
	Success = 1
	Caution = 2
	Critical = 3
	Neutral = 4

class ThemeResource:
	TextFillColorPrimaryBrush = "var(--TextFillColorPrimaryBrush)"
	TextFillColorSecondaryBrush = "var(--TextFillColorSecondaryBrush)"
	TextFillColorTertiaryBrush = "var(--TextFillColorTertiaryBrush)"
	TextFillColorDisabledBrush = "var(--TextFillColorDisabledBrush)"
	TextFillColorInverseBrush = "var(--TextFillColorInverseBrush)"
	AccentTextFillColorPrimaryBrush = "var(--AccentTextFillColorPrimaryBrush)"
	AccentTextFillColorSecondaryBrush = "var(--AccentTextFillColorSecondaryBrush)"
	AccentTextFillColorTertiaryBrush = "var(--AccentTextFillColorTertiaryBrush)"
	AccentTextFillColorDisabledBrush = "var(--AccentTextFillColorDisabledBrush)"
	TextOnAccentFillColorPrimaryBrush = "var(--TextOnAccentFillColorPrimaryBrush)"
	TextOnAccentFillColorSecondaryBrush = "var(--TextOnAccentFillColorSecondaryBrush)"
	TextOnAccentFillColorDisabledBrush = "var(--TextOnAccentFillColorDisabledBrush)"
	TextOnAccentFillColorSelectedTextBrush = "var(--TextOnAccentFillColorSelectedTextBrush)"
	ControlFillColorDefaultBrush = "var(--ControlFillColorDefaultBrush)"
	ControlFillColorSecondaryBrush = "var(--ControlFillColorSecondaryBrush)"
	ControlFillColorTertiaryBrush = "var(--ControlFillColorTertiaryBrush)"
	ControlFillColorDisabledBrush = "var(--ControlFillColorDisabledBrush)"
	ControlFillColorTransparentBrush = "var(--ControlFillColorTransparentBrush)"
	ControlFillColorInputActiveBrush = "var(--ControlFillColorInputActiveBrush)"
	ControlAltFillColorTransparentBrush = "var(--ControlAltFillColorTransparentBrush)"
	ControlAltFillColorSecondaryBrush = "var(--ControlAltFillColorSecondaryBrush)"
	ControlAltFillColorTertiaryBrush = "var(--ControlAltFillColorTertiaryBrush)"
	ControlAltFillColorQuarternaryBrush = "var(--ControlAltFillColorQuarternaryBrush)"
	ControlAltFillColorDisabledBrush = "var(--ControlAltFillColorDisabledBrush)"
	ControlSolidFillColorDefaultBrush = "var(--ControlSolidFillColorDefaultBrush)"
	ControlStrongFillColorDefaultBrush = "var(--ControlStrongFillColorDefaultBrush)"
	ControlStrongFillColorDisabledBrush = "var(--ControlStrongFillColorDisabledBrush)"
	ControlOnImageFillColorDefaultBrush = "var(--ControlOnImageFillColorDefaultBrush)"
	ControlOnImageFillColorSecondaryBrush = "var(--ControlOnImageFillColorSecondaryBrush)"
	ControlOnImageFillColorTertiaryBrush = "var(--ControlOnImageFillColorTertiaryBrush)"
	ControlOnImageFillColorDisabledBrush = "var(--ControlOnImageFillColorDisabledBrush)"
	SubtleFillColorTransparentBrush = "var(--SubtleFillColorTransparentBrush)"
	SubtleFillColorSecondaryBrush = "var(--SubtleFillColorSecondaryBrush)"
	SubtleFillColorTertiaryBrush = "var(--SubtleFillColorTertiaryBrush)"
	SubtleFillColorDisabledBrush = "var(--SubtleFillColorDisabledBrush)"
	AccentFillColorDefaultBrush = "var(--AccentFillColorDefaultBrush)"
	AccentFillColorSecondaryBrush = "var(--AccentFillColorSecondaryBrush)"
	AccentFillColorTertiaryBrush = "var(--AccentFillColorTertiaryBrush)"
	AccentFillColorDisabledBrush = "var(--AccentFillColorDisabledBrush)"
	AccentFillColorSelectedTextBackgroundBrush = "var(--AccentFillColorSelectedTextBackgroundBrush)"
	CardStrokeColorDefaultBrush = "var(--CardStrokeColorDefaultBrush)"
	CardStrokeColorDefaultSolidBrush = "var(--CardStrokeColorDefaultSolidBrush)"
	ControlStrokeColorDefaultBrush = "var(--ControlStrokeColorDefaultBrush)"
	ControlStrokeColorSecondaryBrush = "var(--ControlStrokeColorSecondaryBrush)"
	ControlStrokeColorOnAccentDefaultBrush = "var(--ControlStrokeColorOnAccentDefaultBrush)"
	ControlStrokeColorOnAccentSecondaryBrush = "var(--ControlStrokeColorOnAccentSecondaryBrush)"
	ControlStrokeColorOnAccentTertiaryBrush = "var(--ControlStrokeColorOnAccentTertiaryBrush)"
	ControlStrokeColorOnAccentDisabledBrush = "var(--ControlStrokeColorOnAccentDisabledBrush)"
	ControlStrokeColorForStrongFillWhenOnImageBrush = "var(--ControlStrokeColorForStrongFillWhenOnImageBrush)"
	ControlStrongStrokeColorDefaultBrush = "var(--ControlStrongStrokeColorDefaultBrush)"
	ControlStrongStrokeColorDisabledBrush = "var(--ControlStrongStrokeColorDisabledBrush)"
	SurfaceStrokeColorDefaultBrush = "var(--SurfaceStrokeColorDefaultBrush)"
	SurfaceStrokeColorFlyoutBrush = "var(--SurfaceStrokeColorFlyoutBrush)"
	SurfaceStrokeColorInverseBrush = "var(--SurfaceStrokeColorInverseBrush)"
	DividerStrokeColorDefaultBrush = "var(--DividerStrokeColorDefaultBrush)"
	FocusStrokeColorOuterBrush = "var(--FocusStrokeColorOuterBrush)"
	FocusStrokeColorInnerBrush = "var(--FocusStrokeColorInnerBrush)"
	CardBackgroundFillColorDefaultBrush = "var(--CardBackgroundFillColorDefaultBrush)"
	CardBackgroundFillColorSecondaryBrush = "var(--CardBackgroundFillColorSecondaryBrush)"
	SmokeFillColorDefaultBrush = "var(--SmokeFillColorDefaultBrush)"
	LayerFillColorDefaultBrush = "var(--LayerFillColorDefaultBrush)"
	LayerFillColorAltBrush = "var(--LayerFillColorAltBrush)"
	LayerOnAcrylicFillColorDefaultBrush = "var(--LayerOnAcrylicFillColorDefaultBrush)"
	LayerOnAccentAcrylicFillColorDefaultBrush = "var(--LayerOnAccentAcrylicFillColorDefaultBrush)"
	LayerOnMicaBaseAltFillColorDefaultBrush = "var(--LayerOnMicaBaseAltFillColorDefaultBrush)"
	LayerOnMicaBaseAltFillColorSecondaryBrush = "var(--LayerOnMicaBaseAltFillColorSecondaryBrush)"
	LayerOnMicaBaseAltFillColorTertiaryBrush = "var(--LayerOnMicaBaseAltFillColorTertiaryBrush)"
	LayerOnMicaBaseAltFillColorTransparentBrush = "var(--LayerOnMicaBaseAltFillColorTransparentBrush)"
	SolidBackgroundFillColorBaseBrush = "var(--SolidBackgroundFillColorBaseBrush)"
	SolidBackgroundFillColorSecondaryBrush = "var(--SolidBackgroundFillColorSecondaryBrush)"
	SolidBackgroundFillColorTertiaryBrush = "var(--SolidBackgroundFillColorTertiaryBrush)"
	SolidBackgroundFillColorQuarternaryBrush = "var(--SolidBackgroundFillColorQuarternaryBrush)"
	SolidBackgroundFillColorBaseAltBrush = "var(--SolidBackgroundFillColorBaseAltBrush)"
	SystemFillColorAttentionBrush = "var(--SystemFillColorAttentionBrush)"
	SystemFillColorSuccessBrush = "var(--SystemFillColorSuccessBrush)"
	SystemFillColorCautionBrush = "var(--SystemFillColorCautionBrush)"
	SystemFillColorCriticalBrush = "var(--SystemFillColorCriticalBrush)"
	SystemFillColorNeutralBrush = "var(--SystemFillColorNeutralBrush)"
	SystemFillColorAttentionBackgroundBrush = "var(--SystemFillColorAttentionBackgroundBrush)"
	SystemFillColorSuccessBackgroundBrush = "var(--SystemFillColorSuccessBackgroundBrush)"
	SystemFillColorCautionBackgroundBrush = "var(--SystemFillColorCautionBackgroundBrush)"
	SystemFillColorCriticalBackgroundBrush = "var(--SystemFillColorCriticalBackgroundBrush)"
	SystemFillColorNeutralBackgroundBrush = "var(--SystemFillColorNeutralBackgroundBrush)"
	SystemFillColorSolidNeutralBrush = "var(--SystemFillColorSolidNeutralBrush)"
	SystemFillColorSolidAttentionBackgroundBrush = "var(--SystemFillColorSolidAttentionBackgroundBrush)"
	SystemFillColorSolidNeutralBackgroundBrush = "var(--SystemFillColorSolidNeutralBackgroundBrush)"

class Color:

	class Fill:

		class Text:
			Primary = ThemeResource.TextFillColorPrimaryBrush
			Secondary = ThemeResource.TextFillColorSecondaryBrush
			Tertiary = ThemeResource.TextFillColorTertiaryBrush
			Disabled = ThemeResource.TextFillColorDisabledBrush
			Inverse = ThemeResource.TextFillColorInverseBrush

			class Accent:
				Primary = ThemeResource.AccentTextFillColorPrimaryBrush
				Secondary = ThemeResource.AccentTextFillColorSecondaryBrush
				Tertiary = ThemeResource.AccentTextFillColorTertiaryBrush
				Disabled = ThemeResource.AccentTextFillColorDisabledBrush

			class OnAccent:
				Primary = ThemeResource.TextOnAccentFillColorPrimaryBrush
				Secondary = ThemeResource.TextOnAccentFillColorSecondaryBrush
				Disabled = ThemeResource.TextOnAccentFillColorDisabledBrush
				SelectedText = ThemeResource.TextOnAccentFillColorSelectedTextBrush

		class Control:
			Default = ThemeResource.ControlFillColorDefaultBrush
			Secondary = ThemeResource.ControlFillColorSecondaryBrush
			Tertiary = ThemeResource.ControlFillColorTertiaryBrush
			Disabled = ThemeResource.ControlFillColorDisabledBrush
			Transparent = ThemeResource.ControlFillColorTransparentBrush
			InputActive = ThemeResource.ControlFillColorInputActiveBrush

			class Alt:
				Transparent = ThemeResource.ControlAltFillColorTransparentBrush
				Secondary = ThemeResource.ControlAltFillColorSecondaryBrush
				Tertiary = ThemeResource.ControlAltFillColorTertiaryBrush
				Quarternary = ThemeResource.ControlAltFillColorQuarternaryBrush
				Disabled = ThemeResource.ControlAltFillColorDisabledBrush

			class Solid:
				Default = ThemeResource.ControlSolidFillColorDefaultBrush

			class Strong:
				Default = ThemeResource.ControlStrongFillColorDefaultBrush
				Disabled = ThemeResource.ControlStrongFillColorDisabledBrush

			class OnImage:
				Default = ThemeResource.ControlOnImageFillColorDefaultBrush
				Secondary = ThemeResource.ControlOnImageFillColorSecondaryBrush
				Tertiary = ThemeResource.ControlOnImageFillColorTertiaryBrush
				Disabled = ThemeResource.ControlOnImageFillColorDisabledBrush

		class Subtle:
			Transparent = ThemeResource.SubtleFillColorTransparentBrush
			Secondary = ThemeResource.SubtleFillColorSecondaryBrush
			Tertiary = ThemeResource.SubtleFillColorTertiaryBrush
			Disabled = ThemeResource.SubtleFillColorDisabledBrush

		class Accent:
			Default = ThemeResource.AccentFillColorDefaultBrush
			Secondary = ThemeResource.AccentFillColorSecondaryBrush
			Tertiary = ThemeResource.AccentFillColorTertiaryBrush
			Disabled = ThemeResource.AccentFillColorDisabledBrush
			SelectedTextBackground = ThemeResource.AccentFillColorSelectedTextBackgroundBrush

		class Smoke:
			Default = ThemeResource.SmokeFillColorDefaultBrush

		class Layer:
			Default = ThemeResource.LayerFillColorDefaultBrush
			Alt = ThemeResource.LayerFillColorAltBrush

			class OnAcrylic:
				Default = ThemeResource.LayerOnAcrylicFillColorDefaultBrush

			class OnAccentAcrylic:
				Default = ThemeResource.LayerOnAccentAcrylicFillColorDefaultBrush

			class OnMicaBaseAlt:
				Default = ThemeResource.LayerOnMicaBaseAltFillColorDefaultBrush
				Secondary = ThemeResource.LayerOnMicaBaseAltFillColorSecondaryBrush
				Tertiary = ThemeResource.LayerOnMicaBaseAltFillColorTertiaryBrush
				Transparent = ThemeResource.LayerOnMicaBaseAltFillColorTransparentBrush

		class System:
			Attention = ThemeResource.SystemFillColorAttentionBrush
			Success = ThemeResource.SystemFillColorSuccessBrush
			Caution = ThemeResource.SystemFillColorCautionBrush
			Critical = ThemeResource.SystemFillColorCriticalBrush
			Neutral = ThemeResource.SystemFillColorNeutralBrush

			class Solid:
				Neutral = ThemeResource.SystemFillColorSolidNeutralBrush
				
	class Stroke:

		class Card:
			Default = ThemeResource.CardStrokeColorDefaultBrush
			DefaultSolid = ThemeResource.CardStrokeColorDefaultSolidBrush

		class Control:
			Default = ThemeResource.ControlStrokeColorDefaultBrush
			Secondary = ThemeResource.ControlStrokeColorSecondaryBrush
			OnAccentDefault = ThemeResource.ControlStrokeColorOnAccentDefaultBrush
			OnAccentSecondary = ThemeResource.ControlStrokeColorOnAccentSecondaryBrush
			OnAccentTertiary = ThemeResource.ControlStrokeColorOnAccentTertiaryBrush
			OnAccentDisabled = ThemeResource.ControlStrokeColorOnAccentDisabledBrush
			ForStrongFillWhenOnImage = ThemeResource.ControlStrokeColorForStrongFillWhenOnImageBrush

			class Strong:
				Default = ThemeResource.ControlStrongStrokeColorDefaultBrush
				Disabled = ThemeResource.ControlStrongStrokeColorDisabledBrush

		class Surface:
			Default = ThemeResource.SurfaceStrokeColorDefaultBrush
			Flyout = ThemeResource.SurfaceStrokeColorFlyoutBrush
			Inverse = ThemeResource.SurfaceStrokeColorInverseBrush

		class Divider:
			Default = ThemeResource.DividerStrokeColorDefaultBrush

		class Focus:
			Outer = ThemeResource.FocusStrokeColorOuterBrush
			Inner = ThemeResource.FocusStrokeColorInnerBrush

	class Background:

		class Solid:
			Base = ThemeResource.SolidBackgroundFillColorBaseBrush
			Secondary = ThemeResource.SolidBackgroundFillColorSecondaryBrush
			Tertiary = ThemeResource.SolidBackgroundFillColorTertiaryBrush
			Quarternary = ThemeResource.SolidBackgroundFillColorQuarternaryBrush
			BaseAlt = ThemeResource.SolidBackgroundFillColorBaseAltBrush

		class Card:
			Default = ThemeResource.CardBackgroundFillColorDefaultBrush
			Secondary = ThemeResource.CardBackgroundFillColorSecondaryBrush

		class System:
			Attention = ThemeResource.SystemFillColorAttentionBackgroundBrush
			Success = ThemeResource.SystemFillColorSuccessBackgroundBrush
			Caution = ThemeResource.SystemFillColorCautionBackgroundBrush
			Critical = ThemeResource.SystemFillColorCriticalBackgroundBrush
			Neutral = ThemeResource.SystemFillColorNeutralBackgroundBrush

			class Solid:
				Attention = ThemeResource.SystemFillColorSolidAttentionBackgroundBrush
				Neutral = ThemeResource.SystemFillColorSolidNeutralBackgroundBrush

# class Element:
# 	class Box:
# 		gap = "inherit"
# 		round = "4px"
# 		border = "1px"
# 		padding = "16px"
# 		align = "inherit"
# 		background = Color.Background.Card.Default
# 	class Button:
# 		disabled = False
# 		value = None
# 		width = "auto"
# 		height = "auto"
# 		type = None
# 		url = None
# 	class Check:
# 		disabled = False
# 		value = None
# 		align = "left"
# 		type = "two"
# 	class Expender:
# 		disabled = False
# 		gap = "inherit"
# 		round = "4px"
# 		padding = "16px"
# 		align = "inherit"
# 	class Horizontal:
# 		gap = "inherit"
# 		align = "inherit"
# 	class If:
# 		disabled = False
# 		value = None
# 	class Image:
# 		disabled = False
# 		source = None
# 		width = "auto"
# 		height = "auto"
# 	class Input:
# 		disabled = False
# 		width = "auto"
# 		height = "auto"
# 		type = "text"
# 		min = None
# 		max = None
# 		value = None
# 	class Line:
# 		margin = "0"
# 		size = "1"
# 		color = Color.Fill.Control.Strong.Default
# 	class Match:
# 		disabled = False
# 		value = None
# 	class Option:
# 		value = None
# 	class Page:
# 		title = None
# 		name = None
# 		path = None
# 		icon = ""
# 		state = None
# 		badge = None
# 	class Progressbar:
# 		disabled = False
# 		type = None
# 		width = "160px"
# 		value = None
# 	class Radio:
# 		disabled = False
# 		group = None
# 		value = None
# 	class Repeat:
# 		disabled = False
# 		data = None
# 		value = None
# 	class Select:
# 		disabled = False
# 		width = "auto"
# 		height = "auto"
# 		value = None
# 	class Slider:
# 		disabled = False
# 		width = "160px"
# 		type = "horizontal"
# 		min = 0
# 		max = 100
# 		step = 1
# 		value = None
# 	class Space:
# 		factor = 1
# 	class Switch:
# 		disabled = False
# 		align = "left"
# 		on = "ON"
# 		off = "OFF"
# 		value = None
# 	class Text:
# 		disabled = False
# 		type = "default"
# 		margin = "0"
# 		color = None
# 		size = None
# 		url = None
# 	class Vertical:
# 		gap = "inherit"
# 		width = "auto"
# 		align = "inherit"
# 	class Webview:
# 		disabled = False
# 		source = None
# 		width = "auto"
# 		height = "auto"

# 	Other = [
# 		"Case",
# 		"True",
# 		"False",
# 		"Header",
# 		"Content",
# 	]