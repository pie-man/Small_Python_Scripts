# Attempt to create a sudoku board object, and popoulate it with all the values still possible

def full_set(): 
    return [x +1 for x in range(9)]

def remove_possibles(input, del_list):
    return [a for a in input if a not in del_list]

class possibles(object):
    def __init__(self):
        self.possibles = full_set()

class sudoku_board(object):
    def __init__(self, setup_values):
        self.solved = 0
        self.possibles = []
        for _ in range(81):
            self.possibles.append(possibles())
        self.solution = []
        for _ in range(81):
            self.solution.append(0)
        self.rows = []
        for row in range(9):
            self.rows.append([self.possibles[9*row + x] for x in range(9)])
        self.columns = []
        for column in range(9):
            self.columns.append([self.possibles[9*x + column] for x in range(9)])
        self.blocks = []
        for block in range(9):
            self.blocks.append([])
            column = block % 3
            home_row = block - column
            for row in range(3):
                for sub_column in range(3):
                    index = ((home_row + row) * 9) + ((column * 3) + sub_column)
                    self.blocks[block].append(self.possibles[index])
        for row, column, value in setup_values:
            index = (row * 9) + column
            #self.solution[index] = value
            self.set_value(index, value)

    def set_value(self, index, value):
        column = index % 9
        row = index // 9
        block = (column //3) + (row //3)*3
        self.solution[index] = value
        self.solved += 1
        mask_set = remove_possibles(full_set(), [value])
        self.possibles[index].possibles = remove_possibles(self.possibles[index].possibles, mask_set)
        for possible in self.rows[row]:
             possible.possibles = remove_possibles(possible.possibles, [value])
        for possible in self.columns[column]:
             possible.possibles = remove_possibles(possible.possibles, [value])
        for possible in self.blocks[block]:
             possible.possibles = remove_possibles(possible.possibles, [value])

    def only_row_in_block(self):
        '''Needs something to remove a value from the same 'whole row' if it must appear in
           a given row in a block'''
 
    def only_column_in_block(self):
        '''Needs something to remove a value from the same 'whole column' if it must appear in
           a given column in a block'''
 
    def check_single_possibles(self):
        for index in range(81):
            if self.solution[index] ==0:
                if len( self.possibles[index].possibles ) == 1:
                     #print "At index {0:} got one possibe of {1:}".format(index, self.possibles[index].possibles[0])
                     self.set_value(index, self.possibles[index].possibles[0])

    def only_place_in_row(self):
        row_c = 0
        for row in self.rows:
           for value in range(1,10):
               max_count = 0
               column_c = -1
               for possibility in row:
                   column_c += 1
                   if value in possibility.possibles:
                       max_count += 1
                       column = column_c
               if max_count == 1:
                   index = (row_c * 9) + column
                   print "r-check: only one place for a {0:} at {3:} : row {1:} column {2:}".format(value, row_c, column, index)
                   self.set_value(index, value)
           row_c += 1

    def only_place_in_column(self):
        column_c = 0
        for column in self.columns:
           for value in range(1,10):
               max_count = 0
               row_c = -1
               for possibility in column:
                   row_c += 1
                   if value in possibility.possibles:
                       max_count += 1
                       row = row_c
               if max_count == 1:
                   index = (row * 9) + column_c
                   print "c-check: only one place for a {0:} at {3:} : row {1:} column {2:}".format(value, row, column_c, index)
                   self.set_value(index, value)
           column_c += 1

    def reduce_possibles_blocks(self):
        force = False
        max_changes = 0
        for block in self.blocks:
            changes = 1
            while changes != 0:
                changes = self.reduce_possibles_generic(block)
                if changes > 0:
                    if changes > max_changes:
                         max_changes = changes
                    print "After checking a block : identified {0:} changes".format(changes)
        if max_changes > 0:
            print "max changes from block hecking was {0:}".format(max_changes)
            self.check_single_possibles()
            force = True
        return force

    def reduce_possibles_rows(self):
        force = False
        max_changes = 0
        for row in self.rows:
            changes = 1
            while changes != 0:
                changes = self.reduce_possibles_generic(row)
                if changes > 0:
                    if changes > max_changes:
                         max_changes = changes
                    print "After checking a row : identified {0:} changes".format(changes)
        if max_changes > 0:
            print "max changes from row hecking was {0:}".format(max_changes)
            self.check_single_possibles()
            force = True
        return force

    def reduce_possibles_columns(self):
        force = False
        max_changes = 0
        for column in self.columns:
            changes = 1
            while changes != 0:
                changes = self.reduce_possibles_generic(column)
                if changes > 0:
                    if changes > max_changes:
                         max_changes = changes
                    print "After checking a column : identified {0:} changes".format(changes)
        if max_changes > 0:
            print "max changes from column hecking was {0:}".format(max_changes)
            self.check_single_possibles()
            force = True
        return force


    def reduce_possibles_generic(self, grouping):
        reductions = 0
        groups = []
        duplicates = []
        #for possible_obj in self.blocks[block_no]:
        for possible_obj in grouping:
             possible_group = possible_obj.possibles
             if possible_group:
                 possible_group.sort()
                 if possible_group in groups:
                     duplicates.append(possible_group)
                     print "Found a duplicate set of possibles : {0:}".format(possible_group)
                 else:
                     groups.append(possible_group)

        true_duplicates = []
        for duplicate in duplicates:
            found = duplicates.count(duplicate) + 1
            if found == len(duplicate):
                print"I think I found enough of {0} to elimate them from others".format(duplicate)
                if duplicate not in true_duplicates:
                    true_duplicates.append(duplicate)
                    print "added {0:} to list of true duplictaes".format(duplicate)

        #for possible_obj in self.blocks[block_no]:
        for possible_obj in grouping:
             for duplicate in true_duplicates:
                 #if possible_obj.possibles and possible_obj.possibles != duplicate:
                 if (any([value in possible_obj.possibles for value in duplicate]) and
                         possible_obj.possibles != duplicate):
                      print "Removing {0:} from {1:}".format(duplicate, possible_obj.possibles)
                      possible_obj.possibles = remove_possibles(possible_obj.possibles, duplicate)
                      reductions += 1
                 elif possible_obj.possibles:
                     print "match or mismatch ? : {0:} v {1:}".format(duplicate, possible_obj.possibles)
        return reductions

    def print_solution(self):
        for row_block in range(3):
          print("===========================================")
          for row_count in range(3):
            row = (row_block * 3) + row_count
            index_start = row * 9
            index_end = index_start + 9
            str_row = ("#  {0:} | {1:} | {2:}  #  {3:} | {4:} | {5:}  #  {6:} | {7:} | {8:}  #".
                                                   format(*self.solution[index_start:index_end]))
            str_row = str_row.replace("0"," ")
            print str_row
            if row_count != 2:
              print("-------------------------------------------")

        print("===========================================")
        
def main():
    #setup = [
    #         [0,2,1], [0,3,2], [0,4,8], [0,7,6],
    #         [1,0,4], [1,3,6], [1,5,3], [1,6,5], [1,8,7],
    #         [2,0,5], [2,2,9], [2,8,3],
    #         [3,0,6], [3,1,5], [3,6,2],
    #         [4,4,3],
    #         [5,0,2], [5,2,7], [5,5,4], [5,7,5], [5,8,1],
    #         [6,0,3], [6,6,1], [6,8,4],
    #         [7,0,9], [7,2,8], [7,3,1], [7,5,7], [7,8,2],
    #         [8,1,2], [8,4,4], [8,5,8], [8,6,7],
    #        ]
    setup = [
             [0,2,6], [0,5,1], [0,7,7],
             [1,2,8], [1,4,7],
             [2,1,3], [2,5,6], [2,6,9],
             [3,4,8], [3,5,9], [3,7,4], [3,8,2],
             [4,0,2], [4,8,5],
             [5,0,8], [5,1,6], [5,3,3], [5,4,5],
             [6,2,9], [6,3,6], [6,7,3],
             [7,4,1], [7,6,4],
             [8,1,5], [8,3,4], [8,6,1],
            ]
    board = sudoku_board(setup)
    board.print_solution()

    print "starting out with {0:} solved squares".format(board.solved)
    passes = 0
    old_solved = board.solved - 1
    max_depth = 0
    while ((board.solved - old_solved) > 0 and board.solved != 81) or recheck:
        recheck = False
        old_solved = board.solved
        passes += 1
        if max_depth < 1:
            max_depth = 1
        # Do some funky stuff
        board.check_single_possibles()
        if board.solved != old_solved:
            print "After single possibility elimiination : now solved {0:} squares".format(board.solved)
            continue

        if max_depth < 2:
            max_depth = 2
        board.only_place_in_row()
        if board.solved != old_solved:
            print "After row checking : now solved {0:} squares".format(board.solved)
            board.print_solution()
            continue

        if max_depth < 3:
            max_depth = 3
        board.only_place_in_column()
        if board.solved != old_solved:
            print "After column checking : now solved {0:} squares".format(board.solved)
            board.print_solution()
            continue

        if max_depth < 4:
            max_depth = 4
        recheck = board.reduce_possibles_blocks()
        if board.solved != old_solved:
            print "After block checking : now solved {0:} squares".format(board.solved)
            board.print_solution()
            continue

        if max_depth < 5:
            max_depth = 5
        recheck = board.reduce_possibles_rows()
        if board.solved != old_solved:
            print "After row checking : now solved {0:} squares".format(board.solved)
            board.print_solution()
            continue
        else:
            print "After row checking : now solved {0:} squares".format(board.solved)

        if max_depth < 6:
            max_depth = 6
        recheck = board.reduce_possibles_columns()
        if board.solved != old_solved:
            print "After column checking : now solved {0:} squares".format(board.solved)
            board.print_solution()
            continue
        else:
            print "After column checking : now solved {0:} squares".format(board.solved)

    print "## Solved that puzzle in {0:} passes  max depth = {1:} ##".format(passes, max_depth)
    board.print_solution()
    possibles_by_block(7,board)
    possibles_by_block(2,board)

def possibles_by_row(row_num):
    for column in range(9):
        print "row {0:} : column {1:}  :: {2:}".format(row_num, column, board.rows[row_num][column].possibles)

def possibles_by_column(column_num):
        for row in range(9):
            print "row {0:} : column {1:}  :: {2:}".format(row, column_num, board.rows[row][column_num].possibles)

def possibles_by_block(block_num, board):
    block_col = block_num % 3
    block_row = block_num // 3
    home_row = block_row * 3
    for row in range(3):
        row_contents = []
        for column in range(3):
            row_contents.append(board.blocks[block_num][(row*3)+column].possibles)
        print "block {0:} , row {1:} : {2:}".format(block_num, row, row_contents)


if __name__ == "__main__":
    main()
    #for row in [0,4,6]:
    #for column in [2,6]:
