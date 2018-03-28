#!/usr/bin/env python3
# inki = INverse KInematics

# Limb lengths (all in mm, from https://hexyrobot.wordpress.com/2015/11/20/hexapod-leg-kinematics/)
HIP_LENGTH = 26
THIGH_LENGTH = 49
KNEE_LENGTH = 52
LEG_LENGTHS = (HIP_LENGTH, THIGH_LENGTH, KNEE_LENGTH)

def foot_location(joint_positions, lengths=LEG_LENGTHS, origin=(0,0,0), leg_angle=0):
    '''
    Returns the (x,y,z) coordinates of the foot, in mm, given the joint positions.
    origin should be the coordinates of the hip joint relative to whatever you consider the center of the body.
    leg_angle should be the angle from the center to the hip joint.
    origin and leg_andle are used in conjunction with the leg position to determing the complete relative position of the foot.
    '''
    print("foot_location not yet implemented!  Returning (0,0,0) as a placeholder.")
    return (0,0,0)

def joint_positions(foot_location, lengths=LEG_LENGTHS, origin=(0,0,0), leg_angle=0):
    '''
    Returns the (a,b,c) angles that the servos in the leg need to have in order to put the foot in the desired location.
    If the point is impossible, this will get it something vaguely near the closest point it can manage.
    If origin and leg angle are provided, they'll be used to remove the location of the hip joint
    from foot_location prior to calculating the joint positions.
    '''
    print("joint_positions not yet implemented!  Returning (0,0,0) as a placeholder.")
    return (0,0,0)
