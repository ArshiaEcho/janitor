"""Blender script: the Janitor broom as a pearl chrome object, in the Altocue house style. Run with `blender -b -P`."""

import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
OUT_PNG, OUT_GLB = args[0], args[1]
SIZE = int(args[2]) if len(args) > 2 else 2048
SAMPLES = int(args[3]) if len(args) > 3 else 256

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def rounded_polygon(corners, radius, steps=12):
    outline = []
    for index, corner in enumerate(corners):
        before, after = corners[index - 1], corners[(index + 1) % len(corners)]
        to_before, to_after = (before - corner).normalized(), (after - corner).normalized()
        angle = to_before.angle(to_after)
        offset = radius / math.tan(angle / 2)
        start, end = corner + to_before * offset, corner + to_after * offset
        bisector = (to_before + to_after).normalized()
        centre = corner + bisector * (radius / math.sin(angle / 2))
        first = math.atan2(*(start - centre).yx)
        last = math.atan2(*(end - centre).yx)
        sweep = (last - first + math.pi) % (2 * math.pi) - math.pi
        for step in range(steps + 1):
            theta = first + sweep * step / steps
            outline.append(centre + Vector((math.cos(theta), math.sin(theta))) * radius)
    return outline


def to_world(point, depth=0.0):
    return ((point.x - 50) * 0.05, -(point.y - 50) * 0.05, depth)


def prism(name, outline, thickness):
    verts = [to_world(p, -thickness / 2) for p in outline] + [to_world(p, thickness / 2) for p in outline]
    count = len(outline)
    faces = [list(range(count - 1, -1, -1)), list(range(count, 2 * count))]
    faces += [[i, (i + 1) % count, count + (i + 1) % count, count + i] for i in range(count)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    return obj


# The same broom as assets/logos/janitor.svg: a handle above a rounded head, the slanted cut through the bristles.
handle = prism("handle", rounded_polygon([Vector((44, 5)), Vector((56, 5)), Vector((56, 49)), Vector((44, 49))], 5.6), 0.5)
# The head is a band and four bristles, built apart so no boolean leaves a seam for the bevel to catch.
TILT = math.tan(math.radians(10))


def edge(y, side):
    return 29 - 12 * (y - 51) / 44 if side < 0 else 71 + 12 * (y - 51) / 44


def gap(y, centre, side):
    return centre + side * 2.5 - (y - 50) * TILT


band = prism("band", rounded_polygon([Vector((29, 51)), Vector((71, 51)), Vector((edge(70, 1), 70)), Vector((edge(70, -1), 70))], 5.0), 0.62)
pieces = [band]
bounds = [lambda y: edge(y, -1)]
for centre in (37, 50, 63):
    bounds += [lambda y, c=centre: gap(y, c, -1), lambda y, c=centre: gap(y, c, 1)]
bounds.append(lambda y: edge(y, 1))
for index in range(4):
    left, right = bounds[2 * index], bounds[2 * index + 1]
    corners = [Vector((left(64), 64)), Vector((right(64), 64)), Vector((right(95), 95)), Vector((left(95), 95))]
    pieces.append(prism(f"bristle{index}", rounded_polygon(corners, 2.6), 0.62))

for part in [handle, *pieces]:
    part.select_set(True)
bpy.context.view_layer.objects.active = band
bpy.ops.object.join()
mark = band

bevel = mark.modifiers.new("bevel", "BEVEL")
bevel.width = 0.3
bevel.segments = 14
bevel.limit_method = "ANGLE"
bevel.angle_limit = math.radians(25)
bevel.profile = 0.5
bevel.harden_normals = False
bpy.context.view_layer.objects.active = mark
bpy.ops.object.modifier_apply(modifier="bevel")
bpy.ops.object.shade_smooth(keep_sharp_edges=False) if False else None
for poly in mark.data.polygons:
    poly.use_smooth = True
weighted = mark.modifiers.new("weighted", "WEIGHTED_NORMAL")
weighted.keep_sharp = True
weighted.weight = 100
bpy.ops.object.modifier_apply(modifier="weighted")

mat = bpy.data.materials.new("pearl")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.86, 0.90, 0.92, 1)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.035
for name, value in (("Thin Film Thickness", 430.0), ("Thin Film IOR", 1.45)):
    if name in bsdf.inputs:
        bsdf.inputs[name].default_value = value
tree = mat.node_tree
geometry = tree.nodes.new("ShaderNodeNewGeometry")
ripple = tree.nodes.new("ShaderNodeTexNoise")
ripple.inputs["Scale"].default_value = 1.7
ripple.inputs["Detail"].default_value = 0.6
ripple.inputs["Roughness"].default_value = 0.35
bump = tree.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.15
bump.inputs["Distance"].default_value = 0.02
tree.links.new(geometry.outputs["Position"], ripple.inputs["Vector"])
tree.links.new(ripple.outputs["Fac"], bump.inputs["Height"])
tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
mark.data.materials.append(mat)
mark.rotation_euler = (math.radians(-26), math.radians(-38), math.radians(-6))

world = bpy.data.worlds.new("studio")
scene.world = world
world.use_nodes = True
nodes, links = world.node_tree.nodes, world.node_tree.links
texture = nodes.new("ShaderNodeTexEnvironment")
texture.image = bpy.data.images.load(args[4])
background = next(node for node in nodes if node.type == "BACKGROUND")
background.inputs["Strength"].default_value = 2.2
links.new(texture.outputs["Color"], background.inputs["Color"])

camera = bpy.data.cameras.new("camera")
camera.lens = 85
view = bpy.data.objects.new("camera", camera)
view.location = (0, 0, 15)
scene.collection.objects.link(view)
scene.camera = view

scene.render.engine = "CYCLES"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.device = "GPU"
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "METAL"
prefs.get_devices()
for device in prefs.devices:
    device.use = True
scene.render.film_transparent = True
scene.render.resolution_x = scene.render.resolution_y = SIZE
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "Standard"
scene.render.filepath = OUT_PNG
bpy.ops.render.render(write_still=True)

bpy.ops.object.select_all(action="DESELECT")
mark.select_set(True)
bpy.context.view_layer.objects.active = mark
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.export_scene.gltf(filepath=OUT_GLB, export_format="GLB", use_selection=True, export_apply=True)
