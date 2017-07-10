#!/usr/bin/env python

# Copyright (C) 2017 Electric Movement Inc.
#
# This file is part of Robotic Arm: Pick and Place project for Udacity
# Robotics nano-degree program
#
# All Rights Reserved.

# Author: Harsh Pandya

# import modules
import rospy
import tf
from kuka_arm.srv import *
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Pose
from mpmath import *
from sympy import *

# Define functions for Rotation Matrices about x, y, and z given specific angle
# From lesson 2 part 11
def rot_x(q):
    R_x = Matrix([[1,      0,       0], 
                  [0, cos(q), -sin(q)],
                  [0, sin(q),  cos(q)]])
    
    return R_x
    
def rot_y(q):              
    R_y = Matrix([[ cos(q), 0, sin(q)],
                  [      0, 1,      0],
                  [-sin(q), 0, cos(q)]])
    
    return R_y

def rot_z(q):    
    R_z = Matrix([[cos(q), -sin(q), 0], 
                  [sin(q),  cos(q), 0],
                  [     0,       0, 1]])
    
    return R_z

def handle_calculate_IK(req):
    rospy.loginfo("Received %s eef-poses from the plan" % len(req.poses))
    if len(req.poses) < 1:
        print "No valid poses received"
        return -1
    else:
        # Initialize service response
        joint_trajectory_list = []
        for x in xrange(0, len(req.poses)):
            # IK code starts here
            joint_trajectory_point = JointTrajectoryPoint()

            # Define DH param symbols
            q1, q2, q3, q4, q5, q6, q7 = symbols('q1:8')
            d1, d2, d3, d4, d5, d6, d7 = symbols('d1:8')
            alpha0, alpha1, alpha2, alpha3, alpha4, alpha5, alpha6 = symbols('alpha0:7')
            a0, a1, a2, a3, a4, a5, a6 = symbols('a0:7')
            
            # Joint angle symbols
                # Defined above with DH param symbols
      
            # Modified DH params
            s = {alpha0:     0, a0:      0, d1:  0.75,
                 alpha1: -pi/2, a1:   0.35, d2:     0, q2: q2-pi/2,
                 alpha2:     0, a2:   1.25, d3:     0, 
                 alpha3: -pi/2, a3: -0.054, d4:   1.5,
                 alpha4:  pi/2, a4:      0, d5:     0,
                 alpha5: -pi/2, a5:      0, d6:     0,
                 alpha6:     0, a6:      0, d7: 0.303, q7:       0}
            
            # Define Modified DH Transformation matrix
                # Total transform defined after individual transforms

            # Create individual transformation matrices
            T0_1 = Matrix([[            cos(q1),            -sin(q1),            0,              a0],
                           [sin(q1)*cos(alpha0), cos(q1)*cos(alpha0), -sin(alpha0), -sin(alpha0)*d1],
                           [sin(q1)*sin(alpha0), cos(q1)*sin(alpha0),  cos(alpha0),  cos(alpha0)*d1],
                           [                  0,                   0,            0,               1]])
            T0_1 = T0_1.subs(s)

            T1_2 = Matrix([[            cos(q2),            -sin(q2),            0,              a1],
                           [sin(q2)*cos(alpha1), cos(q2)*cos(alpha1), -sin(alpha1), -sin(alpha1)*d2],
                           [sin(q2)*sin(alpha1), cos(q2)*sin(alpha1),  cos(alpha1),  cos(alpha1)*d2],
                           [                  0,                   0,            0,               1]])
            T1_2 = T1_2.subs(s)

            T2_3 = Matrix([[            cos(q3),            -sin(q3),            0,              a2],
                           [sin(q3)*cos(alpha2), cos(q3)*cos(alpha2), -sin(alpha2), -sin(alpha2)*d3],
                           [sin(q3)*sin(alpha2), cos(q3)*sin(alpha2),  cos(alpha2),  cos(alpha2)*d3],
                           [                  0,                   0,            0,               1]])
            T2_3 = T2_3.subs(s)

            T3_4 = Matrix([[            cos(q4),            -sin(q4),            0,              a3],
                           [sin(q4)*cos(alpha3), cos(q4)*cos(alpha3), -sin(alpha3), -sin(alpha3)*d4],
                           [sin(q4)*sin(alpha3), cos(q4)*sin(alpha3),  cos(alpha3),  cos(alpha3)*d4],
                           [                  0,                   0,            0,               1]])
            T3_4 = T3_4.subs(s)

            T4_5 = Matrix([[            cos(q5),            -sin(q5),            0,              a4],
                           [sin(q5)*cos(alpha4), cos(q5)*cos(alpha4), -sin(alpha4), -sin(alpha4)*d5],
                           [sin(q5)*sin(alpha4), cos(q5)*sin(alpha4),  cos(alpha4),  cos(alpha4)*d5],
                           [                  0,                   0,            0,               1]])
            T4_5 = T4_5.subs(s)
            

            T5_6 = Matrix([[            cos(q6),            -sin(q6),            0,              a5],
                           [sin(q6)*cos(alpha5), cos(q6)*cos(alpha5), -sin(alpha5), -sin(alpha5)*d6],
                           [sin(q6)*sin(alpha5), cos(q6)*sin(alpha5),  cos(alpha5),  cos(alpha5)*d6],
                           [                  0,                   0,            0,               1]])
            T5_6 = T5_6.subs(s)

            T6_G = Matrix([[            cos(q7),            -sin(q7),            0,              a6],
                           [sin(q7)*cos(alpha6), cos(q7)*cos(alpha6), -sin(alpha6), -sin(alpha6)*d7],
                           [sin(q7)*sin(alpha6), cos(q7)*sin(alpha6),  cos(alpha6),  cos(alpha6)*d7],
                           [                  0,                   0,            0,               1]])
            T6_G = T6_G.subs(s)

            T0_2 = simplify(T0_1 * T1_2)
            T0_3 = simplify(T0_2 * T2_3)
            T0_4 = simplify(T0_3 * T3_4)
            T0_5 = simplify(T0_4 * T4_5)
            T0_6 = simplify(T0_5 * T5_6)
            T0_G = simplify(T0_6 * T6_G)

            # Correct orientation of gripper link in URDF vs. DH convention
            # 180 degree rotation about the z-axis
            R_z = Matrix([[cos(pi), -sin(pi), 0, 0],
                          [sin(pi),  cos(pi), 0, 0],
                          [      0,        0, 1, 0],
                          [      0,        0, 0, 1]])
            # 90 degree rotation about the y-axis
            R_y = Matrix([[ cos(-pi/2), 0, sin(-pi/2), 0],
                          [          0, 1,          0, 0],
                          [-sin(-pi/2), 0, cos(-pi/2), 0],
                          [          0, 0,          0, 1]])
            R_corr = simplify(R_z * R_y)
	
            # Total transform with gripper orientation corrected
            T_total = simplify(T0_G * R_corr) 

            # Extract end-effector position and orientation from request
	    # px,py,pz = end-effector position
	    # roll, pitch, yaw = end-effector orientation
            px = req.poses[x].position.x
            py = req.poses[x].position.y
            pz = req.poses[x].position.z

            (roll, pitch, yaw) = tf.transformations.euler_from_quaternion(
                [req.poses[x].orientation.x, req.poses[x].orientation.y,
                    req.poses[x].orientation.z, req.poses[x].orientation.w])
     
            # Calculate joint angles using Geometric IK method

            # 0. Useful Constants
            ee_length = d7
            ee_length = ee_length.subs(s)

            # 1. Find R3_6 from orientation data
            R_total = Matrix([[T_total[0,0], T_total[0,1], T_total[0,2]],
                              [T_total[1,0], T_total[1,1], T_total[1,2]],
                              [T_total[2,0], T_total[2,1], T_total[2,2]]])

            R_rpy = R_total
        
            R3_6 = simplify(R0_3.T * R_rpy)

            # 2. Find alpha, beta, gamma euler angles as done in lesson 2 part 8.
            # alpha
            theta4 = atan2(R3_6[1,0], R3_6[0,0])
            # beta
            theta5 = atan2(-R3_6[2,0], sqrt(R3_6[0,0] * R3_6[0,0] + R3_6[1,0] * R3_6[1,0]))
            # gamma
            theta6 = atan2(R3_6[2,1], R3_6[2,2])

            # 3. Find wrist center position using the end effector position and orientation
                # d6 = 0
                # wx = px - (d6 + l) * nx
                # wy = py - (d6 + l) * ny
                # wz = pz - (d6 + l) * nz
            wx = px - ee_length * [[1], [0], [0]]
            wy = py - ee_length * [[0], [1], [0]]
            wz = pz - ee_length * [[0], [0], [1]]

            # 4. theta1 calc
            theta1 = atan2(wy, wx)

            # 5. theta2 calc
            # Replace symbols with actual values
            # theta2 = pi/2 - (acos((b**2 - a**2 - xc**2 - yc**2)/(-2*a*sqrt(xc**2 + yc**2))))
           
            # 6. theta3 calc
            # Replace symbols with actual values
            # theta3_a = pi/2 - atan2(sqrt(1 - ((xc**2 + yc**2 - a**2 - b**2) / (-2*a*b))),
            #                         (xc**2 + yc**2 - a**2 - b**2) / (-2*a*b))

            # theta3_b = pi/2 - atan2(-sqrt(1 - ((xc**2 + yc**2 - a**2 - b**2) / (-2*a*b))),
            #                         (xc**2 + yc**2 - a**2 - b**2) / (-2*a*b))
		


            # Populate response for the IK request
            # In the next line replace theta1,theta2...,theta6 by your joint angle variables
	    joint_trajectory_point.positions = [theta1, theta2, theta3, theta4, theta5, theta6]
	    joint_trajectory_list.append(joint_trajectory_point)

        rospy.loginfo("length of Joint Trajectory List: %s" % len(joint_trajectory_list))
        return CalculateIKResponse(joint_trajectory_list)


def IK_server():
    # initialize node and declare calculate_ik service
    rospy.init_node('IK_server')
    s = rospy.Service('calculate_ik', CalculateIK, handle_calculate_IK)
    print "Ready to receive an IK request"
    rospy.spin()

if __name__ == "__main__":
    IK_server()
