import os

ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
suits = {
    'S': '♠', 
    'H': '♥', 
    'D': '♦', 
    'C': '♣'  
}

def create_card_file(rank, suit, symbol):
    filename = f"{rank}{suit}_M.txt"
    content = f"""7 9	
╭───────╮
│{rank:<2}    {symbol}│
│       │
│       │
│       │
│       │
╰───────╯
Created by \"AjinGixtas\" (https://github.com/AjinGixtas)
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

for rank in ranks:
    for suit, symbol in suits.items():
        create_card_file(rank, suit, symbol)

