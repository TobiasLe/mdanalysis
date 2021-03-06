# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDAnalysis --- https://www.mdanalysis.org
# Copyright (c) 2006-2017 The MDAnalysis Development Team and contributors
# (see the file AUTHORS for the full list of names)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# R. J. Gowers, M. Linke, J. Barnoud, T. J. E. Reddy, M. N. Melo, S. L. Seyler,
# D. L. Dotson, J. Domanski, S. Buchoux, I. M. Kenney, and O. Beckstein.
# MDAnalysis: A Python package for the rapid analysis of molecular dynamics
# simulations. In S. Benthall and S. Rostrup editors, Proceedings of the 15th
# Python in Science Conference, pages 102-109, Austin, TX, 2016. SciPy.
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#

from __future__ import absolute_import

import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal

import MDAnalysis as mda
from MDAnalysis.transformations import rotateby
from MDAnalysis.lib.transformations import rotation_matrix
from MDAnalysisTests import make_Universe

@pytest.fixture()
def rotate_universes():
    # create the Universe objects for the tests
    reference = make_Universe(trajectory=True)
    transformed = make_Universe(['masses'], trajectory=True)
    transformed.trajectory.ts.dimensions = np.array([372., 373., 374., 90, 90, 90])
    return reference, transformed

def test_rotation_matrix():
    # test if the rotation_matrix function is working properly
    # simple angle and unit vector on origin
    angle = 180
    vector = [0, 0, 1]
    pos = [0, 0, 0]
    ref_matrix = np.asarray([[-1, 0, 0],
                             [0, -1, 0],
                             [0, 0, 1]], np.float64)
    matrix = rotation_matrix(np.deg2rad(angle), vector, pos)[:3, :3]
    assert_array_almost_equal(matrix, ref_matrix, decimal=6)
    # another angle in a custom axis
    angle = 60
    vector = [1, 2, 3]
    pos = [1, 2, 3]
    ref_matrix = np.asarray([[ 0.53571429, -0.6229365 ,  0.57005291],
                             [ 0.76579365,  0.64285714, -0.01716931],
                             [-0.35576719,  0.44574074,  0.82142857]], np.float64)
    matrix = rotation_matrix(np.deg2rad(angle), vector, pos)[:3, :3]
    assert_array_almost_equal(matrix, ref_matrix, decimal=6)
    

def test_rotateby_custom_position(rotate_universes):
    # what happens when we use a custom point for the axis of rotation?
    ref_u = rotate_universes[0]
    trans_u = rotate_universes[1]
    trans = trans_u.trajectory.ts
    ref = ref_u.trajectory.ts
    vector = [1,0,0]
    pos = [0,0,0]
    angle = 90
    matrix = rotation_matrix(np.deg2rad(angle), vector, pos)[:3, :3]
    ref.positions = np.dot(ref.positions, matrix)
    transformed = rotateby(angle, vector, point=pos)(trans)
    assert_array_almost_equal(transformed.positions, ref.positions, decimal=6)
    
def test_rotateby_atomgroup_cog_nopbc(rotate_universes):
    # what happens when we rotate arround the center of geometry of a residue
    # without pbc?
    ref_u = rotate_universes[0]
    trans_u = rotate_universes[1]
    trans = trans_u.trajectory.ts
    ref = ref_u.trajectory.ts
    center_pos = [6,7,8]
    vector = [1,0,0]
    angle = 90
    matrix = rotation_matrix(np.deg2rad(angle), vector, center_pos)[:3, :3]
    ref.positions = np.dot(ref.positions, matrix)
    selection = trans_u.residues[0].atoms
    transformed = rotateby(angle, vector, ag=selection, center='geometry')(trans) 
    assert_array_almost_equal(transformed.positions, ref.positions, decimal=6)

def test_rotateby_atomgroup_com_nopbc(rotate_universes):
    # what happens when we rotate arround the center of mass of a residue
    # without pbc?
    ref_u = rotate_universes[0]
    trans_u = rotate_universes[1]
    trans = trans_u.trajectory.ts
    ref = ref_u.trajectory.ts
    vector = [1,0,0]
    angle = 90
    selection = trans_u.residues[0].atoms
    center_pos = selection.center_of_mass()
    matrix = rotation_matrix(np.deg2rad(angle), vector, center_pos)[:3, :3]
    ref.positions = np.dot(ref.positions, matrix)
    transformed = rotateby(angle, vector, ag=selection, center='mass')(trans) 
    assert_array_almost_equal(transformed.positions, ref.positions, decimal=6)
    
