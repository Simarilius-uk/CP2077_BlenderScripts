import bpy

# Ensure an object is selected and it's a mesh
obj = bpy.context.object
if obj is None or obj.type != 'MESH':
    raise ValueError("Please select a mesh object.")

# Get the mesh data
mesh = obj.data

# Extract vertices and faces
vertices = [(v.co.x, v.co.y, v.co.z) for v in mesh.vertices]
faces = [tuple(p.vertices) for p in mesh.polygons]

# Output the data in bm.from_pydata format
print("Vertices:")
print(vertices)
print("\nFaces:")
print(faces)

# Example usage for bm.from_pydata
print("\nExample bm.from_pydata command:")
print(f"bm.from_pydata({vertices}, [], {faces})")
