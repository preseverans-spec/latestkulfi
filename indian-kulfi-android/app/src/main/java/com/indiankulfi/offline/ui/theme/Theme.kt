package com.indiankulfi.offline.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = KulfiBrown,
    onPrimary = KulfiCream,
    primaryContainer = KulfiTan,
    secondary = KulfiGold,
    onSecondary = KulfiCream,
    background = KulfiCream,
    onBackground = KulfiBrown,
    surface = KulfiSurface,
    onSurface = KulfiBrown,
    error = KulfiError,
)

private val DarkColors = darkColorScheme(
    primary = KulfiGold,
    onPrimary = KulfiBrown,
    secondary = KulfiTan,
    onSecondary = KulfiBrown,
    background = KulfiBrown,
    onBackground = KulfiCream,
    surface = Color(0xFF3C1B05),
    onSurface = KulfiCream,
)

@Composable
fun IndianKulfiOfflineTheme(
    darkTheme: Boolean = false,
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        typography = AppTypography,
        content = content,
    )
}
