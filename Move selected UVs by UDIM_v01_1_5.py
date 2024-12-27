bl_info = {
    "name": "Move to next UDIM",
    "author": "Max Puliero",
    "version": (1, 1, 5),
    "blender": (4, 3, 0),
    "location": "UV Editor",
    "description": "Move selected UVs by UDIM",
    "category": "UV",
}

import bpy
import bmesh
from bpy.types import Operator, AddonPreferences, Panel
from bpy.props import BoolProperty, EnumProperty

addon_keymaps = []  # Stores keymap references


class OBJECT_OT_move_selected_uvs(Operator):
    """Move selected UVs by UDIM"""
    bl_idname = "object.move_selected_uvs"
    bl_label = "Move Selected UVs"
    bl_options = {'REGISTER', 'UNDO'}

    direction: EnumProperty(
        name="Direction",
        description="Direction to move UVs",
        items=[
            ('RIGHT', "Right", "Move UVs to the right"),
            ('LEFT', "Left", "Move UVs to the left"),
            ('UP', "Up", "Move UVs upward"),
            ('DOWN', "Down", "Move UVs downward"),
        ],
        default='RIGHT',
    )

    def execute(self, context):
        direction_map = {
            'RIGHT': (1, 0),
            'LEFT': (-1, 0),
            'UP': (0, 1),
            'DOWN': (0, -1),
        }

        move_vector = direction_map[self.direction]
        moved = False

        # Iterate through selected objects
        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.active
                if not uv_layer:
                    continue  # Skip objects without active UV maps

                for face in bm.faces:
                    for loop in face.loops:
                        uv = loop[uv_layer]
                        if uv.select:
                            uv.uv.x += move_vector[0]
                            uv.uv.y += move_vector[1]
                            moved = True

                bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        if not moved:
            self.report({'WARNING'}, "No UVs were moved. Ensure UVs are selected.")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Selected UVs moved {self.direction.lower()} by 1 UDIM.")
        return {'FINISHED'}


class MPKeymapPreferences(AddonPreferences):
    bl_idname = __name__

    enable_shortcuts: BoolProperty(
        name="Enable UV Editor Shortcuts  [Ctrl ↑、↓、→、←]",
        default=True,
        description="Toggle keymap shortcuts for moving UVs"
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "enable_shortcuts")


class UV_PT_move_udim_panel(Panel):
    """Panel for moving UVs by UDIM"""
    bl_label = "Move by UDIM"
    bl_idname = "UV_PT_move_udim_panel"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Move by UDIM"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Move UVs:")

        col = layout.column()
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator(OBJECT_OT_move_selected_uvs.bl_idname, text="↑").direction = 'UP'

        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator(OBJECT_OT_move_selected_uvs.bl_idname, text="←").direction = 'LEFT'
        row.operator(OBJECT_OT_move_selected_uvs.bl_idname, text="→").direction = 'RIGHT'

        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator(OBJECT_OT_move_selected_uvs.bl_idname, text="↓").direction = 'DOWN'


def register_keymaps():
    """Register custom keymaps."""
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')

        directions = {
            'UP': 'UP_ARROW',
            'DOWN': 'DOWN_ARROW',
            'LEFT': 'LEFT_ARROW',
            'RIGHT': 'RIGHT_ARROW',
        }

        for direction, key in directions.items():
            kmi = km.keymap_items.new(OBJECT_OT_move_selected_uvs.bl_idname, key, 'PRESS', ctrl=True)
            kmi.properties.direction = direction
            addon_keymaps.append((km, kmi))


def unregister_keymaps():
    """Unregister custom keymaps."""
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    bpy.utils.register_class(OBJECT_OT_move_selected_uvs)
    bpy.utils.register_class(MPKeymapPreferences)
    bpy.utils.register_class(UV_PT_move_udim_panel)
    register_keymaps()


def unregister():
    unregister_keymaps()
    bpy.utils.unregister_class(UV_PT_move_udim_panel)
    bpy.utils.unregister_class(MPKeymapPreferences)
    bpy.utils.unregister_class(OBJECT_OT_move_selected_uvs)


if __name__ == "__main__":
    register()
