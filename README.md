# Usage:

1. Find the bot on Telegram.

   Bot handle: [zerowastesgbot](t.me/zerowastesgbot)

2. Press `\start`.

   If the `\start` button is not available for you, you can type it out too.

3. Select the option `Yes` when prompted.

   The bot will require you verification to start.

4. Use `\start` again if you wish to stop the bot.

<br/>

# Installation:

1.  Dependencies:

    - [pyyaml](https://pypi.org/project/PyYAML/)
    - [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

    <br/>

    ```bash
    $ python -m pip install -r requirements.txt

    # or if pip is already in your PATH
    $ pip -r requirements.txt
    ```

    Additionally you can create a virtual environment for your project:

    ```bash
    $ python -m venv venv

    # Unix
    $ source venv/bin/activate
    # Same command as before

    # Windows
    $ .\venv\Scripts\activate.bat
    ```

2.  `config.yaml`:

    You will also need to supply a `config.yaml` file.\
    The following values have be configured in the file:

    ```yaml
    # ---------------------------------- RUNTIME --------------------------------- #
    RUNTIME:
    LIVE_MODE: false
    FRESH_START: false

    # -------------------------------- BOT CONFIG -------------------------------- #
    BOT_TOKENS:
    LIVE: ""
    TEST: ""

    BOT:
    REMOVE_INLINE_KEYBOARD_MARKUP: true

    # -------------------------------- LOG CONFIG -------------------------------- #
    LOG_USER_TO_APP_LOGS: false
    ```

3.  Create a Telegram bot with [BotFather](https://telegram.me/botfather).

    After successfully creating your bot, copy the `BOT TOKEN`.

    Set `config.yaml -> BOT_TOKENS -> LIVE/TEST` to be the token.

4.  Run the bot.

    ```python
    $ python main.py
    ```

    You may need to activate `venv` if you have set it up in the earlier steps..
