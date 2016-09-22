import bpy, bmesh
from mathutils import Vector
import math

import collections

import numpy as np

import functools

import itertools

import os

import sys

# To add objects to MCell
from cellblender.cellblender_utils import preserve_selection_use_operator

# Function to project point onto line
'''
def project_pt_line(v, w, p):
    v_to_p = p-v
    v_to_w = w-v
    
    vtw2 = v_to_w.length
    vtp2 = v_to_p.length
    
    v_to_p.normalize()
    v_to_w.normalize()
    
    vtp_dot_vtw = v_to_p.dot(v_to_w)
    
    t2 = vtp_dot_vtw * vtp2 / vtw2;
    
    v_to_w = w-v
    
    return v + (v_to_w * t2)
'''

# Deep copy a list
def unshared_copy(inList):
    if isinstance(inList, list):
        return list( map(unshared_copy, inList) )
    return inList

# Read in the swc file to know what's connected
def get_connections(fname):
    
    # Store the swc data
    swc_data = []
    
    # Read the file
    f = open(fname,'r')
    for i_line,line in enumerate(f):
        line_s = line.split();
        if len(line_s) > 0 and line_s[0] != "#":
            line_data = []
            line_data.append(int(float(line_s[0])))
            line_data.append(int(float(line_s[1])))
            line_data.append(float(line_s[2]))
            line_data.append(float(line_s[3]))
            line_data.append(float(line_s[4]))
            line_data.append(float(line_s[5]))
            line_data.append(int(float(line_s[6])))
            swc_data.append(line_data)

    # Vertex coordinates
    vert_list = [Vector(item[2:5]) for item in swc_data]

    # Find connections
    pt_connect = []
    for i in range(0,len(swc_data)):
        pt_connect.append([])

    for i,data in enumerate(swc_data):
        if i > 0: # The first is the -1 index
            pt_connect[data[6]-1].append(i+1)

    pt_connect_dup = unshared_copy(pt_connect) # copy

    for i_list, sub_list in enumerate(pt_connect_dup):
        for idx in sub_list:
            pt_connect[idx-1].append(i_list+1)

    return pt_connect, vert_list

# Function to construct a neighbour list from a list of face vertices
'''
def construct_neighbor_list(face_list):
    neigh_list = []
    for f in face_list:
        neigh_list.append([])

    # Go through each face
    for i_f, f in enumerate(face_list):
        
        # Go through every edge pair of vertices
        for i in range(0,3):
            # If we already have three neighbors, stop
            if len(neigh_list[i_f]) == 3:
                break
            
            # Edge vertices
            ev1 = f[i]
            ev2 = f[(i+1)%3]
            # Search tediously for this face's neighbor
            for i_fo, fo in enumerate(face_list[i_f+1:]): # and don't double count
                if ev1 in fo and ev2 in fo:
                    # Found the neighbor!
                    neigh_list[i_f].append(i_fo)
                    neigh_list[i_fo].append(i_f)
                    break

    return neigh_list
'''

# Construct planes for vertices
def construct_dividing_plane_normals(pt_connect, vert_co_list):

    # Dictionary of vertex to segment to normals
    # Each index is a vertex in the SWC
    # Each entry is another dictionary: one for each segment that connects to this vertex
    # Each entry in this dictionary is a list of all the plane normals to consider
    normal_dict = {}
    
    # Go through all vertices
    for i_pt, conn_pts in enumerate(pt_connect):
        pt = i_pt + 1
        normal_dict[pt] = {}
    
        # Go through all connecting points
        for i_pt_o, pt_o in enumerate(conn_pts[:-1]):

            # Vector for this segment
            vec_1 = vert_co_list[pt_o-1] - vert_co_list[pt-1]
            vec_1.normalize()
            
            # Check against all other connecting segments
            for pt_p in conn_pts[i_pt_o+1:]:

                # Vector for this segment
                vec_2 = vert_co_list[pt_p-1] - vert_co_list[pt-1]
                vec_2.normalize()

                # Average
                vec_a = 0.5*(vec_1 + vec_2)

                # Cross
                vec_c = vec_1.cross(vec_2)

                # Plane's normal
                vec_n = vec_a.cross(vec_c)

                # Ensure that we are pointing in the same hemisphere as vec_1 or 2
                if vec_n.dot(vec_1) < 0:
                    vec_n *= -1.0

                # Store
                if pt_o in normal_dict[pt]:
                    normal_dict[pt][pt_o].append(vec_n)
                else:
                    normal_dict[pt][pt_o] = [vec_n]
                if pt_p in normal_dict[pt]:
                    normal_dict[pt][pt_p].append(-1.0*vec_n)
                else:
                    normal_dict[pt][pt_p] = [-1.0*vec_n]

                # Make a plane for viz
                '''
                vec_a.normalize()
                vec_c.normalize()
                r = 1.0
                verts = [vert_co_list[pt-1]+r*vec_a, vert_co_list[pt-1]+r*vec_c, vert_co_list[pt-1]-r*vec_a, vert_co_list[pt-1]-r*vec_c];
                # Make a new obj
                mesh_new = bpy.data.meshes.new("planes_%02d_%02d_%02d_mesh"%(pt,pt_o,pt_p))
                verts = [tuple(item) for item in verts]
                edges = [[0,1],[1,2],[2,3],[3,0]]
                faces = [[0,1,2,3]]
                mesh_new.from_pydata(verts,edges,faces)
                mesh_new.validate(verbose=False) # Important! and i dont know why
                mesh_new.update()
                obj_new = bpy.data.objects.new("planes_%02d_%02d_%02d"%(pt,pt_o,pt_p),mesh_new)
                bpy.context.scene.objects.link(obj_new)
                '''

    return normal_dict

