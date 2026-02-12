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
    git clone https://github.com/your-username/poker-probas.git
    cd poker-probas
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
Follow the prompts to enter your hand (e.g., `Ah Kd`) and the board.

### 2. Web Application
Start the Flask server:
```bash
python app.py
```
Open your browser and go to `http://127.0.0.1:5000`.

## Project Structure

*   `simulator.py`: Core simulation engine (Outs, Heatmap, Monte Carlo).
*   `evaluator_fast.py`: Optimized 7-card hand evaluator.
*   `card.py`: Card and Deck definitions.
*   `main.py`: Entry point for the CLI.
*   `app.py`: Entry point for the Web App.
*   `test_logic.py`: Unit tests to verify logic correctness.

## Contributing

Feel free to open issues or submit pull requests to improve the simulator's speed or accuracy.
