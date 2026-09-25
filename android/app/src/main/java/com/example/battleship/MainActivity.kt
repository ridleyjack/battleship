package com.example.battleship

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.runtime.saveable.rememberSaveable
import kotlinx.coroutines.launch
import androidx.compose.foundation.background

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            BattleshipApp()
        }
    }
}

@Composable
fun BattleshipApp() {
    var serverAddress by rememberSaveable {
        mutableStateOf("http://192.168.1.68:8000")
    }
    var board by remember {
        mutableStateOf<List<List<String>>?>(null)
    }
    var error by remember {
        mutableStateOf<String?>(null)
    }
    var isLoading by remember {
        mutableStateOf(false)
    }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text("Battleship")

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = serverAddress,
            onValueChange = { serverAddress = it },
            label = { Text("Server address") },
            placeholder = { Text("http://192.168.1.68:8000") },
            singleLine = true,
            enabled = !isLoading,
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            enabled = !isLoading && serverAddress.isNotBlank(),
            onClick = {
                val address = serverAddress.trim().trimEnd('/')
                error = null
                isLoading = true

                scope.launch {
                    try {
                        board = getGame(address)
                    } catch (e: kotlinx.coroutines.CancellationException) {
                        throw e
                    } catch (e: Exception) {
                        error = e.message ?: "Unable to load game"
                    } finally {
                        isLoading = false
                    }
                }
            }
        ) {
            Text(if (isLoading) "Loading..." else "Load")
        }

        Spacer(modifier = Modifier.height(16.dp))

        when {
            isLoading -> Text("Loading...")
            error != null -> Text("Error: $error")
            board != null -> GameBoard(board!!)
            else -> Text("Enter the server address and hit Load.")
        }
    }
}

suspend fun getGame(serverAddress: String): List<List<String>> {
    return withContext(Dispatchers.IO) {

        val url = URL("$serverAddress/game/0")

        val connection = url.openConnection() as HttpURLConnection

        try {
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000

            if (connection.responseCode != 200) {
                throw Exception(
                    "Server returned ${connection.responseCode}"
                )
            }

            val response =
                connection.inputStream.bufferedReader().use {
                    it.readText()
                }

            val json = JSONObject(response)
            val jsonBoard = json.getJSONArray("ownBoard")
            val board = mutableListOf<List<String>>()

            for (rowIndex in 0 until jsonBoard.length()) {
                val jsonRow = jsonBoard.getJSONArray(rowIndex)
                val row = mutableListOf<String>()

                for (columnIndex in 0 until jsonRow.length()) {
                    row.add(jsonRow.getString(columnIndex))
                }
                board.add(row)
            }
            board
        } finally {
            connection.disconnect()
        }
    }
}

@Composable
fun GameBoard(board: List<List<String>>) {
    Column {
        for (row in board) {
            Row {
                for (cell in row) {
                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .background(
                                when (cell) {
                                    "S" -> Color.Green
                                    "X" -> Color.Red
                                    "M" -> Color.Yellow
                                    else -> Color(0xFFBBDEFB)
                                }
                            )
                            .border(
                                width = 1.dp,
                                color = Color.Gray
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(cell)
                    }
                }
            }
        }
    }
}