def test_rotateby_atomgroup_cog_pbc(rotate_universes):
    # what happens when we rotate arround the center of geometry of a residue
    # with pbc?
    ref_u = rotate_universes[0]
    trans_u = rotate_universes[1]
    trans = trans_u.trajectory.ts
    ref = ref_u.trajectory.ts
    vector = [1,0,0]
    angle = 90
    selection = trans_u.residues[0].atoms
    center_pos = selection.center_of_geometry(pbc=True)
    matrix = rotation_matrix(np.deg2rad(angle), vector, center_pos)[:3, :3]
    ref.positions = np.dot(ref.positions, matrix)
    transformed = rotateby(angle, vector, ag=selection, center='geometry', wrap=True)(trans) 
    assert_array_almost_equal(transformed.positions, ref.positions, decimal=6)

def test_rotateby_atomgroup_com_pbc(rotate_universes):
    # what happens when we rotate arround the center of mass of a residue
    # with pbc?
    ref_u = rotate_universes[0]
    trans_u = rotate_universes[1]
    trans = trans_u.trajectory.ts
    ref = ref_u.trajectory.ts
    vector = [1,0,0]
    angle = 90
    selection = trans_u.residues[0].atoms
    center_pos = selection.center_of_mass(pbc=True)
    matrix = rotation_matrix(np.deg2rad(angle), vector, center_pos)[:3, :3]
    ref.positions = np.dot(ref.positions, matrix)
    transformed = rotateby(angle, vector, ag=selection, center='mass', wrap=True)(trans) 
    assert_array_almost_equal(transformed.positions, ref.positions, decimal=6)
    
def test_rotateby_bad_ag(rotate_universes):
    # this universe as a box size zero
    ts = rotate_universes[0].trajectory.ts
    ag = rotate_universes[0].residues[0].atoms
    # what happens if something other than an AtomGroup is given?
    angle = 90
    vector = [0, 0, 1]
    bad_ag = 1
    with pytest.raises(ValueError): 
        rotateby(angle, vector, ag = bad_ag)(ts)

def test_rotateby_bad_position(rotate_universes):
    # this universe as a box size zero
    ts = rotate_universes[0].trajectory.ts
    # what if the box is in the wrong format?
    angle = 90
    vector = [0, 0, 1]
    bad_position = [1]
    with pytest.raises(ValueError): 
        rotateby(angle, vector, point=bad_position)(ts)
    
def test_rotateby_bad_pbc(rotate_universes):    
    # this universe as a box size zero
    ts = rotate_universes[0].trajectory.ts
    ag = rotate_universes[0].residues[0].atoms
    # is pbc passed to the center methods?
    # if yes it should raise an exception for boxes that are zero in size
    angle = 90
    vector = [0, 0, 1]
    with pytest.raises(ValueError): 
        rotateby(angle, vector, ag = ag, wrap=True)(ts)

def test_rotateby_bad_center(rotate_universes):
    # this universe as a box size zero
    ts = rotate_universes[0].trajectory.ts
    ag = rotate_universes[0].residues[0].atoms
    # what if a wrong center type name is passed?
    angle = 90
    vector = [0, 0, 1]
    bad_center = " "
    with pytest.raises(ValueError): 
        rotateby(angle, vector, ag = ag, center=bad_center)(ts)
    
def test_rotateby_no_masses(rotate_universes):   
    # this universe as a box size zero
    ts = rotate_universes[0].trajectory.ts
    ag = rotate_universes[0].residues[0].atoms
    # if the universe has no masses and `mass` is passed as the center arg
    angle = 90
    vector = [0, 0, 1]
    bad_center = "mass"
    with pytest.raises(AttributeError): 
        rotateby(angle, vector, ag = ag, center=bad_center)(ts)

def test_rotateby_no_args(rotate_universes):
    # this universe as a box size zero
    ts = rotate_universes[0].trajectory.ts
    angle = 90
    vector = [0, 0, 1]
    # if no point or AtomGroup are passed to the function
    # it should raise a ValueError
    with pytest.raises(ValueError): 
        rotateby(angle, vector)(ts)