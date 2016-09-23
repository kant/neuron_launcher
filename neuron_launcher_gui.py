import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
    FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, \
    PointerProperty, StringProperty, BoolVectorProperty
from bpy.app.handlers import persistent
import mathutils
from bpy_extras.io_utils import ImportHelper

# Close end caps of an open mesh
from . import close_open_caps

# Assign surface regions to a mesh
from . import surface_sections

# Check for faces that may border other faces in regions not allowed by the connectivity of the SWC file
from . import check_bordering_surfaces

# Check for faces that may be falsely assigned to two regions
from . import check_double_assignments

# Color regions randomly
from . import color_regions

# Compartmentalize a mesh using the tetrahedral meshing method
from . import compartmentize

# Compartmentalize sections only + simultaneously create separate objects
from . import compartmentize_sc_only

# Explode compartments for visualisation if they exist
from . import explode

import os

# Register
def register():
    bpy.utils.register_module(__name__)

# Unregister
def unregister():
    bpy.utils.unregister_module(__name__)

# Main panel class
class NeuronLauncherVizPanel(bpy.types.Panel):
    bl_label = "Neuron Launcher - Model Geometry" # Panel name
    bl_space_type = "VIEW_3D" # where to put panel
    bl_region_type = "TOOLS" # sub location
    bl_category = "Neuron Launcher"

    @classmethod
    def poll(cls, context):
        return (context.scene is not None)
            
    def draw(self, context):
        context.scene.nrnlauncher.draw ( self.layout )

# Class to pick a file to set the cable model
class SetSWCFilePicker(bpy.types.Operator, ImportHelper):
    bl_idname = "nrnlauncher.set_swc_data_picker"
    bl_label = "Set SWC file"
    
    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
    
    filename_ext = ".swc" # allowed extensions
    
    # Get the filename
    def execute(self, context):
        
        # Set the SWC file
        context.scene.nrnlauncher.set_swc_file(self.filepath)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Class to close open caps
class CloseOpenCaps(bpy.types.Operator):
    bl_idname = "nrnlauncher.close_open_caps"
    bl_label = "Close open caps"

    def execute ( self, context ):
        print ( "Execute CloseOpenCaps" )
        close_open_caps.f_close_open_caps(context)
        return {"FINISHED"}
    
    def invoke ( self, context, event ):
        print ( "Invoke CloseOpenCaps" )
        close_open_caps.f_close_open_caps(context)
        return {"FINISHED"}

