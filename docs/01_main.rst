###########
Description
###########

`DCC Tips Bot <https://t.me/DCCTipsBot>`_ is a chatbot, powered by the `DecentralChain <https://decentralchain.io/>`_ blockchain, it enables sending tips of any asset on the blockchain to Telegram users by tagging their username (the recipient must have a username set up on their Telegram account for the bot to work correctly).

The bot automatically creates a `Decentral.Exchange <https://decentral.exchange/>`_ wallet for each user and provides several useful commands to help manage it.

Please keep in mind that the created wallet should never be used as the primary one, it's meant for tipping only therefore avoid storing large amounts of funds due to potential security flaws. Keys are stored somewhere, we are not responsible for any lost of funds.

########
Commands
########

Check out the available commands offered by the bot:

* /help - show help message.
* /address - show the address on your tipping wallet.
* /seed - show the seed on your tipping wallet.
* /dcc_balance - show the DCC balance on your tipping wallet.
* /all_balances - show ALL the balances on your tipping wallet.
* /tipping <username> <amount> <token> - tip a user tagging their username.
* /withdraw <address> <amount> <token> - withdraw to a DecentralChain address.
* /stats - show the amount of users on the bot.