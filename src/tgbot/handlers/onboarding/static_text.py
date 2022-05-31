private = '{bot_name} is a chatbot, powered by the <a href="https://decentralchain.io">DecentralChain</a> blockchain, it enables sending tips of any asset on the blockchain to Telegram users by tagging their username (the recipient must have a username set up on their Telegram account for the bot to work correctly).\n\n'\
          f'The bot automatically creates a <a href="https://decentral.exchange/">Decentral.Exchange</a> wallet for each user and provides several useful commands to help manage it.\n\n'\
          f'Please keep in mind that the created wallet should never be used as the primary one, it\'s meant for tipping only therefore avoid storing large amounts of funds due to potential security flaws. Keys are stored somewhere, we are not responsible for any lost of funds.\n\n'\
          'Check out the available commands of {bot_username}'
help_desc = f'show this help message'
address_desc = f'show the address on your tipping wallet'
seed_desc = f'show the seed on your tipping wallet'
dcc_balance_desc = f'show the DCC balance on your tipping wallet'
all_balances_desc = f'show ALL the balances on your tipping wallet'
tipping = f'/tipping username amount token - tip a user tagging their username'
withdraw = f'/withdraw address amount token - withdraw to a DecentralChain address'
stats_desc = f'show the amount of users on the bot'
help =  f'{private}:\n'\
        f'/help - {help_desc}.\n'\
        f'/address - {address_desc}.\n'\
        f'/seed - {seed_desc}.\n'\
        f'/dcc_balance - {dcc_balance_desc}.\n'\
        f'/all_balances - {all_balances_desc}.\n'\
        f'{tipping}.\n'\
        f'{withdraw}.\n'\
        f'/stats - {stats_desc}.'        