# Class to make surface regions
class MakeSurfaceRegions(bpy.types.Operator):
    bl_idname = "nrnlauncher.make_surface_regions"
    bl_label = "Make MCell surface regions"

    def execute ( self, context ):
        print ( "Execute MakeSurfaceRegions" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            surface_sections.f_surface_sections(context, res[1])
        else:
            raise SystemError(res[1])

        return {"FINISHED"}
    
    def invoke ( self, context, event ):
        print ( "Invoke MakeSurfaceRegions" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            surface_sections.f_surface_sections(context, res[1])
        else:
            raise SystemError(res[1])

        return {"FINISHED"}

#######################################################
#######################################################
# Checks for the surface mesh face assignments to regions
#######################################################
#######################################################

# Class to check the neighbors of faces against the connections in the cable model
class CheckBorderingFacesRegions(bpy.types.Operator):
    bl_idname = "nrnlauncher.check_bordering_faces_regions"
    bl_label = "Check bordering surface assignments"

    def execute ( self, context ):
        print ( "Execute CheckBorderingFacesRegions" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            check_bordering_surfaces.f_check_bordering_surfaces(context, res[1])
        else:
            raise SystemError(res[1])

        return {"FINISHED"}
    
    def invoke ( self, context, event ):
        print ( "Invoke CheckBorderingFacesRegions" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            check_bordering_surfaces.f_check_bordering_surfaces(context, res[1])
        else:
            raise SystemError(res[1])

        return {"FINISHED"}

# Class to check the neighbors of faces against the connections in the cable model
class CheckDoubleAssignments(bpy.types.Operator):
    bl_idname = "nrnlauncher.check_double_assignments"
    bl_label = "Check for double assigned faces"

    def execute ( self, context ):
        print ( "Execute CheckDoubleAssignments" )
        check_double_assignments.f_check_double_assignments(context)
        return {"FINISHED"}
    
    def invoke ( self, context, event ):
        print ( "Invoke CheckDoubleAssignments" )
        check_double_assignments.f_check_double_assignments(context)
        return {"FINISHED"}

#######################################################
#######################################################
# Materials and colors
#######################################################
#######################################################

# Class to make a material for each MCell region
class MCellRegionsToMaterials(bpy.types.Operator):
    bl_idname = "nrnlauncher.mcell_regions_to_materials"
    bl_label = "Assign material to each MCell region"

    def execute ( self, context ):
        print ( "Execute MCellRegionsToMaterials" )
        color_regions.f_mcell_reg_to_mat(context)
        return {"FINISHED"}
    
    def invoke ( self, context, event ):
        print ( "Invoke MCellRegionsToMaterials" )
        color_regions.f_mcell_reg_to_mat(context)
        return {"FINISHED"}

# Class to make random colors
class ColorRegions(bpy.types.Operator):
    bl_idname = "nrnlauncher.color_regions"
    bl_label = "Color regions randomly"

    def execute ( self, context ):
        print ( "Execute ColorRegions" )
        color_regions.f_color_regions(context)
        return {"FINISHED"}
    
    def invoke ( self, context, event ):
        print ( "Invoke ColorRegions" )
        color_regions.f_color_regions(context)
        return {"FINISHED"}

#######################################################
#######################################################
# Compartmentize classes
#######################################################
#######################################################

# Class to compartmentize
class Compartmentize(bpy.types.Operator):
    bl_idname = "nrnlauncher.compartmentize"
    bl_label = "Compartmentalize"

    def execute ( self, context ):
        print ( "Execute Compartmentize" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            compartmentize.f_compartmentize(context, res[1])
        else:
            raise SystemError(res[1])

        return {"FINISHED"}
    
    def invoke ( self, context, event ):
        print ( "Invoke Compartmentize" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            compartmentize.f_compartmentize(context, res[1])
        else:
            raise SystemError(res[1])        

        return {"FINISHED"}

# Class to compartmentize sections only and simultaneously create separate compartments
class CompartmentizeSCOnly(bpy.types.Operator):
    bl_idname = "nrnlauncher.compartmentize_sc_only"
    bl_label = "Compartmentalize Sections Only + Create as Objects"

    def execute ( self, context ):
        print ( "Execute CompartmentizeSCOnly" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            compartmentize_sc_only.f_compartmentize_sc_only(context, res[1])
        else:
            raise SystemError(res[1])

        return {"FINISHED"}
    
    def invoke ( self, context, event ):
        print ( "Invoke CompartmentizeSCOnly" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            compartmentize_sc_only.f_compartmentize_sc_only(context, res[1])
        else:
            raise SystemError(res[1])        

        return {"FINISHED"}

# Class to explode compartments if they have been created by CompartmentizeSCOnly
class ExplodeCompartments(bpy.types.Operator):
    bl_idname = "nrnlauncher.explode_compartments"
    bl_label = "Explode Compartments"

    def execute ( self, context ):
        print ( "Execute ExplodeCompartments" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            explode.f_explode(context, res[1], context.scene.nrnlauncher.explode_factor)
        else:
            raise SystemError(res[1])        

        return {"FINISHED"}
    
    def invoke ( self, context, event ):
        print ( "Invoke ExplodeCompartments" )
        res = context.scene.nrnlauncher.get_swc_filepath(context)
        if res[0] == 0:
            explode.f_explode(context, res[1], context.scene.nrnlauncher.explode_factor)
        else:
            raise SystemError(res[1])  

        return {"FINISHED"}

#######################################################
#######################################################
# Mesh object list
#######################################################
#######################################################

# Class to hold the object
class NeuronLauncherMeshObject(bpy.types.PropertyGroup):
    name = StringProperty ( name="Name", default="", description="Object Name" )
    swc_filename = StringProperty ( name="SWC filename", default="", description="SWC filename" )
    swc_filepath = StringProperty ( name="SWC filepath", default="", description="SWC filepath" )

    # Draw in list of objects
    def draw_item_in_row ( self, row ):
        col = row.column()
        col.label ( str(self.name) )
        col = row.column()
        col.label ( str(self.swc_filename) )

# Model object item to draw in the list
class NeuronLauncher_UL_object(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # The item will be a NeuronLauncherObjectPropertyGroup
        # Let it draw itself in a new row:
        item.draw_item_in_row ( layout.row() )

# Button to add model object
class NeuronLauncherObjectAdd(bpy.types.Operator):
    bl_idname = "nrnlauncher.mesh_object_add"
    bl_label = "Add a Mesh Object"
    bl_description = "Add a mesh object to model"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.nrnlauncher.add_mesh_object(context)
        return {'FINISHED'}

# Button to remove model object
class NeuronLauncherObjectRemove(bpy.types.Operator):
    bl_idname = "nrnlauncher.mesh_object_remove"
    bl_label = "Remove a Mesh Object"
    bl_description = "Remove a mesh object"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.nrnlauncher.remove_mesh_object(context)
        return {'FINISHED'}

# Button to remove all model objects
class NeuronLauncherObjectRemoveAll(bpy.types.Operator):
    bl_idname = "nrnlauncher.mesh_object_remove_all"
    bl_label = "Remove all Mesh Objects"
    bl_description = "Remove all mesh objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.nrnlauncher.remove_all_mesh_objects(context)
        return {'FINISHED'}


# Class for context that contains all the functions
class NeuronLauncherPropGroup(bpy.types.PropertyGroup):
    
    # List of mesh objects
    mesh_obj_list = CollectionProperty(type=NeuronLauncherMeshObject, name="Mesh List")
    active_object_index = IntProperty(name="Active Object Index", default=0)

    # The explode factor
    explode_factor = FloatProperty ( default=1.0, precision=1, description="Explode scale factor")

    # Booleans for showing things
    show_swc_files = BoolProperty( default = False )
    show_surf_mesh_tools = BoolProperty( default = False )
    show_compartmentize_tools = BoolProperty( default = False )
    show_material_tools = BoolProperty( default = False )

    # Draw
    def draw(self,layout):

        ###
        # List of model objects and corresponding SWC files
        ###

        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'

        if not self.show_swc_files:
            row.prop(self, "show_swc_files", icon='TRIA_RIGHT', text="Mesh objects and corresponding SWC files", emboss=False)
        else:
            row.prop(self, "show_swc_files", icon='TRIA_DOWN', text="Mesh objects and corresponding SWC files", emboss=False)

            row = box.row()
            row.label("Set SWC files corresponding to mesh objects", icon='CURVE_DATA')

            row = box.row()
            col = row.column()
        
            col.template_list("NeuronLauncher_UL_object", "",
                              self, "mesh_obj_list",
                              self, "active_object_index",
                              rows=2)
            
            col = row.column(align=True)
            col.operator("nrnlauncher.mesh_object_add", icon='ZOOMIN', text="")
            col.operator("nrnlauncher.mesh_object_remove", icon='ZOOMOUT', text="")
            col.operator("nrnlauncher.mesh_object_remove_all", icon='X', text="")
            
            # Set the swc file        
            row = box.row()
            row.operator("nrnlauncher.set_swc_data_picker")

        ###
        # MCell surface mesh tools
        ###

        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'

        if not self.show_surf_mesh_tools:
            row.prop(self, "show_surf_mesh_tools", icon='TRIA_RIGHT', text="Surface mesh tools", emboss=False)
        else:
            row.prop(self, "show_surf_mesh_tools", icon='TRIA_DOWN', text="Surface mesh tools", emboss=False)

            row = box.row()
            row.label("Tools for the MCell surface mesh", icon='SURFACE_DATA')

            row = box.row()
            split = box.split()
            col = split.column(align=True)
            col.label("Close open caps on the mesh")
            col.operator("nrnlauncher.close_open_caps")
                   
            row = box.row()
            split = box.split()
            col = split.column(align=True)
            col.label("Attempt to create surface regions")
            col.operator("nrnlauncher.make_surface_regions")

            row = box.row()
            split = box.split()
            col = split.column(align=True)
            col.label("Check surface region assignments")
            col.operator("nrnlauncher.check_bordering_faces_regions")
            col.operator("nrnlauncher.check_double_assignments")

        ###
        # Tools to divide a surface mesh into compartments
        ###

        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'

        if not self.show_compartmentize_tools:
            row.prop(self, "show_compartmentize_tools", icon='TRIA_RIGHT', text="Compartmentization tools", emboss=False)
        else:
            row.prop(self, "show_compartmentize_tools", icon='TRIA_DOWN', text="Compartmentization tools", emboss=False)

            row = box.row()
            row.label("Divide the MCell surface mesh into compartments", icon='PARTICLE_POINT')

            row = box.row()
            split = box.split()
            col = split.column(align=True)
            col.label("Create section and segment compartments in the surface mesh")
            col.label("Method: tetrahedral mesh for the volume (SLOW)")
            col.operator("nrnlauncher.compartmentize")

            row = box.row()
            split = box.split()
            col = split.column(align=True)
            col.label("Create only section compartments, and add as separate objects")
            col.operator("nrnlauncher.compartmentize_sc_only")

            row = box.row()
            split = box.split()
            col = split.column(align=True)
            col.label("Explode compartments for visualisation")
            col.operator("nrnlauncher.explode_compartments")
            col.prop(self, "explode_factor", text="Scale factor")

        ###
        # Tools to deal with materials/colors
        ###

        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'

        if not self.show_material_tools:
            row.prop(self, "show_material_tools", icon='TRIA_RIGHT', text="Visualisation Tools", emboss=False)
        else:
            row.prop(self, "show_material_tools", icon='TRIA_DOWN', text="Visualisation Tools", emboss=False)

            row = box.row()
            row.label("Materials and Colors", icon='COLOR')

            row = box.row()
            row.operator("nrnlauncher.mcell_regions_to_materials")

            row = box.row()
            row.operator("nrnlauncher.color_regions")

    #####
    # Function to set the SWC file for a selected mesh object
    #####

    # Set the cable model swc file
    def set_swc_file(self, fpath):
        self.mesh_obj_list[self.active_object_index].swc_filepath = fpath
        self.mesh_obj_list[self.active_object_index].swc_filename = os.path.basename(fpath)[:-4]

    ###
    # Function to return the swc file assigned to the active object, IF it exists
    ###

    def get_swc_filepath(self, context):
        obj_list = context.selected_objects
        if len(obj_list) != 1:
            return (1, "Too many objects selected. Please select only one object.")
        else:
            obj_name = obj_list[0].name

            # Check if this object has an swc file assigned
            for mesh_ob in self.mesh_obj_list:
                if mesh_ob.name == obj_name:
                    return (0, mesh_ob.swc_filepath)

            # If we get here, no SWC file exists for this object (none assigned)
            return (1, "No SWC file assigned for the selected object. Please assign an SWC file.")

    #####
    # Functions to add/remove mesh objects to identify which objects belong to which SWC files
    #####

    # Add a mesh object to the list
    def add_mesh_object(self, context):
        print("Adding mesh object to the list")

        # Get the active object
        obj_list = context.selected_objects
        if len(obj_list) > 0:
            for obj in obj_list:
                # Check by name if the object already is in the list
                current_object_names = [d.name for d in self.mesh_obj_list]
                if not obj.name in current_object_names:
                    new_obj = self.mesh_obj_list.add()
                    new_obj.name = obj.name

    # Remove a mesh object
    def remove_mesh_object(self, context):
        print("Removing mesh object from the list")

        self.mesh_obj_list.remove ( self.active_object_index )
        self.active_object_index -= 1
        if self.active_object_index < 0:
            self.active_object_index = 0

    # Remove all mesh objects
    def remove_all_mesh_objects(self, context):
        print("Removing all mesh objects")

        while len(self.mesh_obj_list) > 0:
            self.mesh_obj_list.remove ( 0 )
        self.active_object_index = 0
