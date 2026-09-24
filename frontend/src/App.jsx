import { useEffect, useState } from 'react'
import './App.css'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const [player, setPlayer] = useState(0)

  const [game, setGame] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [refreshCount, setRefreshCount] = useState(0)

  const [message, setMessage] = useState('Choose a tile to fire.')
  const [gameOver, setGameOver] = useState(false)

  useEffect(() => {
    const controller = new AbortController()

    async function loadGame() {
      setLoading(true)
      setError(null)
      setGame(null)

      try {
        const response = await fetch(
          `${API_BASE_URL}/game/${player}`,
          { signal: controller.signal }
        )

        if (!response.ok) {
          throw new Error(`Could not load game (${response.status})`)
        }

        const data = await response.json()

        if (!controller.signal.aborted) {
          setGame(data)
          setGameOver(data.gameOver)
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err.message)
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    loadGame()

    return () => controller.abort()
  }, [player, refreshCount])

  async function handleClick(x, y,) {
    if (gameOver || loading) return
    setError(null)

    try {
      const response = await fetch(`${API_BASE_URL}/shoot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player: player, x: x, y: y })
      })

      const data = await response.json()
      if (!response.ok) {
        setMessage(
          typeof data.detail === 'string'
            ? data.detail
            : `Invalid shot (${response.status})`
        )
        return
      }

      console.log(data)

      if (data.gameOver) {
        setMessage(`${data.result} Game over!`)
        setGameOver(true)
      }
      else
        setMessage(data.result)


      setRefreshCount(count => count + 1)
    }
    catch (err) {
      setError(err.message)
    }
  }

  async function reset() {
    setError(null)

    try {
      const response = await fetch(`${API_BASE_URL}/reset`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error(`Reset failed (${response.status})`)
      }

      setMessage('New game! Choose a tile to fire.')
      setRefreshCount(count => count + 1)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <PlayerSelect
        player={player}
        setPlayer={setPlayer}
      />
      <button
        onClick={() => reset()}
      >
        Reset
      </button>

      {loading && <p role="status">Loading game…</p>}
      {error && <p role="alert">{error}</p>}

      {!loading && game && (
        <div className="boards">
          <GameBoard board={game.targetBoard} title="Enemy Fleet" handleClick={handleClick} clickable disabled={gameOver} />
          <GameBoard board={game.ownBoard} title="Friendly Fleet" handleClick={handleClick} />
        </div>
      )}

      <p className="game-message" role="status">
        {message}
      </p>
    </>
  )
}


function Square({ x, y, value, handleClick, clickable = false, disabled }) {
  const className = `square square--${value}`

  if (clickable) {
    return (
      <button
        className={className}
        onClick={() => handleClick(x, y)}
        disabled={disabled}
      >
        {value}
      </button>
    )
  }

  return (
    <div className={className}>
      {value}
    </div>
  )
}


function GameBoard({ board, title, handleClick, clickable = false, disabled }) {
  const columns = board[0]?.length ?? 0;
  if (columns === 0) return null;

  const squares = []
  for (let y = 0; y < board.length; y++) {
    for (let x = 0; x < columns; x++) {
      squares.push(
        <Square
          key={`${x}-${y}`}
          x={x}
          y={y}
          value={board[y][x]}
          clickable={clickable}
          handleClick={handleClick}
          disabled={disabled}
        />
      )
    }
  }

  return (
    <section className="board-panel">
      <h2>{title}</h2>
      <div
        className="board"
        style={{ "--board-columns": board[0]?.length ?? 0 }}
      >
        {squares}
      </div>
    </section>
  )
}

function PlayerSelect({ player, setPlayer }) {
  return (
    <>
      <button
        onClick={() => setPlayer(0)}
        disabled={player === 0}
      >
        Player A
      </button>

      <button
        onClick={() => setPlayer(1)}
        disabled={player === 1}
      >
        Player B
      </button>
    </>
  )
}


export default App
