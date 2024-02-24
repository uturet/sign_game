

class Sign:
    DIMENSIONS = 20

    def __init__(self, mask):
        self.mask = mask  # int2[DIMS][DIMS]
        self.mask_weight = self.get_sign_weight(mask)

    def is_valid_sign(self, sign):
        intersection = self.get_intersection(sign)
        inters_weight = self.get_sign_weight(intersection)
        sign_diff_weight = self.get_sign_weight(self.get_difference(sign))

        return inters_weight/self.mask_weight >= 0.5 and sign_diff_weight/self.mask_weight < 0.1

    def get_empty_mask(self):
        return [[0 for _ in range(self.DIMENSIONS)] for _ in range(self.DIMENSIONS)]

    def get_sign_weight(self, sign):
        weight = 0
        for row in range(len(sign)):
            weight += sum(sign[row])
        return weight

    def get_intersection(self, sign):
        intersection = self.get_empty_mask()
        for row in range(len(sign)):
            for col in range(len(sign[0])):
                if sign[row][col] == 1 and self.mask[row][col] == 1:
                    intersection[row][col] = 1
        return intersection

    def get_difference(self, sign):
        diff = self.get_empty_mask()
        for row in range(len(sign)):
            for col in range(len(sign[0])):
                if sign[row][col] == 1 and self.mask[row][col] == 0:
                    diff[row][col] = 1
        return diff

