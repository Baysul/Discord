# Discord
An IRC bot written in Python that uses Markov chains to interact.

## Prerequisites
* Twisted
* NLTK
* PyMarkov

## Instructions
1. Install the modules with Pip.
  * **Do not** install *PyMarkov* using Pip! Instead, run this command to have submodule download it for you.
  ```
  git submodule update --init --recursive
  ```
2. Once you've installed the modules, download *all* of the NLTK collections (maybe not all of them, but that's what I did).
  * I downloaded them using the NLTK downloader which you can run by starting an interactive Python console, then importing the **nltk** module, and finally invoking its *download* method.
3. Run the script like
```
python Discord.py address [+]port
```

Adding a plus sign to the port tells the script to connect over a secure connection.

<small>**Tip:** You can have the script run like a bash script or any other binary program under a UNIX-like platform by adding a she-bang (usually *#!/usr/bin/python*) to the top.</small>

## Configuration
You can't really "configure" anything at the moment. You change the bot's nickname, username, etc. by modifying the **Discord** class' properties. You can also create hooks - read more about them [here](https://twistedmatrix.com/documents/current/api/twisted.words.protocols.irc.IRCClient.html).

## Todo
- [ ] Implement configuration and [SQLite](https://docs.python.org/2/library/sqlite3.html).
- [ ] Fix white-spaces before punctuation.
- [ ] Define logger property in **Commands** module (maybe use self.bot's?)
