# MicroPython Simulation in Wokwi for VS Code

Example project for running MicroPython on [Wokwi for VS Code](https://marketplace.visualstudio.com/items?itemName=Wokwi.wokwi-vscode).

## Prerequisites

1. Install the [Wokwi for VS Code](https://marketplace.visualstudio.com/items?itemName=Wokwi.wokwi-vscode) extension.
2. Install the [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) tool, e.g. `pip install mpremote`.

## Usage

1. From the command palette, select "Wokwi: Start Simulator". You may need to activate your license first.
2. Select one of the directories to simulate, e.g. "esp32".
3. While the simulator is running, open a command prompt, and type:

   ```python
   py -m mpremote connect port:rfc2217://localhost:4000 run main.py
   ```

   This will connect to the simulator and run the `main.py` file on the board.
   Note: keep the simulator tab visible while running the command, otherwise the simulator will pause and the command will timeout.