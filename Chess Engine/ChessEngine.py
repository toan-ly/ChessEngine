"""
This class is responsible for storing all the info about the current state of a chess game.
It'll also responsible for determining the valid moves at current state.
It'll also keep a move log.
"""
class GameState():
  def __init__(self):
    # 8x8 2d list
    # b for black, w for white
    # R: Rook, N: Knight, B: Bishop, Q: Queen, K: King
    # p: pawn
    # --: empty space 
    self.board = [
      ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'], 
      ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'], 
      ['--', '--', '--', '--', '--', '--', '--', '--'], 
      ['--', '--', '--', '--', '--', '--', '--', '--'], 
      ['--', '--', '--', '--', '--', '--', '--', '--'], 
      ['--', '--', '--', '--', '--', '--', '--', '--'], 
      ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'], 
      ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
    self.moveFunctions = {'p': self.getPawnMoves, 
                          'R': self.getRookMoves,
                          'N': self.getKnightMoves,
                          'B': self.getBishopMoves,
                          'Q': self.getQueenMoves,
                          'K': self.getKingMoves}
    self.whiteToMove = True
    self.moveLog = []
    self.whiteKingLocation = (7, 4)
    self.blackKingLocation = (0, 4)
    # self.inCheck = False
    # self.pins = []
    # self.checks = []
    
    self.checkMate = False
    self.staleMate = False
    
  '''
  Takes a move as a parameter and executes it 
  (Won't work for castling, pawn promotion, and en-passant)
  '''
  def makeMove(self, move):
    self.board[move.startRow][move.startCol] = '--'
    self.board[move.endRow][move.endCol] = move.pieceMoved
    self.moveLog.append(move)
    self.switchTurn() # swap turn
    
    # update king's location if moved
    if move.pieceMoved == 'wK':
      self.whiteKingLocation = (move.endRow, move.endCol)
    elif move.pieceMoved == 'bK':
      self.blackKingLocation = (move.endRow, move.endCol)
      

    
  '''
  Undo the last move made
  '''
  def undoMove(self):
    if len(self.moveLog) != 0: # make sure there's a move to undo
      move = self.moveLog.pop()
      self.board[move.startRow][move.startCol] = move.pieceMoved
      self.board[move.endRow][move.endCol] = move.pieceCaptured
      self.switchTurn() # switch turns back
      
      # update king's location if needed
      if move.pieceMoved == 'wK':
        self.whiteKingLocation = (move.startRow, move.startCol)
      elif move.pieceMoved == 'bK':
        self.blackKingLocation = (move.startRow, move.startCol)

  '''
  All moves considering checks
  '''
  def getValidMoves(self):
    # 1. generate all possible moves
    moves = self.getAllPossibleMoves()
    # 2. for each move, make the move
    for i in range(len(moves) - 1, -1, -1):
      self.makeMove(moves[i])
      # 3. generate all opponent's moves
      # 4. for each opponent's move, see if they attack the king
      self.switchTurn()
      if self.inCheck():
        moves.remove(moves[i])
      self.switchTurn()
      self.undoMove()
    if len(moves) == 0: # either checkmate or stalemate
      if self.inCheck():
        self.checkMate = True
      else:
        self.staleMate = True
    else:
      self.checkMate = False
      self.staleMate = False
    
    return moves
  
  '''
  Determine if the current player is in check
  '''
  def inCheck(self):
    if self.whiteToMove:
      return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
    else:
      return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
  '''
  Determine if the opponent can attack the square (r, c)
  '''
  def squareUnderAttack(self, r, c):
    self.switchTurn()
    oppMoves = self.getAllPossibleMoves()
    self.switchTurn()
    for move in oppMoves:
      if move.endRow == r and move.endCol == c:
        return True
    return False

  def switchTurn(self):
    self.whiteToMove = not self.whiteToMove

  '''
  All moves without considering checks
  '''
  def getAllPossibleMoves(self):
    moves = []
    for r in range(len(self.board)):
      for c in range(len(self.board[r])):
        turn = self.board[r][c][0]
        if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove): 
          piece = self.board[r][c][1]
          self.moveFunctions[piece](r, c, moves) # call appropriate move function based on piece type
            
    return moves
    
  '''
  Get all the pawn moves
  '''
  def getPawnMoves(self, r, c, moves):
    if self.whiteToMove: # white's turn
      if self.board[r - 1][c] == '--': # 1 square pawn advance
        moves.append(Move((r, c), (r-1, c), self.board))
        if r == 6 and self.board[r-2][c] == '--': # 2 square pawn advance
          moves.append(Move((r, c), (r-2, c), self.board))
          
      if c - 1 >= 0: # capture to the left
        if self.board[r-1][c-1][0] == 'b': # enemy piece to capture
          moves.append(Move((r, c), (r-1, c-1), self.board))
      if c + 1 <= 7: # capture to the right
        if self.board[r-1][c+1][0] == 'b':
          moves.append(Move((r, c), (r-1, c+1), self.board)) 
    
    else: # black's turn
      if self.board[r + 1][c] == '--': # 1 square pawn advance
        moves.append(Move((r, c), (r+1, c), self.board))
        if r == 1 and self.board[r+1][c] == '--': # 2 square
          moves.append(Move((r, c), (r+2, c), self.board))

      if c - 1 >= 0:
        if self.board[r+1][c-1][0] == 'w':
          moves.append(Move((r, c), (r+1, c-1), self.board))
      if c + 1 <= 7:
        if self.board[r+1][c+1][0] == 'w':
          moves.append(Move((r, c), (r+1, c+1), self.board))
          
    # add pawn promotions
          
  '''
  Get all the rook moves
  '''
  def getRookMoves(self, r, c, moves):
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left, down, right
    enemyColor = 'b' if self.whiteToMove else 'w'
    for d in directions:
      for i in range(1, 8):
        endRow = r + d[0] * i
        endCol = c + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
          endPiece = self.board[endRow][endCol]
          if endPiece == '--': # empty space
            moves.append(Move((r, c), (endRow, endCol), self.board))
          elif endPiece[0] == enemyColor: # enemy piece on the way, can capture
            moves.append(Move((r, c), (endRow, endCol), self.board))
            break
          else: # friend piece, cannot capture
            break
        else: # off board
          break

  '''
  Get all the knight moves
  '''
  def getKnightMoves(self, r, c, moves):
    directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
    allyColor = 'w' if self.whiteToMove else 'b'
    for d in directions:
      endRow = r + d[0]
      endCol = c + d[1]
      if 0 <= endRow < 8 and 0 <= endCol < 8:
        endPiece = self.board[endRow][endCol]
        if endPiece[0] != allyColor:
          moves.append(Move((r, c), (endRow, endCol), self.board))
  
  '''
  Get all the bishop moves
  '''
  def getBishopMoves(self, r, c, moves):
    directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) 
    enemyColor = 'b' if self.whiteToMove else 'w'
    for d in directions:
      for i in range(1, 8):
        endRow = r + d[0] * i
        endCol = c + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
          endPiece = self.board[endRow][endCol]
          if endPiece == '--': # empty space
            moves.append(Move((r, c), (endRow, endCol), self.board))
          elif endPiece[0] == enemyColor: # enemy piece on the way, can capture
            moves.append(Move((r, c), (endRow, endCol), self.board))
            break
          else: # friend piece, cannot capture
            break
        else: # off board
          break     

  '''
  Get all the queen moves
  '''
  def getQueenMoves(self, r, c, moves):
    self.getRookMoves(r, c, moves)
    self.getBishopMoves(r, c, moves)

  '''
  Get all the king moves
  '''
  def getKingMoves(self, r, c, moves):
    directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))     
    allyColor = 'w' if self.whiteToMove else 'b'
    for i in range(8):
      endRow = r + directions[i][0]
      endCol = c + directions[i][1]
      if 0 <= endRow < 8 and 0 <= endCol < 8: 
        endPiece = self.board[endRow][endCol]
        if endPiece[0] != allyColor:
          moves.append(Move((r, c), (endRow, endCol), self.board))
    

    
class Move():
  ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
  rowsToRanks = {v: k for k, v in ranksToRows.items()}
  filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
  colsToFiles = {v: k for k, v in filesToCols.items()}
  
  def __init__(self, startSq, endSq, board):
    self.startRow = startSq[0]
    self.startCol = startSq[1]
    self.endRow = endSq[0]
    self.endCol = endSq[1]
    self.pieceMoved = board[self.startRow][self.startCol]
    self.pieceCaptured = board[self.endRow][self.endCol] 
    self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    
  '''
  Override equals method
  '''
  def __eq__(self, other):
    if isinstance(other, Move):
      return self.moveID == other.moveID
    return False

  def getChessNotation(self):
    return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
  
  def getRankFile(self, r, c):
    return self.colsToFiles[c] + self.rowsToRanks[r]
