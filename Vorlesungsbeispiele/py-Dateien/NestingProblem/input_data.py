import math

class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def rotate(self, angle = 0):
        new_x = int(round(self.x * math.cos(angle * math.pi / 180) + self.y * math.sin(angle * math.pi / 180), 0))
        new_y = int(round(-1 * self.x * math.sin(angle * math.pi / 180) + self.y * math.cos(angle * math.pi / 180),0))

        return Point(new_x, new_y)

    def move(self, delta_width = 0, delta_height = 0, angle = 0):
        if angle == 90:
            new_x = self.x
            new_y = self.y - delta_width
        elif angle == 180:
            new_x = self.x - delta_width
            new_y = self.y - delta_height
        elif angle == 270:
            new_x = self.x - delta_height
            new_y = self.y

        return Point(new_x, new_y)

class Part:
    def __init__(self, number, ref_point, width, height):
        self.id = number
        self.reference_point = ref_point
        self.width = width
        self.height = height
    assigned_point = Point()
    global_id = 0

    def rotate_dimensions(self, angle = 0):
        if angle == 90:
            new_width = self.height
            new_height = self.width
        elif angle == 180:
            new_width = self.width
            new_height = self.height
        elif angle == 270:
            new_width = self.height
            new_height = self.width
        return([new_width, new_height])


class Variant:
    def __init__(self, number = -1, parts = []):
        self.id = number
        self.parts = parts
    total_width = 0
    total_height = 0
    def set_total_width(self):
        self.total_width = int(max([(part.reference_point.x + part.width) for part in self.parts]))
    def set_total_height(self):
        self.total_height = int(max([(part.reference_point.y + part.height) for part in self.parts]))
    global_id = 0

    def mirror_parts(self):
        mirrored_parts = []
        for part in self.parts:
            new_x = -part.reference_point.x - part.width
            new_y = part.reference_point.y
            mirrored_parts.append(Part(part.id, Point(new_x, new_y), part.width, part.height))

        return mirrored_parts
    
    def rotate_parts(self, angle = 0):
        rotated_parts = []
        for part in self.parts:
            new_ref_point = part.reference_point.rotate(angle)
            new_ref_point = new_ref_point.move(part.width, part.height, angle)
            new_dimensions = part.rotate_dimensions(angle)
            rotated_parts.append(Part(part.id, new_ref_point, new_dimensions[0], new_dimensions[1]))
        return rotated_parts

class Piece:
    def __init__(self, number, name, number_parts, variants, rotation, reflection, color):
        self.id = number
        self.name = name
        self.variants = variants
        self.number_parts = number_parts
        self.number_variants = len(variants)
        self.rotation = rotation
        self.reflection = reflection
        self.color = color

    selected_variant = Variant()
    
    def normalize(self):
        for variant in self.variants:
            relocation_x = 0
            relocation_y = 0
            for part in variant.parts:
                if part.reference_point.x < relocation_x:
                    relocation_x = part.reference_point.x
                if part.reference_point.y < relocation_y:
                    relocation_y = part.reference_point.y
            for part in variant.parts:
                part.reference_point.x += -1 * relocation_x
                part.reference_point.y += -1 * relocation_y
    
    def create_new_variants(self, rotation_allowed = True, reflection_allowed = True, angles = [90, 180, 270]):
        if rotation_allowed and self.rotation:
            for angle in angles:
                rotated_parts = self.variants[0].rotate_parts(angle)
                self.variants.append(Variant(self.variants[-1].id + 1, rotated_parts))

        if reflection_allowed and self.reflection:
            mirrored_parts = self.variants[0].mirror_parts()
            mirrored_variant = Variant(self.variants[-1].id + 1, mirrored_parts)
            self.variants.append(mirrored_variant)

            if rotation_allowed and self.rotation:
                for angle in angles:
                    rotated_parts = mirrored_variant.rotate_parts(angle)
                    self.variants.append(Variant(self.variants[-1].id + 1, rotated_parts))

        self.normalize()

        for variant in self.variants:
            variant.set_total_width()
            variant.set_total_height()

        self.number_variants = len(self.variants)
        
one = Piece(0, 1, 1,
                    [Variant(0, [Part(0, Point(0,0), 1, 5)])
                    ], False, False, 'royalblue')

two = Piece(1, 2, 2,
                    [Variant(0, [Part(0, Point(0,0), 1, 4), Part(1, Point(1,0), 1, 1)])
                    ], True, True, 'saddlebrown')

three = Piece(2, 3, 2,
                    [Variant(0, [Part(0, Point(1,0), 1, 4), Part(1, Point(0,2), 1, 1)])
                    ], True, True, 'goldenrod')

four = Piece(3, 4, 2,
                    [Variant(0, [Part(0, Point(0,0), 1, 2), Part(1, Point(1,1), 1, 3)])
                    ], True, True, 'gold' )

five = Piece(4, 5, 2,
                    [Variant(0, [Part(0, Point(0,0), 3, 1), Part(1, Point(2,1), 1, 2)])
                    ], True, False, 'forestgreen')

six = Piece(5, 6, 2,
                    [Variant(0, [Part(0, Point(0,0), 1, 3), Part(1, Point(1,1), 1, 2)])
                    ], True, True,  'lightskyblue')

seven = Piece(6, 7, 3,
                    [Variant(0, [Part(0, Point(0,0), 3, 1), Part(1, Point(0,1), 1, 1), Part(2, Point(2,1), 1,1)])
                    ], True, False, 'orchid')

eight = Piece(7, 8, 3,
                    [Variant(0, [Part(0, Point(1,0), 1, 3), Part(1, Point(0,2), 1, 1), Part(2, Point(2,0), 1, 1)])
                    ], True, True, 'grey')

nine = Piece(8, 9, 3,
                    [Variant(0, [Part(0, Point(1,0), 1, 3), Part(1, Point(0,1), 1, 1), Part(2, Point(2,2), 1, 1)])
                    ], True, True, 'purple')

ten = Piece(9, 10, 2,
                     [Variant(0, [Part(0, Point(0,0), 3, 1), Part(1, Point(1,1), 1, 2)])
                     ], True, False, 'greenyellow')

eleven = Piece(10, 11, 3,
                    [Variant(0, [Part(0, Point(0,0), 1, 2), Part(1, Point(1,1), 1, 2), Part(2, Point(2,2), 1, 1)])
                    ], True, False, 'darkcyan')


twelve = Piece(11, 12, 3,
                    [Variant(0, [Part(0, Point(0,1), 3, 1), Part(1, Point(1,0), 1, 1), Part(2, Point(1,2), 1, 1)])
                    ], False, False, 'tomato')

thirteen = Piece(12, 13, 4,
                    [Variant(0, [Part(0, Point(0,0), 5, 1), Part(1, Point(0,1), 1, 5), Part(2, Point(1,5), 4, 1), Part(3, Point(4,1), 1, 5)])
                    ], False, False, 'black'
                    )

all_pieces = [one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve, thirteen]