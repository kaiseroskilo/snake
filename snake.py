# a snake game written for python3.2


# TODO
# * correlate the terminal's dimensions with the field dimensions
# * employ restart functionality
# * use colors
import queue
import random
import curses
import threading
import time

class GameOver(Exception):
    pass

class snakeGame:
    #some class variables/map indicators
    empty = ' '
    snake = '*'
    apple = '@'
    wall_corner = '+'
    wall_vertical = '|'
    wall_horizontal = '-'

    field_size = 20

    def __init__(self, game_id):
        self.game_id = game_id
        self.turn = 0
        self.field = [[self.empty for j in range(self.field_size)] for i in range(self.field_size)]
        #position walls 
        for i in range(self.field_size):
            self.field[0][i] = self.wall_horizontal
            self.field[self.field_size-1][i] = self.wall_horizontal
            self.field[i][0] = self.wall_vertical
            self.field[i][self.field_size-1] = self.wall_vertical
        self.field[0][0] = self.wall_corner
        self.field[0][self.field_size-1] = self.wall_corner
        self.field[self.field_size-1][0] = self.wall_corner
        self.field[self.field_size-1][self.field_size-1] = self.wall_corner

        #create and position snake
        self.snake_queue = queue.Queue()
        
        self.snake_queue.put((self.field_size // 2 , self.field_size //2))
        self.snake_queue.put((self.field_size // 2 , self.field_size //2 + 1))
        self.snake_queue.put((self.field_size // 2 , self.field_size //2 + 2))


        self.field[self.field_size // 2][self.field_size // 2] = self.snake
        self.field[self.field_size // 2][self.field_size // 2 + 1] = self.snake
        self.field[self.field_size // 2][self.field_size // 2 + 2] = self.snake
        
        #snake's default direction
        self.default_direction = 'R'

        #existence of apple in field
        self.apple_exists = 0

    def set_direction(self,direction):
        #check validity of direction
        head = self.snake_queue.queue[-1]
        before_head = self.snake_queue.queue[-2]  # maybe this is the neck :P
        x_coord = head[0]-before_head[0]
        y_coord = head[1]-before_head[1]

        if( x_coord == 0 ):
            if ( y_coord > 0 ) : non_valid_direction = 'L'
            else : non_valid_direction = 'R'
        else:  #y_coord is 0
            if ( x_coord > 0 ) : non_valid_direction = 'U'
            else : non_valid_direction = 'D'

        if ( direction != non_valid_direction) and (direction in ('R','L','U','D')) : self.default_direction = direction
        return


    def move_snake(self):
        """
        Move the snake across the map. If the head of the snake hits a wall or itself the game ends
        while if it hits an apple the snake's length is increased by one.
        """

        #translate direction into coordinates
        if self.default_direction == 'R':
            self.field_block_to_be_occupied = (self.snake_queue.queue[-1][0], self.snake_queue.queue[-1][1] + 1)
        elif self.default_direction == 'L' :
            self.field_block_to_be_occupied = (self.snake_queue.queue[-1][0], self.snake_queue.queue[-1][1] - 1)
        elif self.default_direction == 'U' :
            self.field_block_to_be_occupied = (self.snake_queue.queue[-1][0] - 1, self.snake_queue.queue[-1][1])
        elif self.default_direction == 'D' :
            self.field_block_to_be_occupied = (self.snake_queue.queue[-1][0] + 1, self.snake_queue.queue[-1][1])

        #check for obstacles
        x_coord = self.field_block_to_be_occupied[0]
        y_coord = self.field_block_to_be_occupied[1]

        if( (self.field[x_coord][y_coord] == self.wall_vertical) or self.field[x_coord][y_coord] == self.wall_horizontal or (self.field[x_coord][y_coord] == self.snake) ):
            self.end_game()  #game over
        elif self.field[x_coord][y_coord] == self.apple:
            self.snake_queue.put((x_coord,y_coord))
            self.field[x_coord][y_coord] = self.snake
            self.apple_exists = 0
        else:
            self.snake_queue.put((x_coord,y_coord))
            self.field[x_coord][y_coord] = self.snake
            (x_coord,y_coord) = self.snake_queue.get()
            self.field[x_coord][y_coord] = self.empty
        return


    def spawn_apple(self):
        while(True):
            self.new_apple_position = (random.randint(1,self.field_size-1),random.randint(1,self.field_size-1))
            print(self.new_apple_position)
            if self.field[self.new_apple_position[0]][self.new_apple_position[1]] == self.empty :
                #delete old apple
                self.field[self.new_apple_position[0]][self.new_apple_position[1]] = self.empty
                #position new apple in field
                self.field[self.new_apple_position[0]][self.new_apple_position[1]] = self.apple
                #toggle apple_exists
                self.apple_exists = 1
                return

    def take_turn(self):
        self.turn = self.turn + 1
        self.move_snake()
        if(self.apple_exists == 0) :
            self.spawn_apple()
        return


    def end_game(self):
        raise GameOver()

def keyloop(stdscr, game):
    stdscr.clear()
    stdscr_y,stdscr_x = stdscr.getmaxyx()

    stdscr.addstr(game.field_size+1,0,"simple game of snake :P, you know the drill")
    stdscr.addstr(game.field_size+2,0,"Exit with Q.")
    stdscr.refresh()
    while True:
        c = stdscr.getch()
        if chr(c) in 'Qq':
            #quit game
            raise GameOver()
        elif chr(c) in 'Rr':
            #restart game
            pass
        elif c == curses.KEY_UP:
            game.set_direction('U')
        elif c == curses.KEY_DOWN:
            game.set_direction('D')
        elif c == curses.KEY_RIGHT:
            game.set_direction('R')
        elif c == curses.KEY_LEFT:
            game.set_direction('L')
        else:
            pass

    return

def display(stdscr, game):
    for i in range(game.field_size):
        for j in range(game.field_size):
            stdscr.addch(j, i, game.field[j][i])
    stdscr.refresh()
    return

def my_timer(period,function, game, stdscr):
    """
    periodically invokes function
    """
    try:
        while(True):
            function()
            display(stdscr, game)
            time.sleep(period)

    except Exception as exc:
        raise exc #propagate back
        return
    finally:
        return   #duh :/

def main(stdscr):
    game_instance = snakeGame(1)
    t = threading.Thread(target = my_timer, args = (0.5, game_instance.take_turn, game_instance, stdscr)) # a kind of one-threaded periodic timer
    t.daemon = True
    t.start()         #activate the thread
    keyloop(stdscr, game_instance) #loop while reading keys

if __name__ == "__main__":
    import sys
    sys.stderr=sys.stdout = open("debug.txt",'w')
    try:
        curses.wrapper(main)
    except Exception:
        pass
