import gurobipy as gp
from gurobipy import GRB
import math
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import input_data

class Model:
    def __init__(self):
        self.zvars = []
        self.xvars = []
        self.yvars = []
        self.lvars = []
        self.bvars = []
        self.model = gp.Model("StripPacking")

    def build(self, pieces, board_width, board_height):
        for piece in pieces:
            self.zvars.append([])
            for variant in piece.variants:
                self.zvars[piece.id].append(self.model.addVar(vtype = GRB.BINARY,
                                            name = "z[%d,%d]" % (piece.name, variant.id)))
                
        for piece in pieces:
            self.xvars.append([])
            parts = range(piece.number_parts)
            for p in parts:
                self.xvars[piece.id].append(self.model.addVar(vtype = GRB.INTEGER,
                                            ub = board_width - 1,
                                            name = "x[%d,%d]" % (piece.name, p)))

        for piece in pieces:
            self.yvars.append([])
            parts = range(piece.number_parts)
            for p in parts:
                self.yvars[piece.id].append(self.model.addVar(vtype = GRB.INTEGER,
                                            ub = board_height - 1,
                                            name = "y[%d,%d]" % (piece.name, p)))
                
        for first_piece in pieces:
            self.lvars.append([])
            first_parts = range(first_piece.number_parts)
            for p in first_parts:
                self.lvars[first_piece.id].append([])
                for second_piece in pieces:
                    self.lvars[first_piece.id][p].append([])
                    second_parts = range(second_piece.number_parts)
                    for q in second_parts:
                        self.lvars[first_piece.id][p][second_piece.id].append(self.model.addVar(vtype = GRB.BINARY,
                                                        name = "l[%d,%d,%d,%d]" % (first_piece.name, p, second_piece.name, q)))

        for first_piece in pieces:
            self.bvars.append([])
            first_parts = range(first_piece.number_parts)
            for p in first_parts:
                self.bvars[first_piece.id].append([])
                for second_piece in pieces:
                    self.bvars[first_piece.id][p].append([])
                    second_parts = range(second_piece.number_parts)
                    for q in second_parts:
                        self.bvars[first_piece.id][p][second_piece.id].append(self.model.addVar(vtype = GRB.BINARY,
                                                        name = "b[%d,%d,%d,%d]" % (first_piece.name, p, second_piece.name, q)))
                            
        total_length = self.model.addVar(vtype = GRB.INTEGER,
                                    name = "total_length")

        #### CONSTRAINTS ####

        for first_piece in pieces[:-1]:
            i = first_piece.id
            for second_piece in pieces[(i+1):]:
                j = second_piece.id
                parts_i = range(first_piece.number_parts)
                parts_j = range(second_piece.number_parts)
                for p in parts_i:                    
                    for q in parts_j:
                        self.model.addConstr(self.lvars[i][p][j][q] + self.lvars[j][q][i][p] + self.bvars[i][p][j][q] + self.bvars[j][q][i][p] >= 1,
                                            "non_overlap")

        for first_piece in pieces:
            i = first_piece.id
            parts_i = range(first_piece.number_parts)
            for p in parts_i:
                for second_piece in pieces:
                    j = second_piece.id
                    if i != j:
                        parts_j = range(second_piece.number_parts)
                        for q in parts_j:
                            self.model.addConstr(self.xvars[i][p] + sum(self.zvars[i][variant.id] * variant.parts[p].width for variant in first_piece.variants)
                                            <= self.xvars[j][q] + (board_width - 0) * (1 - self.lvars[i][p][j][q]),
                                            "left[%d,%d,%d,%d]" % (i,p,j,q))

        for first_piece in pieces:
            i = first_piece.id
            parts_i = range(first_piece.number_parts)
            for p in parts_i:
                for second_piece in pieces:
                    j = second_piece.id
                    if i != j:
                        parts_j = range(second_piece.number_parts)
                        for q in parts_j:
                            self.model.addConstr(self.yvars[i][p] + sum(self.zvars[i][variant.id] * variant.parts[p].height for variant in first_piece.variants)
                                            <= self.yvars[j][q] + (board_height - 0) * (1 - self.bvars[i][p][j][q]),
                                            "below[%d,%d,%d,%d]" % (i,p,j,q))

        for piece in pieces:
            i = piece.id
            parts = range(piece.number_parts)
            for p in parts:
                self.model.addConstr(self.xvars[i][p] + sum(self.zvars[i][variant.id] * variant.parts[p].width for variant in piece.variants) 
                                <= board_width,
                                "board_limit_width[%d,%d]" % (i,p))

        for piece in pieces:
            i = piece.id
            parts = range(piece.number_parts)
            for p in parts[1:]:
                self.model.addConstr(self.xvars[i][0] + sum(self.zvars[i][variant.id] * (variant.parts[p].reference_point.x - variant.parts[0].reference_point.x)
                                for variant in piece.variants) 
                                == self.xvars[i][p],
                                "delta_width[%d,%d]" % (i,p))

        for piece in pieces:
            i = piece.id
            parts = range(piece.number_parts)
            for p in parts[1:]:
                self.model.addConstr(self.yvars[i][0] + sum(self.zvars[i][variant.id] * (variant.parts[p].reference_point.y - variant.parts[0].reference_point.y)
                                for variant in piece.variants) 
                                == self.yvars[i][p],
                                "delta_height[%d,%d]" % (i,p))

        for piece in pieces:
            i = piece.id
            self.model.addConstr(sum(self.zvars[i][variant.id] for variant in piece.variants) == 1.0,
                            "one_variant[%d]" % (i))
            
        #### OBJECTIVE FUNCTION ####
        for piece in pieces:
            i = piece.id
            parts = range(piece.number_parts)
            for p in parts:
                self.model.addConstr(self.yvars[i][p] + sum(self.zvars[i][variant.id] * variant.parts[p].height for variant in piece.variants) <= total_length,
                                "board_limit_width[%d,%d]" % (i,p))

        self.model.setObjective(total_length, GRB.MINIMIZE)

        for piece in pieces:
            for variant in piece.variants:
                for part in variant.parts:
                    # model.addConstr(xvars[piece.id][part.id] <= zvars[piece.id][variant.id] * (board_width - part.width) + (1-zvars[piece.id][variant.id]) * part.reference_point.x)
                    self.model.addConstr(self.xvars[piece.id][part.id] >= self.zvars[piece.id][variant.id] * part.reference_point.x)
                    # model.addConstr(yvars[piece.id][part.id] >= zvars[piece.id][variant.id] * part.reference_point.y)


        for first_piece in pieces[:-1]:
            i = first_piece.id
            for second_piece in pieces[(i+1):]:
                j = second_piece.id
                P = range(first_piece.number_parts)
                Q = range(second_piece.number_parts)
                no_fit_in_all_variants = True
                for variant_first_piece in first_piece.variants:           
                    for variant_second_piece in second_piece.variants:
                        no_fit_variants = False
                        for p in P:                    
                            for q in Q:
                                if variant_first_piece.parts[p].reference_point.x + variant_first_piece.parts[p].width + variant_second_piece.parts[q].reference_point.x + variant_second_piece.parts[q].width > board_width:
                                    self.model.addQConstr(self.bvars[i][p][j][q] + self.bvars[j][q][i][p] 
                                                    >= self.zvars[i][variant_first_piece.id] * self.zvars[j][variant_second_piece.id],
                                                    "no_fit")
                                    no_fit_variants = True
                                    break
                            if no_fit_variants:
                                break
                        if not no_fit_variants:
                            break
                    if no_fit_variants:
                        continue
                    else:
                        no_fit_in_all_variants = False
                        break
                if no_fit_in_all_variants:
                    self.model.addConstr(sum(self.bvars[i][p][j][q] for p in P for q in Q) + sum(self.bvars[j][q][i][p] for p in P for q in Q)>= 1,
                        "no_fit")

        self.model.update()
    def solve(self, threads, time_limit):
        self.model.write("Model.LP")
        self.model.setParam("Threads", threads)
        self.model.setParam("TimeLimit", time_limit)            

        self.model.optimize()
        self.model.write("Solution.SOL")
            
    def extract_solution(self, pieces):
        for piece in pieces:
            for variant in piece.variants:
                if self.zvars[piece.id][variant.id].X > 0.5:                        
                    piece.selected_variant = variant

        for piece in pieces:
            parts = range(piece.number_parts)
            for p in parts:
                piece.selected_variant.parts[p].assigned_point = input_data.Point(self.xvars[piece.id][p].X, self.yvars[piece.id][p].X)
