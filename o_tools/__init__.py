# ##### BEGIN GPL LICENSE BLOCK #####
#
#  O Tools — Quick rigging & playback utilities
#  Author: Olivier L with Grok
#  Version: 1.2.2
#  Blender: 4.2+
#
# ##### END GPL LICENSE BLOCK #####

from __future__ import annotations
import bpy
import json
from bpy.types import Operator, Panel, Context, Scene, SpaceView3D, PropertyGroup
from bpy.props import StringProperty, CollectionProperty
from typing import List, Dict, Any


bl_info = {
    "name": "O Tools",
    "author": "Olivier L with Grok",
    "version": (1, 2, 2),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar > Tool tab > O Tools",
    "description": "Bone Wire/In Front • Slow-Mo 5 fps • Profil Viewport (Flat+Black+Clean)",
}


# ———————————————————————— Serialized state storage ————————————————————————
class OToolsViewportStateItem(PropertyGroup):
    """Temporary storage for JSON-serialized viewport state."""
    data: StringProperty()  # JSON string


# ———————————————————————— Utilities ————————————————————————
def get_3d_views(context: Context) -> List[SpaceView3D]:
    """Return all active 3D view spaces in the current screen."""
    return [a.spaces.active for a in context.screen.areas if a.type == 'VIEW_3D']


def force_redraw_3d_views(context: Context) -> None:
    """Force redraw of all 3D viewports to avoid visual glitches."""
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()


# ———————————————————————— 1. Bone Wire / In Front Toggle ————————————————————————
class OTOOLS_OT_bone_wire_front(Operator):
    bl_idname = "otools.bone_wire_front"
    bl_label = "Bone Wire / In Front"
    bl_description = "Toggle selected armature Wire display + Show In Front"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context) -> set:
        arm = context.active_object
        if arm and arm.type == 'ARMATURE':
            arm.show_in_front = not arm.show_in_front
            arm.display_type = 'WIRE'
            state = "ON" if arm.show_in_front else "OFF"
            self.report({'INFO'}, f"Bone Wire/In Front: {state}")
            return {'FINISHED'}

        self.report({'WARNING'}, "No armature selected")
        return {'CANCELLED'}


# ———————————————————————— 2. Slow-Mo Toggle ————————————————————————
class OTOOLS_OT_toggle_slowmo(Operator):
    bl_idname = "otools.toggle_slowmo"
    bl_label = "Toggle Slow-Mo (5 fps)"
    bl_description = "Toggle between 5 fps and original scene FPS"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context) -> set:
        scene = context.scene
        prop = "otools_original_fps"

        if prop not in scene:
            scene[prop] = scene.render.fps

        current = scene.render.fps
        original = scene.get(prop, current)

        if current != 5:
            scene[prop] = current
            scene.render.fps = 5
            scene.render.fps_base = 1.0
            self.report({'INFO'}, f"Slow-Mo → 5 fps (original: {original})")
        else:
            scene.render.fps = original
            scene.render.fps_base = 1.0
            self.report({'INFO'}, f"Back to {original} fps")

        return {'FINISHED'}


# ———————————————————————— 3. Profil Viewport (Flat + Black + Clean) ————————————————————————
class OTOOLS_OT_viewport_profile(Operator):
    bl_idname = "otools.viewport_profile"
    bl_label = "Profil Viewport"
    bl_description = "Toggle clean silhouette mode (works from any viewport mode: Solid/Wireframe/Material/Rendered)"
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def _save_state(view: SpaceView3D) -> Dict[str, Any]:
        """Capture complete shading state of a single 3D view."""
        sh = view.shading
        ov = view.overlay
        return {
            'type'         : sh.type,                              # SOLID, WIREFRAME, MATERIAL, RENDERED
            'light'        : sh.light,
            'color_type'   : sh.color_type,
            'single_color' : tuple(sh.single_color) if sh.color_type == 'SINGLE' else (0.0, 0.0, 0.0),
            'show_overlays': ov.show_overlays,
            'show_gizmo'   : view.show_gizmo,
        }

    @staticmethod
    def _apply_profile(view: SpaceView3D) -> None:
        """Apply clean silhouette profile."""
        sh = view.shading
        ov = view.overlay
        sh.type = 'SOLID'
        sh.light = 'FLAT'
        sh.color_type = 'SINGLE'
        sh.single_color = (0.0, 0.0, 0.0)
        ov.show_overlays = False
        view.show_gizmo = False

    @staticmethod
    def _restore_state(view: SpaceView3D, state: Dict[str, Any]) -> None:
        """Restore previously saved shading state."""
        sh = view.shading
        ov = view.overlay
        sh.type = state['type']
        sh.light = state['light']
        sh.color_type = state['color_type']
        if sh.color_type == 'SINGLE':
            sh.single_color = state['single_color']
        ov.show_overlays = state['show_overlays']
        view.show_gizmo = state['show_gizmo']

    def execute(self, context: Context) -> set:
        views = get_3d_views(context)
        if not views:
            self.report({'WARNING'}, "No 3D View open")
            return {'CANCELLED'}

        scene = context.scene

        if scene.otools_viewport_saved:
            # Restore
            for view, item in zip(views, scene.otools_viewport_saved):
                state = json.loads(item.data)
                self._restore_state(view, state)
            count = len(views)
            self.report({'INFO'}, f"Profil Viewport disabled — {count} view(s) restored")
            scene.otools_viewport_saved.clear()
        else:
            # Apply profile
            scene.otools_viewport_saved.clear()
            for v in views:
                state = self._save_state(v)
                item = scene.otools_viewport_saved.add()
                item.data = json.dumps(state)
            for v in views:
                self._apply_profile(v)
            count = len(views)
            self.report({'INFO'}, f"Profil Viewport enabled — {count} view(s)")

        force_redraw_3d_views(context)
        return {'FINISHED'}


# ———————————————————————— Panel ————————————————————————
class OTOOLS_PT_panel(Panel):
    bl_label = "O Tools"
    bl_idname = "OTOOLS_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context: Context) -> None:
        layout = self.layout.column(align=True)
        layout.operator("otools.bone_wire_front", icon='ARMATURE_DATA')
        layout.operator("otools.toggle_slowmo", icon='PREVIEW_RANGE')
        layout.separator()
        layout.operator("otools.viewport_profile", icon='SHADING_RENDERED')


# ———————————————————————— Registration ————————————————————————
classes = (
    OTOOLS_OT_bone_wire_front,
    OTOOLS_OT_toggle_slowmo,
    OTOOLS_OT_viewport_profile,
    OTOOLS_PT_panel,
    OToolsViewportStateItem,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)
    Scene.otools_viewport_saved = CollectionProperty(type=OToolsViewportStateItem)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(Scene, "otools_viewport_saved"):
        del Scene.otools_viewport_saved


if __name__ == "__main__":
    register()