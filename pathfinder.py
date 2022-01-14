import pygame
import math
from queue import PriorityQueue

# Set display window
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("Pathfinder")

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
GREY = (128,128,128)
TURQUOISE = (64,224,208)

# Define points on grid
class Point:
  def __init__(self, row, col, width, total_rows):
    self.row = row
    self.col = col
    self.x = row * width
    self.y = col * width
    self.color = WHITE
    self.neighbors = []
    self.width = WIDTH
    self.total_rows = total_rows

  def get_position(self):
    return self.row, self.col

  # Point on grid has already been examined
  def is_closed(self):
    return self.color == RED

  def is_open(self):
    return self.color == GREEN

  def is_barrier(self):
    return self.color == BLACK

  def is_start(self):
    return self.color == ORANGE

  def is_end(self):
    return self.color == TURQUOISE

  def reset(self):
    self.color = WHITE

  def make_start(self):
    self.color = ORANGE

  def make_closed(self):
    self.color = RED

  def make_open(self):
    self.color = GREEN

  def make_barrier(self):
    self.color = BLACK

  def make_end(self):
    self.color = TURQUOISE

  def make_path(self):
    self.color = PURPLE

  def draw(self, win):
    pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

  def update_neighbors(self, grid):
    self.neighbors = []

    # check downward neighbor
    if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
      self.neighbors.append(grid[self.row + 1][self.col])

    # check upward neighbor
    if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
      self.neighbors.append(grid[self.row - 1][self.col])

    # check right neighbor
    if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
      self.neighbors.append(grid[self.row][self.col + 1])

    # check left neighbor
    if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
      self.neighbors.append(grid[self.row][self.col - 1])

  def __lt__(self, other):
    return False

# Manhattan distance
def hueristic(p1, p2):
  x1, y1 = p1
  x2, y2 = p2
  return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, curr, draw):
  while curr in came_from:
    curr = came_from[curr]
    curr.make_path()
    draw()

def Astar(draw, grid, start, end):
  count = 0
  open_set = PriorityQueue()
  open_set.put((0, count, start)) # put starting node in set
  came_from = {} # keep tack of what node we came from
  g_score = {point: float("inf") for row in grid for point in row} # keeps track of current shortest dist
  g_score[start] = 0
  f_score = {point: float("inf") for row in grid for point in row} # predicted distance
  f_score[start] = hueristic(start.get_position(), end.get_position())

  # enables to check whether a point is in the priority queue
  open_set_hash = {start}

  while not open_set.empty():
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()

    curr = open_set.get()[2] # get the node with lowest f score from th PQ
    open_set_hash.remove(curr)

    # path is found
    if curr == end:
      reconstruct_path(came_from, end, draw)
      end.make_end()
      start.make_start()
      return True

    # Check neighbors of current node if path not found
    for neighbor in curr.neighbors:
      temp_g_score = g_score[curr] + 1  # calc g score

      if temp_g_score < g_score[neighbor]:  #if less, then a better path has been found
        came_from[neighbor] = curr
        g_score[neighbor] = temp_g_score
        f_score[neighbor] = temp_g_score + hueristic(neighbor.get_position(), end.get_position())

        if neighbor not in open_set_hash:
          count += 1
          open_set.put((f_score[neighbor], count, neighbor))
          open_set_hash.add(neighbor)
          neighbor.make_open()

    draw()

    if curr != start:
      curr.make_closed()

  return False

def make_grid(rows, width):
  grid = []
  gap = width // rows
  for i in range(rows):
      grid.append([])
      for j in range(rows):
        point = Point(i, j, gap, rows)
        grid[i].append(point)

  return grid

def draw_grid(win, rows, width):
  gap = width//rows
  # horizontal lines
  for i in range(rows):
    pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
    # vertical
    for j in range(rows):
        pygame.draw.line (win, GREY, (j * gap, 0), (j * gap, width))

def draw (win, grid, rows, width):
  win.fill(WHITE)

  for row in grid:
    for point in row:
      point.draw(win)

  draw_grid(win, rows, width)
  pygame.display.update()

def get_clicked_pos(pos, rows, width):
  gap = width // rows
  y, x = pos
  row = y // gap
  col = x // gap

  return row, col

def main(win, width):
  ROWS = 50
  grid = make_grid(ROWS, WIDTH)
  start = None
  end = None
  run = True

  while run:
    draw(win, grid, ROWS, width)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False

      # left mb
      if pygame.mouse.get_pressed()[0]:
        pos = pygame.mouse.get_pos()
        row, col = get_clicked_pos(pos, ROWS, width)
        point = grid[row][col]

        if not start and point != end:
          start = point
          start.make_start()

        elif not end and point != start:
          end = point
          end.make_end()

        elif point != end and point != start:
          point.make_barrier()

      # right mb
      elif pygame.mouse.get_pressed()[2]:
        pos = pygame.mouse.get_pos()
        row, col = get_clicked_pos(pos, ROWS, width)
        point = grid[row][col]
        point.reset()

        if point == start:
          start = None

        elif point == end:
          end = None

      # run pathfinder
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE and start and end:
          for row in grid:
            for point in row:
              point.update_neighbors(grid)

          Astar(lambda: draw(win, grid, ROWS, width), grid, start, end)

        if event.key == pygame.K_c:
          start = None
          end = None
          grid = make_grid(ROWS, width)

  pygame.quit()

main(WIN, WIDTH)