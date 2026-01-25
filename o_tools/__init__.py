# ##### BEGIN GPL LICENSE BLOCK #####
#
#  O Tools — Quick rigging & playback utilities
#  Author: Olivier L with Grok
#  Version: 1.3.0
#  Blender: 4.2+
#
# ##### END GPL LICENSE BLOCK #####

from __future__ import annotations
import bpy
import json
from bpy.types import Operator, Panel, Context, Scene, SpaceView3D, PropertyGroup, AddonPreferences
from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty
from typing import List, Dict, Any


bl_info = {
    "name": "O Tools",
    "author": "Olivier L with Grok",
    "version": (1, 3, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar > Tool tab > O Tools + Status Bar",
    "description": "Bone Wire/In Front • Smart Slow-Mo • Profil Viewport • Status Bar Filename",
}


# ———————————————————————— Addon Preferences ————————————————————————
class OToolsPreferences(AddonPreferences):
    """O Tools preferences – enable/disable individual features"""
    bl_idname = __name__

    enable_bone_wire: BoolProperty(
        name="Bone Wire / In Front",
        description="Show Bone Wire / In Front button in panel",
        default=True,
    )

    enable_slow_mo: BoolProperty(
        name="Smart Slow-Mo",
        description="Show Smart Slow-Mo button in panel",
        default=True,
    )

    enable_profil_viewport: BoolProperty(
        name="Profil Viewport",
        description="Show Profil Viewport button in panel",
        default=True,
    )

    enable_statusbar_filename: BoolProperty(
        name="Status Bar Filename",
        description="Display current .blend filename in status bar (right side)",
        default=True,
    )

    def draw(self, context: Context) -> None:
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Enable / Disable features:")
        col.prop(self, "enable_bone_wire")
        col.prop(self, "enable_slow_mo")
        col.prop(self, "enable_profil_viewport")
        col.prop(self, "enable_statusbar_filename")


# ———————————————————————— Serialized state storage ————————————————————————
class OToolsViewportStateItem(PropertyGroup):
    """Temporary storage for JSON-serialized viewport state."""
    data: StringProperty()


# ———————————————————————— Utilities ————————————————————————
def get_3d_views(context: Context) -> List[SpaceView3D]:
    """Return all active 3D view spaces in the current screen."""
    return [a.spaces.active for a in context.screen.areas if a.type == 'VIEW_3D']


def force_redraw_3d_views(context: Context) -> None:
    """Force redraw of all 3D viewports."""
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()


# ———————————————————————— Status Bar Filename draw callback ————————————————————————
def draw_filename_statusbar(self, context: Context) -> None:
    """Draw current .blend filename on the extreme right of the status bar."""
    prefs = context.preferences.addons[__name__].preferences
    if not prefs.enable_statusbar_filename:
        return

    layout = self.layout

    filepath = bpy.data.filepath
    filename = bpy.path.basename(filepath) if filepath else "Untitled.blend"

    if bpy.data.is_dirty:
        filename += " *"

    layout.alignment = 'RIGHT'
    layout.label(text=filename, icon='FILE_BLEND')


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


# ———————————————————————— 2. Smart Slow-Mo Toggle (×4 or ×5) ————————————————————————
class OTOOLS_OT_toggle_slowmo(Operator):
    """Toggle between original FPS and a clean integer multiple (24→6, 25→5, 30→6, etc.)"""
    bl_idname = "otools.toggle_slowmo"
    bl_label = "Toggle Slow-Mo"
    bl_description = "Toggle smart slow motion: ×4 for 24/48 fps, ×5 otherwise"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context) -> set:
        scene = context.scene

        if scene.otools_original_fps == 0:
            scene.otools_original_fps = scene.render.fps

        original = scene.otools_original_fps
        current = scene.render.fps

        if not scene.otools_slow_mo_active:
            slow_fps = original // 4 if original in (24, 48) else original // 5
            factor = 4 if original in (24, 48) else 5
            scene.render.fps = slow_fps
            scene.render.fps_base = 1.0
            scene.otools_slow_mo_active = True
            self.report({'INFO'}, f"Slow-Mo → {slow_fps} fps ({original} ÷ {factor})")
        else:
            scene.render.fps = original
            scene.render.fps_base = 1.0
            scene.otools_slow_mo_active = False
            self.report({'INFO'}, f"Back to {original} fps")

        return {'FINISHED'}


# ———————————————————————— 3. Profil Viewport (Flat + Black + Clean) ————————————————————————
class OTOOLS_OT_viewport_profile(Operator):
    bl_idname = "otools.viewport_profile"
    bl_label = "Profil Viewport"
    bl_description = "Toggle clean silhouette mode (works from any viewport mode)"
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def _save_state(view: SpaceView3D) -> Dict[str, Any]:
        sh = view.shading
        ov = view.overlay
        return {
            'type': sh.type,
            'light': sh.light,
            'color_type': sh.color_type,
            'single_color': tuple(sh.single_color) if sh.color_type == 'SINGLE' else (0.0, 0.0, 0.0),
            'show_overlays': ov.show_overlays,
            'show_gizmo': view.show_gizmo,
        }

    @staticmethod
    def _apply_profile(view: SpaceView3D) -> None:
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
            for view, item in zip(views, scene.otools_viewport_saved):
                state = json.loads(item.data)
                self._restore_state(view, state)
            count = len(views)
            self.report({'INFO'}, f"Profil Viewport disabled — {count} view(s) restored")
            scene.otools_viewport_saved.clear()
        else:
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
        prefs = context.preferences.addons[__name__].preferences
        col = self.layout.column(align=True)

        if prefs.enable_bone_wire:
            col.operator("otools.bone_wire_front", icon='ARMATURE_DATA')

        if prefs.enable_profil_viewport:
            col.operator("otools.viewport_profile", icon='SHADING_RENDERED')

        col.separator()

        if prefs.enable_slow_mo:
            col.operator("otools.toggle_slowmo", text="Slow-Mo (×4/×5)", icon='PREVIEW_RANGE')
            col.label(text=f"FPS: {context.scene.render.fps}")

# ———————————————————————— Registration ————————————————————————
classes = (
    OTOOLS_OT_bone_wire_front,
    OTOOLS_OT_toggle_slowmo,
    OTOOLS_OT_viewport_profile,
    OTOOLS_PT_panel,
    OToolsViewportStateItem,
    OToolsPreferences,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)
    Scene.otools_viewport_saved = CollectionProperty(type=OToolsViewportStateItem)
    bpy.types.Scene.otools_original_fps = IntProperty(name="Original FPS", default=0)
    bpy.types.Scene.otools_slow_mo_active = BoolProperty(name="Slow-Mo Active", default=False)
    bpy.types.STATUSBAR_HT_header.append(draw_filename_statusbar)


def unregister() -> None:
    bpy.types.STATUSBAR_HT_header.remove(draw_filename_statusbar)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(Scene, "otools_viewport_saved"):
        del Scene.otools_viewport_saved
    if hasattr(bpy.types.Scene, "otools_original_fps"):
        del bpy.types.Scene.otools_original_fps
    if hasattr(bpy.types.Scene, "otools_slow_mo_active"):
        del bpy.types.Scene.otools_slow_mo_active


if __name__ == "__main__":
    register()