# Main

def f_surface_sections(context, swc_filepath):

    print("> Running: f_surface_sections")

    # Get data from the SWC file
    pt_connect, vert_co_list = get_connections(swc_filepath)
    
    # Construct dividing planes
    normal_dict = construct_dividing_plane_normals(pt_connect, vert_co_list)

    # List of sections
    sec_list = []
    # Go through all the points
    for i_pt, conn_pts in enumerate(pt_connect):
        for conn_pt in conn_pts:
            # Check against duplicates
            if conn_pt > i_pt + 1:
                sec_list.append((i_pt+1,conn_pt))

    # Get the object
    ob_list = context.selected_objects

    if len(ob_list) == 1:
        ob = ob_list[0]

        # Create a list of face indexes in ob.data.polygons that need to be assigned to sections
        # As faces are assigned they are removed from this list
        face_idx_list = list(range(0,len(ob.data.polygons)))

        # Go through every section and assign faces to it
        sec_face_dict = {}
        for sec in sec_list:
            print("Assigning faces for section " + str(sec) + "...")
            
            # Coordinate of vertices
            v_co_0 = vert_co_list[sec[0]-1]
            v_co_1 = vert_co_list[sec[1]-1]

            # Max dist that faces are allowed to be away from either vertex
            max_dist = 1.5*(v_co_1-v_co_0).length

            # First find all faces that are within max_dist
            tri_list = []
            for f in face_idx_list:
        
                # Distances from each vert
                ctr = ob.data.polygons[f].center
                disps = [ctr - v_co_0, ctr - v_co_1]

                # Check that distances are allowed
                if disps[0].length <= max_dist and disps[1].length <= max_dist:
                    
                    # This is not sufficient - this just indicates that this face lies in the intersection region of two spheres!
                    # Now use the normals of the planes that define the regions to further constrain which elements are allowed
                    
                    # Flag
                    COUNT_FACE = True
                    
                    # Check each vertex
                    for i_vert in [0,1]:
                        
                        # Get all the planes from this section, that occur at this vertex
                        normal_tmp = normal_dict[sec[i_vert]]
                        if not sec[(i_vert+1)%2] in normal_tmp:
                            # This vertex has no other sections that connect to it!
                            # Skip and check the next section
                            continue
                        plane_normals = normal_tmp[sec[(i_vert+1)%2]]
                    
                        # Check all the normals
                        for normal in plane_normals:
                    
                            if normal.dot(disps[i_vert]) < 0:
                                COUNT_FACE = False
                                break
                
                        # Don't keep search for this face if we already violated one of the vertices
                        if COUNT_FACE == False:
                            break
                                
                    # Append
                    if COUNT_FACE == True:
                        tri_list.append(f)

            # Proceed using the "select more" = bpy.ops.mesh.select_more() function

            # First set the mode
            bpy.ops.object.mode_set(mode='EDIT')
            # Face selection mode
            context.tool_settings.mesh_select_mode = (False, False, True)
            # Deselect all
            bpy.ops.mesh.select_all(action='DESELECT')
            # Must be in object mode to select faces!
            bpy.ops.object.mode_set(mode='OBJECT')

            # Initially select the faces in tri_list which are closest to each of the vertices
            min_f0 = -1
            dist_f0 = -1
            min_f1 = -1
            dist_f1 = -1
            for f in tri_list:
                dist_v0 = (ob.data.polygons[f].center - v_co_0).length
                if dist_v0 < dist_f0 or dist_f0 == -1:
                    min_f0 = f
                    dist_f0 = dist_v0
                dist_v1 = (ob.data.polygons[f].center - v_co_1).length
                if dist_v1 < dist_f1 or dist_f1 == -1:
                    min_f1 = f
                    dist_f1 = dist_v1

            ob.data.polygons[min_f0].select = True
            ob.data.polygons[min_f1].select = True

            # Search for faces that belong to this section

            # Init list of faces that belong to this section
            sec_face_dict[sec] = []
            # Init list of indexes to delete from the face_idx_list to prevent double checking
            delete_list = []

            SEARCH = True
            while SEARCH:
                
                # Use the select more function
                # Must be in edit mode to use select more!
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_more()
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # Check each of the possible faces if it is selected
                new_faces = []
                delete_tri_list = []
                
                # Fast but worse
                '''
                for i_f,f in enumerate(tri_list):
                    if ob.data.polygons[f].select == True:
                '''
                # Slower but better
                for f, f_face in enumerate(ob.data.polygons):
                    if f_face.select == True:
                        if f in tri_list:
                            i_f = tri_list.index(f)
                            # Add it as a valid face
                            new_faces.append(f)
                            # Store for deletion from tri_list to prevent double counting at next iteration
                            delete_tri_list.append(i_f)
                        else:
                            # Turn off the face selection so that we do not continue to "grow" in this direction using the select more function
                            f_face.select = False

                # Check that there was something new added
                if len(new_faces) == 0:
                    SEARCH = False
                    break
                
                # Delete triangles from tri_list to prevent double counting in the future (+ faster!)
                delete_tri_list.reverse()
                for i_f in delete_tri_list:
                    del tri_list[i_f]

                # Add the new faces
                for f in new_faces:
                    sec_face_dict[sec].append(f)
                    delete_list.append(face_idx_list.index(f))

            # Select the region
            '''
            # First set the mode
            bpy.ops.object.mode_set(mode='EDIT')
            # Face selection mode
            context.tool_settings.mesh_select_mode = (False, False, True)
            # Deselect all
            bpy.ops.mesh.select_all(action='DESELECT')
            # Must be in object mode to select faces!
            bpy.ops.object.mode_set(mode='OBJECT')
            # Select
            for t in sec_face_dict[sec]:
                ob.data.polygons[t].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            '''

            # Do the deletion
            delete_list.sort()
            delete_list.reverse()
            for i_f in delete_list:
                del face_idx_list[i_f]

        ###
        # Finished assigning faces to sections!
        ###

        ###
        # Sanity check: are all faces assigned?
        ###

        f_ctr = 0
        for f_list in sec_face_dict.values():
            f_ctr += len(f_list)

        print("Number of faces to assign: " + str(len(ob.data.polygons)))
        print("Number of faces assigned: " + str(f_ctr))

        if len(ob.data.polygons) != f_ctr:
            print("WARNING! There are faces that have not been assigned to regions.")

        ###
        # Turn the dictionary into MCell regions
        ###

        print("Adding regions to MCell...")

        # Ensure object is active
        context.scene.objects.active = ob
        ob.select = True
        
        # First add the object to MCell
        preserve_selection_use_operator(bpy.ops.mcell.model_objects_add, ob)

        # Add the sections as regions
        existing_reg_names = [item.name for item in ob.mcell.regions.region_list]
        for sec_id,f_list in sec_face_dict.items():

            # Region name
            reg_name = "sc_%02d_%02d"%sec_id

            # Check that the region does not exist
            if reg_name in existing_reg_names:
                # Get region
                new_reg = ob.mcell.regions.region_list[reg_name]
                # Clear it
                new_reg.reset_region(context)
            else:
                # Make region
                ob.mcell.regions.add_region_by_name(context,reg_name)
                # Get region
                new_reg = ob.mcell.regions.region_list[reg_name]
        
            # Assign faces
            new_reg.set_region_faces(ob.data, f_list)

        # Update (but dont validate because who knows)
        ob.data.update()

    print("> Finished: f_surface_sections")




