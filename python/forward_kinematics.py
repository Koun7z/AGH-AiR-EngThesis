from typing import List
import numpy as np
import scipy as sp

from scipy.spatial.transform import Rotation

class MDH_Param:
    def __init__(self, theta, alpha, d, a):
        self.theta: np.float64 = theta
        self.alpha: np.float64 = alpha
        self.d: np.float64 = d
        self.a: np.float64 = a

class MDH_Matrix:
    def __init__(self, joint_rotation: np.float64,  dh_param: MDH_Param):
        
        theta = dh_param.theta + joint_rotation
        alpha = dh_param.alpha
        d = dh_param.d
        a = dh_param.a

        c_theta = np.cos(theta)
        s_theta = np.sin(theta)

        c_alpha = np.cos(alpha)
        s_alpha = np.sin(alpha)

        self._matrix = np.array([
        [          c_theta,          -s_theta,        0,            a],
        [s_theta * c_alpha, c_theta * c_alpha, -s_alpha, -d * s_alpha],
        [s_theta * s_alpha, c_theta * s_alpha,  c_alpha,  d * c_alpha],
        [                0,                 0,        0,            1]
        ], dtype=np.float64)


    def get_translation(self) -> np.ndarray:
        return self._matrix[0:3, 3].copy()

    def get_rotation_matrix(self) -> np.ndarray:
        return self._matrix[0:3, 0:3].copy()

    def get_rotation(self) -> Rotation:
        return Rotation.from_matrix(self._matrix[0:3, 0:3])

    @staticmethod
    def eye() -> MDH_Matrix:    
        result = MDH_Matrix.__new__(MDH_Matrix)
        result._matrix = np.eye(4)
        return result

    def __matmul__(self, other: 'MDH_Matrix') -> 'MDH_Matrix':
        result = MDH_Matrix.eye()
        result._matrix = self._matrix @ other._matrix
        return result

DH_Table: List[MDH_Param] = [
    #                theta,      alpha,      d,     a
    MDH_Param(   np.pi / 2,          0,    0.2,     0),
    MDH_Param(  -np.pi / 2,  np.pi / 2,      0,     0),
    MDH_Param(           0,          0,      0,  -0.3),
    MDH_Param(   np.pi / 2,          0,   0.25, -0.32),
    MDH_Param(           0, -np.pi / 2,      0,     0),
    MDH_Param(   np.pi / 2,  np.pi / 2,      0,     0)
]

def forward_kinematics(joint_angles: List[np.float64], dh_table: List[MDH_Param] = DH_Table) -> MDH_Matrix:
    assert len(joint_angles) <= len(dh_table), "Joint angles length must match DH table length"

    result = MDH_Matrix.eye()
    for i, angle in enumerate(joint_angles):
        result = result @ MDH_Matrix(angle, dh_table[i])

    return result


if __name__ == "__main__":
    joint_angles: np.ndarray[np.float64] = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float64)
    result = forward_kinematics(joint_angles)
    result._matrix = np.round(result._matrix, decimals=6)  # Round the matrix for better readability
    print("Transformation Matrix:\n", result._matrix)
    print("Translation:", result.get_translation())
    print("Rotation Matrix:\n", result.get_rotation_matrix())
    print("Rotation (as quaternion):", result.get_rotation().as_quat())