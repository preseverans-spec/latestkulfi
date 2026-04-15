package com.indiankulfi.offline

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import com.indiankulfi.offline.ui.IndianKulfiApp
import com.indiankulfi.offline.ui.theme.IndianKulfiOfflineTheme
import com.indiankulfi.offline.viewmodel.MainViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            IndianKulfiRoot()
        }
    }
}

@Composable
private fun IndianKulfiRoot() {
    val viewModel: MainViewModel = viewModel()
    IndianKulfiOfflineTheme {
        IndianKulfiApp(viewModel = viewModel)
    }
}
