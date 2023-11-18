import numpy as np
class AHP:
    """
    """

    def __init__(self, array):
        self.array = array
        self.n = array.shape[0]
        self.RI_list = [0, 0, 0.52, 0.89, 1.12, 1.26, 1.36, 1.41, 1.46, 1.49, 1.52, 1.54, 1.56, 1.58,
                        1.59]
        self.eig_val, self.eig_vector = np.linalg.eig(self.array)
        self.max_eig_val = np.max(self.eig_val)
        self.max_eig_vector = self.eig_vector[:, np.argmax(self.eig_val)].real
        self.CI_val = (self.max_eig_val - self.n) / (self.n - 1)
        self.CR_val = self.CI_val / (self.RI_list[self.n - 1])

    """
    consistency judgment
    """

    def test_consist(self):
        print(str(self.CI_val))
        print(str(self.CR_val))
        if self.n == 2:
            print("invalid")
        else:
            if self.CR_val < 0.1:
                return True
            else:
                return False

    """
    Arithmetic average method to find weight
    """

    def cal_weight_by_arithmetic_method(self):
        col_sum = np.sum(self.array, axis=0)
        array_normed = self.array / col_sum
        array_weight = np.sum(array_normed, axis=1) / self.n
        return array_weight

    """
    Calculate weight using geometric mean method
    """

    def cal_weight__by_geometric_method(self):
        col_product = np.product(self.array, axis=0)
        array_power = np.power(col_product, 1 / self.n)
        array_weight = array_power / np.sum(array_power)
        return array_weight

    """
    Eigenvalue method to find weight
    """

    def cal_weight__by_eigenvalue_method(self):
        array_weight = self.max_eig_vector / np.sum(self.max_eig_vector)
        return array_weight


if __name__ == "__main__":
    b = np.array([[1,   9, 7,   7,   6],
                  [1/9, 1, 1/5, 1/5, 1/6],
                  [1/7, 5, 1,   1,   1/2],
                  [1/7, 5, 1,   1,   1/2],
                  [1/6, 6, 2,   2,   1]])

    # b = np.array([[1, 7, 8, 5],
    #               [1/7, 1, 3, 1/3],
    #               [1/8, 1/3, 1, 1/5],
    #               [1/5, 3, 5, 1]])

    # weight1 = AHP(b).cal_weight_by_arithmetic_method()
    # weight2 = AHP(b).cal_weight__by_geometric_method()
    weight3 = AHP(b).cal_weight__by_eigenvalue_method()

    AHP(b).test_consist()
