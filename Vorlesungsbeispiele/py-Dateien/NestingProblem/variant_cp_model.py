from ortools.sat.python import cp_model
import collections
import math
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import input_data

class Model:
    def __init__(self):
        self.dimensions = {}
        self.positions = {}
        self.intervals = collections.defaultdict(list)
        self.variant_used = {}
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

    def build(self, pieces, board_width, board_height):

        position = collections.namedtuple('position', 'x_start x_end y_start y_end')
        dimension = collections.namedtuple('dimension', 'width height')
        
        total_length = self.model.NewIntVar(0, board_height, 'total_length')

        for piece in pieces:
            for variant in piece.variants:
                self.variant_used[(piece.id,variant.id)] = self.model.NewBoolVar('variant_used(' + str(piece.id) + ',' + str(variant.id) + ')' )
        
        for piece in pieces:
            for variant in piece.variants:
                for part in variant.parts:
                    interval_name = str(piece.id) + ',' + str(variant.id) + ',' + str(part.id)
                    x_start =  self.model.NewIntVar(0, board_width, 'x_start(' + interval_name + ')')
                    x_end =  self.model.NewIntVar(0, board_width, 'x_start(' + interval_name + ')')
                    y_start =  self.model.NewIntVar(0, board_height, 'y_start(' + interval_name + ')')
                    y_end =  self.model.NewIntVar(0, board_height, 'y_end(' + interval_name + ')')
            
                    self.positions[(piece.id, variant.id, part.id)] = position(x_start = x_start, x_end = x_end,
                                                                        y_start = y_start, y_end = y_end)
                    
                    part_width = self.model.NewIntVarFromDomain(cp_model.Domain.FromIntervals([[0], [part.width]]), 'width(' + interval_name + ')')
                    part_height = self.model.NewIntVarFromDomain(cp_model.Domain.FromIntervals([[0], [part.height]]), 'height(' + interval_name + ')')
                    
                    self.model.Add(part_width == part.width).OnlyEnforceIf(self.variant_used[(piece.id,variant.id)])
                    self.model.Add(part_height == part.height).OnlyEnforceIf(self.variant_used[(piece.id,variant.id)])

                    self.model.Add(part_width == 0).OnlyEnforceIf(self.variant_used[(piece.id,variant.id)].Not())
                    self.model.Add(part_height == 0).OnlyEnforceIf(self.variant_used[(piece.id,variant.id)].Not())

                    x_interval = self.model.NewIntervalVar(x_start, part_width, x_end, 'x_interval(' + interval_name + ')')
                    y_interval = self.model.NewIntervalVar(y_start, part_height, y_end, 'y_interval(' + interval_name + ')')

                    self.dimensions[(piece.id, variant.id, part.id)] = dimension(width = part_width, height = part_height)
                    
                    self.intervals["x"].append(x_interval)
                    self.intervals["y"].append(y_interval)

        self.model.AddNoOverlap2D(self.intervals['x'], self.intervals['y'])

        for piece in pieces:
            for variant in piece.variants:
                first_part = variant.parts[0]
                for part in variant.parts[1:]:
                    self.model.Add(self.positions[(piece.id, variant.id, part.id)].x_start 
                        == self.positions[(piece.id, variant.id, first_part.id)].x_start
                        + int(part.reference_point.x - first_part.reference_point.x)).OnlyEnforceIf(self.variant_used[(piece.id,variant.id)])
                    self.model.Add(self.positions[(piece.id, variant.id, part.id)].y_start 
                        == self.positions[(piece.id, variant.id, first_part.id)].y_start
                        + int(part.reference_point.y - first_part.reference_point.y)).OnlyEnforceIf(self.variant_used[(piece.id,variant.id)])

        for piece in pieces:
            self.model.Add(sum(self.variant_used[(piece.id,variant.id)] for variant in piece.variants) == 1)

        self.model.AddMaxEquality(total_length,
                            [self.positions[(piece.id, variant.id, part.id)].y_end for piece in pieces 
                            for variant in piece.variants 
                            for part in variant.parts])

        # self.model.Add(total_length >= len(pieces))

        self.model.Minimize(total_length)
        # self.model.AddDecisionStrategy([self.positions[(piece.id, variant.id, part.id)].y_end for piece in pieces 
        #                                 for variant in piece.variants 
        #                                 for part in variant.parts], 
        #                                 cp_model.CHOOSE_FIRST,
        #                                 cp_model.SELECT_MAX_VALUE)        
    def solve(self, threads, time_limit):
        solution_callback = cp_model.ObjectiveSolutionPrinter()
        self.solver.parameters.num_search_workers = threads
        self.solver.parameters.max_time_in_seconds = time_limit

        self.solver.SolveWithSolutionCallback(self.model, solution_callback)

        print(self.solver.ResponseStats())

    def extract_solution(self, pieces):
        for piece in pieces:
            for variant in piece.variants:
                if self.solver.Value(self.variant_used[(piece.id,variant.id)]) > 0.5:
                    piece.selected_variant = variant
                    break
            for part in piece.selected_variant.parts:
                part.assigned_point = input_data.Point(self.solver.Value(self.positions[(piece.id, piece.selected_variant.id, part.id)].x_start), 
                                                        self.solver.Value(self.positions[(piece.id, piece.selected_variant.id, part.id)].y_start))

    def print_solution(self, pieces):
        for piece in pieces:
            print(piece.name)
            for variant in piece.variants:
                print(str(variant.id) + ": " + str(self.solver.Value(self.variant_used[(piece.id,variant.id)])))
                for part in variant.parts:
                    print(part.id)
                    print(self.solver.Value(self.positions[(piece.id, variant.id, part.id)].x_start), 
                            self.solver.Value(self.positions[(piece.id, variant.id, part.id)].y_start))
                    print(self.solver.Value(self.positions[(piece.id, variant.id, part.id)].x_end), 
                            self.solver.Value(self.positions[(piece.id, variant.id, part.id)].y_end))