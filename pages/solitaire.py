BOARD_DIV = { 
    'index':0, 'src':'solitaire_board.txt',
    'draw_amount':1,
    'stock_pile':[], 'waste_pile':[], 
    'foundation_piles':[[] for _ in range(4)], 
    'tableau_piles':[[] for _ in range(7)],
    'focused_foundation_pile_index':0,
    'focused_tableau_pile_index':0,
}