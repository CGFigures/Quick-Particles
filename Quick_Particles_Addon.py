# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This addon was generated with the Visual Scripting Addon.
# You can find the addon under https://blendermarket.com/products/serpens
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
sn_tree_name = "NodeTree"
addon_keymaps = []

bl_info = {
    "name": "Quick Particles",
    "author": "Joseph Manion",
    "description": "Adds hair particle systems and linked vertex groups to all verts in a mesh. Add-on interface created with Serpens",
    "location": "",
    "doc_url": "",
    "warning": "",
    "category": "General",
    "blender": (2,90,0),
    "version": (0,0,0)
}


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# IMPORTS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import bpy
from bpy.app.handlers import persistent


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# UTILITY FUNCTIONS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def sn_print(*text):
    text = ', '.join(map(str, text))
    print(text) # actual print command
    try: # try to find the area in which the addon is opened and add the print text
        for area in bpy.context.screen.areas:
            if area.type == "NODE_EDITOR":
                if area.spaces[0].node_tree:
                    if area.spaces[0].node_tree.bl_idname == "ScriptingNodesTree":
                        if sn_tree_name == area.spaces[0].node_tree.name:
                            bpy.context.scene.sn_properties.print_texts.add().text = str(text)

        for area in bpy.context.screen.areas:
            area.tag_redraw()
    except: pass
    
def get_enum_identifier(enumItems, name):
    for item in enumItems:
        if item.name == name:
            return item.identifier
            
    return ''

def report_sn_error(self,error):
    self.report({"ERROR"},message="There was an error when running this operation! It has been printed to the console.")
    print("START ERROR | Node Name: ",self.name," | (If you are this addons developer you might want to report this to the Serpens team) ")
    print("")
    print(error)
    print("")
    print("END ERROR - - - - ")
    print("")
    
def get_python_filepath():
    path = os.path.dirname(bpy.data.filepath)
    try:
        __file__
        exported = True
    except:
        exported = False
    if exported:
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    return path


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# CODE
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class SNA_OT_BTN_382ab4efc2(bpy.types.Operator):
    bl_idname = 'Quick Particles'
    bl_label = r"Quick Particles"
    bl_description = r"Add a Quick Particle System"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        try:
            pass
            import bpy
            
            #Collects ID of all selected objects and isolates the active object
            user_obs = bpy.context.selected_objects
            ao = bpy.context.active_object
            
            #Add vertex group to all the existing verts of the active object to use for particle system density (for clean boolean operations)
            bpy.ops.object.vertex_group_add()
            vert_group = ao.vertex_groups[-1].name #stores name of the vertex group created in case there are other vertex groups
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.editmode_toggle()
            
            #Default setup assuming two objects are selected. One to receive the system and one to act as the particle
            ps_obs = [ao] #list to organize active vs selected objects
            use_obj = True #Default assumption that only two objects are being used
            
            #If the user selects more than two objects then all objects except the active object will be put into a new collection for use
            if len(user_obs) > 2:
                use_obj = False #Used to indicate a collection should be used instead of an object
                particles_col = bpy.data.collections.new("Particles") #Creates new collection if more than two objects are selected
                bpy.context.collection.children.link(particles_col)
                for i in user_obs:
                    if i != ao:
                        particles_col.objects.link(i)    
            elif len(user_obs) == 2: #If the user only selects two objects then the active object receives the particle system
                for i in user_obs:
                    if i != ao: #places the non-active object into the second index in the list
                        ps_obs.append(i)  
            else: #If the user only selects one object then a default, smooth shaded, UV-sphere will be added and used as the particle
                bpy.ops.mesh.primitive_uv_sphere_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
                bpy.ops.object.shade_smooth()
                ps_obs.append(bpy.context.active_object)
            
            #Setting up the particle system
            ro = ps_obs[0] #defines the object receiving the particle system
            
            #Creates the particle system
            ps = ro.modifiers.new('mesh_particles','PARTICLE_SYSTEM')
            psys = ro.particle_systems[ps.name]
            psys.settings.use_advanced_hair = True
            psys.settings.count = len(ro.data.vertices) #Number of vertices in the receiving object
            psys.settings.type = 'HAIR'
            psys.settings.emit_from = 'VERT'
            psys.settings.use_modifier_stack = True
            psys.settings.use_emit_random = False
            
            if use_obj: #If use_obj is true then the second index in the list is used as the object
                psys.settings.render_type = 'OBJECT'
                psys.settings.instance_object = ps_obs[1]
            else: #If use_obj is False then the particle system is setup to use the automatically created collection of non-active selected objects
                psys.settings.render_type = 'COLLECTION'
                psys.settings.instance_collection = particles_col
                psys.settings.use_collection_pick_random = True #Automatically sets up collection to pick randomly to allow use of seeds
            
            if ao.scale[0] > 0: #Uses a default particle scale of 1/20 th of the x-scale for the object assuming it's greater than zero
                psys.settings.particle_size = ao.scale[0]/20
            else: #If the x-scale is 0 uses a default particle size of 0.05
                psys.settings.particle_size = 0.05
                
            psys.vertex_group_density = "Group" #Sets a density vertex group mapped to every vert of the receiving object to enable boolean interaction
            
            #Deselects everything
            bpy.ops.object.select_all(action='DESELECT')
            
            
        except Exception as exc:
            report_sn_error(self,exc)
        return {"FINISHED"}
        

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# PROPERTIES
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# REGISTER / UNREGISTER
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def register():
    bpy.utils.register_class(SNA_OT_BTN_382ab4efc2)

def unregister():
    global addon_keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(SNA_OT_BTN_382ab4efc2)
