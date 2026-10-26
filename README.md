# Poker Probabilities Calculator

A high-performance Python Poker Calculator that computes winning probabilities (equity), outs, and heatmaps for Texas Hold'em. It includes both a **CLI** (Command Line Interface) and a **Web Interface** powered by Flask.

## Features

*   **Monte Carlo Simulation**: Fast estimation of winning probabilities against N opponents.
*   **Outs Calculation**: Identifies cards that immediately improve your hand.
*   **Heatmap Analysis**: Visualizes which future cards (Turn/River) increase or decrease your equity.
*   **Optimized Evaluator**: Uses bitwise operations and prime number products (Cactus Kev's algorithm variant) for rapid hand evaluation.
*   **Dual Interface**: Run it in your terminal or view it in your browser.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/LFM57/Poker-Probas.git
    cd Poker-Probas
    ```

2.  **Install dependencies** (Required for the Web App):
    ```bash
    pip install flask
    ```
    *(The core logic and CLI depend only on Python's standard library.)*

## Usage

### 1. Command Line Interface (CLI)
Run the text-based analyzer:
```bash
python main.py
```
Follow the prompts to enter your hand (e.g., `Ah Kd` or `10s 10h`), the board (0, 3, 4, or 5 cards), and dead/folded cards.

### 2. Web Application
Start the Flask server:
```bash
python app.py
```
Open your browser and go to `http://127.0.0.1:5000`.

### 3. Running Unit Tests
Run the automated test suite to verify hand evaluations, outs calculations, Monte Carlo simulations, and API endpoints:
```bash
python -m unittest test_logic.py
```

## Project Structure

*   `simulator.py`: Core simulation engine (Outs, Heatmap, Monte Carlo).
*   `evaluator_fast.py`: Optimized 7-card hand evaluator.
*   `card.py`: Card and Deck definitions.
*   `main.py`: Entry point for the CLI.
*   `app.py`: Entry point for the Web App.
*   `test_logic.py`: Unit tests to verify logic correctness.

## Contributing

Feel free to open issues or submit pull requests to improve the simulator's speed or accuracy.
