import input_data
import variant_cp_model as vcp
import piece_mip_model as pmip

from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import enum

class Solver(enum.Enum):
    piece_mip = 0
#    variant_mip = 1 currently not implemented
#    piece_cp = 2 currently not implemented
    variant_cp = 3

def select_pieces(selected_pieces):
    piece_id = 0
    pieces = []
    for piece in input_data.all_pieces:
        if piece.name in selected_pieces:
            piece.id = piece_id
            piece_id += 1
            piece.create_new_variants(enable_rotation, enable_reflection, rotation_angles)
            pieces.append(piece)
    return pieces

def print_board(pieces, board_width, board_height):
    plt.figure()
    axes = plt.gca()
    axes.set_xlim([0,board_width])
    axes.set_ylim([0,board_height])
    axes.set_aspect('equal')

    for piece in pieces:
        for part in piece.selected_variant.parts:
            axes.add_patch(Rectangle((part.assigned_point.x, part.assigned_point.y),
                                            part.width, part.height,
                                            facecolor = piece.color))
    plt.show()

selected_pieces = [i for i in range(6,12)] # 1 to 12

enable_rotation = True 
enable_reflection = True
rotation_angles = [90, 180, 270]

board_width = 5
board_height = 12

threads = 2
time_limit = 3600

pieces = select_pieces(selected_pieces)

solver = Solver.variant_cp
if solver == Solver.variant_cp:
    model = vcp.Model()
elif solver == Solver.piece_mip:
    model = pmip.Model()

model.build(pieces, board_width, board_height)
model.solve(threads, time_limit)
model.extract_solution(pieces)

print_board(pieces, board_width, board_height)
