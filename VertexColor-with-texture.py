import bpy
bl_info = {
    'name': 'VertexColor-with-texture',
    'author': 'etcdk',
    'version': (1,0),
    'blender': (2, 80, 0),
    'location': '3D Viewport > Object',
    'description': 'Making vertex color by using texture.',
    'warning': '',
    'support': 'COMMUNITY',
    'doc_url': 'https://github.com/etcdk/VertexColor-with-texture',
    'tracker_url': 'https://github.com/etcdk/VertexColor-with-texture/issues',
    'category': 'Object'
}

class UV2COLOR_OT_Reducer(bpy.types.Operator):
    bl_idname = 'object.output_vertex_color'
    bl_label = 'Output vertexColor'
    bl_description = bl_info['description']+'\n"'+bl_info['name']+'" add-on'
    bl_space_type = "VIEW_3D"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if len(bpy.context.selected_objects)==0:
            ShowMessageBox('Objects are not selected.')
            return{'FINISHED'}
        print(bl_info['name'],'execute')
        col_layer=None
        for ob in bpy.context.selected_objects:
            if ob.type != 'MESH' or len(ob.data.polygons)==0 or len(ob.material_slots)==0: continue
            print(bl_info['name'],'object name =',ob.name,'polygons length =',len(ob.data.polygons))
            uv_layer=ob.data.uv_layers.active.data
            material_img=[None]*len(ob.material_slots)
            createdVertexColor=False
            for ms in range(len(ob.material_slots)):
                mat=ob.material_slots[ms].material
                if not (mat and mat.use_nodes):continue
                img=None
                for n in mat.node_tree.nodes:
                    if n.type == 'TEX_IMAGE':
                        img=n.image
                if img is None:
                    print(bl_info['name'],'this material has not texture. material index=',ms)
                    continue
                if img.size[0]==0 or img.size[1]==0:
                    print(bl_info['name'],'this material has invailed size texture. material index=',ms)
                    continue
                material_img[ms]=img
                createdVertexColor=True
            if createdVertexColor==False:continue
            col_layer=ob.data.vertex_colors.new(name=str(ob.name)+'-created_by_add_on')
            for poly in ob.data.polygons:
                img=material_img[poly.material_index]
                if img is None:continue
                color_elm=[0,0,0,0]#r,g,b,a
                for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                    uv_coords=uv_layer[loop_index].uv
                    u=round(uv_coords[0]*img.size[0])
                    v=img.size[1]-round(uv_coords[1]*img.size[1])
                    if u>=img.size[0]:u=img.size[0]-1
                    if v>=img.size[1]:v=img.size[1]-1
                    index=(v*img.size[0]+u)*img.channels
                    for c in range(img.channels):
                        color_elm[c]+=img.pixels[index+c]
                color=(color_elm[0]/poly.loop_total,color_elm[1]/poly.loop_total,color_elm[2]/poly.loop_total,color_elm[3]/poly.loop_total)
                for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                    col_layer.data[loop_index].color=color
        if col_layer is None:ShowMessageBox('VertexColor was not outputted.')
        print(bl_info['name'],'finish')
        return {'FINISHED'}

def ShowMessageBox(message = '', title = bl_info['name'], icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def menu_fn(self, context):
    self.layout.separator()
    self.layout.operator(UV2COLOR_OT_Reducer.bl_idname)
classes = [
    UV2COLOR_OT_Reducer,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_object.append(menu_fn)
    print(bl_info['name'],'enable')
def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_fn)
    for c in classes:
        bpy.utils.unregister_class(c)
if __name__ == '__main__':
    register()
